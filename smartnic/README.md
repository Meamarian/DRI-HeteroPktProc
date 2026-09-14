# SmartNIC setup

The paper testbed uses five Netronome Agilio CX 2x40 G SmartNICs.

Use [`testbed.env.example`](testbed.env.example) to record the local PF addresses, RTE ports, SDK path, and VF count for the five cards. The setup files under `smartnic/upstream/` can then be adapted to those local values.

A typical setup sequence is:

1. install the matching Netronome SDK and P4 toolchain;
2. configure the NFP driver and SR-IOV mode;
3. create the required VFs on each SmartNIC;
4. load the selected P4 firmware and runtime configuration;
5. bind the host-facing VFs to the DPDK driver used on the DUT;
6. verify the NUMA node for every VF and pin the corresponding DPDK worker locally;
7. record the final PF/VF PCI map with the experiment metadata.

The five-card layout is distributed across both NUMA domains. Keep each DPDK worker and its packet buffers local to the SmartNIC it serves.
