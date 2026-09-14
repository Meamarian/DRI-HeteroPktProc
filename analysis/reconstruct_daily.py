import argparse
import csv
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()
    agg = defaultdict(lambda: {"bytes": 0.0, "bw_j": 0.0, "pa_j": 0.0})
    with open(args.input, newline="") as f:
        for row in csv.DictReader(f):
            direction = row["direction"].strip().lower()
            packet = row["packet"].strip()
            processed_bytes = float(row["processed_bytes"])
            bw = float(row["bw_nj_per_byte"])
            pa = float(row["pa_nj_per_byte"])
            key = (direction, packet)
            agg[key]["bytes"] += processed_bytes
            agg[key]["bw_j"] += bw * processed_bytes * 1e-9
            agg[key]["pa_j"] += pa * processed_bytes * 1e-9
    out = []
    for (direction, packet), values in sorted(agg.items()):
        saved_j = values["bw_j"] - values["pa_j"]
        saved_wh = saved_j / 3600.0
        saved_pct = 100.0 * saved_j / values["bw_j"] if values["bw_j"] else 0.0
        avg_saved = saved_j * 1e9 / values["bytes"] if values["bytes"] else 0.0
        out.append({
            "direction": direction,
            "packet": packet,
            "avg_saved_nj_per_byte": f"{avg_saved:.6f}",
            "total_saved_wh": f"{saved_wh:.6f}",
            "saved_percent": f"{saved_pct:.6f}"
        })
    fields = ["direction", "packet", "avg_saved_nj_per_byte", "total_saved_wh", "saved_percent"]
    if args.output:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out)
    else:
        writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)


if __name__ == "__main__":
    main()
