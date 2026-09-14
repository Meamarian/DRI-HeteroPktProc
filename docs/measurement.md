# Measurement methodology

The controlled operating-point experiments first bring TRex to the target load and allow the system to reach steady state. Power is then recorded over a 20 s measurement window.

The reconstructed daily analysis uses independent one-minute TRex runs for each hourly operating point. The measured operating points are weighted afterward by the corresponding hourly traffic volumes; the experiment is not a continuous 24-hour replay.

## Measurement hierarchy

- Supermicro ECO PDU outlet power at 1 Hz, corrected using the PSU efficiency curve used in the paper: 90% at 20% load, 92% at 50% load, and 89% at full load.
- Aggregate ACPI-domain power at 1 Hz from the server's on-board meters.
- CPU package power, DRAM power, and average CPU frequency at 100 ms using Intel SoC Watch 2024.6.0.
- Per-card SmartNIC power at 1 Hz using the Netronome SDK, aggregated over the five cards.

The ACPI domain includes active host cores and shared server resources such as uncore, LLC, memory-controller and PCIe activity, together with mapped SmartNIC devices. ACPI and SmartNIC measurements therefore overlap and must not be added as independent components.

The daily analysis uses an idle ACPI baseline of approximately 255–258 W. Reported savings are reductions in energy above this idle baseline relative to busy waiting; they are not reductions in total server, facility, or lifecycle energy.

`../measurement/` contains the ACPI/RAPL helper scripts and their scope.
