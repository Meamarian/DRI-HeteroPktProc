# EnergyTracer

This directory contains the EnergyTracer material used with the DPDK implementation in this project.

EnergyTracer is a cross-layer observability framework for DPDK packet-processing systems. It aligns DPDK dataplane events, Linux CPU power-state activity, and hardware energy measurements on a common timeline.

The framework is described in:

**EnergyTracer: Energy Analysis of Packet Processing Events in DPDK-Based Applications**

**Authors:** Mohsen Memarian, Andreas Kassler, Karl-Johan Grinnemo, Sándor Laki, Gergely Pongrácz, and Johan Forsman.

Original repository: [Meamarian/EnergyTracer](https://github.com/Meamarian/EnergyTracer)

The source revision used here is recorded in [`../sources.lock`](../sources.lock).

## Fetching the tools

Run from the repository root:

```bash
./scripts/fetch_upstream.sh
```

The script imports:

```text
EnergyTracer/
├── upstream/
│   ├── README.md
│   └── RUN_GUIDE.md
├── tools/
│   ├── ltracer.py
│   ├── dtracer.py
│   ├── sync.py
│   ├── chart.py
│   └── Validators/
└── traffic/
    └── test_burst_dist.py
```

`ltracer.py` records Linux CPU idle/frequency events and energy samples. `dtracer.py` exports DPDK trace data. `sync.py` aligns Linux and DPDK timelines in a common database, and `chart.py` generates the corresponding visualizations. The validation scripts check synchronization and measurement consistency.

The EnergyTracer burst profile is useful for event-level tracing experiments. The heterogeneous packet-processing experiments in this repository use the controlled-rate TRex profile under [`../traffic/`](../traffic/) for throughput, latency, power, and hourly operating-point measurements.

## Relation to the DPDK application

The host gNB implementation starts from EnergyTracer's `DPDK/gNB_power_aware.c`. [`../scripts/prepare_dpdk.py`](../scripts/prepare_dpdk.py) applies the parameter set used in this paper and generates the power-aware and busy-wait DPDK variants for DPDK 20.08.
