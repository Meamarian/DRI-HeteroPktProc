# P4 and SmartNIC processing

The P4 implementation is imported from `Meamarian/Hybrid_P4_IFIP_WMNC_24` at the revision recorded in `../sources.lock`.

Run:

```bash
./scripts/fetch_upstream.sh
```

The imported files are placed under `p4/upstream/`:

```text
main.p4
main_clone.p4
base.p4cfg
p4_cfg_generator.py
```

`main.p4` contains the gNB header parsing, DRB/TEID table logic, host-VF steering, and DL/UL protocol actions. `main_clone.p4` contains the SmartNIC cloning path used for the DL cloning case.

The paper evaluates the placement boundaries listed in `SPLITS.md`. The common P4 ingress parser, offload decision, and VF distributor remain on the SmartNIC for all split points. Flow-based assignment uses an offload tag carried in the IPv4 Identification field to select the SmartNIC or host path.

The original public IFIP repository does not contain a separate P4 source file for every DL and UL split used in the journal evaluation. For that reason this repository preserves the exact available P4 sources and documents the split semantics without inventing unvalidated split-specific programs. Exact compiled P4 sources or firmware used for each reported split should be added under `p4/paper/` when the archived experiment copies are available.
