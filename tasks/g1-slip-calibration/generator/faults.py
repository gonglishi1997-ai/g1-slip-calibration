"""Stage 2: add the faults the agent has to handle to a labelled base campaign.

For each record:
- mount slip (records 2 and 3 when `slips` is on): the arm with more detections gets a new mount
  at 56-72 % of its frames, rotated by ~N(0, 0.08 rad) per axis and moved 27-47 mm;
- ghost target: the stage-1 outliers, topped up to 24 % of packets, are replaced by projections of
  the same markers through a mount shifted by a fixed (26, -19, 11) mm, so clutter moves with the arm;
- every detection is re-measured from its noiseless projection with N(0, 0.2 px) noise;
- about 2 % of packets are sent twice (exact retransmissions) and packet order is shuffled;
- 90 perturbed held-out joint configurations per arm and regime are stored for grading.
"""

import copy
import json
import shutil
import struct
import sys
import zlib
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK / "environment"))
from kinematics import Trajectory
from camera_model import LABELS, predict, project_static, nominal_times


def save(p, x):
    p.write_text(json.dumps(x, separators=(",", ":")))


def create(source, target, seed, slips=True, clutter=True):
    """Read a stage-1 campaign from `source` and write the final campaign to `target`."""
    rng = np.random.default_rng(seed)
    target.mkdir(parents=True, exist_ok=True)
    campaign = json.loads((source / "campaign.json").read_text())
    save(target / "campaign.json", campaign)
    truth = json.loads((source / "answer.json").read_text())
    out = {"shared": truth["shared"], "records": {}}
    for ri, name in enumerate(campaign["records"]):
        src = source / name
        dst = target / name
        dst.mkdir(exist_ok=True)
        for file in ["states.json", "manifest.json"]:
            shutil.copy2(src / file, dst / file)
        tr = Trajectory(dst / "states.json")
        manifest = json.loads((dst / "manifest.json").read_text())
        a = truth["shared"] | truth["records"][name]
        blob = (src / "camera.bin").read_bytes()
        pk = {}
        for k in range(struct.unpack_from("<I", blob, 4)[0]):
            v = struct.unpack_from("<IBd2fI", blob, 8 + 25 * k)
            pk[v[0]] = v
        bootorder = {b["id"]: i for i, b in enumerate(manifest["boots"])}
        keys = sorted({(v[1], v[2]) for v in pk.values()}, key=lambda k: (bootorder[k[0]], k[1]))
        frame = {k: i for i, k in enumerate(keys)}
        segments = [{"start_frame": 0, "X_left": a["X_left"], "X_right": a["X_right"]}]
        counts = {
            side: sum(str(v).startswith(side) for v in a["associations"].values())
            for side in ["left", "right"]
        }
        # Zero or one mount slip; camera, clocks and the other arm stay unchanged.
        if slips and ri in (1, 2):
            side = max(counts, key=counts.get)
            cut = int(len(keys) * rng.uniform(0.56, 0.72))
            x = np.array(a["X_" + side])
            x[:3, :3] = Rotation.from_rotvec(rng.normal(0, 0.08, 3)).as_matrix() @ x[:3, :3]
            move = rng.normal(size=3)
            x[:3, 3] += move / np.linalg.norm(move) * rng.uniform(0.027, 0.047)
            new = copy.deepcopy(segments[0])
            new["start_frame"] = cut
            new["X_" + side] = x.tolist()
            segments.append(new)
        # Every packet gets a label; outliers borrow a random represented identity so that their
        # ghost projection follows a real marker.
        labels = []
        boots = []
        counters = []
        ids = []
        fis = []
        origin = (
            json.loads((src / "private.json").read_text())
            if (src / "private.json").exists()
            else {}
        )
        original_by_id = dict(zip(origin.get("ids", []), origin.get("original_labels", [])))
        represented = [l for l in LABELS if l in set(a["associations"].values())]
        for pid, v in pk.items():
            ids.append(pid)
            boots.append(v[1])
            counters.append(v[2])
            fis.append(frame[v[1], v[2]])
            label = a["associations"][str(pid)] or rng.choice(represented)
            if not clutter and pid in original_by_id:
                label = original_by_id[pid]
            labels.append(label)
        fis = np.array(fis)
        boots = np.array(boots)
        counters = np.array(counters)
        # Noiseless projections, regime by regime.
        uv = np.empty((len(ids), 2))
        for si, seg in enumerate(segments):
            mask = (fis >= seg["start_frame"]) & (
                fis < (segments[si + 1]["start_frame"] if si + 1 < len(segments) else len(keys))
            )
            cal = a | {k: seg[k] for k in ("X_left", "X_right")}
            ix = np.flatnonzero(mask)
            uv[ix] = predict(tr, np.array(labels)[ix], counters[ix], boots[ix], manifest, cal)
        # Ghost constellation: same kinematics, wrong mount.
        ghost = copy.deepcopy(a)
        for side in ["left", "right"]:
            x = np.array(a["X_" + side])
            x[:3, 3] += np.array([0.026, -0.019, 0.011])
            ghost["X_" + side] = x.tolist()
        guv = predict(tr, labels, counters, boots, manifest, ghost)
        bad = np.array([a["associations"][str(i)] is None for i in ids])
        extra = np.flatnonzero(~bad)
        rng.shuffle(extra)
        if clutter:
            bad[extra[: max(0, round(0.24 * len(ids)) - bad.sum())]] = True
        else:
            bad[:] = False
        # Measurements, retransmissions, CRC-protected packets.
        associations = {}
        packets = []
        for j, pid in enumerate(ids):
            measured = (guv[j] if bad[j] else uv[j]) + rng.normal(0, 0.20, 2)
            associations[str(pid)] = None if bad[j] else labels[j]
            payload = struct.pack("<IBd2f", pid, int(boots[j]), counters[j], *measured)
            p = payload + struct.pack("<I", zlib.crc32(payload))
            packets.append(p)
            if rng.random() < 0.02:
                packets.append(p)
        rng.shuffle(packets)
        (dst / "camera.bin").write_bytes(
            struct.pack("<4sI", b"G1UA", len(packets)) + b"".join(packets)
        )
        rec = {"clocks": a["clocks"], "associations": associations, "segments": segments}
        out["records"][name] = rec
        # Held-out probes per regime, for both arms (also an arm that this record never shows).
        probes = []
        for seg in segments:
            probe = {}
            for side in ["left", "right"]:
                q = tr.q[side][rng.integers(len(tr.times), size=90)] + rng.uniform(
                    -0.1, 0.1, (90, 7)
                )
                m = rng.integers(6, size=90)
                probe[side] = {
                    "q": q.tolist(),
                    "markers": m.tolist(),
                    "pixels": project_static(
                        q, m, side, a | {k: seg[k] for k in ["X_left", "X_right"]}
                    ).tolist(),
                }
            probes.append(probe)
        private = {
            "ids": ids,
            "boots": boots.tolist(),
            "counters": counters.tolist(),
            "frames": fis.tolist(),
            "times": nominal_times(counters, boots, manifest, a).tolist(),
            "probes": probes,
            "frame_count": len(keys),
            "labels": labels,
            "clean_pixels": uv.tolist(),
            "ghost_pixels": guv.tolist(),
        }
        save(dst / "private.json", private)
    save(target / "answer.json", out)
