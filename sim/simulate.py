"""Replay real G1 arm joint recordings in MuJoCo with physics, and render the calibration camera.

- Pelvis is fixed; all joints are driven by the menagerie's position actuators (PD control).
- Arm targets come from the benchmark's states.json (left = state[0:7], right = state[8:15]).
- Legs and waist are held at 0.
- Outputs: simulation video, per-frame ground-truth marker pixels, detected blobs, and
  commanded vs simulated joint angles.
"""
import json
import sys

import cv2
import imageio
import mujoco
import numpy as np

from build_scene import build

STATES = sys.argv[1] if len(sys.argv) > 1 else "../tasks/g1-slip-calibration/environment/public/example_a/capture_37/states.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "g1_sim"
MAX_SECONDS = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9

W, H = 640, 480
ARM_JOINTS = ["shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow",
              "wrist_roll", "wrist_pitch", "wrist_yaw"]


def load_states(path):
    rows = json.load(open(path))
    t = np.array([r["timestamp"] for r in rows], float)
    s = np.array([r["state"] for r in rows], float)
    return t - t[0], {"left": s[:, 0:7], "right": s[:, 8:15]}


def project(model, data, cam_id, points):
    """Pinhole projection of world points into the MuJoCo camera image (no distortion)."""
    pos = data.cam_xpos[cam_id]
    R = data.cam_xmat[cam_id].reshape(3, 3)          # columns: camera x, y, z in world
    pc = (points - pos) @ R                           # world -> camera frame
    depth = -pc[:, 2]                                 # camera looks along -z
    f = 0.5 * H / np.tan(np.deg2rad(model.cam_fovy[cam_id]) / 2)
    u = W / 2 + f * pc[:, 0] / depth
    v = H / 2 - f * pc[:, 1] / depth
    return np.column_stack([u, v]), depth


def detect_blobs(img):
    """Find bright green marker blobs: threshold in HSV, take connected-component centroids."""
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, (45, 120, 150), (85, 255, 255))
    n, _, stats, cents = cv2.connectedComponentsWithStats(mask)
    keep = stats[1:, cv2.CC_STAT_AREA] >= 4
    return cents[1:][keep]


def main():
    spec, model = build()
    data = mujoco.MjData(model)
    t_rec, q_rec = load_states(STATES)
    duration = min(t_rec[-1], MAX_SECONDS)

    act = {side: [model.actuator(f"{side}_{j}_joint").id for j in ARM_JOINTS] for side in ("left", "right")}
    qadr = {side: [model.jnt_qposadr[model.joint(f"{side}_{j}_joint").id] for j in ARM_JOINTS]
            for side in ("left", "right")}
    sites = {side: [model.site(f"{side}_m{k}").id for k in range(6)] for side in ("left", "right")}
    cam = model.camera("calib_cam").id

    # Start in the first recorded pose and let the PD controllers settle.
    for side in ("left", "right"):
        data.qpos[qadr[side]] = q_rec[side][0]
        data.ctrl[act[side]] = q_rec[side][0]
    mujoco.mj_forward(model, data)
    for _ in range(500):
        mujoco.mj_step(model, data)

    calib = mujoco.Renderer(model, H, W)
    over = mujoco.Renderer(model, H, W)
    ocam = mujoco.MjvCamera()
    ocam.lookat[:] = [0.1, 0.0, 0.85]
    ocam.distance, ocam.azimuth, ocam.elevation = 1.7, 145, -12

    fps = 30
    n_frames = int(duration * fps)
    steps_per_frame = int(round(1 / fps / model.opt.timestep))
    writer = imageio.get_writer(f"{OUT}.mp4", fps=fps, codec="libx264", quality=8,
                                macro_block_size=8)
    log = {"t": [], "cmd": {"left": [], "right": []}, "sim": {"left": [], "right": []},
           "truth_px": [], "depth": [], "detected": []}

    for i in range(n_frames):
        t = i / fps
        for side in ("left", "right"):
            target = np.array([np.interp(t, t_rec, q_rec[side][:, j]) for j in range(7)])
            data.ctrl[act[side]] = target
            log["cmd"][side].append(target.tolist())
        for _ in range(steps_per_frame):
            mujoco.mj_step(model, data)

        for side in ("left", "right"):
            log["sim"][side].append(data.qpos[qadr[side]].tolist())
        pts = np.vstack([data.site_xpos[sites[s]] for s in ("left", "right")])
        px, depth = project(model, data, cam, pts)

        calib.update_scene(data, camera=cam)
        img = calib.render()
        blobs = detect_blobs(img)
        over.update_scene(data, camera=ocam)
        ov = over.render()

        log["t"].append(t)
        log["truth_px"].append(px.tolist())
        log["depth"].append(depth.tolist())
        log["detected"].append(blobs.tolist())

        # Annotate calibration view: red ring = projected truth, white cross = detected blob.
        vis = img.copy()
        for (u, v) in px:
            cv2.circle(vis, (int(round(u)), int(round(v))), 9, (255, 60, 60), 1, cv2.LINE_AA)
        for (u, v) in blobs:
            cv2.drawMarker(vis, (int(round(u)), int(round(v))), (255, 255, 255),
                           cv2.MARKER_CROSS, 7, 1, cv2.LINE_AA)
        cv2.putText(ov, "MuJoCo physics: G1 replaying recorded arm joints", (12, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(vis, f"Calibration camera  t={t:5.2f}s  blobs={len(blobs)}/12", (12, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(vis, "red ring: projected truth   white cross: detected", (12, H - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        writer.append_data(np.hstack([ov, vis]))

    writer.close()
    json.dump(log, open(f"{OUT}_log.json", "w"))
    print("frames", n_frames)


if __name__ == "__main__":
    main()
