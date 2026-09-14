# DRI-HeteroPktProc

Reproducibility artifact for the paper:

**Energy-Efficient Heterogeneous Packet Processing for Digital Research Infrastructures: SmartNIC Offloading and Adaptive CPU Power Management**

Mohsen Memarian, Andreas Kassler, Karl-Johan Grinnemo, Sándor Laki, Gergely Pongrácz, Johan Forsman, and Chrysa Papagianni.

This repository contains the host-side DPDK workflow, P4/SmartNIC source provenance, TRex traffic profiles, experiment matrices, power-measurement helpers, and analysis scripts used to reproduce the paper's heterogeneous packet-processing evaluation. The 5G gNB user plane is the concrete workload; the broader objective is to study how packet-processing stages should be placed across a programmable SmartNIC and a general-purpose host, and how the residual host workload should be power-managed.

## Artifact scope

The repository is organized around three reproducibility goals:

1. **Artifact availability:** preserve the implementation sources, source revisions, parameter sets, traffic profiles, and testbed configuration needed to reconstruct the evaluated system.
2. **Artifact functionality:** provide machine-checkable scripts and command generators for the DPDK, TRex, daily-profile, and analysis paths.
3. **Result reproduction:** map the experiment inputs to the figures and tables in the paper and document the measurement boundaries needed to compare reproduced results correctly.

The hardware-specific toolchains themselves are not redistributed here. DPDK 20.08, TRex v3.04, the Netronome SDK/P4 toolchain, and Intel SoC Watch must be installed separately on compatible systems.

## Repository structure

```text
DRI-HeteroPktProc/
├── dpdk/                 Host gNB implementation preparation and PA/BW configuration
├── p4/                   P4 source provenance and function-split definitions
├── smartnic/             Netronome setup notes and five-card inventory template
├── traffic/              Configurable TRex STL profile and command generator
├── experiments/          Flow, function, latency, and 24-hour experiment matrices
├── measurement/          ACPI/RAPL helpers and measurement-boundary documentation
├── analysis/             Daily non-idle energy reconstruction
├── data/                 Daily-profile inputs and result-data layout
├── EnergyTracer/         EnergyTracer project information and retained tooling path
├── docs/                 Testbed, expected results, and reproduction checklist
└── scripts/              Source import, DPDK preparation, and artifact checks
```

## Quick start

Clone the repository and first verify the self-contained artifact files:

```bash
git clone https://github.com/Meamarian/DRI-HeteroPktProc.git
cd DRI-HeteroPktProc
make check
```

Fetch the pinned source material from the two earlier implementation repositories and prepare the paper DPDK variants:

```bash
make fetch
make dpdk
```

The pinned source revisions are recorded in `sources.lock`. The fetch step imports the EnergyTracer DPDK application and the P4, SmartNIC, configuration, and reference TRex files from the earlier IFIP implementation. `scripts/prepare_dpdk.py` then produces the paper-aligned power-aware and busy-wait DPDK variants.

Generate TRex commands for an experiment matrix, for example the downlink flow-based evaluation:

```bash
python3 traffic/run_matrix.py experiments/flow/dl.csv
```

Detailed setup and measurement instructions are in `docs/reproduction.md`.

## Paper-to-artifact map

| Paper evaluation | Artifact entry point | Main configuration |
| --- | --- | --- |
| Fig. 3 — DL flow-based offloading | `experiments/flow/dl.csv` | SmartNIC-SA; 30/50/70/100% host offload |
| Fig. 4 — DL function-based partitioning | `experiments/function/dl.csv` | DL Split-0 through Split-4 |
| Fig. 5 — UL flow-based offloading | `experiments/flow/ul.csv` | SmartNIC-SA; 30/50/70/100% host offload |
| Fig. 6 — UL function-based partitioning | `experiments/function/ul.csv` | UL Split-0 through Split-3 |
| Fig. 7 — RTD percentile analysis | `experiments/latency/latency.csv` | 50 kpps latency probes |
| Fig. 8 — 24 h load and CPU demand | `experiments/daily/`, `data/daily/` | DL Split-3; UL Split-2 |
| Figs. 9–10 — hourly non-idle energy | `experiments/daily/`, `measurement/` | BW versus PA |
| Tables 4–5 — daily savings | `analysis/reconstruct_daily.py` | independent hourly operating points |

