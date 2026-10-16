"""Scoring of one campaign output against the hidden ground truth.

Every requirement is a separate named check, so a failed submission gets a full scorecard rather
than only its first error. The task is passed only if every check passes (see check.py).

Geometry is scored by behaviour, not by parameter equality: different parameter sets that predict
the same pixels are equally correct. Thresholds:

    static_projection    P95 reprojection error <= 2 px on held-out joint configurations,
                         per arm and per mount regime
    dynamic_projection   P95 <= 2 px at the true packet times, using the submitted clocks
    association          >= 95 % of true detections labelled correctly
    clutter              rejection precision and recall >= 0.90
    slip_count/boundary  right number of regimes; boundary within 3 frames
    clock_error          RMS <= 0.060 s, max <= 0.180 s
"""

import json
import struct
from dataclasses import dataclass, field

import numpy as np

from camera_model import LABELS, at_observed_rows, nominal_times, project_static
from kinematics import Trajectory

PIXEL_TOL = 2.0
CAMERA_BOUNDS = {
    "fx": (750, 1250),
    "fy": (750, 1250),
    "k1": (-0.18, 0.18),
    "k2": (-0.06, 0.06),
    "readout": (0.008, 0.035),
}
MOUNT_MAX_T, CAMERA_MAX_T, ZERO_MAX = 0.25, 3.5, 0.18


@dataclass
class Check:
    name: str
    scope: str  # "campaign", or a record name
    passed: bool
    detail: str = ""
    value: float | None = None


@dataclass
class Scorecard:
    checks: list = field(default_factory=list)

    def run(self, name, scope, fn):
        """Run one check. fn returns (passed, detail, value); any exception counts as a failure."""
        try:
            passed, detail, value = fn()
        except Exception as e:  # malformed numbers, negative depth, missing keys, ...
            passed, detail, value = False, f"{type(e).__name__}: {e}", None
        self.checks.append(Check(name, scope, bool(passed), detail, value))
        return bool(passed)

    def skip(self, name, scope, reason):
        self.checks.append(Check(name, scope, False, "not evaluated: " + reason))

    @property
    def passed(self):
        return bool(self.checks) and all(c.passed for c in self.checks)


# ---------------------------------------------------------------------------------------------
# helpers


def rigid(x, max_translation):
    """A proper 4x4 rigid transform within the translation bound."""
    a = np.asarray(x, float)
    assert a.shape == (4, 4) and np.isfinite(a).all(), "not a finite 4x4 matrix"
    assert np.max(abs(a[3] - [0, 0, 0, 1])) < 1e-5, "last row is not [0 0 0 1]"
    r = a[:3, :3]
    assert (
        np.max(abs(r.T @ r - np.eye(3))) < 1e-5 and abs(np.linalg.det(r) - 1) < 1e-5
    ), "rotation is not orthonormal with det 1"
    assert np.linalg.norm(a[:3, 3]) <= max_translation + 1e-6, "translation above its bound"
    return a


def p95(errors):
    return float(np.quantile(errors, 0.95))


def ok(passed, detail="", value=None):
    return passed, detail, value


def regime_masks(frames, segments, frame_count):
    for i, seg in enumerate(segments):
        stop = segments[i + 1]["start_frame"] if i + 1 < len(segments) else frame_count
        yield i, seg, (frames >= seg["start_frame"]) & (frames < stop)


# ---------------------------------------------------------------------------------------------
# campaign-level checks


def check_shared(out, truth):
    assert isinstance(out, dict) and set(out) == {"shared", "records"}, "top-level keys"
    shared = out["shared"]
    assert set(shared) == {"X_left", "X_right", "Y", "zeros", "camera"}, "shared keys"
    rigid(shared["Y"], CAMERA_MAX_T)
    for side in ("left", "right"):
        rigid(shared["X_" + side], MOUNT_MAX_T)
    assert set(shared["zeros"]) == {"left", "right"}, "zeros keys"
    for v in shared["zeros"].values():
        v = np.asarray(v, float)
        assert (
            v.shape == (2,) and np.isfinite(v).all() and np.max(abs(v)) <= ZERO_MAX + 1e-6
        ), "encoder zero out of bounds"
    assert set(shared["camera"]) == set(CAMERA_BOUNDS), "camera keys"
    for k, (lo, hi) in CAMERA_BOUNDS.items():
        v = shared["camera"][k]
        assert np.isfinite(v) and lo - 1e-8 <= v <= hi + 1e-8, f"camera {k} out of bounds"
    assert set(out["records"]) == set(truth["records"]), "record names"
    return ok(True)


# ---------------------------------------------------------------------------------------------
# record-level checks


