# EnergyTracer

This directory keeps the EnergyTracer material used alongside the DPDK implementation in this repository.

EnergyTracer is a cross-layer observability framework for DPDK packet-processing systems. It correlates fine-grained DPDK dataplane events with Linux CPU power-state activity and hardware energy measurements on a common timeline.

The framework is described in the paper:

**EnergyTracer: Energy Analysis of Packet Processing Events in DPDK-Based Applications**

Authors: Mohsen Memarian, Andreas Kassler, Karl-Johan Grinnemo, Sándor Laki, Gergely Pongrácz, and Johan Forsman.

Original repository:

`https://github.com/Meamarian/EnergyTracer`

The pinned EnergyTracer revision used by this artifact is recorded in `../sources.lock`.

## Imported material

Running:

```bash
../scripts/fetch_upstream.sh
```

populates this directory with the pinned EnergyTracer documentation, tracing tools, validation utilities, and burst-traffic profile:

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

`ltracer.py` records Linux CPU idle/frequency events and energy samples. `dtracer.py` exports DPDK trace data. `sync.py` aligns Linux and DPDK timelines into a common database. `chart.py` generates timeline and energy visualizations, while the validation utilities check synchronization and measurement consistency.

The EnergyTracer burst profile is retained for event-level tracing experiments. The DRI-HeteroPktProc paper uses the controlled-rate TRex profile under `../traffic/` for its throughput, latency, power, and reconstructed hourly operating-point measurements.

## DPDK provenance

The host gNB implementation in this artifact starts from EnergyTracer's `DPDK/gNB_power_aware.c`. `../scripts/prepare_dpdk.py` applies the parameter set reported in the DRI-HeteroPktProc paper and generates separate PA and BW variants for DPDK 20.08.
