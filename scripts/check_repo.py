from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "dpdk/README.md",
    "dpdk/config/power-paper.conf",
    "p4/README.md",
    "p4/SPLITS.md",
    "smartnic/README.md",
    "traffic/README.md",
    "traffic/trex_gnb_profile.py",
    "traffic/experiment_sweep.py",
    "experiments/README.md",
    "measurement/README.md",
    "measurement/tools/acpi.sh",
    "measurement/tools/msr.py",
    "EnergyTracer/README.md",
]


def main():
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        raise SystemExit("repository check failed: " + ", ".join(missing))

    sweep = (ROOT / "traffic/experiment_sweep.py").read_text()
    required_values = [
        "RATE_POINTS_MPPS = [7, 21, 35, 49, 63, 77, 100]",
        "FLOW_OFFLOAD_PERCENTAGES = [0, 30, 50, 70, 100]",
        "DAILY_PACKET_PROFILES = [128, \"imix\", 590, 1518]",
        "DIRECTIONS = [\"dl\", \"ul\"]",
        "default=5.0",
    ]
    missing_values = [value for value in required_values if value not in sweep]
    if missing_values:
        raise SystemExit("experiment sweep settings changed")

    print("repository check passed")


if __name__ == "__main__":
    main()
