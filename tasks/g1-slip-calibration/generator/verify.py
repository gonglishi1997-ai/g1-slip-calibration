"""Check that the committed task data are exactly what the generator produces.

    python generator/verify.py

Steps: check the source recordings against DATA_PROVENANCE.json, check the committed fixtures
against fixture-sha256.json, regenerate everything in a temporary directory, and compare file by
file. Binary files must match byte for byte. JSON files must have identical structure, keys,
integers, strings and booleans; floats may differ by at most 1e-10 (cross-platform rounding).
Exit code 0 means the data are reproducible.
"""

import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(HERE))

from build import build  # noqa: E402

FIXTURE_DIRS = ["environment/public", "tests/cases"]
ATOL = 1e-10


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equivalent(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= ATOL
    return a == b


def main():
    provenance = json.loads((TASK / "DATA_PROVENANCE.json").read_text())
    for episode in provenance["episodes"]:
        path = HERE / "sources" / f"episode_{episode['episode']}.json"
        assert sha256(path) == episode["sha256"], f"source recording changed: {path.name}"

    expected_hashes = json.loads((HERE / "fixture-sha256.json").read_text())
    committed = {
        str(p.relative_to(TASK)) for d in FIXTURE_DIRS for p in (TASK / d).rglob("*") if p.is_file()
    }
    assert committed == set(expected_hashes), "fixture file set differs from fixture-sha256.json"
    changed = [p for p, digest in expected_hashes.items() if sha256(TASK / p) != digest]
    assert not changed, f"fixtures differ from fixture-sha256.json: {changed[:5]}"

    identical, rounding_only, different = 0, 0, []
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp)
        for rel in sorted(committed):
            old, new = TASK / rel, Path(tmp) / rel
            if new.exists() and old.read_bytes() == new.read_bytes():
                identical += 1
            elif (
                new.exists()
                and old.suffix == ".json"
                and equivalent(json.loads(old.read_text()), json.loads(new.read_text()))
            ):
                rounding_only += 1
            else:
                different.append(rel)

    print(
        f"{len(committed)} files: {identical} byte-identical, {rounding_only} equal up to float rounding, "
        f"{len(different)} different"
    )
    for rel in different:
        print("  DIFFERENT", rel)
    sys.exit(1 if different else 0)


if __name__ == "__main__":
    main()
