# P4 / SmartNIC processing

The P4 implementation provides the SmartNIC-side gNB processing used in the experiments.

Fetch the files from the repository root with:

```bash
make fetch
```

The main files are placed under `p4/upstream/`:

```text
main.p4
main_clone.p4
base.p4cfg
p4_cfg_generator.py
```

`main.p4` contains the gNB parser, TEID/DRB table logic, host-VF steering, and DL/UL protocol actions. `main_clone.p4` contains the SmartNIC cloning path used by the DL cloning case.

The processing placements used in the paper are listed in [`SPLITS.md`](SPLITS.md). The SmartNIC keeps the common ingress parsing and steering logic, and each split moves additional gNB processing stages to the SmartNIC.

For flow-based offloading, the traffic generator places the path tag in the outer IPv4 Identification field. The tag selects the SmartNIC path or the host path for the complete flow.

Use `base.p4cfg` and `p4_cfg_generator.py` to prepare the P4 runtime configuration and the 64k-entry DRB/TEID table used by the experiments.
