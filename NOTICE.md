# Notice

Project-specific scripts and documentation in this repository are distributed under the repository MIT license.

Imported or derived source files retain the copyright and license notices present in their upstream sources. DPDK-derived source files use the BSD-3-Clause license where indicated by their SPDX headers.

Source provenance is pinned in `sources.lock`:

- `Meamarian/EnergyTracer` supplies the DPDK gNB/power-aware implementation and EnergyTracer tooling path;
- `Meamarian/Hybrid_P4_IFIP_WMNC_24` supplies the P4/SmartNIC implementation, Netronome setup material, configuration generation, and reference TRex packet templates;
- `Meamarian/GreenQUIC` supplies the ACPI and Intel RAPL measurement helpers under `measurement/tools/`.

The external DPDK, TRex, Netronome SDK/P4 toolchain, and Intel SoC Watch distributions are not redistributed by this repository and remain subject to their own licenses and terms.
