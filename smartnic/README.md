# SmartNIC setup

The reported DUT uses five Netronome Agilio CX 2x40 G SmartNICs. The original setup scripts from the earlier IFIP implementation are imported under `smartnic/upstream/`.

Those scripts contain lab-specific PCI addresses, service names, and SDK paths. Review them before use. `testbed.env.example` provides a neutral five-card inventory template for recording the local PF addresses, RTE ports, SDK location, and VF count.

The expected setup sequence is:

1. install the matching Netronome SDK/P4 toolchain;
2. configure the NFP kernel module and SR-IOV mode;
3. create the required VFs for each SmartNIC;
4. load the selected P4 firmware/configuration;
5. bind host-facing VFs to the DPDK driver used on the DUT;
6. verify NUMA locality for each VF and its DPDK worker;
7. record the final PF/VF PCI map with the experiment metadata.

The earlier two-card scripts are retained as implementation references rather than executed automatically on a five-card system.
