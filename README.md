# DRI-HeteroPktProc

## Energy-Efficient Heterogeneous Packet Processing for Digital Research Infrastructures: SmartNIC Offloading and Adaptive CPU Power Management

**Mohsen Memarian\*, Andreas Kassler\*†, Karl-Johan Grinnemo\*, Sándor Laki‡, Gergely Pongrácz§, Johan Forsman¶, Chrysa Papagianni‖**

\* Karlstad University, Sweden  
† Deggendorf Institute of Technology, Germany  
‡ ELTE Eötvös Loránd University, Hungary  
§ Ericsson Research, Hungary  
¶ TietoEvry, Sweden  
‖ University of Amsterdam, The Netherlands

**Contact:** mohsen.memarian@kau.se, andreas.kassler@kau.se, karlgrin@kau.se, lakis@inf.elte.hu, gergely.pongracz@ericsson.com, johan.forsman@tietoevry.com, c.papagianni@uva.nl

DRI-HeteroPktProc contains the implementation and experiment workflow for the paper **“Energy-Efficient Heterogeneous Packet Processing for Digital Research Infrastructures: SmartNIC Offloading and Adaptive CPU Power Management.”**

Modern networking nodes increasingly combine general-purpose CPUs with programmable SmartNICs or other accelerators. The main question studied in this work is not simply *how much processing can be offloaded*, but **where packet-processing stages should execute and how the remaining host resources should be power-managed**.

We study this problem using a 5G gNB user-plane pipeline as a concrete heterogeneous networking workload. P4-programmable SmartNICs execute selected parsing, lookup, header-processing, forwarding, and cloning operations, while a DPDK-enabled x86 host executes the remaining software stages and packet buffering. We evaluate both complete-flow placement and finer-grained function placement, and combine them with adaptive CPU P-state and C-state control on the host.

The main evaluated dimensions are:

- **flow-based offloading:** complete flows are assigned to either the SmartNIC or the host;
- **function-based partitioning:** the processing boundary is moved between stages of the gNB pipeline;
- **host execution:** DPDK busy waiting (`BW`) versus adaptive power-aware execution (`PA`);
- **performance:** throughput, required CPU cores, and round-trip delay percentiles;
- **power and energy:** host ACPI-domain power, SmartNIC power, CPU frequency, and non-idle energy;
- **time-varying operation:** independent hourly measurements are combined to reconstruct a 24-hour workload.

For 128-byte traffic, the best function-based placements reach **108.5 MPPS in downlink** and **110.5 MPPS in uplink**. The selected DL/UL function splits reduce the measured 99.9th-percentile round-trip delay by about **70% compared with full host processing under busy waiting**, while the power-aware host configuration reduces **ACPI-domain non-idle energy by up to 59%** in the reconstructed 24-hour analysis.

---

## System overview

```text
                          +--------------------------+
                          |      TRex generator      |
                          |  ConnectX-5 / TRex 3.04  |
                          +------------+-------------+
                                       |
                                    100 GbE
                                       |
                          +------------v-------------+
                          |     Arista 100G switch    |
                          +------------+-------------+
                                       |
                    +------------------+------------------+
                    |                                     |
          +---------v-------------------------------------v---------+
          |          5 x Netronome Agilio CX SmartNICs             |
          |     P4 parsing / lookup / protocol stages / steering    |
          +---------------------------+------------------------------+
                                      |
                              PCIe / SR-IOV VFs
                                      |
          +---------------------------v------------------------------+
          |                    x86 DPDK host                         |
          |   remaining gNB stages + buffering + CPU power control  |
          +----------------------------------------------------------+
```

The processing boundary is configurable. A packet can remain on the SmartNIC, be sent to the host for the full software pipeline, or cross between the two at an intermediate function boundary. The host power manager then adapts CPU frequency and idle behavior to the residual workload created by that placement.

---

## Repository layout

| Path | Purpose |
|---|---|
| `dpdk/` | Host gNB application, busy-wait/power-aware preparation, and paper power parameters |
| `p4/` | P4 source import, SmartNIC processing description, and DL/UL split definitions |
| `smartnic/` | Netronome setup notes and five-SmartNIC testbed configuration template |
| `traffic/` | TRex STL profile for DL/UL traffic, flow tags, packet sizes, IMIX, and latency probes |
| `experiments/` | Flow-based, function-based, latency, and daily operating-point matrices |
| `measurement/` | Host/SmartNIC measurement notes and ACPI/RAPL helper scripts |
| `analysis/` | Reconstruction of daily non-idle energy from independently measured operating points |
| `data/` | Hourly-profile inputs and layout for measured/processed data |
| `EnergyTracer/` | EnergyTracer project information and tracing workflow used alongside the DPDK implementation |
| `docs/` | Testbed description, expected paper results, and full reproduction checklist |
| `scripts/` | Pinned source import, DPDK preparation, and repository checks |

