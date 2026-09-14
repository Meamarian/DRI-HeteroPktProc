# Reconstructed 24-hour experiment

The daily analysis uses hourly traffic characteristics and does not require a continuous 24-hour TRex run. Each hour is represented by an independent one-minute operating point. The measured result is then weighted by that hour's traffic volume.

The paper uses DL Split-3 and UL Split-2. Measurements are performed separately for DL and UL and later combined for mixed-direction profiles.

Packet profiles:

- 128 B
- IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B
- 590 B
- 1518 B

`make_runs.py` reads `data/daily/hourly_profile_template.csv` or a completed equivalent and prints one TRex console command per required operating point. Use `--unique` to remove duplicate direction/rate/packet combinations.

The template intentionally leaves the hourly MPPS values empty. The manuscript describes the source and reconstruction method but does not provide a numerical table of all 24 hourly rates. Use the exact hourly values from the experiment record or the source traffic dataset rather than values digitized approximately from a figure.
