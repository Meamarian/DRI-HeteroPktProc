# TRex traffic generation

The experiments use TRex v3.04 on a separate x86 traffic-generator server with two Mellanox ConnectX-5 dual-port 100 G NICs. Traffic reaches the DUT through an Arista 100 G switch.

[`trex_gnb_profile.py`](trex_gnb_profile.py) is the common STL profile used for the paper operating points. The earlier IFIP TRex scripts can be fetched under `traffic/upstream/` for comparison with the original implementation.

The profile supports:

- DL GTP-U packet generation;
- UL RLC/PDCP/SDAP packet generation;
- UE/TEID variation up to 64k entries;
- flow-based SmartNIC/host tagging;
- fixed packet sizes and IMIX;
- controlled MPPS rates;
- dedicated latency probes.

## Controlled-rate example

From the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

The steady-state power measurements use a 20 s measurement window after the target load has stabilized. The example above uses a 30 s TRex duration only to leave room for warm-up and measurement. Record the actual warm-up and measurement intervals used on the testbed.

Generate commands for a matrix with:

```bash
python3 traffic/run_matrix.py experiments/flow/dl.csv --duration 30
```

## Flow-based assignment

`--offload` controls the share of traffic sent to the host path. The profile creates host-tagged and SmartNIC-tagged streams in the requested ratio, using the outer IPv4 Identification field as the offload tag.

For example, `--offload 30` sends 30% of the configured packet rate on the host-tagged path and 70% on the SmartNIC path.

## Latency probes

Use `--latency` to add the dedicated 50 kpps latency stream used in the RTD measurements. The SmartNIC-only DL reference is evaluated at 7, 21, and 35 MPPS. Host-only and selected hybrid placements use the operating points listed in `experiments/latency/latency.csv`.

The reported latency is round-trip delay between the TRex host and the DUT, not one-way gNB processing latency.

## Daily measurements

The daily analysis does not replay a continuous 24-hour trace. Each hourly traffic level is measured as an independent one-minute operating point. `../experiments/daily/make_runs.py` turns a completed hourly profile CSV into the required TRex commands.

Packet profiles used in the daily evaluation:

- 128 B;
- IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B;
- 590 B;
- 1518 B.

The daily evaluation uses DL Split-3 and UL Split-2.