Reference values reported in the manuscript are summarized in `docs/expected_results.md` so reproduced runs can be checked against the corresponding paper claims.

## Experimental platform

The reported DUT is a dual-socket server with:

- two Intel Xeon Gold 5418Y processors;
- 24 physical cores per socket, 48 physical cores total;
- 256 GB DDR5 RAM;
- five Netronome Agilio CX 2x40 G SmartNICs;
- 60 SmartNIC micro-engine cores per card at 800 MHz;
- Ubuntu 18.04 with an HWE kernel;
- DPDK 20.08.

The SmartNICs are distributed across both NUMA domains. DPDK workers are pinned to CPU cores local to their SmartNICs, packet buffers use NUMA-local hugepages, and the uncore frequency is fixed at 1.4 GHz in the reported measurements.

Traffic is generated on a separate x86 server using TRex v3.04 and two Mellanox ConnectX-5 dual-port 100 G NICs. An Arista 100 G switch distributes traffic to the five SmartNICs using static MAC-based forwarding rules.

See `docs/testbed.md` for the testbed checklist.

## Heterogeneous processing model

The implementation supports two placement mechanisms.

**Flow-based offloading** assigns complete flows either to the SmartNIC path or to the host path. The IPv4 Identification field carries the offload tag used by the experiment traffic generator.

**Function-based partitioning** moves the processing boundary within the packet-processing pipeline. The evaluated split points are:

### Downlink

| Split | SmartNIC processing | Host processing |
| --- | --- | --- |
| Split-0 | parsing, offload decision, VF steering | complete gNB processing chain |
| Split-1 | Split-0 + GTP-U decapsulation | remaining DL processing |
| Split-2 | Split-1 + DRB lookup | SDAP/PDCP/RLC insertion, cloning, saving |
| Split-3 | Split-2 + SDAP/PDCP/RLC insertion | cloning and saving |
| Split-4 | Split-3 + cloning | packet storage |

### Uplink

| Split | SmartNIC processing | Host processing |
| --- | --- | --- |
| Split-0 | parsing, offload decision, VF steering | complete UL processing chain |
| Split-1 | Split-0 + RLC/PDCP/SDAP removal | DRB lookup and GTP-U encapsulation |
| Split-2 | Split-1 + DRB lookup | GTP-U encapsulation |
| Split-3 | Split-2 + GTP-U encapsulation | none |

The full split definitions are in `p4/SPLITS.md`.

## DPDK power management

The paper compares busy-wait execution (`BW`) with a power-aware DPDK path (`PA`). The PA path combines per-poll idle/frequency decisions with a periodic frequency-down callback. The exact parameter set is stored in `dpdk/config/power-paper.conf`:

| Parameter | Value |
| --- | ---: |
| `MIN_EMPTY_POLL_COUNT` | 10 polls |
| `PAUSE_THRESHOLD` | 10 us |
| `GO_TO_SLEEP_THRESHOLD` | 300 polls |
| `GEAR1_RX_PKT_THRESHOLD` | 96 packets |
| `GEAR2_RX_PKT_THRESHOLD` | 64 packets |
| `GEAR3_RX_PKT_THRESHOLD` | 32 packets |
| `TREND_INC_LEVEL1` | 250 |
| `TREND_INC_LEVEL2` | 3 |
| `FREQ_UP_THRESHOLD` | 10000 |
| `EVENT_CHECKING_INTERVAL` | 10 ms |
| `SCALING_PERIOD` | 100 ms |
| `SCALING_DOWN_SLEEP_RATIO_THR` | 0.25 |
| `MAX_PKT_BURST` | 32 packets |

The host implementation is prepared from the pinned EnergyTracer `gNB_power_aware.c` source. `dpdk/README.md` describes how the paper-aligned PA and BW variants are generated and built against DPDK 20.08.

## TRex traffic generation

`traffic/trex_gnb_profile.py` provides a single STL profile for the paper operating points. It supports:

- DL GTP-U packet templates;
- UL RLC/PDCP/SDAP packet templates;
- up to 64k UE/TEID values;
- controlled MPPS rates;
- flow-based SmartNIC/host assignment;
- fixed-size and IMIX traffic;
- 50 kpps latency probes.