The exact source revisions imported from the earlier EnergyTracer and IFIP implementations are recorded in [`sources.lock`](sources.lock).

---

## Getting started

Clone the repository:

```bash
git clone https://github.com/Meamarian/DRI-HeteroPktProc.git
cd DRI-HeteroPktProc
```

Check the repository scripts and configuration files:

```bash
make check
```

Fetch the pinned implementation sources:

```bash
make fetch
```

This imports the source files used as the basis of the paper implementation and prepares the DPDK variants. In particular, it creates:

```text
dpdk/upstream/gNB_power_aware.c
dpdk/src/power_aware/main.c
dpdk/src/busy_wait/main.c
p4/upstream/main.p4
p4/upstream/main_clone.p4
p4/upstream/base.p4cfg
p4/upstream/p4_cfg_generator.py
smartnic/upstream/...
traffic/upstream/...
EnergyTracer/tools/...
```

If the DPDK source has already been fetched and only the paper power configuration has changed, regenerate the host variants with:

```bash
make dpdk
```

The generated `power_aware` and `busy_wait` versions use the same gNB packet-processing path; the intended difference is the CPU power-management behavior.

---

## Paper testbed

The reported Device Under Test uses:

| Component | Paper configuration |
|---|---|
| Host CPU | 2 x Intel Xeon Gold 5418Y, 24 physical cores per socket |
| Memory | 256 GB DDR5 |
| SmartNICs | 5 x Netronome Agilio CX 2x40 G |
| SmartNIC processing | 60 micro-engine cores per card at 800 MHz |
| Host OS | Ubuntu 18.04 with HWE kernel |
| DPDK | 20.08 |
| Traffic generator | TRex v3.04 |
| TG NICs | 2 x Mellanox ConnectX-5 dual-port 100 G |
| Network | Arista 100 G switch |
| Uncore frequency | fixed at 1.4 GHz |

The five SmartNICs are distributed across the two NUMA domains. DPDK workers are pinned to CPU cores local to the corresponding SmartNICs, and packet buffers use NUMA-local hugepages.

The exact paper hardware is not required to inspect the implementation or generate the experiment commands, but comparable performance and power results require a platform with equivalent capabilities and careful CPU/NUMA placement.

See [`docs/testbed.md`](docs/testbed.md) and [`smartnic/README.md`](smartnic/README.md) before configuring the DUT.

---

## 1. Prepare the DPDK host application

The host implementation starts from the EnergyTracer `gNB_power_aware.c` application and the DPDK `l3fwd-power` example.

After `make fetch`, choose one generated variant:

```text
dpdk/src/power_aware/main.c
dpdk/src/busy_wait/main.c
```

A clean DPDK 20.08 tree is required because the application uses the `l3fwd-power` support files and power-management interfaces from that release. Copy the selected variant into the DPDK example tree:

```bash
cp dpdk/src/power_aware/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

or:

```bash
cp dpdk/src/busy_wait/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

Keep `main.h`, `perf_core.c`, and `perf_core.h` from the same DPDK 20.08 `l3fwd-power` example and build with the DPDK 20.08 toolchain.

The gNB table configuration is selected at runtime through:

```bash
export GNB_CONFIG=/path/to/config_table.json
```

The imported P4 configuration generator under `p4/upstream/` can be used as the starting point for the 64k-entry DRB/TEID table.

Full host-side instructions are in [`dpdk/README.md`](dpdk/README.md).

### Power-aware parameters

The paper configuration is stored in [`dpdk/config/power-paper.conf`](dpdk/config/power-paper.conf):

| Parameter | Value |
|---|---:|
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

---

## 2. Prepare the P4 / SmartNIC path

The P4 implementation is imported from the earlier hybrid gNB implementation at the pinned revision in `sources.lock`.

After `make fetch`:

```text
p4/upstream/main.p4
p4/upstream/main_clone.p4
p4/upstream/base.p4cfg
p4/upstream/p4_cfg_generator.py
```

