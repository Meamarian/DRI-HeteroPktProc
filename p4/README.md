# P4 / SmartNIC processing

The P4 implementation comes from `Meamarian/Hybrid_P4_IFIP_WMNC_24` at the revision listed in [`../sources.lock`](../sources.lock).

Fetch the source files with:

```bash
./scripts/fetch_upstream.sh
```

They are placed under `p4/upstream/`:

```text
main.p4
main_clone.p4
base.p4cfg
p4_cfg_generator.py
```

`main.p4` contains the gNB parser, TEID/DRB table logic, host-VF steering, and DL/UL protocol actions. `main_clone.p4` contains the SmartNIC cloning path used by the DL cloning case.

The placement points evaluated in the paper are listed in [`SPLITS.md`](SPLITS.md). Across these placements, the SmartNIC keeps the common ingress parsing and steering logic while additional processing stages are moved between the SmartNIC and the host.

For flow-based offloading, the traffic generator places the offload tag in the outer IPv4 Identification field. The tag selects whether a complete flow follows the SmartNIC path or is forwarded to the host.

The earlier public IFIP repository does not contain a separate archived P4 program for every DL and UL split used in the journal evaluation. The available source is therefore kept unchanged here, and `SPLITS.md` documents the placement semantics. Archived split-specific P4 programs or firmware should be added separately if they become available.