Unless stated otherwise, the controlled experiments use 128-byte packets. The standard offered-load points are 7, 21, 35, 49, 63, 77, and 100 MPPS. SmartNIC-only latency measurements use 7, 21, and 35 MPPS to stay below the reported saturation point.

The paper records each steady-state power operating point over a 20 s window after warm-up. The exact warm-up used on a reproduction platform should be logged together with the run metadata.

See `traffic/README.md` and `experiments/README.md`.

## Reconstructing the 24-hour analysis

The 24-hour evaluation is **not** one continuous 24-hour TRex run. Each hourly load is represented by an independent one-minute TRex operating point and is weighted afterward by the corresponding hourly traffic volume. This is important for reproducing the paper correctly.

The daily evaluation uses:

- DL Split-3;
- UL Split-2;
- 128 B packets;
- IMIX: 58.33% 64 B, 33.33% 590 B, 8.33% 1514 B;
- 590 B packets;
- 1518 B packets.

`experiments/daily/make_runs.py` converts a completed hourly profile CSV into the required TRex commands. `data/daily/hourly_profile_template.csv` intentionally leaves the 24 hourly MPPS values blank: the manuscript describes the source profile and reconstruction method but does not provide the complete numerical hourly table. Exact archived experiment values or the original traffic dataset should be used rather than values digitized from the figure.

For mixed-direction reconstruction, `data/daily/ul_dl_profiles.csv` contains the four UL/DL ratios reported in the paper.

After collecting the independently measured hourly BW and PA values, run:

```bash
python3 analysis/reconstruct_daily.py hourly_results.csv
```

The analysis reports the accumulated non-idle energy saving and the relative reduction against BW.

## Power measurement

The paper uses three measurement levels:

- corrected PDU outlet power at 1 Hz;
- aggregate ACPI-domain power at 1 Hz;
- CPU package/DRAM power and CPU frequency using Intel SoC Watch 2024.6.0 at 100 ms, together with per-card SmartNIC power at 1 Hz using the Netronome SDK.

`measurement/tools/acpi.sh` and `measurement/tools/msr.py` are retained from the GreenQUIC experimental tooling. `acpi.sh` is useful for the 1 Hz board/ACPI sensor path when the platform exposes the corresponding `power1` sensor. `msr.py` provides a lightweight Intel RAPL package/DRAM sampling path for diagnostics and cross-checking; it is **not** a replacement for the SoC Watch measurements reported in this paper.

The ACPI and SmartNIC domains overlap and must not be added as independent power components. See `measurement/README.md` and `docs/measurement.md`.

## EnergyTracer

`EnergyTracer/` documents the EnergyTracer framework and the provenance of the DPDK application used as the starting point for the host implementation. EnergyTracer correlates DPDK dataplane events, Linux CPU power-state activity, and hardware energy measurements on a synchronized timeline.

The original project is available at `Meamarian/EnergyTracer`. The pinned revision used by this artifact is recorded in `sources.lock`.

## Reproducibility notes

For every run, record at least the repository revision, P4 placement, DPDK mode, CPU/lcore map, NUMA placement, hugepage configuration, packet profile, offered rate, UE count, warm-up interval, measurement interval, TRex TX/RX/drop counters, and measurement filenames. `docs/reproduction.md` provides the complete checklist.

Large raw measurement files are not committed by default. If the archived raw dataset is published separately, record its immutable identifier in `data/README.md` and keep the processed tables required for the paper figures under `data/processed/`.

## Source provenance

The artifact builds on three existing project sources:

- `Meamarian/EnergyTracer` — DPDK gNB/power-aware implementation and EnergyTracer tools;
- `Meamarian/Hybrid_P4_IFIP_WMNC_24` — P4/SmartNIC implementation, Netronome setup material, configuration generation, and reference TRex packet templates;
- `Meamarian/GreenQUIC` — ACPI and Intel RAPL measurement helpers.

All source revisions are pinned in `sources.lock`. Imported or derived files retain their original copyright and license notices where applicable. See `NOTICE.md`.

## Citation

A machine-readable citation is provided in `CITATION.cff`.
