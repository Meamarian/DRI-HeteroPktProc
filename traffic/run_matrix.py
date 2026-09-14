import argparse
import csv
import shlex


def command(row, profile_path, port, duration):
    direction = row["direction"]
    mpps = row["mpps"]
    packet = row.get("packet", "128")
    offload = row.get("offload", "100")
    profile = "imix" if packet.lower() == "imix" else "fixed"
    pktsize = "128" if profile == "imix" else packet
    args = [
        "start",
        "-f",
        profile_path,
        "-p",
        str(port),
        "-d",
        str(duration),
        "-t",
        "--direction",
        direction,
        "--mpps",
        mpps,
        "--pktsize",
        pktsize,
        "--profile",
        profile,
        "--offload",
        offload,
    ]

    if row.get("latency", "0") in {"1", "true", "True", "yes"}:
        args.append("--latency")

    return " ".join(shlex.quote(value) for value in args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix")
    parser.add_argument("--profile-path", default="traffic/trex_gnb_profile.py")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()

    with open(args.matrix, newline="") as handle:
        for row in csv.DictReader(handle):
            print(command(row, args.profile_path, args.port, args.duration))


if __name__ == "__main__":
    main()
