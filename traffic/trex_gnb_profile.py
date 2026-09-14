from trex_stl_lib.api import STLFlowLatencyStats, STLPktBuilder, STLStream, STLTXCont, STLVmFixIpv4, STLVmFlowVar, STLVmWrFlowVar
from scapy.all import BitField, IPField, Packet, Raw
import argparse
import os


class EthLayer(Packet):
    name = "EthLayer"
    fields_desc = [BitField("dmac", 0, 48), BitField("smac", 0, 48), BitField("type", 0x0800, 16)]


class IPv4Layer(Packet):
    name = "IPv4Layer"
    fields_desc = [
        BitField("version", 4, 4), BitField("ihl", 5, 4), BitField("diffserv", 0, 8),
        BitField("totalLen", 0, 16), BitField("identification", 0, 16), BitField("flags", 0, 3),
        BitField("fragOffset", 0, 13), BitField("ttl", 64, 8), BitField("protocol", 17, 8),
        BitField("hdrChecksum", 0, 16), IPField("srcAddr", "10.0.0.1"), IPField("dstAddr", "10.0.0.2")
    ]


class UDPLayer(Packet):
    name = "UDPLayer"
    fields_desc = [BitField("srcPort", 0, 16), BitField("dstPort", 0, 16), BitField("len", 0, 16), BitField("checksum", 0, 16)]


class GTPULayer(Packet):
    name = "GTPULayer"
    fields_desc = [
        BitField("flags", 1, 8), BitField("type", 0xff, 8), BitField("length", 32, 16),
        BitField("teid", 0, 32), BitField("seq_num", 0, 16), BitField("qfi", 0, 8)
    ]


class RLCackmodeLayer(Packet):
    name = "RLCackmodeLayer"
    fields_desc = [
        BitField("dc", 1, 1), BitField("p", 0, 1), BitField("si", 0, 2), BitField("r", 0, 2),
        BitField("snpadding", 0, 2), BitField("sn", 0, 16), BitField("teid", 0, 32)
    ]


class PDCPLayer(Packet):
    name = "PDCPLayer"
    fields_desc = [BitField("dc", 0, 4), BitField("r", 0, 4), BitField("sn", 0, 16)]


class SDAPULLayer(Packet):
    name = "SDAPULLayer"
    fields_desc = [BitField("dc", 0, 1), BitField("r", 0, 1), BitField("qfi", 0, 6)]


def _pad(pkt, wire_size):
    target = max(60, int(wire_size) - 4)
    missing = target - len(pkt)
    return pkt / Raw(b"x" * missing) if missing > 0 else pkt


def dl_packet(wire_size, tag):
    pkt = (
        EthLayer(dmac=0x112233445566, smac=0x66778899aabb)
        / IPv4Layer(totalLen=wire_size, identification=tag)
        / UDPLayer(srcPort=2152, dstPort=2152)
        / GTPULayer()
        / IPv4Layer(totalLen=wire_size, srcAddr="10.0.0.1", dstAddr="10.0.0.2")
        / UDPLayer(srcPort=2153, dstPort=2152)
    )
    return _pad(pkt, wire_size)


def ul_packet(wire_size, tag):
    pkt = (
        EthLayer(dmac=0x112233445566, smac=0x66778899aabb)
        / IPv4Layer(totalLen=wire_size, identification=tag)
        / UDPLayer(srcPort=8042, dstPort=2152)
        / RLCackmodeLayer()
        / PDCPLayer()
        / SDAPULLayer()
        / IPv4Layer(totalLen=wire_size, srcAddr="10.0.0.1", dstAddr="10.0.0.2")
        / UDPLayer(srcPort=2153, dstPort=2152)
    )
    return _pad(pkt, wire_size)


def profile_sizes(name, fixed_size):
    if name == "imix":
        return [(64, 0.5833), (590, 0.3333), (1514, 0.0834)]
    return [(fixed_size, 1.0)]


def make_builder(direction, wire_size, tag, uecount):
    pkt = dl_packet(wire_size, tag) if direction == "dl" else ul_packet(wire_size, tag)
    vm = [
        STLVmFlowVar("dstip", min_value="10.0.0.1", max_value="10.0.255.255", size=4, op="inc"),
        STLVmWrFlowVar(fv_name="dstip", pkt_offset="IPv4Layer.dstAddr"),
        STLVmFixIpv4(offset="IPv4Layer")
    ]
    if direction == "dl":
        vm.insert(0, STLVmFlowVar("teid", min_value=0, max_value=max(0, min(63999, uecount - 1)), size=4, op="inc"))
        vm.insert(1, STLVmWrFlowVar(fv_name="teid", pkt_offset="GTPULayer.teid"))
    return STLPktBuilder(pkt=pkt, vm=vm)


def add_background(streams, args, tag, path_weight):
    if path_weight <= 0:
        return
    for wire_size, size_weight in profile_sizes(args.profile, args.pktsize):
        pps = args.mpps * 1_000_000.0 * path_weight * size_weight
        if pps <= 0:
            continue
        builder = make_builder(args.direction, wire_size, tag, args.uecount)
        streams.append(STLStream(packet=builder, mode=STLTXCont(pps=pps)))


def build_streams(args):
    streams = []
    host_weight = args.offload / 100.0
    add_background(streams, args, args.host_tag, host_weight)
    add_background(streams, args, args.smartnic_tag, 1.0 - host_weight)
    if args.latency:
        tag = args.host_tag if args.offload >= 50 else args.smartnic_tag
        pkt = dl_packet(args.pktsize, tag) if args.direction == "dl" else ul_packet(args.pktsize, tag)
        streams.append(
            STLStream(
                packet=STLPktBuilder(pkt=pkt),
                mode=STLTXCont(pps=args.latency_pps),
                flow_stats=STLFlowLatencyStats(pg_id=args.pg_id)
            )
        )
    return streams


class STLGnbProfile:
    def get_streams(self, tunables, **kwargs):
        parser = argparse.ArgumentParser(description=os.path.basename(__file__))
        parser.add_argument("--direction", choices=["dl", "ul"], required=True)
        parser.add_argument("--mpps", type=float, required=True)
        parser.add_argument("--pktsize", type=int, default=128)
        parser.add_argument("--profile", choices=["fixed", "imix"], default="fixed")
        parser.add_argument("--uecount", type=int, default=64000)
        parser.add_argument("--offload", type=float, default=100.0)
        parser.add_argument("--host-tag", type=int, default=1)
        parser.add_argument("--smartnic-tag", type=int, default=0)
        parser.add_argument("--latency", action="store_true")
        parser.add_argument("--latency-pps", type=float, default=50000.0)
        parser.add_argument("--pg-id", type=int, default=13)
        args = parser.parse_args(tunables)
        if not 0.0 <= args.offload <= 100.0:
            raise ValueError("--offload must be between 0 and 100")
        if not 1 <= args.uecount <= 64000:
            raise ValueError("--uecount must be between 1 and 64000")
        if args.mpps <= 0:
            raise ValueError("--mpps must be positive")
        return build_streams(args)


def register():
    return STLGnbProfile()
