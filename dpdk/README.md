# DPDK host implementation

The host implementation is based on the `gNB_power_aware.c` application in EnergyTracer and the DPDK `l3fwd-power` example. The source import is pinned in `../sources.lock`.

The reported platform uses DPDK 20.08. A matching DPDK 20.08 source tree is required because the application uses the `l3fwd-power` support files and DPDK power-management interfaces from that release.

## Prepare the source

```bash
make fetch
```

or, if the upstream source is already present:

```bash
python3 scripts/prepare_dpdk.py
```

This creates:

```text
dpdk/src/power_aware/main.c
dpdk/src/busy_wait/main.c
```

The power-aware variant applies the parameter set in `config/power-paper.conf`. The busy-wait variant keeps the same gNB packet-processing path while disabling frequency and idle decisions.

## Build with DPDK 20.08

Copy one variant over the `l3fwd-power` main source in a clean DPDK 20.08 tree:

```bash
cp dpdk/src/power_aware/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

or:

```bash
cp dpdk/src/busy_wait/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

Keep the DPDK 20.08 `main.h`, `perf_core.c`, and `perf_core.h` from the same example directory. Build the example with the DPDK 20.08 toolchain used on the DUT.

The gNB table configuration is selected through `GNB_CONFIG` rather than a machine-specific absolute path:

```bash
export GNB_CONFIG=/path/to/config_table.json
```

The config generator imported under `../p4/upstream/` can be used as the starting point for the 64k-entry DRB/TEID table.

## CPU and NUMA placement

Each SmartNIC VF is assigned to a receive queue polled by one DPDK worker. Workers should be pinned to cores on the NUMA node local to the associated SmartNIC. Packet and clone pools should use NUMA-local hugepages.

The reported experiments use a 32-packet maximum burst. The worker/core counts vary with the placement and offered load; the experiment matrices under `../experiments/` identify the traffic operating points, while the exact CPU mapping should be recorded for every reproduced run.

## Power-aware configuration

The paper configuration is:

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
