# Experiments

The paper evaluates a fixed set of traffic operating points while processing placement and DPDK power mode are configured separately on the DUT.

The traffic-side sequences are defined in [`../traffic/experiment_sweep.py`](../traffic/experiment_sweep.py). The main rate points are 7, 21, 35, 49, 63, 77, and 100 MPPS. Consecutive runs are separated by a 5 s gap by default.

## Flow-based offloading

Flow-based experiments use the same rate sequence with 0%, 30%, 50%, 70%, and 100% host offload. The offload tag is carried in the outer IPv4 Identification field.

```bash
python3 traffic/experiment_sweep.py --suite flow --direction dl --duration 30 --gap 5
python3 traffic/experiment_sweep.py --suite flow --direction ul --duration 30 --gap 5
```

## Function-based partitioning

The processing split is selected on the SmartNIC/DPDK side. After configuring the DUT, run the corresponding 128-byte rate sweep:

```bash
python3 traffic/experiment_sweep.py --suite rate --direction dl --duration 30 --gap 5
python3 traffic/experiment_sweep.py --suite rate --direction ul --duration 30 --gap 5
```

The evaluated DL placements are Split-0 through Split-4. The evaluated UL placements are Split-0 through Split-3. BW and PA use the same traffic sequence; only the host power-management mode changes.

## Latency

Latency measurements add a 50 kpps probe stream to the background traffic. The SmartNIC-only DL reference uses 7, 21, and 35 MPPS; the host and selected hybrid cases use the required load points from the paper.

```bash
python3 traffic/experiment_sweep.py --suite latency --direction dl --rates 7 21 35 --duration 30 --gap 5
```

## Daily operating points

The 24-hour results are reconstructed from independent one-minute measurements rather than a continuous replay. The daily sweep evaluates DL and UL separately and uses the packet-size order reported in the paper:

```python
[128, "imix", 590, 1518]
```

Run the sequence with:

```bash
python3 traffic/experiment_sweep.py --suite daily --duration 60 --gap 5
```

The daily placement is DL Split-3 and UL Split-2. The exact hourly traffic volumes are applied when reconstructing the daily result; they are not synthesized by the traffic generator.