class RecordGrader:
    def __init__(self, case, name, shared, pred, target):
        self.name, self.shared, self.pred, self.target = name, shared, pred, target
        self.private = json.loads((case / name / "private.json").read_text())
        self.manifest = json.loads((case / name / "manifest.json").read_text())
        self.traj = Trajectory(case / name / "states.json")
        blob = (case / name / "camera.bin").read_bytes()
        self.packet_rows = {
            struct.unpack_from("<I", blob, pos)[0]: struct.unpack_from("<f", blob, pos + 17)[0]
            for pos in range(8, len(blob), 25)
        }

    # -- mount regimes ---------------------------------------------------------------------
    def segments_valid(self):
        segs, truth = self.pred["segments"], self.target["segments"]
        assert isinstance(segs, list) and 1 <= len(segs) <= 2, "one or two segments required"
        for i, seg in enumerate(segs):
            assert isinstance(seg, dict) and set(seg) == {
                "start_frame",
                "X_left",
                "X_right",
            }, "segment keys"
            assert type(seg["start_frame"]) is int, "start_frame must be an integer"
            if i:
                assert seg["start_frame"] > segs[i - 1]["start_frame"], "segments out of order"
            for side in ("left", "right"):
                rigid(seg["X_" + side], MOUNT_MAX_T)
        assert segs[0]["start_frame"] == 0, "first segment must start at frame 0"
        for side in ("left", "right"):
            assert (
                np.max(abs(np.array(segs[0]["X_" + side]) - self.shared["X_" + side])) < 1e-5
            ), "first segment must use the shared mounts"
        return ok(True)

    def slip_count(self):
        n, m = len(self.pred["segments"]), len(self.target["segments"])
        return ok(n == m, f"{n} regimes, expected {m}", n)

    def slip_boundary(self):
        errs = [
            abs(s["start_frame"] - t["start_frame"])
            for s, t in zip(self.pred["segments"], self.target["segments"])
        ]
        return ok(max(errs) <= 3, f"boundary off by {max(errs)} frames", max(errs))

    def unaffected_arm(self):
        """The arm that did not slip must keep exactly the same mount (within 1e-5)."""
        segs, truth = self.pred["segments"], self.target["segments"]
        for i in range(1, len(truth)):
            for side in ("left", "right"):
                if (
                    np.max(
                        abs(
                            np.asarray(truth[i]["X_" + side])
                            - np.asarray(truth[i - 1]["X_" + side])
                        )
                    )
                    < 1e-12
                ):
                    diff = np.max(
                        abs(np.asarray(segs[i]["X_" + side]) - np.asarray(segs[i - 1]["X_" + side]))
                    )
                    if diff >= 1e-5:
                        return ok(
                            False, f"{side} mount changed by {diff:.2e} although it did not slip"
                        )
        return ok(True)

    def static_projection(self):
        worst, detail = 0.0, []
        for i, seg in enumerate(self.pred["segments"]):
            for side in ("left", "right"):
                probe = self.private["probes"][i][side]
                cal = self.shared | {"X_left": seg["X_left"], "X_right": seg["X_right"]}
                uv = project_static(probe["q"], probe["markers"], side, cal)
                err = p95(np.linalg.norm(uv - np.asarray(probe["pixels"]), axis=1))
                worst = max(worst, err)
                if err > PIXEL_TOL:
                    detail.append(f"regime {i} {side}: {err:.3f} px")
        return ok(worst <= PIXEL_TOL, "; ".join(detail) or f"worst P95 {worst:.3f} px", worst)

    # -- identities --------------------------------------------------------------------------
    def associations_valid(self):
        a = self.pred["associations"]
        assert isinstance(a, dict) and set(a) == set(self.target["associations"]), "packet ID set"
        assert all(v is None or v in LABELS for v in a.values()), "unknown identity label"
        used = set()
        for pid, boot, counter in zip(
            self.private["ids"], self.private["boots"], self.private["counters"]
        ):
            label = a[str(pid)]
            if label is not None:
                key = (boot, counter, label)
                assert key not in used, "identity assigned twice in one image"
                used.add(key)
        return ok(True)

    def association(self):
        a, truth = self.pred["associations"], self.target["associations"]
        good = [k for k, v in truth.items() if v is not None]
        acc = sum(truth[k] == a[k] for k in good) / len(good)
        return ok(acc >= 0.95, f"accuracy {acc:.4f}", acc)

    def clutter(self):
        a, truth = self.pred["associations"], self.target["associations"]
        bad = {k for k, v in truth.items() if v is None}
        rejected = {k for k, v in a.items() if v is None}
        if not bad:
            return ok(len(rejected) <= 1, f"{len(rejected)} packets rejected, no clutter present")
        precision = len(bad & rejected) / max(1, len(rejected))
        recall = len(bad & rejected) / len(bad)
        return ok(
            min(precision, recall) >= 0.9,
            f"precision {precision:.3f}, recall {recall:.3f}",
            min(precision, recall),
        )

    # -- clocks --------------------------------------------------------------------------------
    def clocks_valid(self):
        clocks = self.pred["clocks"]
        assert isinstance(clocks, dict) and set(clocks) == set(self.target["clocks"]), "boot ID set"
        counters, boots = np.asarray(self.private["counters"]), np.asarray(self.private["boots"])
        for boot in self.manifest["boots"]:
            c = clocks[str(boot["id"])]
            assert (
                set(c) == {"offset", "rate", "curvature"} and np.isfinite(list(c.values())).all()
            ), "clock keys"
            assert (
                abs(c["offset"] - boot["host_hint"]) <= 1.25 + 1e-6
            ), "offset too far from host_hint"
            assert (
                0.9 <= c["rate"] <= 1.1 and abs(c["curvature"]) <= 0.003 + 1e-6
            ), "rate/curvature bounds"
            s = counters[boots == boot["id"]] - boot["c0"]
            assert np.min(c["rate"] + 2 * c["curvature"] * s) > 0, "clock not increasing"
        return ok(True)

    def times(self):
        cal = self.shared | {"clocks": self.pred["clocks"]}
        return nominal_times(self.private["counters"], self.private["boots"], self.manifest, cal)

    def time_domain(self):
        """Nominal and exposure times of every packet (clutter included) must lie inside the states."""
        t = self.times()
        rows = np.array([self.packet_rows[int(pid)] for pid in self.private["ids"]], float)
        exposure = t + self.shared["camera"]["readout"] * (rows / 960 - 0.5)
        lo, hi = self.traj.times[0], self.traj.times[-1]
        inside = (
            np.isfinite(exposure).all()
            and np.all((t >= lo) & (t <= hi))
            and np.all((exposure >= lo) & (exposure <= hi))
        )
        return ok(inside, "" if inside else "packet or exposure time outside the state record")

    def clock_error(self):
        e = self.times() - np.asarray(self.private["times"])
        rmse, worst = float(np.sqrt(np.mean(e * e))), float(np.max(abs(e)))
        return ok(rmse <= 0.06 and worst <= 0.18, f"RMS {rmse:.4f} s, max {worst:.4f} s", rmse)

    def dynamic_projection(self):
        p = self.private
        truth = self.target["associations"]
        t = self.times()
        frames, clean, labels = (
            np.array(p["frames"]),
            np.array(p["clean_pixels"]),
            np.array(p["labels"]),
        )
        inliers = np.array([i for i, pid in enumerate(p["ids"]) if truth[str(pid)] is not None])
        cal = self.shared | {"clocks": self.pred["clocks"]}
        errors = []
        for _, seg, mask in regime_masks(frames[inliers], self.pred["segments"], p["frame_count"]):
            use = inliers[mask]
            if len(use):
                uv = at_observed_rows(
                    self.traj,
                    labels[use],
                    t[use],
                    clean[use, 1],
                    cal | {"X_left": seg["X_left"], "X_right": seg["X_right"]},
                )
                errors.extend(np.linalg.norm(uv - clean[use], axis=1).tolist())
        err = p95(errors)
        return ok(err <= PIXEL_TOL, f"P95 {err:.3f} px", err)


