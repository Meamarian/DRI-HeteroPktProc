# Power measurement

The evaluation uses three measurement levels so power can be viewed at system, server, and component level.

## Measurements used in the paper

- **System power:** Supermicro ECO PDU outlet at 1 Hz, corrected with the PSU efficiency curve.
- **Server/ACPI domain:** aggregate on-board ACPI power at 1 Hz.
- **CPU and memory:** Intel SoC Watch 2024.6.0 at 100 ms for package power, DRAM power, and average CPU frequency.
- **SmartNICs:** Netronome SDK power readings at 1 Hz per card,  summed across the five SmartNICs.

The ACPI domain includes active CPU cores together with shared host resources such as uncore, LLC, memory controller, PCIe activity, and mapped SmartNIC devices. Report ACPI and SmartNIC values as separate, overlapping measurement domains.

## Power-management threshold tuning

The power controller was tuned by sweeping each threshold from deliberately wide low and high bounds and then narrowing the range with midpoint tests. The sweep covers RX batching, queue-driven frequency increases, empty-poll idle entry, and periodic frequency down-scaling. Promising settings were then combined, with throughput used as the primary selection criterion, followed by power and Q99.9 round-trip delay.

The complete tuning sheet is [`tuning/power_alg_thr_tunning.xlsx`](tuning/power_alg_thr_tunning.xlsx). The final controller values are listed in [`../dpdk/config/power-paper.conf`](../dpdk/config/power-paper.conf).

## Helper scripts

`tools/acpi.sh` and `tools/msr.py` provide lightweight command-line measurements for the host.

### ACPI/platform sensor

`acpi.sh` records the last `power1` value reported by `lm-sensors` once per second for the requested duration:

```bash
bash measurement/tools/acpi.sh 20 > acpi.log
```

Use the platform sensor that corresponds to the on-board aggregate ACPI measurement on the DUT.

### Intel RAPL helper

`msr.py` reads Intel RAPL package and DRAM energy counters from Linux `sysfs`, converts counter deltas to watts, and reports samples together with time-weighted averages:

```bash
sudo python3 measurement/tools/msr.py 100 20
```

The default paths point to package 0 and its first DRAM domain. The script is useful for quick checks and cross-comparison with the Intel SoC Watch measurements used in the paper.

## Measurement windows

For controlled operating points, TRex reaches the target rate before the **20 s** steady-state power window starts.

For the reconstructed 24-hour evaluation, each hourly traffic level is measured in an independent **one-minute TRex run**. These hourly measurements are then weighted by the corresponding traffic volumes.
