# Experiments

The paper evaluates a fixed set of traffic operating points while processing placement and DPDK power mode are configured on the DUT.

The traffic sequences are defined in [`../traffic/experiment_sweep.py`](../traffic/experiment_sweep.py). The main offered-load points are 7, 21, 35, 49, 63, 77, and 100 MPPS. Consecutive runs use a 5 s gap by default.

## Flow-based offloading

Flow-based experiments use the same rate sequence with 0%, 30%, 50%, 70%, and 100% host offload. The path tag is carried in the outer IPv4 Identification field.

```bash
python3 traffic/experiment_sweep.py --suite flow --direction dl --duration 30 --gap 5
python3 traffic/experiment_sweep.py --suite flow --direction ul --duration 30 --gap 5
```

## Function-based partitioning

Select the processing split on the SmartNIC/DPDK side, then run the 128-byte rate sweep for that direction:

```bash
python3 traffic/experiment_sweep.py --suite rate --direction dl --duration 30 --gap 5
python3 traffic/experiment_sweep.py --suite rate --direction ul --duration 30 --gap 5
```

The DL evaluation covers Split-0 through Split-4. The UL evaluation covers Split-0 through Split-3. BW and PA use the same traffic sequence so the comparison changes only the host power-management mode.

## Latency

Latency measurements add a 50 kpps probe stream to the background traffic.

```bash
python3 traffic/experiment_sweep.py --suite latency --direction dl --rates 7 21 35 --duration 30 --gap 5
```

The SmartNIC-only DL reference uses 7, 21, and 35 MPPS. Host and selected hybrid placements use the corresponding load points after the DUT placement is configured.

## 24-hour evaluation

Each hourly traffic level is measured as a one-minute TRex operating point. The hourly measurements are then weighted by the corresponding traffic volumes to build the 24-hour result.

The daily sweep evaluates DL and UL separately and follows the packet-size order used in the paper:

```python
[128, "imix", 590, 1518]
```

Run the sequence with:

```bash
python3 traffic/experiment_sweep.py --suite daily --duration 60 --gap 5
```

The daily placement uses DL Split-3 and UL Split-2. Supply the hourly rate sequence with `--rates` when running the daily measurements.
