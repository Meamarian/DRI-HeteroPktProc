# SmartNIC setup

The paper testbed uses five Netronome Agilio CX 2x40 G SmartNICs. The setup files from the earlier IFIP implementation are imported under `smartnic/upstream/`.

Those files were written for the original lab setup and include machine-specific PCI addresses, service names, and SDK paths. Check them before running anything on a different system. [`testbed.env.example`](testbed.env.example) provides a clean five-card inventory template for recording the local PF addresses, RTE ports, SDK location, and VF count.

A typical setup sequence is:

1. install the matching Netronome SDK/P4 toolchain;
2. configure the NFP driver and SR-IOV mode;
3. create the required VFs on each SmartNIC;
4. load the selected P4 firmware/configuration;
5. bind the host-facing VFs to the DPDK driver used on the DUT;
6. verify the NUMA node for every VF and pin the corresponding DPDK worker locally;
7. record the final PF/VF PCI map with the experiment metadata.

The imported scripts target the earlier two-card setup and are kept as a reference. Do not run them unchanged on the five-card testbed.
