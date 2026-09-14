# Analysis

`reconstruct_daily.py` implements the daily non-idle energy accounting used in the paper. It expects one row per independently measured hourly operating point and computes the energy saved by power-aware execution relative to busy waiting.

Input CSV columns:

```text
hour,direction,packet,processed_bytes,bw_nj_per_byte,pa_nj_per_byte
```

Run:

```bash
python3 analysis/reconstruct_daily.py hourly_results.csv
```

The script reports average saved nJ/B, total saved Wh, and the percentage reduction in accumulated BW non-idle energy. The approximately 255–258 W idle baseline is not included in these percentages.
