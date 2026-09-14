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

This repository contains the implementation and experiment workflow for the paper **“Energy-Efficient Heterogeneous Packet Processing for Digital Research Infrastructures: SmartNIC Offloading and Adaptive CPU Power Management.”**

Digital Research Infrastructures increasingly combine general-purpose CPUs with programmable network accelerators such as SmartNICs. This creates a placement problem inside the networking node: packet-processing stages differ in compute, memory, state, and communication requirements, while the available execution resources differ in programmability and capacity. Moving more work to the accelerator is therefore not necessarily the highest-performing or most energy-efficient choice.

Placement also changes the amount of work that remains on the host. This is important for DPDK-based software data planes because polling cores can stay active even when little useful work is available. The residual host workload determines how much opportunity remains for CPU frequency scaling and idle-state entry. We therefore consider processing placement and host power management together.

We use a softwarized 5G gNB user-plane pipeline as a concrete case study. The workload combines table-driven header processing and bearer lookups with stateful, memory-intensive buffering, giving the pipeline stages substantially different resource requirements. The methodology itself is not tied to the 5G protocol stack. Our implementation combines P4-programmable SmartNICs with a DPDK-enabled x86 host and evaluates both complete-flow placement and finer-grained function placement in downlink and uplink.

The evaluation covers flow-based offloading, function-based partitioning, DPDK busy waiting (`BW`) versus adaptive power-aware execution (`PA`), throughput, required CPU cores, round-trip delay percentiles, host and SmartNIC power, CPU frequency, and reconstructed time-varying operation.

On the five-SmartNIC testbed, the best function-based placements reach **108.5 MPPS in downlink** and **110.5 MPPS in uplink** for 128-byte packets, corresponding to **173%** and **62%** higher throughput than SmartNIC-only processing. Under busy waiting, the selected DL/UL function splits reduce Q99.9 round-trip delay by about **70%** compared with full host processing. With adaptive host power management, the reconstructed 24-hour analysis shows up to **59% lower ACPI-domain non-idle energy**. This percentage excludes the measured idle baseline and does not represent total facility or lifecycle energy.

---

## Repository layout

| Path | Purpose |
|---|---|
| `dpdk/` | Host gNB application preparation and the BW/PA power configuration |
| `p4/` | P4 processing code and DL/UL function-split definitions |
| `smartnic/` | Netronome setup notes and the five-SmartNIC testbed template |
| `traffic/` | TRex packet profiles and Python experiment sweeps |
| `experiments/` | Experiment order and DUT-side placement notes |
| `measurement/` | ACPI/RAPL helpers and measurement boundaries |
| `EnergyTracer/` | EnergyTracer tools used with the DPDK implementation |
| `scripts/` | Source preparation and repository checks |

---

## Getting started

Clone the repository:

```bash
git clone https://github.com/Meamarian/DRI-HeteroPktProc.git
cd DRI-HeteroPktProc
```

Check the repository:

```bash
make check
```

Fetch the pinned implementation sources and prepare the DPDK variants:

```bash
make fetch
```

This creates the main source paths used by the workflow:

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

If the source has already been fetched and only the DPDK preparation needs to be rerun:

```bash
make dpdk
```

The generated `power_aware` and `busy_wait` versions use the same gNB packet-processing path. Their intended difference is the CPU power-management behavior.

---

## Paper testbed

The Device Under Test used in the paper is:

| Component | Configuration |
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

The SmartNICs are distributed across both NUMA domains. DPDK workers are pinned to CPU cores local to the corresponding SmartNICs, and packet buffers use NUMA-local hugepages.

Comparable performance and power measurements require equivalent hardware capabilities and careful NUMA placement. The source code and traffic sequences can still be inspected and exercised on other compatible systems.

---

## 1. Prepare the DPDK host application

The host implementation starts from the EnergyTracer `gNB_power_aware.c` application and the DPDK `l3fwd-power` example.

