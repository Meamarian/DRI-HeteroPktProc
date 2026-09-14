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

Digital Research Infrastructures increasingly combine general-purpose CPUs with programmable network accelerators such as SmartNICs. Packet-processing stages have different compute, memory, state, and communication requirements, while CPUs and SmartNICs provide different processing capabilities. Our design jointly considers **where each stage runs** and **how the remaining host workload is power-managed**.

We use a softwarized 5G gNB user-plane pipeline as a concrete heterogeneous networking workload. It combines table-driven parsing and lookups with stateful, memory-intensive buffering, which makes the effect of processing placement easy to study. The implementation combines P4-programmable SmartNICs with a DPDK-enabled x86 host and supports both flow-based offloading and function-based partitioning in downlink and uplink.

The evaluation studies throughput, required CPU cores, round-trip delay, host and SmartNIC power, CPU frequency, and time-varying traffic. The host runs in either DPDK busy-wait mode (`BW`) or adaptive power-aware mode (`PA`), where CPU frequency and idle behavior follow the residual packet-processing workload.

On the five-SmartNIC testbed, the best function-based placements reach **108.5 MPPS in downlink** and **110.5 MPPS in uplink** for 128-byte packets, corresponding to **173%** and **62%** higher throughput than SmartNIC-only processing. The selected DL/UL function splits reduce Q99.9 round-trip delay by about **70%** compared with full host processing under busy waiting. Adaptive host power management reduces **ACPI-domain non-idle energy by up to 59%** in the reconstructed 24-hour evaluation. The reported energy saving is measured above the ACPI idle baseline.

---

## Repository layout

| Path | Purpose |
|---|---|
| `dpdk/` | Host gNB application preparation and BW/PA power configuration |
| `p4/` | P4 processing code and DL/UL function-split definitions |
| `smartnic/` | Netronome setup notes and five-SmartNIC testbed template |
| `traffic/` | TRex packet profiles and Python experiment sweeps |
| `measurement/` | ACPI/RAPL helpers and power-measurement instructions |
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

Fetch the implementation files and prepare the DPDK variants:

```bash
make fetch
```

The main generated/imported paths are:

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

To regenerate the DPDK variants after changing the power configuration:

```bash
make dpdk
```

The `power_aware` and `busy_wait` variants use the same gNB packet-processing path. `power_aware` applies the adaptive CPU policy, while `busy_wait` keeps the DPDK polling baseline.

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

The five SmartNICs are distributed across both NUMA domains. DPDK workers are pinned to CPU cores local to their SmartNICs, and packet buffers use NUMA-local hugepages.

For comparable performance and power measurements, use equivalent hardware capabilities and keep CPU, SmartNIC, and memory placement NUMA-local.

---

## 1. Prepare the DPDK host application

The host implementation uses the DPDK 20.08 `l3fwd-power` framework together with the gNB packet-processing application.

After `make fetch`, select one of the generated variants:

```text
dpdk/src/power_aware/main.c
dpdk/src/busy_wait/main.c
```

Copy the selected file into a DPDK 20.08 `l3fwd-power` tree. For example:

