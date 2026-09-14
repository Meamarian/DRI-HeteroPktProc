# Function split definitions

## Downlink

| Split | SmartNIC stages | Host stages |
| --- | --- | --- |
| 0 | parser, offload decision, VFD | GTP-U decapsulation, DRB lookup, SDAP/PDCP/RLC insertion, cloning, saving |
| 1 | Split-0 + GTP-U decapsulation | DRB lookup, SDAP/PDCP/RLC insertion, cloning, saving |
| 2 | Split-1 + DRB lookup | SDAP/PDCP/RLC insertion, cloning, saving |
| 3 | Split-2 + SDAP/PDCP/RLC insertion | cloning, saving |
| 4 | Split-3 + cloning | saving |

## Uplink

| Split | SmartNIC stages | Host stages |
| --- | --- | --- |
| 0 | parser, offload decision, VFD | RLC/PDCP/SDAP removal, DRB lookup, GTP-U encapsulation |
| 1 | Split-0 + RLC/PDCP/SDAP removal | DRB lookup, GTP-U encapsulation |
| 2 | Split-1 + DRB lookup | GTP-U encapsulation |
| 3 | Split-2 + GTP-U encapsulation | none |

Packet-buffer storage remains in host memory. At DL Split-4 the SmartNIC creates the clone and the clone is transferred to the host for storage.