After `make fetch`, choose one of the generated variants:

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

The paper power-management parameters are stored in [`dpdk/config/power-paper.conf`](dpdk/config/power-paper.conf):

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

See [`dpdk/README.md`](dpdk/README.md) for the host-side setup.

---

## 2. Prepare the P4 / SmartNIC path

After `make fetch`, the main P4 files are available under:

```text
p4/upstream/main.p4
p4/upstream/main_clone.p4
p4/upstream/base.p4cfg
p4/upstream/p4_cfg_generator.py
```

`main.p4` contains the common gNB parser, TEID/DRB table logic, host-VF steering, and DL/UL protocol actions. `main_clone.p4` contains the SmartNIC cloning path used by the DL cloning case.

The evaluated processing boundaries are listed in [`p4/SPLITS.md`](p4/SPLITS.md). The common P4 ingress parser, path decision, and VF distribution remain on the SmartNIC, while the function-based experiments move the processing boundary deeper into the gNB pipeline.

The Netronome setup material is placed under `smartnic/upstream/`. The original scripts contain lab-specific PCI addresses and SDK paths, so they should be adjusted to the local system before use. [`smartnic/testbed.env.example`](smartnic/testbed.env.example) provides the five-card inventory format used for the paper setup.

---

## 3. Generate traffic with TRex

[`traffic/trex_gnb_profile.py`](traffic/trex_gnb_profile.py) defines the DL and UL packet formats and the individual TRex streams.

It supports:

- DL GTP-U traffic;
- UL RLC/PDCP/SDAP traffic;
- up to 64k UE/TEID values;
- SmartNIC/host flow tagging through the outer IPv4 Identification field;
- fixed packet sizes and IMIX;
- controlled MPPS rates;
- 50 kpps latency probes.

A single operating point can be started directly from the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

For the complete experiment sequence, [`traffic/experiment_sweep.py`](traffic/experiment_sweep.py) keeps the operating points directly in Python:

```python
RATE_POINTS_MPPS = [7, 21, 35, 49, 63, 77, 100]
FLOW_OFFLOAD_PERCENTAGES = [0, 30, 50, 70, 100]
DAILY_PACKET_PROFILES = [128, "imix", 590, 1518]
DIRECTIONS = ["dl", "ul"]
```

The script sends one operating point, stops it, waits **5 s**, and starts the next one. No external experiment table is required.

Preview the daily sequence:

```bash
python3 traffic/experiment_sweep.py --suite daily --dry-run
```

Run it against TRex:

```bash
python3 traffic/experiment_sweep.py --suite daily --server 127.0.0.1 --port 0
```

The daily sequence runs **DL first and then UL**. Within each direction, packet profiles are evaluated in the order used in the paper:

1. 128 B
2. IMIX
3. 590 B
4. 1518 B

Each daily operating point runs for **60 s** by default. The gap defaults to **5 s**. Both values can be changed from the command line.

For a normal 128-byte load sweep:

```bash
python3 traffic/experiment_sweep.py --suite rate --direction dl --duration 30 --gap 5
```

For the flow-based experiment:

```bash
python3 traffic/experiment_sweep.py --suite flow --direction dl --duration 30 --gap 5
```

See [`traffic/README.md`](traffic/README.md) for all options.

---

## 4. Processing placement

### Flow-based offloading

Complete flows are assigned either to the SmartNIC path or to the host path. The traffic generator carries the path tag in the outer IPv4 Identification field. The paper evaluates SmartNIC stand-alone processing and 30%, 50%, 70%, and 100% host offload.

### Function-based partitioning

The processing boundary is moved inside the packet-processing pipeline.

#### Downlink

| Split | SmartNIC | Host |
|---|---|---|
| Split-0 | parsing, path decision, VF steering | complete gNB processing chain |
| Split-1 | Split-0 + GTP-U decapsulation | remaining DL processing |
| Split-2 | Split-1 + DRB lookup | SDAP/PDCP/RLC insertion, cloning, saving |
| Split-3 | Split-2 + SDAP/PDCP/RLC insertion | cloning and saving |
| Split-4 | Split-3 + cloning | packet storage |

