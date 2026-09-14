# Daily energy analysis

`reconstruct_daily.py` combines the independently measured hourly operating points used in the 24-hour evaluation. For each hour, it compares power-aware (`PA`) execution with busy waiting (`BW`) and accumulates the corresponding non-idle energy saving.

The input CSV uses one row per measured operating point:

```text
hour,direction,packet,processed_bytes,bw_nj_per_byte,pa_nj_per_byte
```

Run:

```bash
python3 analysis/reconstruct_daily.py hourly_results.csv
```

The script reports:

- average saved energy in nJ/B;
- total saved energy in Wh;
- percentage reduction relative to accumulated BW non-idle energy.

The percentage excludes the measured ACPI idle baseline of approximately 255–258 W, matching the accounting used in the paper.