`main.p4` contains the common gNB parser, TEID/DRB table logic, host-VF steering, and DL/UL protocol actions. `main_clone.p4` contains the SmartNIC cloning path used by the DL cloning case.

The evaluated placement boundaries are documented in [`p4/SPLITS.md`](p4/SPLITS.md). The original public IFIP source does not contain a separate archived P4 source for every journal-paper split, so this repository keeps the available implementation unchanged and documents the exact split semantics rather than creating unverified split-specific P4 programs.

The original Netronome setup scripts are imported under `smartnic/upstream/`. They contain lab-specific PCI addresses and SDK paths and should be reviewed before use on another system. [`smartnic/testbed.env.example`](smartnic/testbed.env.example) provides a neutral five-card inventory template.

---

## 3. Generate traffic with TRex

The paper uses TRex v3.04 on a separate traffic-generator server. [`traffic/trex_gnb_profile.py`](traffic/trex_gnb_profile.py) provides the common profile used to generate the paper operating points.

It supports:

- DL GTP-U traffic;
- UL RLC/PDCP/SDAP traffic;
- up to 64k UE/TEID values;
- flow-based SmartNIC/host assignment through the outer IPv4 Identification field;
- fixed-size packets and IMIX;
- controlled MPPS rates;
- dedicated 50 kpps latency probes.

Example from the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

Generate all commands for one experiment matrix with:

```bash
python3 traffic/run_matrix.py experiments/flow/dl.csv
```

The standard offered-load points are **7, 21, 35, 49, 63, 77, and 100 MPPS**. Unless stated otherwise, the paper uses **128-byte packets**.

See [`traffic/README.md`](traffic/README.md) for the profile options and [`experiments/README.md`](experiments/README.md) for the complete operating-point matrices.

---

## 4. Select the processing placement

### Flow-based offloading

Complete flows are assigned either to the SmartNIC path or to the host path. The traffic generator carries the offload tag in the outer IPv4 Identification field. The paper evaluates SmartNIC stand-alone processing and **30%, 50%, 70%, and 100% host offload**.

### Function-based partitioning

The processing boundary is moved inside the packet-processing pipeline.

#### Downlink

| Split | SmartNIC | Host |
|---|---|---|
| Split-0 | parsing, offload decision, VF steering | complete gNB processing chain |
| Split-1 | Split-0 + GTP-U decapsulation | remaining DL processing |
| Split-2 | Split-1 + DRB lookup | SDAP/PDCP/RLC insertion, cloning, saving |
| Split-3 | Split-2 + SDAP/PDCP/RLC insertion | cloning and saving |
| Split-4 | Split-3 + cloning | packet storage |

#### Uplink

| Split | SmartNIC | Host |
|---|---|---|
| Split-0 | parsing, offload decision, VF steering | complete UL processing chain |
| Split-1 | Split-0 + RLC/PDCP/SDAP removal | DRB lookup and GTP-U encapsulation |
| Split-2 | Split-1 + DRB lookup | GTP-U encapsulation |
| Split-3 | Split-2 + GTP-U encapsulation | none |

The main daily evaluation uses **DL Split-3** and **UL Split-2**, the highest-throughput function placements found in the paper.

---

## 5. Run the paper experiments

The CSV files under `experiments/` define the controlled operating points without embedding testbed-specific commands.

| Paper result | Experiment input | Configuration |
|---|---|---|
| DL flow-based offloading | `experiments/flow/dl.csv` | SmartNIC-SA; 30/50/70/100% host offload |
| DL function-based partitioning | `experiments/function/dl.csv` | Split-0 to Split-4; BW and PA |
| UL flow-based offloading | `experiments/flow/ul.csv` | SmartNIC-SA; 30/50/70/100% host offload |
| UL function-based partitioning | `experiments/function/ul.csv` | Split-0 to Split-3; BW and PA |
| RTD percentile analysis | `experiments/latency/latency.csv` | 50 kpps latency probes |
| 24-hour load reconstruction | `experiments/daily/`, `data/daily/` | DL Split-3; UL Split-2 |
| Daily energy calculation | `analysis/reconstruct_daily.py` | independently measured hourly BW/PA values |

Reference values from the paper are collected in [`docs/expected_results.md`](docs/expected_results.md).

For the steady-state power experiments, bring TRex to the target load, allow the system to stabilize, and measure power over the **20 s window** used in the paper. Record the actual warm-up period with the experiment metadata.

---

## Latency measurements

