# Data

Raw power and packet-trace files can be large, so they are not stored in this repository by default.

Suggested layout:

```text
data/
├── raw/
│   └── <run-id>/
├── processed/
└── daily/
    ├── hourly_profile_template.csv
    └── ul_dl_profiles.csv
```

For each run, keep enough metadata to identify the exact operating point and machine configuration. At minimum, record the repository revision, P4 placement, DPDK mode, CPU/lcore map, NUMA placement, hugepage allocation, packet profile, offered rate, UE count, warm-up interval, measurement interval, TRex TX/RX/drop counters, and the associated measurement files.

`daily/hourly_profile_template.csv` does not contain guessed hourly rates. The paper gives the source and reconstruction method for the 24-hour workload but not the complete numerical hourly series. Fill this file from the archived experiment input or the original traffic dataset rather than digitizing the plotted curve.

If the raw measurements are published separately, add the DOI, immutable URL, or checksum here. Small processed tables needed to regenerate figures can be kept under `data/processed/`.
