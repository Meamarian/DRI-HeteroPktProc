import argparse
import csv
from pathlib import Path


PACKETS = ["128", "imix", "590", "1518"]


def make_command(direction, mpps, packet, duration, port):
    profile = "imix" if packet == "imix" else "fixed"
    pktsize = "128" if packet == "imix" else packet
    return (
        f"start -f traffic/trex_gnb_profile.py -p {port} -d {duration} -t "
        f"--direction {direction} --mpps {mpps} --pktsize {pktsize} --profile {profile} --offload 100"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    seen = set()
    rows = []
    with open(args.profile, newline="") as f:
        for row in csv.DictReader(f):
            hour = row["hour"]
            for direction in ("dl", "ul"):
                mpps = row.get(f"{direction}_mpps", "").strip()
                if not mpps:
                    continue
                for packet in PACKETS:
                    key = (direction, mpps, packet)
                    if args.unique and key in seen:
                        continue
                    seen.add(key)
                    rows.append((hour, direction, mpps, packet))
    if not rows:
        raise SystemExit("no hourly MPPS values found in the profile CSV")
    for hour, direction, mpps, packet in rows:
        print(f"hour={hour} direction={direction} packet={packet}")
        print(make_command(direction, mpps, packet, args.duration, args.port))


if __name__ == "__main__":
    main()
