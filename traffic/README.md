# TRex traffic generation

The reported experiments use TRex v3.04 on a separate x86 server with two Mellanox ConnectX-5 dual-port 100 G NICs. The traffic generator connects to the DUT through an Arista 100 G switch.

`trex_gnb_profile.py` is the consolidated STL profile for the paper operating points. The earlier IFIP TRex scripts can be fetched under `traffic/upstream/` for provenance and comparison.

The profile supports DL and UL packet templates, controlled MPPS rates, UE/TEID variation, flow-based host/SmartNIC tags, fixed packet sizes, IMIX, and dedicated latency probes.

## Controlled-rate example

From the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

The paper measures power over a 20 s steady-state window after warm-up. The traffic run must therefore remain active long enough to stabilize and cover the measurement interval. `run_matrix.py` defaults to a 30 s TRex duration only as a command-generation convenience; set `--duration` to the value used on the reproduction platform and record the actual warm-up and measurement windows.

Generate commands for a matrix with:

```bash
python3 traffic/run_matrix.py experiments/flow/dl.csv --duration 30
```

## Flow-based assignment

The profile creates host-tagged and SmartNIC-tagged streams in the ratio selected by `--offload`. The tag is carried in the outer IPv4 Identification field. `--offload 30`, for example, sends 30% of the configured packet rate on the host-tagged path and 70% on the SmartNIC-tagged path.

## Latency probes

Use `--latency` to add a dedicated 50 kpps latency stream to the background traffic. The SmartNIC-only DL reference uses 7, 21, and 35 MPPS. Host-only and selected hybrid placements use the standard 7, 21, 35, 49, 63, 77, and 100 MPPS operating points.

The resulting value is round-trip delay between the TRex host and the DUT, not one-way gNB processing latency.

## Daily reconstruction

The daily experiment is not a continuous 24-hour replay. Each hourly operating point is an independent one-minute TRex run. `../experiments/daily/make_runs.py` converts a completed hourly profile CSV into the required commands.

Daily packet profiles:

- 128 B;
- IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B;
- 590 B;
- 1518 B.

The daily analysis uses DL Split-3 and UL Split-2.
