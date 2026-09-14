# Reproduction checklist

A run is reproducible only when the software revision, placement, CPU map, traffic parameters, and measurement boundaries are recorded together.

Record at least:

- repository revision
- DPDK 20.08 build revision and build flags
- P4 source/firmware revision
- SmartNIC PF/VF map and NUMA node
- worker lcore map
- hugepage allocation
- BW or PA mode
- power-management parameter file
- DL/UL direction
- flow offload percentage or function split
- packet profile
- offered rate
- UE count
- warm-up duration
- measurement duration
- TRex TX/RX/loss counters
- ACPI/PDU/CPU/DRAM/SmartNIC measurement files

Raw measurements should be stored outside Git if they are large and referenced by an immutable archive identifier. Small processed tables can be kept under `data/processed/`.
