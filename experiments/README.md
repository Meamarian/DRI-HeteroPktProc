# Experiments

The CSV files in this directory define the operating points used in the paper. Traffic rate, processing placement, and DPDK power mode are kept separate so that each run can be launched and logged independently.

## Controlled operating points

The standard offered-load points are 7, 21, 35, 49, 63, 77, and 100 MPPS.

- `flow/dl.csv` — DL SmartNIC-SA plus 30%, 50%, 70%, and 100% host offload.
- `flow/ul.csv` — UL SmartNIC-SA plus 30%, 50%, 70%, and 100% host offload.
- `function/dl.csv` — DL Split-0 through Split-4 under BW and PA.
- `function/ul.csv` — UL Split-0 through Split-3 under BW and PA.
- `latency/latency.csv` — SmartNIC-only, host-only, and selected function-based RTD cases.

For the steady-state power measurements, TRex first reaches the target load and the system is allowed to stabilize. Power is then recorded over the 20 s window used in the paper.

Placement is configured on the SmartNIC/DPDK side. The CSV files specify the corresponding traffic operating point and BW/PA mode. Generate TRex console commands with:

```bash
python3 traffic/run_matrix.py experiments/flow/dl.csv
```

## Daily operating points

The `daily/` directory covers the reconstructed 24-hour analysis. Each hourly traffic level is measured as an independent one-minute TRex run; the day is reconstructed afterward from those operating points. DL uses Split-3 and UL uses Split-2.

See the root README for the paper-to-file map and [`../docs/expected_results.md`](../docs/expected_results.md) for the reference values reported in the paper.
