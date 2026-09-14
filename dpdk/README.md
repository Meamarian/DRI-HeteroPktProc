# DPDK host implementation

The host-side gNB application is based on EnergyTracer's `gNB_power_aware.c` and the DPDK `l3fwd-power` example. The imported source revision is recorded in [`../sources.lock`](../sources.lock).

The experiments use DPDK 20.08. Use a matching DPDK 20.08 source tree because the application depends on the `l3fwd-power` support files and power-management interfaces from that release.

## Prepare the source

From the repository root:

```bash
make fetch
```

If the upstream file is already present, rerun only the DPDK preparation step with:

```bash
python3 scripts/prepare_dpdk.py
```

This creates:

```text
dpdk/src/power_aware/main.c
dpdk/src/busy_wait/main.c
```

Both variants use the same gNB packet-processing path. The power-aware version enables the CPU frequency/idle policy used in the paper; the busy-wait version disables those decisions.

## Build with DPDK 20.08

Copy the selected `main.c` into a clean `l3fwd-power` example tree. For example:

```bash
cp dpdk/src/power_aware/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

For busy waiting:

```bash
cp dpdk/src/busy_wait/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

Keep `main.h`, `perf_core.c`, and `perf_core.h` from the same DPDK 20.08 example directory and build with the DPDK 20.08 toolchain.

Select the gNB table configuration at runtime with:

```bash
export GNB_CONFIG=/path/to/config_table.json
```

The configuration generator imported under `../p4/upstream/` can be used as the starting point for the 64k-entry DRB/TEID table.

## CPU and NUMA placement

Each SmartNIC VF is handled by a DPDK worker. Pin each worker to a core on the NUMA node local to its SmartNIC, and allocate packet/clone pools from NUMA-local hugepages.

The experiments use a maximum burst of 32 packets. Worker counts depend on traffic direction, placement, and offered load. Keep the exact CPU map with the run metadata.

## Power-aware parameters

The paper configuration is stored in [`config/power-paper.conf`](config/power-paper.conf):

```text
MIN_EMPTY_POLL_COUNT=10
PAUSE_THRESHOLD_US=10
GO_TO_SLEEP_THRESHOLD=300
GEAR1_RX_PKT_THRESHOLD=96
GEAR2_RX_PKT_THRESHOLD=64
GEAR3_RX_PKT_THRESHOLD=32
TREND_INC_LEVEL1=250
TREND_INC_LEVEL2=3
FREQ_UP_THRESHOLD=10000
EVENT_CHECKING_INTERVAL_MS=10
SCALING_PERIOD_MS=100
SCALING_DOWN_SLEEP_RATIO_THR=0.25
MAX_PKT_BURST=32
```

The uncore frequency is fixed at 1.4 GHz in the reported measurements.
