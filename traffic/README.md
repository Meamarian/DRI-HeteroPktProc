# TRex traffic generation

The experiments use TRex v3.04 on a separate x86 traffic-generator server with two Mellanox ConnectX-5 dual-port 100 G NICs. Traffic reaches the DUT through an Arista 100 G switch.

[`trex_gnb_profile.py`](trex_gnb_profile.py) defines the packet formats and streams used by the paper. It supports DL GTP-U traffic, UL RLC/PDCP/SDAP traffic, UE/TEID variation up to 64k entries, flow-based SmartNIC/host tagging, fixed packet sizes, IMIX, controlled MPPS rates, and the 50 kpps latency probes.

A single operating point can be started directly from the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

## Experiment sweep

[`experiment_sweep.py`](experiment_sweep.py) keeps the traffic operating points directly in Python lists:

```python
RATE_POINTS_MPPS = [7, 21, 35, 49, 63, 77, 100]
FLOW_OFFLOAD_PERCENTAGES = [0, 30, 50, 70, 100]
DAILY_PACKET_PROFILES = [128, "imix", 590, 1518]
DIRECTIONS = ["dl", "ul"]
```

The script executes one operating point at a time and waits 5 s before starting the next one. The default daily sequence is DL first and then UL; within each direction it evaluates packet profiles in the paper order: 128 B, IMIX, 590 B, and 1518 B. Each daily operating point runs for 60 s by default.

Show the sequence without connecting to TRex:

```bash
python3 traffic/experiment_sweep.py --suite daily --dry-run
```

Run the sequence against a TRex server:

```bash
python3 traffic/experiment_sweep.py --suite daily --server 127.0.0.1 --port 0
```

The 5 s inter-run gap can be changed with `--gap`. The run duration can be changed with `--duration`.

For the short steady-state experiments, a 30 s traffic run leaves time for stabilization and the 20 s measurement window used in the paper:

```bash
python3 traffic/experiment_sweep.py --suite rate --direction dl --duration 30 --gap 5
```

## Flow-based assignment

`--offload` controls the share of traffic sent to the host path. The outer IPv4 Identification field carries the path tag.

The full flow sweep uses 0%, 30%, 50%, 70%, and 100% host offload:

```bash
python3 traffic/experiment_sweep.py --suite flow --direction dl --duration 30 --gap 5
```

## Function-based placement

Function placement is configured on the SmartNIC/DPDK side, not by the traffic generator. After selecting a DL or UL split on the DUT, run the normal rate sweep with the corresponding direction. This keeps traffic generation independent from the processing placement being evaluated.

## Latency

Use the latency suite to add the dedicated 50 kpps probe stream:

```bash
python3 traffic/experiment_sweep.py --suite latency --direction dl --rates 7 21 35 --duration 30 --gap 5
```

The reported value is round-trip delay between the TRex host and the DUT, not one-way gNB processing latency.

## Time-varying evaluation

The 24-hour analysis in the paper is reconstructed from independent operating-point measurements; it is not a continuous 24-hour replay. Each hourly load is represented by a one-minute TRex run and later weighted by the corresponding hourly traffic volume.

The repository therefore keeps the measurement points as Python lists rather than encoding a synthetic day-long curve. If the exact archived hourly rates are available, they can be passed directly with `--rates` or placed in the Python rate list before running the sequence.

The packet-size order used for the daily measurements is:

1. 128 B
2. IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B
3. 590 B
4. 1518 B

The daily evaluation uses DL Split-3 and UL Split-2.
