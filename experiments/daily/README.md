# 24-hour workload reconstruction

The daily result is reconstructed from hourly operating points; it is not a continuous 24-hour TRex run. Each hourly traffic level is measured with an independent one-minute run, and the resulting measurements are weighted by the traffic volume for that hour.

The daily evaluation uses:

- DL Split-3;
- UL Split-2;
- 128 B packets;
- IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B;
- 590 B packets;
- 1518 B packets.

DL and UL are measured separately and combined afterward when constructing mixed-direction profiles.

`make_runs.py` reads `data/daily/hourly_profile_template.csv` (or a completed copy) and prints the TRex command for each required operating point. Use `--unique` when the same direction/rate/packet combination appears more than once and only one measurement is needed.

The template leaves the hourly MPPS values empty because the paper does not print the complete 24-point numerical series. Fill it with the archived experiment values or the original traffic dataset rather than approximating values from the plot.
