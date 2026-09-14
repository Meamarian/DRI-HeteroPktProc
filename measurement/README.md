# Power measurement

The evaluation uses three measurement levels and keeps their boundaries separate.

## Measurements used in the paper

- **System power:** Supermicro ECO PDU outlet at 1 Hz, corrected with the PSU efficiency curve.
- **Server/ACPI domain:** aggregate on-board ACPI power at 1 Hz.
- **CPU and memory:** Intel SoC Watch 2024.6.0 at 100 ms for package power, DRAM power, and average CPU frequency.
- **SmartNICs:** Netronome SDK power readings at 1 Hz per card, summed across the five SmartNICs.

The ACPI domain includes the active CPU cores together with shared host resources such as uncore, LLC, memory-controller and PCIe activity, as well as the mapped SmartNIC devices. Because the ACPI and SmartNIC domains overlap, they must not be added as independent power components.

## Included helper scripts

`tools/acpi.sh` and `tools/msr.py` come from the GreenQUIC measurement workflow at the revision listed in [`../sources.lock`](../sources.lock).

### ACPI/platform sensor

`acpi.sh` records the last `power1` value reported by `lm-sensors` once per second for a requested duration:

```bash
bash measurement/tools/acpi.sh 20 > acpi.log
```

Use this only when the exposed `power1` sensor corresponds to the on-board aggregate power measurement intended for the experiment.

### Intel RAPL helper

`msr.py` reads Intel RAPL package and DRAM energy counters from Linux `sysfs`, converts the counter deltas to watts, and reports both samples and time-weighted averages:

```bash
sudo python3 measurement/tools/msr.py 100 20
```

Its default paths point to package 0 and the first DRAM domain. This script is useful for diagnostics and cross-checking; the package/DRAM/frequency values reported in the paper were measured with SoC Watch.

## Measurement windows

For the controlled operating points, TRex is brought to the target rate before a 20 s steady-state power window is recorded. The reconstructed daily analysis uses independent one-minute TRex runs for the hourly operating points.
