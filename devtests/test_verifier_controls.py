"""Known-good and known-bad outputs for the grader.

The ground truth must pass; small harmless changes must pass; each listed defect must fail, and
must fail on the check that is meant to catch it. Runs in a few seconds; no solver needed.
"""

import copy
import json

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from conftest import TASK
from grading import grade_campaign

CASES = sorted(p for p in (TASK / "tests" / "cases").iterdir() if p.is_dir())


def truth(case):
    return json.loads((case / "answer.json").read_text())


def failing(card):
    return {c.name for c in card.checks if not c.passed}


def slip_record(out):
    return next((r for r, v in out["records"].items() if len(v["segments"]) == 2), None)


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_truth_passes(case):
    card = grade_campaign(case, truth(case))
    assert card.passed, failing(card)


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_rounding_noise_passes(case):
    out = truth(case)
    out["shared"]["Y"] = (
        np.array(out["shared"]["Y"]) + np.r_[np.full((3, 4), 1e-7), np.zeros((1, 4))]
    ).tolist()
    assert grade_campaign(case, out).passed


def mutate_unaffected_arm(out, kind):
    seg0, seg1 = out["records"][slip_record(out)]["segments"]
    side = "left" if np.allclose(seg0["X_left"], seg1["X_left"]) else "right"
    x = np.array(seg1["X_" + side])
    if kind == "shift_1mm":
        x[0, 3] += 1e-3
    else:
        x[:3, :3] = Rotation.from_rotvec([1e-3, 0, 0]).as_matrix() @ x[:3, :3]
    seg1["X_" + side] = x.tolist()


SLIP_DEFECTS = {
    # name: (mutation, check that must fail)
    "unaffected_arm_shift_1mm": (lambda o: mutate_unaffected_arm(o, "shift_1mm"), "unaffected_arm"),
    "unaffected_arm_rot_1mrad": (lambda o: mutate_unaffected_arm(o, "rot_1mrad"), "unaffected_arm"),
    "missed_slip": (
        lambda o: o["records"][slip_record(o)].__setitem__(
            "segments", o["records"][slip_record(o)]["segments"][:1]
        ),
        "slip_count",
    ),
    "boundary_off_by_4": (
        lambda o: o["records"][slip_record(o)]["segments"][1].__setitem__(
            "start_frame", o["records"][slip_record(o)]["segments"][1]["start_frame"] + 4
        ),
        "slip_boundary",
    ),
    "float_start_frame": (
        lambda o: o["records"][slip_record(o)]["segments"][1].__setitem__(
            "start_frame", float(o["records"][slip_record(o)]["segments"][1]["start_frame"])
        ),
        "segments_valid",
    ),
}

GENERAL_DEFECTS = {
    "clock_offset_0.1s": (
        lambda o: [
            c.__setitem__("offset", c["offset"] + 0.1)
            for r in o["records"].values()
            for c in r["clocks"].values()
        ],
        "clock_error",
    ),
    "everything_rejected": (
        lambda o: [
            r.__setitem__("associations", {k: None for k in r["associations"]})
            for r in o["records"].values()
        ],
        "association",
    ),
    "nothing_rejected": (
        lambda o: [
            r["associations"].__setitem__(k, "left:0")
            for r in o["records"].values()
            for k, v in r["associations"].items()
            if v is None
        ],
        "clutter",
    ),
    "arms_swapped": (
        lambda o: [
            r["associations"].__setitem__(
                k, v.replace("left", "#").replace("right", "left").replace("#", "right")
            )
            for r in o["records"].values()
            for k, v in r["associations"].items()
            if v
        ],
        "association",
    ),
    "camera_moved_5cm": (
        lambda o: o["shared"]["Y"][2].__setitem__(3, o["shared"]["Y"][2][3] + 0.05),
        "static_projection",
    ),
    "encoder_zeros_negated": (
        lambda o: [
            o["shared"]["zeros"].__setitem__(s, [-v for v in o["shared"]["zeros"][s]])
            for s in ("left", "right")
        ],
        "static_projection",
    ),
    "fx_out_of_bounds": (
        lambda o: o["shared"]["camera"].__setitem__("fx", 1300.0),
        "output_schema",
    ),
    "mount_translation_too_large": (
        lambda o: o["shared"]["X_left"][0].__setitem__(3, 0.3),
        "output_schema",
    ),
    "missing_record": (lambda o: o["records"].pop(next(iter(o["records"]))), "output_schema"),
    "extra_key": (
        lambda o: o["records"][next(iter(o["records"]))].__setitem__("note", 1),
        "record_schema",
    ),
}


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
@pytest.mark.parametrize("defect", list(GENERAL_DEFECTS) + list(SLIP_DEFECTS))
def test_defect_fails(case, defect):
    out = truth(case)
    if defect in SLIP_DEFECTS and slip_record(out) is None:
        pytest.skip("campaign has no slip")
    mutate, expected_check = (GENERAL_DEFECTS | SLIP_DEFECTS)[defect]
    mutate(out)
    card = grade_campaign(case, out)
    assert not card.passed
    assert expected_check in failing(card), failing(card)


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_duplicate_identity_fails(case):
    out = truth(case)
    name = next(iter(out["records"]))
    private = json.loads((case / name / "private.json").read_text())
    assoc, first = out["records"][name]["associations"], {}
    for pid, boot, counter in zip(private["ids"], private["boots"], private["counters"]):
        if assoc[str(pid)] is None:
            continue
        if (boot, counter) in first:
            assoc[str(pid)] = assoc[str(first[boot, counter])]
            break
        first[boot, counter] = pid
    assert "associations_valid" in failing(grade_campaign(case, out))
