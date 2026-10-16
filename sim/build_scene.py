"""Build a MuJoCo scene: Unitree G1 (fixed pelvis) + 6-marker targets on both wrists + a calibration camera.

Marker layout is copied from the benchmark's camera_model.py (MARKERS, in metres, target frame).
"""
import numpy as np
import mujoco

MENAGERIE = "menagerie/unitree_g1/scene.xml"

MARKERS = np.array([[-.09, -.055, -.025], [.08, -.06, .02], [.085, .065, -.03],
                    [-.07, .06, .04], [.015, .01, .075], [-.025, -.015, -.065]])

# Target frame relative to the wrist_yaw_link: a bit beyond the rubber hand.
TARGET_POS = [0.13, 0.0, 0.0]

# Calibration camera: in front of the robot, slightly above the shoulders, looking back at the torso.
CAM_POS = np.array([1.25, 0.0, 1.10])
CAM_LOOK_AT = np.array([0.15, 0.0, 0.80])
CAM_FOVY = 45.0


def look_at_quat(pos, target, up=(0, 0, 1)):
    """MuJoCo cameras look along their local -z axis with +y up."""
    z = pos - target
    z = z / np.linalg.norm(z)
    x = np.cross(up, z)
    x = x / np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.column_stack([x, y, z])
    q = np.zeros(4)
    mujoco.mju_mat2Quat(q, R.flatten())
    return q


def build():
    spec = mujoco.MjSpec.from_file(MENAGERIE)

    # Fix the pelvis in place: remove the floating base so the robot hangs at standing height.
    pelvis = spec.body("pelvis")
    for j in list(pelvis.joints):
        if j.type == mujoco.mjtJoint.mjJNT_FREE:
            spec.delete(j)

    # The menagerie keyframe assumes a floating base (36 qpos); drop it.
    for k in list(spec.keys):
        spec.delete(k)

    marker_mat = spec.add_material(name="marker_glow", rgba=[0.2, 1.0, 0.2, 1], emission=1.0)
    plate_mat = spec.add_material(name="plate", rgba=[0.15, 0.15, 0.18, 1])

    for side in ("left", "right"):
        wrist = spec.body(f"{side}_wrist_yaw_link")
        target = wrist.add_body(name=f"{side}_target", pos=TARGET_POS)
        # Thin cross-shaped frame so the markers visibly belong to one rigid target.
        target.add_geom(type=mujoco.mjtGeom.mjGEOM_BOX, size=[0.09, 0.01, 0.01],
                        material="plate", contype=0, conaffinity=0, mass=0.01)
        target.add_geom(type=mujoco.mjtGeom.mjGEOM_BOX, size=[0.01, 0.065, 0.01],
                        material="plate", contype=0, conaffinity=0, mass=0.01)
        for k, p in enumerate(MARKERS):
            target.add_geom(name=f"{side}_marker_{k}", type=mujoco.mjtGeom.mjGEOM_SPHERE,
                            size=[0.009, 0, 0], pos=p, material="marker_glow",
                            contype=0, conaffinity=0, mass=0.001)
            target.add_site(name=f"{side}_m{k}", pos=p, size=[0.002, 0, 0])

    spec.worldbody.add_camera(name="calib_cam", pos=CAM_POS,
                              quat=look_at_quat(CAM_POS, CAM_LOOK_AT), fovy=CAM_FOVY)
    model = spec.compile()
    return spec, model


if __name__ == "__main__":
    spec, model = build()
    print("nq", model.nq, "nu", model.nu, "ncam", model.ncam, "nsite", model.nsite, "dt", model.opt.timestep)
    with open("g1_calib_scene.xml", "w") as f:
        f.write(spec.to_xml())
