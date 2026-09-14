# DPDK host implementation

The host-side gNB application uses DPDK 20.08 and the `l3fwd-power` framework. The repository prepares two versions of the same packet-processing path:

- `power_aware`: adaptive CPU frequency and idle control;
- `busy_wait`: the DPDK polling baseline.

## Prepare the source

From the repository root:

```bash
make fetch
```

To regenerate the DPDK files after changing the power configuration:

```bash
python3 scripts/prepare_dpdk.py
```

This creates:

```text
dpdk/src/power_aware/main.c
dpdk/src/busy_wait/main.c
```

## Build with DPDK 20.08

Copy the selected `main.c` into a DPDK 20.08 `l3fwd-power` example tree. For example:

```bash
cp dpdk/src/power_aware/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

For the busy-wait baseline:

```bash
cp dpdk/src/busy_wait/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

Use `main.h`, `perf_core.c`, and `perf_core.h` from the same DPDK 20.08 example directory and build with the DPDK 20.08 toolchain.

Select the gNB table configuration at runtime with:

```bash
export GNB_CONFIG=/path/to/config_table.json
```

The P4 configuration generator under `../p4/upstream/` can be used to prepare the 64k-entry DRB/TEID table.

## CPU and NUMA placement

Each SmartNIC VF is handled by a DPDK worker. Pin each worker to a CPU core on the NUMA node local to its SmartNIC and allocate packet/clone pools from NUMA-local hugepages.

The experiments use a maximum burst of 32 packets. Worker counts depend on traffic direction, function placement, and offered load. Record the CPU map with each run.

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

The reported measurements use a fixed uncore frequency of 1.4 GHz.