Latency is measured using dedicated **50 kpps** TRex probes. The reported value is **round-trip delay (RTD)** from the traffic-generator host through the DUT and back; it is not one-way gNB processing latency.

The SmartNIC-only DL case is measured at 7, 21, and 35 MPPS to stay below its saturation point. The host and selected hybrid cases use the operating points defined in [`experiments/latency/latency.csv`](experiments/latency/latency.csv).

The selected busy-wait function placements, DL Split-3 and UL Split-2, reach a Q99.9 of approximately **182 us** at full rate, compared with approximately **601 us** for full host processing.

---

## Power measurement

The paper uses three measurement levels:

1. **System power:** Supermicro ECO PDU outlet, sampled at 1 Hz and corrected using the PSU efficiency curve.
2. **Server/ACPI domain:** aggregate on-board ACPI power at 1 Hz.
3. **Components:** CPU package power, DRAM power, and CPU frequency with Intel SoC Watch 2024.6.0 at 100 ms; SmartNIC power at 1 Hz per card using the Netronome SDK.

The ACPI domain includes host processing and shared resources such as uncore, LLC, memory-controller and PCIe activity, as well as mapped SmartNIC devices. **ACPI and SmartNIC measurements overlap and must not be added as independent power components.**

[`measurement/tools/acpi.sh`](measurement/tools/acpi.sh) and [`measurement/tools/msr.py`](measurement/tools/msr.py) are retained from the GreenQUIC measurement workflow. `acpi.sh` samples the platform `power1` sensor when exposed by the system. `msr.py` provides a lightweight Intel RAPL package/DRAM measurement path for diagnostics and cross-checking; the paper's reported package/DRAM/frequency measurements use SoC Watch.

See [`docs/measurement.md`](docs/measurement.md) for the measurement boundaries.

---

## Reconstructing the 24-hour workload

The 24-hour result is **not a continuous 24-hour TRex replay**. Each hourly traffic level is represented by an independent **one-minute TRex run**. The measured operating points are then weighted by the corresponding hourly traffic volumes.

The daily evaluation uses:

- DL Split-3 and UL Split-2;
- 128 B packets;
- IMIX: 58.33% 64 B, 33.33% 590 B, and 8.33% 1514 B;
- 590 B packets;
- 1518 B packets.

The four UL/DL traffic-ratio profiles reported in the paper are stored in [`data/daily/ul_dl_profiles.csv`](data/daily/ul_dl_profiles.csv).

[`data/daily/hourly_profile_template.csv`](data/daily/hourly_profile_template.csv) intentionally leaves the 24 hourly MPPS values empty. The paper describes the source traffic profile and reconstruction method but does not publish the complete numerical hourly series. Exact archived values or the original source dataset should be used instead of digitizing values from the plot.

Once the hourly values are available, generate the one-minute runs with:

```bash
python3 experiments/daily/make_runs.py data/daily/hourly_profile.csv
```

After collecting the independently measured BW and PA values, reconstruct the daily non-idle energy with:

```bash
python3 analysis/reconstruct_daily.py hourly_results.csv
```

The reported percentage savings refer to **energy above the measured idle baseline**, not to total server, facility, or lifecycle energy. The paper's idle ACPI baseline is approximately **255–258 W**.

---

## EnergyTracer

The [`EnergyTracer/`](EnergyTracer/) directory documents the EnergyTracer framework used alongside the DPDK implementation.

EnergyTracer correlates DPDK dataplane events with Linux CPU power-state activity and hardware energy measurements on a common timeline. Its tracing tools are kept separate from the main TRex operating-point workflow used for the throughput, latency, and 24-hour results in this paper.

Original project: [Meamarian/EnergyTracer](https://github.com/Meamarian/EnergyTracer)

---

## Source repositories

This repository builds on source material from three earlier projects:

- [Meamarian/EnergyTracer](https://github.com/Meamarian/EnergyTracer) — DPDK gNB/power-aware implementation and EnergyTracer tools;
- [Meamarian/Hybrid_P4_IFIP_WMNC_24](https://github.com/Meamarian/Hybrid_P4_IFIP_WMNC_24) — P4/SmartNIC implementation, Netronome setup material, configuration generation, and reference TRex templates;
- `Meamarian/GreenQUIC` — ACPI and Intel RAPL measurement helpers.

The exact revisions are pinned in [`sources.lock`](sources.lock). Imported or derived source files retain their original copyright and license notices where applicable. See [`NOTICE.md`](NOTICE.md).

---

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).