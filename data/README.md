# Data layout

Large raw measurement files are not committed by default.

Recommended layout:

```text
data/
├── raw/
│   └── <run-id>/
├── processed/
└── daily/
    ├── hourly_profile_template.csv
    └── ul_dl_profiles.csv
```

Each raw run should include metadata recording the repository revision, P4 placement, DPDK mode, CPU/lcore map, NUMA placement, hugepage allocation, packet profile, offered rate, UE count, warm-up duration, measurement duration, TRex TX/RX/drop counters, and measurement filenames.

`daily/hourly_profile_template.csv` deliberately contains no estimated hourly rates. The manuscript states the source and reconstruction procedure but does not print the complete numerical 24-hour traffic table. Populate it from the archived experiment input or the original source dataset rather than digitizing the plotted curve.

If a raw-data archive is published separately, add its DOI, immutable URL, or checksum here and keep any small processed tables required for figure reproduction under `data/processed/`.
