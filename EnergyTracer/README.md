# EnergyTracer

This directory contains the EnergyTracer tools used with the DPDK implementation in this project.

EnergyTracer is a cross-layer observability framework for DPDK packet-processing systems. It aligns DPDK dataplane events, Linux CPU power-state activity, and hardware energy measurements on a common timeline.

The framework is described in:

**EnergyTracer: Energy Analysis of Packet Processing Events in DPDK-Based Applications**

**Authors:** Mohsen Memarian, Andreas Kassler, Karl-Johan Grinnemo, Sándor Laki, Gergely Pongrácz, and Johan Forsman.

Original repository: [Meamarian/EnergyTracer](https://github.com/Meamarian/EnergyTracer)

## Fetching the tools

Run from the repository root:

```bash
make fetch
```

The script places the EnergyTracer material under:

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

`ltracer.py` records Linux CPU idle/frequency events and energy samples. `dtracer.py` exports DPDK trace data. `sync.py` aligns Linux and DPDK timelines in a common database, and `chart.py` generates timeline and energy visualizations. The validation scripts check synchronization and measurement consistency.

The EnergyTracer burst profile supports event-level tracing experiments. The controlled-rate TRex profile under [`../traffic/`](../traffic/) provides the throughput, latency, power, and time-varying operating points used in the heterogeneous packet-processing evaluation.

## Relation to the DPDK application

The host gNB implementation uses the EnergyTracer DPDK application as its base. [`../scripts/prepare_dpdk.py`](../scripts/prepare_dpdk.py) applies the paper power-management parameters and generates the power-aware and busy-wait variants for DPDK 20.08.