```bash
cp dpdk/src/power_aware/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

For the busy-wait baseline:

```bash
cp dpdk/src/busy_wait/main.c <DPDK-20.08>/examples/l3fwd-power/main.c
```

Keep `main.h`, `perf_core.c`, and `perf_core.h` from the same DPDK 20.08 example directory and build with the DPDK 20.08 toolchain.

Select the gNB table configuration at runtime with:

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

After `make fetch`, the P4 files are available under:

```text
p4/upstream/main.p4
p4/upstream/main_clone.p4
p4/upstream/base.p4cfg
p4/upstream/p4_cfg_generator.py
```

`main.p4` contains the gNB parser, TEID/DRB table logic, host-VF steering, and DL/UL protocol actions. `main_clone.p4` contains the SmartNIC cloning path used by the DL cloning case.

The processing boundaries used in the experiments are listed in [`p4/SPLITS.md`](p4/SPLITS.md). The SmartNIC always performs the common ingress parsing and steering logic; each function split then moves additional gNB processing stages to the SmartNIC.

Use [`smartnic/testbed.env.example`](smartnic/testbed.env.example) to map the five SmartNICs to local PF addresses, RTE ports, SDK paths, and VF counts. The setup scripts under `smartnic/upstream/` can then be adapted to the local testbed configuration.

---

## 3. Generate traffic with TRex

[`traffic/trex_gnb_profile.py`](traffic/trex_gnb_profile.py) defines the DL and UL packet formats and TRex streams.

It supports:

- DL GTP-U traffic;
- UL RLC/PDCP/SDAP traffic;
- up to 64k UE/TEID values;
- SmartNIC/host flow tagging through the outer IPv4 Identification field;
- fixed packet sizes and IMIX;
- controlled MPPS rates;
- 50 kpps latency probes.

A single operating point can be started from the TRex console:

```text
start -f traffic/trex_gnb_profile.py -p 0 -d 30 -t --direction dl --mpps 21 --pktsize 128 --offload 50
```

[`traffic/experiment_sweep.py`](traffic/experiment_sweep.py) keeps the experiment points directly in Python:

```python
RATE_POINTS_MPPS = [7, 21, 35, 49, 63, 77, 100]
FLOW_OFFLOAD_PERCENTAGES = [0, 30, 50, 70, 100]
DAILY_PACKET_PROFILES = [128, "imix", 590, 1518]
DIRECTIONS = ["dl", "ul"]
```

The runner sends one operating point, waits **5 s**, and starts the next one. The daily sequence evaluates **DL first and then UL**. Within each direction, packet profiles follow the paper order:

1. 128 B
2. IMIX
3. 590 B
4. 1518 B

Preview the daily sequence:

```bash
python3 traffic/experiment_sweep.py --suite daily --dry-run
```

Run it against TRex:

```bash
python3 traffic/experiment_sweep.py --suite daily --server 127.0.0.1 --port 0
```

Each daily operating point runs for **60 s** by default. The inter-run gap is **5 s** by default. Both values can be changed from the command line.

For the standard 128-byte load sweep:

```bash
python3 traffic/experiment_sweep.py --suite rate --direction dl --duration 30 --gap 5
```

For flow-based offloading:

```bash
python3 traffic/experiment_sweep.py --suite flow --direction dl --duration 30 --gap 5
```

See [`traffic/README.md`](traffic/README.md) for all options.

---

## 4. Processing placement

### Flow-based offloading

Complete flows are assigned to either the SmartNIC path or the host path. The traffic generator carries the path tag in the outer IPv4 Identification field. The paper evaluates SmartNIC stand-alone processing and 30%, 50%, 70%, and 100% host offload.

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
| Split-3 | Split-2 + GTP-U encapsulation | packet forwarding/storage path |

The daily evaluation uses **DL Split-3** and **UL Split-2**.

Placement is selected on the SmartNIC/DPDK side, while the TRex sweep controls the offered traffic. This keeps the same traffic sequence across the processing placements and BW/PA modes.

---

## 5. Latency measurements

Latency measurements add a dedicated **50 kpps** TRex probe stream to the background traffic. The reported metric is round-trip delay (RTD) from the traffic-generator host through the DUT and back.

Example:

```bash
python3 traffic/experiment_sweep.py --suite latency --direction dl --rates 7 21 35 --duration 30 --gap 5
```

The SmartNIC-only DL reference uses 7, 21, and 35 MPPS. Host and selected hybrid placements are evaluated across the required load range after configuring the corresponding DUT placement.

---

## 6. Power measurement

The paper uses three measurement levels:

1. **System power:** Supermicro ECO PDU outlet, sampled at 1 Hz and corrected using the PSU efficiency curve.
2. **Server/ACPI domain:** aggregate on-board ACPI power at 1 Hz.
3. **Components:** CPU package power, DRAM power, and CPU frequency with Intel SoC Watch 2024.6.0 at 100 ms; SmartNIC power at 1 Hz per card using the Netronome SDK.

The ACPI domain includes CPU activity together with shared host resources such as uncore, LLC, memory controller, PCIe activity, and mapped SmartNIC devices. ACPI and SmartNIC values are therefore reported as overlapping measurement domains.

[`measurement/tools/acpi.sh`](measurement/tools/acpi.sh) records the platform `power1` sensor. [`measurement/tools/msr.py`](measurement/tools/msr.py) provides Intel RAPL package and DRAM measurements for diagnostics and cross-checking. The paper reports CPU package, DRAM, and frequency measurements from Intel SoC Watch.

For short steady-state experiments, TRex reaches the target traffic load before the **20 s** power-measurement window starts.

---

## 7. 24-hour evaluation

Each hourly traffic load is measured as a **one-minute TRex operating point**. The hourly measurements are then weighted by the corresponding traffic volumes and combined into the 24-hour evaluation.

Use `--rates` to provide the hourly rate sequence to the runner. The daily sweep applies that sequence to DL and UL and evaluates the packet profiles in this order:

```python
[128, "imix", 590, 1518]
```

IMIX consists of **58.33% 64 B, 33.33% 590 B, and 8.33% 1514 B** packets.

The daily placement uses **DL Split-3** and **UL Split-2**. DL and UL measurements are combined with the selected directional traffic ratio to obtain the mixed daily profiles reported in the paper.

---

## EnergyTracer

The [`EnergyTracer/`](EnergyTracer/) directory contains the EnergyTracer tools used alongside the DPDK implementation. EnergyTracer aligns DPDK dataplane events, Linux CPU power-state activity, and hardware energy measurements on a common timeline.

The EnergyTracer tools support event-level analysis, while the TRex sweep provides the throughput, latency, power, and time-varying operating points used in this paper.

---

## Contact

If you have any question about the repo, please contact mohsen.memarian@kau.se
