import argparse
import time
from types import SimpleNamespace

from trex_stl_lib.api import STLClient

from trex_gnb_profile import build_streams


RATE_POINTS_MPPS = [7, 21, 35, 49, 63, 77, 100]
FLOW_OFFLOAD_PERCENTAGES = [0, 30, 50, 70, 100]
DAILY_PACKET_PROFILES = [128, "imix", 590, 1518]
DIRECTIONS = ["dl", "ul"]


def packet_settings(packet):
    if str(packet).lower() == "imix":
        return "imix", 128
    return "fixed", int(packet)


def stream_args(direction, mpps, packet, offload, uecount, latency, latency_pps, pg_id):
    profile, pktsize = packet_settings(packet)
    return SimpleNamespace(
        direction=direction,
        mpps=float(mpps),
        pktsize=pktsize,
        profile=profile,
        uecount=uecount,
        offload=float(offload),
        host_tag=1,
        smartnic_tag=0,
        latency=latency,
        latency_pps=latency_pps,
        pg_id=pg_id,
    )


def selected_directions(value):
    return DIRECTIONS if value == "both" else [value]


def build_cases(suite, direction, rates, packet, offload):
    directions = selected_directions(direction)
    cases = []

    if suite == "rate":
        for current_direction in directions:
            for rate in rates:
                cases.append((current_direction, rate, packet, offload, False))

    if suite == "flow":
        for current_direction in directions:
            for current_offload in FLOW_OFFLOAD_PERCENTAGES:
                for rate in rates:
                    cases.append((current_direction, rate, 128, current_offload, False))

    if suite == "daily":
        for current_direction in directions:
            for current_packet in DAILY_PACKET_PROFILES:
                for rate in rates:
                    cases.append((current_direction, rate, current_packet, 100, False))

    if suite == "latency":
        for current_direction in directions:
            for rate in rates:
                cases.append((current_direction, rate, packet, offload, True))

    return cases


def case_name(case):
    direction, rate, packet, offload, latency = case
    suffix = " latency" if latency else ""
    return f"{direction.upper()} packet={packet} rate={rate:g}MPPS offload={offload:g}%{suffix}"


def run_case(client, port, duration, case, uecount, latency_pps, pg_id):
    direction, rate, packet, offload, latency = case
    args = stream_args(direction, rate, packet, offload, uecount, latency, latency_pps, pg_id)
    streams = build_streams(args)
    client.remove_all_streams(ports=[port])
    client.add_streams(streams, ports=[port])
    client.clear_stats(ports=[port])
    client.start(ports=[port], duration=duration, force=True)
    client.wait_on_traffic(ports=[port], timeout=duration + 30)
    stats = client.get_stats(ports=[port]).get(port, {})
    print(
        f"tx={stats.get('opackets', 0)} rx={stats.get('ipackets', 0)} "
        f"tx_pps={stats.get('tx_pps', 0):.0f} rx_pps={stats.get('rx_pps', 0):.0f}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=["rate", "flow", "daily", "latency"], default="rate")
    parser.add_argument("--direction", choices=["dl", "ul", "both"], default="both")
    parser.add_argument("--rates", nargs="+", type=float)
    parser.add_argument("--packet", default="128")
    parser.add_argument("--offload", type=float, default=100.0)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--gap", type=float, default=5.0)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--server", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--uecount", type=int, default=64000)
    parser.add_argument("--latency-pps", type=float, default=50000.0)
    parser.add_argument("--pg-id", type=int, default=13)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not 0 <= args.offload <= 100:
        raise SystemExit("--offload must be between 0 and 100")
    if args.repeat < 1:
        raise SystemExit("--repeat must be at least 1")

    rates = args.rates or RATE_POINTS_MPPS
    duration = args.duration if args.duration is not None else (60.0 if args.suite == "daily" else 30.0)
    cases = build_cases(args.suite, args.direction, rates, args.packet, args.offload)
    sequence = cases * args.repeat

    if args.dry_run:
        for index, case in enumerate(sequence, 1):
            print(f"{index:03d} {case_name(case)} duration={duration:g}s gap={args.gap:g}s")
        return

    client = STLClient(server=args.server)
    client.connect()
    try:
        client.acquire(ports=[args.port], force=True)
        client.reset(ports=[args.port])
        for index, case in enumerate(sequence, 1):
            print(f"[{index}/{len(sequence)}] {case_name(case)}")
            run_case(client, args.port, duration, case, args.uecount, args.latency_pps, args.pg_id)
            if index != len(sequence):
                time.sleep(args.gap)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
