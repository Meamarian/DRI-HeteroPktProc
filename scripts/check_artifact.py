from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "CITATION.cff",
    "sources.lock",
    "dpdk/README.md",
    "dpdk/config/power-paper.conf",
    "p4/README.md",
    "p4/SPLITS.md",
    "smartnic/README.md",
    "traffic/README.md",
    "traffic/trex_gnb_profile.py",
    "experiments/README.md",
    "analysis/README.md",
    "measurement/README.md",
    "measurement/tools/acpi.sh",
    "measurement/tools/msr.py",
    "EnergyTracer/README.md",
    "docs/testbed.md",
    "docs/measurement.md",
    "docs/reproduction.md",
    "docs/expected_results.md",
]


def main():
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        raise SystemExit("missing files: " + ", ".join(missing))

    with open(ROOT / "data/daily/ul_dl_profiles.csv", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if len(rows) != 4:
        raise SystemExit("expected four mixed UL/DL profiles")

    expected = {
        "1": ("42.5", "57.5"),
        "2": ("40.0", "60.0"),
        "3": ("25.0", "75.0"),
        "4": ("10.0", "90.0"),
    }

    for row in rows:
        pair = expected.get(row["profile"])
        if pair != (row["ul_percent"], row["dl_percent"]):
            raise SystemExit("unexpected UL/DL profile table")

    print("artifact layout OK")


if __name__ == "__main__":
    main()
