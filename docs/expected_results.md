# Expected reference results

This file summarizes the principal values reported in the paper. They are reference targets for reproductions on the same testbed, not portable performance guarantees for different hardware.

## Peak packet-processing capacity

| Configuration | Reported capacity |
| --- | ---: |
| DL SmartNIC-only | approximately 40 MPPS |
| DL function-based Split-3 | 108.5 MPPS |
| UL SmartNIC-only | approximately 68 MPPS |
| UL function-based Split-2 | 110.5 MPPS |

The function-based peak corresponds to approximately 173% improvement over the DL SmartNIC-only case and approximately 62% over the UL SmartNIC-only case.

## Tail latency

Dedicated RTD probes run at 50 kpps. SmartNIC-only DL Q99.9 is approximately 38 us at 7 MPPS, 39 us at 21 MPPS, and 53 us at 35 MPPS. At full host processing, Q99.9 is approximately 601 us in busy-wait mode at 100 MPPS. The selected function-based placements, DL Split-3 and UL Split-2 under busy wait, reach approximately 182 us Q99.9 at full rate.

## Separate-direction daily non-idle energy savings

Idle ACPI baseline: approximately 255–258 W, corresponding to 6120–6192 Wh/day. This baseline is shown for context and is not included in the reported percentage reductions.

| Direction | Packet profile | Avg. saved (nJ/B) | Total saved (Wh) | Saved (%) |
| --- | --- | ---: | ---: | ---: |
| DL | 128 B | 7.8 | 1268.2 | 57.9 |
| DL | IMIX | 3.7 | 1407.7 | 59.0 |
| DL | 590 B | 1.4 | 456.9 | 56.6 |
| DL | 1518 B | 0.9 | 439.7 | 56.9 |
| UL | 128 B | 2.2 | 362.2 | 43.9 |
| UL | IMIX | 1.2 | 315.8 | 46.1 |
| UL | 590 B | 0.7 | 198.9 | 48.0 |
| UL | 1518 B | 0.6 | 187.8 | 49.7 |

## Mixed UL/DL daily profiles

| Profile | UL/DL ratio | Packet | Avg. saved (nJ/B) | Total saved (Wh) | Saved (%) |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | 42.5 / 57.5 | 128 B | 5.4 | 1777.7 | 54.9 |
| 1 | 42.5 / 57.5 | IMIX | 2.6 | 1687.2 | 55.9 |
| 1 | 42.5 / 57.5 | 590 B | 1.1 | 672.6 | 54.0 |
| 1 | 42.5 / 57.5 | 1518 B | 0.8 | 620.5 | 54.4 |
| 2 | 40.0 / 60.0 | 128 B | 5.6 | 1823.8 | 55.2 |
| 2 | 40.0 / 60.0 | IMIX | 2.7 | 1726.5 | 56.2 |
| 2 | 40.0 / 60.0 | 590 B | 1.1 | 683.2 | 54.2 |
| 2 | 40.0 / 60.0 | 1518 B | 0.8 | 627.0 | 54.6 |
| 3 | 25.0 / 75.0 | 128 B | 6.4 | 2100.4 | 56.4 |
| 3 | 25.0 / 75.0 | IMIX | 3.1 | 1962.2 | 57.5 |
| 3 | 25.0 / 75.0 | 590 B | 1.2 | 747.0 | 55.2 |
| 3 | 25.0 / 75.0 | 1518 B | 0.9 | 665.7 | 55.5 |
| 4 | 10.0 / 90.0 | 128 B | 7.3 | 2377.0 | 57.4 |
| 4 | 10.0 / 90.0 | IMIX | 3.4 | 2197.8 | 58.5 |
| 4 | 10.0 / 90.0 | 590 B | 1.3 | 810.8 | 56.1 |
| 4 | 10.0 / 90.0 | 1518 B | 0.9 | 704.5 | 56.4 |

The mixed profiles are reconstructed from independently measured DL and UL contributions rather than simultaneous bidirectional execution.
