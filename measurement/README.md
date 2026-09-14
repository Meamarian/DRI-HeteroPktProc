# Power measurement tools

The paper separates system-, server-, and component-level measurements and keeps their boundaries explicit.

## Paper measurement path

The reported evaluation uses:

- Supermicro ECO PDU outlet power at 1 Hz, corrected with the PSU efficiency curve;
- aggregate ACPI-domain power at 1 Hz from the server's on-board meters;
- Intel SoC Watch 2024.6.0 at 100 ms for CPU package power, DRAM power, and average CPU frequency;
- Netronome SDK measurements at 1 Hz per SmartNIC, aggregated over all five cards.

The ACPI domain includes host processing, uncore, memory-controller, LLC, PCIe activity, and mapped SmartNIC devices. ACPI and SmartNIC measurements therefore overlap and must not be added as independent components.

## Included helpers

`tools/acpi.sh` and `tools/msr.py` are copied from the GreenQUIC measurement tooling at the pinned revision in `../sources.lock`.

`acpi.sh` samples the last `power1` line exposed by `lm-sensors` once per second for a requested duration. It is appropriate only on systems where that sensor corresponds to the ACPI/on-board aggregate measurement used in the experiment.

Run:

```bash
bash measurement/tools/acpi.sh 20 > acpi.log
```

`msr.py` reads Intel RAPL package and DRAM energy counters from Linux `sysfs`, converts counter deltas to watts, and prints both samples and time-weighted averages. Its default paths point to package 0 and its first DRAM domain.

Run:

```bash
sudo python3 measurement/tools/msr.py 100 20
```

The RAPL helper is provided for diagnostics and cross-checking. The paper's reported package/DRAM/frequency measurements use SoC Watch, not this helper.

## Measurement windows

Controlled operating points are measured over a 20 s steady-state window after TRex reaches the target load and the system stabilizes. Each hourly point used in the reconstructed daily evaluation uses an independent one-minute TRex run.