def grade_campaign(case, out):
    """Return a Scorecard for one campaign output (already parsed JSON)."""
    card = Scorecard()
    truth = json.loads((case / "answer.json").read_text())
    if not card.run("output_schema", "campaign", lambda: check_shared(out, truth)):
        return card
    shared = out["shared"]
    for name, target in truth["records"].items():
        pred = out["records"][name]
        if not card.run(
            "record_schema",
            name,
            lambda: ok(
                isinstance(pred, dict) and set(pred) == {"clocks", "associations", "segments"}
            ),
        ):
            continue
        r = RecordGrader(case, name, shared, pred, target)

        segments_ok = card.run("segments_valid", name, r.segments_valid)
        if segments_ok:
            count_ok = card.run("slip_count", name, r.slip_count)
            if count_ok:
                card.run("slip_boundary", name, r.slip_boundary)
                card.run("unaffected_arm", name, r.unaffected_arm)
                card.run("static_projection", name, r.static_projection)
            else:
                for c in ("slip_boundary", "unaffected_arm", "static_projection"):
                    card.skip(c, name, "wrong number of regimes")
        else:
            for c in ("slip_count", "slip_boundary", "unaffected_arm", "static_projection"):
                card.skip(c, name, "invalid segments")

        if card.run("associations_valid", name, r.associations_valid):
            card.run("association", name, r.association)
            card.run("clutter", name, r.clutter)
        else:
            card.skip("association", name, "invalid associations")
            card.skip("clutter", name, "invalid associations")

        if card.run("clocks_valid", name, r.clocks_valid):
            card.run("time_domain", name, r.time_domain)
            card.run("clock_error", name, r.clock_error)
            if segments_ok:
                card.run("dynamic_projection", name, r.dynamic_projection)
            else:
                card.skip("dynamic_projection", name, "invalid segments")
        else:
            for c in ("time_domain", "clock_error", "dynamic_projection"):
                card.skip(c, name, "invalid clocks")
    return card
