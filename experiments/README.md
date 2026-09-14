# Experiment matrices

The CSV files in this directory list the operating points used by the paper. They keep traffic generation, placement, and DPDK power mode separate so that each run can be reproduced and logged independently.

## Controlled operating points

The standard offered-load points are 7, 21, 35, 49, 63, 77, and 100 MPPS.

- `flow/dl.csv`: DL SmartNIC-SA plus 30%, 50%, 70%, and 100% host offload.
- `flow/ul.csv`: UL SmartNIC-SA plus 30%, 50%, 70%, and 100% host offload.
- `function/dl.csv`: DL Split-0 through Split-4 under BW and PA.
- `function/ul.csv`: UL Split-0 through Split-3 under BW and PA.
- `latency/latency.csv`: the SmartNIC-only, host-only, and selected function-based RTD cases.

Power is recorded over a 20 s steady-state window after warm-up. The traffic-generator runtime must be long enough to include both stabilization and the measurement interval.

The placement itself is configured on the SmartNIC/DPDK side; the matrix controls the offered traffic and the BW/PA comparison. `traffic/run_matrix.py` generates the TRex console command for each row.

## Daily operating points

`daily/` handles the reconstructed 24-hour evaluation. Each hourly traffic load is represented by an independent one-minute TRex run rather than a continuous day-long replay. DL uses Split-3 and UL uses Split-2.

Paper-to-artifact mapping and expected reference results are listed in the root `README.md` and `docs/expected_results.md`.
