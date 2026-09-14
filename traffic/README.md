# TRex traffic generation

The experiments use TRex v3.04 on a separate x86 traffic-generator server with two Mellanox ConnectX-5 dual-port 100 G NICs. Traffic reaches the DUT through an Arista 100 G switch.

[`trex_gnb_profile.py`](trex_gnb_profile.py) defines the packet formats and streams used by the paper. It supports DL GTP-U traffic, UL RLC/PDCP/SDAP traffic, UE/TEID variation up to 64k entries, SmartNIC/host path tagging, fixed packet sizes, IMIX, controlled MPPS rates, and 50 kpps latency probes.

A single operating point can be started from the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

## Experiment sweep

[`experiment_sweep.py`](experiment_sweep.py) stores the experiment points directly in Python:

```python
RATE_POINTS_MPPS = [7, 21, 35, 49, 63, 77, 100]
FLOW_OFFLOAD_PERCENTAGES = [0, 30, 50, 70, 100]
DAILY_PACKET_PROFILES = [128, "imix", 590, 1518]
DIRECTIONS = ["dl", "ul"]
```

The runner sends one operating point, waits 5 s, and starts the next one. The daily sequence evaluates DL first and then UL. Within each direction, packet profiles follow the paper order: 128 B, IMIX, 590 B, and 1518 B. Each daily operating point runs for 60 s by default.

Preview the sequence:

```bash
python3 traffic/experiment_sweep.py --suite daily --dry-run
```

Run the sequence against TRex:

```bash
python3 traffic/experiment_sweep.py --suite daily --server 127.0.0.1 --port 0
```

Use `--gap` to set the delay between operating points and `--duration` to set the run time.

For short steady-state experiments, a 30 s traffic run provides time for stabilization followed by the 20 s power-measurement window:

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

Function placement is configured on the SmartNIC/DPDK side. After selecting a DL or UL split on the DUT, run the standard rate sweep for that direction. Using the same traffic sequence across placements makes the performance and power comparison consistent.

## Latency

Use the latency suite to add the dedicated 50 kpps probe stream:

```bash
python3 traffic/experiment_sweep.py --suite latency --direction dl --rates 7 21 35 --duration 30 --gap 5
```

The reported metric is round-trip delay between the TRex host and the DUT.

## 24-hour evaluation

Each hourly traffic load is measured as a one-minute TRex operating point. The hourly measurements are weighted by the corresponding traffic volumes and combined into the 24-hour result.

Provide the hourly rate sequence with `--rates`. The runner applies that sequence to DL and UL and evaluates packet profiles in this order:

1. 128 B
2. IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B
3. 590 B
4. 1518 B

The daily evaluation uses DL Split-3 and UL Split-2.