#### Uplink

| Split | SmartNIC | Host |
|---|---|---|
| Split-0 | parsing, path decision, VF steering | complete UL processing chain |
| Split-1 | Split-0 + RLC/PDCP/SDAP removal | DRB lookup and GTP-U encapsulation |
| Split-2 | Split-1 + DRB lookup | GTP-U encapsulation |
| Split-3 | Split-2 + GTP-U encapsulation | none |

The main daily evaluation uses **DL Split-3** and **UL Split-2**.

Placement is configured on the SmartNIC/DPDK side. The TRex sweep only controls the offered traffic, which keeps the traffic sequence independent from the processing split and BW/PA mode being tested.

---

## 5. Latency measurements

Latency uses a dedicated **50 kpps** TRex probe stream. The reported quantity is round-trip delay from the traffic-generator host through the DUT and back; it is not one-way gNB processing latency.

For example:

```bash
python3 traffic/experiment_sweep.py --suite latency --direction dl --rates 7 21 35 --duration 30 --gap 5
```

The SmartNIC-only DL reference is evaluated below its saturation point. Host-only and selected hybrid placements are measured across the required load range after the corresponding DUT placement has been configured.

---

## 6. Power measurement

The paper uses three measurement levels:

1. **System power:** Supermicro ECO PDU outlet, sampled at 1 Hz and corrected using the PSU efficiency curve.
2. **Server/ACPI domain:** aggregate on-board ACPI power at 1 Hz.
3. **Components:** CPU package power, DRAM power, and CPU frequency with Intel SoC Watch 2024.6.0 at 100 ms; SmartNIC power at 1 Hz per card using the Netronome SDK.

The ACPI domain includes host processing and shared resources such as uncore, LLC, memory-controller, and PCIe activity, together with mapped SmartNIC devices. **ACPI and SmartNIC measurements overlap and must not be added as independent power components.**

[`measurement/tools/acpi.sh`](measurement/tools/acpi.sh) samples the platform `power1` sensor when exposed by the system. [`measurement/tools/msr.py`](measurement/tools/msr.py) provides an Intel RAPL package/DRAM path for diagnostics and cross-checking. The paper's reported CPU package, DRAM, and frequency measurements use SoC Watch.

For short steady-state experiments, TRex is first brought to the target traffic load and power is then measured over a **20 s** window. For the reconstructed daily study, each hourly load is represented by an independent **one-minute** TRex run.

---

## 7. Reconstructed 24-hour evaluation

The paper does not run TRex continuously for 24 hours. Each hourly traffic load is measured independently and the resulting measurements are weighted by the corresponding hourly traffic volumes.

The repository follows the same operating-point approach. The traffic generator iterates over selected rate points rather than synthesizing a continuous day-long curve. Exact archived hourly rates can be passed directly with `--rates` or placed in the Python rate list before running the sequence.

The daily packet profiles are evaluated in this order:

```python
[128, "imix", 590, 1518]
```

with IMIX defined as 58.33% 64 B, 33.33% 590 B, and 8.33% 1514 B packets.

DL and UL are measured separately, using DL Split-3 and UL Split-2. Mixed UL/DL daily profiles in the paper are reconstructed from these separate directional measurements rather than from simultaneous bidirectional runs.

---

## EnergyTracer

The [`EnergyTracer/`](EnergyTracer/) directory contains the EnergyTracer tools used alongside the DPDK implementation. EnergyTracer aligns DPDK dataplane events, Linux CPU power-state activity, and hardware energy measurements on a common timeline.

The event-level tracing workflow is separate from the TRex operating-point sweeps used for the throughput, latency, and time-varying measurements in this paper.

---

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).
