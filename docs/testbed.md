# Testbed

## Device under test

- 2 x Intel Xeon Gold 5418Y
- 24 cores per socket, 48 physical cores total
- 256 GB DDR5
- 5 x Netronome Agilio CX 2x40 G SmartNICs
- 60 SmartNIC micro-engine cores per card at 800 MHz
- Ubuntu 18.04 with HWE kernel
- DPDK 20.08
- NUMA-local DPDK workers and hugepages
- uncore fixed at 1.4 GHz

## Traffic generator

- separate x86 server
- 2 x Mellanox ConnectX-5 dual-port 100 G NICs
- TRex v3.04
- Arista 100 G switch between traffic generator and DUT
- static MAC-based forwarding across the five SmartNICs

## Traffic

GTP-U traffic is created from Scapy-based templates with varying destination addresses and TEIDs and supports up to 64k UEs. The default controlled-experiment packet size is 128 B. The IPv4 Identification field carries the flow-based offload tag.
