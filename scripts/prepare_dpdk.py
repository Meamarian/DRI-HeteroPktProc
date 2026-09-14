from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "dpdk" / "upstream" / "gNB_power_aware.c"
OUT_PA = ROOT / "dpdk" / "src" / "power_aware" / "main.c"
OUT_BW = ROOT / "dpdk" / "src" / "busy_wait" / "main.c"


def replace_once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one occurrence, found {count}: {old[:80]}")
    return text.replace(old, new, 1)


def prepare_power_aware(text):
    text = replace_once(text, "#define MIN_ZERO_POLL_COUNT 50000", "#define MIN_ZERO_POLL_COUNT 10")
    text = replace_once(text, "#define MINIMUM_SLEEP_TIME         0", "#define MINIMUM_SLEEP_TIME         10")
    text = replace_once(text, "#define SUSPEND_THRESHOLD          30000", "#define SUSPEND_THRESHOLD          300")
    text = replace_once(text, "#define FREQ_GEAR1_RX_PACKET_THRESHOLD             MAX_PKT_BURST\n#define FREQ_GEAR2_RX_PACKET_THRESHOLD             (MAX_PKT_BURST * 2)\n#define FREQ_GEAR3_RX_PACKET_THRESHOLD             (MAX_PKT_BURST * 3)", "#define FREQ_GEAR1_RX_PACKET_THRESHOLD             96\n#define FREQ_GEAR2_RX_PACKET_THRESHOLD             64\n#define FREQ_GEAR3_RX_PACKET_THRESHOLD             32")
    text = replace_once(text, "#define FREQ_UP_TREND1_ACC   3\n#define FREQ_UP_TREND2_ACC   25\n#define FREQ_UP_THRESHOLD    100", "#define FREQ_UP_TREND1_ACC   250\n#define FREQ_UP_TREND2_ACC   3\n#define FREQ_UP_THRESHOLD    10000")
    old = """\tif (likely(rxq_count > FREQ_GEAR3_RX_PACKET_THRESHOLD)) {
\t\tstats[lcore_id].trend = 0;
\t\treturn FREQ_HIGHEST;
\t} else if (likely(rxq_count > FREQ_GEAR2_RX_PACKET_THRESHOLD))
\t\tstats[lcore_id].trend += FREQ_UP_TREND2_ACC;
\telse if (likely(rxq_count > FREQ_GEAR1_RX_PACKET_THRESHOLD))
\t\tstats[lcore_id].trend += FREQ_UP_TREND1_ACC;"""
    new = """\tif (likely(rxq_count > FREQ_GEAR1_RX_PACKET_THRESHOLD)) {
\t\tstats[lcore_id].trend = 0;
\t\treturn FREQ_HIGHEST;
\t} else if (likely(rxq_count > FREQ_GEAR2_RX_PACKET_THRESHOLD))
\t\tstats[lcore_id].trend += FREQ_UP_TREND1_ACC;
\telse if (likely(rxq_count > FREQ_GEAR3_RX_PACKET_THRESHOLD))
\t\tstats[lcore_id].trend += FREQ_UP_TREND2_ACC;"""
    text = replace_once(text, old, new)
    text = replace_once(text, "rte_epoll_wait(RTE_EPOLL_PER_THREAD, event, num, 50)", "rte_epoll_wait(RTE_EPOLL_PER_THREAD, event, num, 10)")
    old_idle = """\t\t\t// if (lcore_idle_hint < SUSPEND_THRESHOLD) {
\t\t\t// \trte_delay_us(lcore_idle_hint);
\t\t\t// } else {
\t\t\t// \t/* suspend until rx interrupt triggers */
\t\t\t// \tif (intr_en) {
\t\t\t// \t\tturn_on_off_intr(qconf, 1);

\t\t\t// \t\tsleep_until_rx_interrupt(
\t\t\t// \t\t\tqconf->n_rx_queue);
\t\t\t// \t\tturn_on_off_intr(qconf, 0);
\t\t\t// \t\t/**
\t\t\t// \t\t * start receiving packets immediately
\t\t\t// \t\t */
\t\t\t// \t\tif (likely(!is_done()))
\t\t\t// \t\t\tgoto start_rx;
\t\t\t// \t}
\t\t\t// }"""
    new_idle = """\t\t\tif (lcore_idle_hint < SUSPEND_THRESHOLD) {
\t\t\t\trte_delay_us(lcore_idle_hint);
\t\t\t} else if (intr_en) {
\t\t\t\tturn_on_off_intr(qconf, 1);
\t\t\t\tsleep_until_rx_interrupt(qconf->n_rx_queue);
\t\t\t\tturn_on_off_intr(qconf, 0);
\t\t\t\tif (likely(!is_done()))
\t\t\t\t\tgoto start_rx;
\t\t\t}"""
    text = replace_once(text, old_idle, new_idle)
    old_timer = """\tif (app_mode == APP_MODE_LEGACY) {
\t\t/* init timer structures for each enabled lcore */
\t\t/* Power Mng Algortimgn heriotic: create and arm the background timer used by the legacy mode for periodic frequency down-scaling decisions. */
\t\trte_timer_init(&power_timers[lcore_id]);
\t\thz = rte_get_timer_hz();
\t\trte_timer_reset(&power_timers[lcore_id],
\t\t\t\thz/TIMER_NUMBER_PER_SECOND,
\t\t\t\tSINGLE, lcore_id,
\t\t\t\tpower_timer_cb, NULL);
\t}"""
    new_timer = """\tif (app_mode == APP_MODE_LEGACY) {
\t\thz = rte_get_timer_hz();
\t\tRTE_LCORE_FOREACH(lcore_id) {
\t\t\trte_timer_init(&power_timers[lcore_id]);
\t\t\trte_timer_reset(&power_timers[lcore_id],
\t\t\t\thz/TIMER_NUMBER_PER_SECOND,
\t\t\t\tSINGLE, lcore_id,
\t\t\t\tpower_timer_cb, NULL);
\t\t}
\t}"""
    text = replace_once(text, old_timer, new_timer)
    hardcoded = 'populate_teid_qfi_table("/home/admin/mohsen/dpdk/examples/l3fwd-power/config_table1_64000_0_table2_10.0.0.0_10.0.250.0_0.txt");'
    portable = 'const char *gnb_config = getenv("GNB_CONFIG");\n\tif (gnb_config == NULL)\n\t\tgnb_config = "./config/teid_table.json";\n\tpopulate_teid_qfi_table(gnb_config);'
    text = replace_once(text, hardcoded, portable)
    return text


def prepare_busy_wait(text):
    text = text.replace("#define MIN_ZERO_POLL_COUNT 10", "#define MIN_ZERO_POLL_COUNT UINT32_MAX", 1)
    text = text.replace("if (app_mode == APP_MODE_LEGACY) {\n\t\thz = rte_get_timer_hz();", "if (0 && app_mode == APP_MODE_LEGACY) {\n\t\thz = rte_get_timer_hz();", 1)
    text = text.replace("if ((app_mode == APP_MODE_LEGACY || app_mode == APP_MODE_EMPTY_POLL) &&\n\t\t\t/* Power Mng Algortimgn heriotic: bring up the power library only for the modes that actively control CPU frequency. */\n\t\t\tinit_power_library())", "if (0 && (app_mode == APP_MODE_LEGACY || app_mode == APP_MODE_EMPTY_POLL) &&\n\t\t\tinit_power_library())", 1)
    text = text.replace("if ((app_mode == APP_MODE_LEGACY || app_mode == APP_MODE_EMPTY_POLL) &&\n\t\t\t/* Power Mng Algortimgn heriotic: shut down the power library after worker loops stop so CPU control state is cleaned up properly. */\n\t\t\tdeinit_power_library())", "if (0 && (app_mode == APP_MODE_LEGACY || app_mode == APP_MODE_EMPTY_POLL) &&\n\t\t\tdeinit_power_library())", 1)
    text = text.replace("rx_queue->freq_up_hint =\n\t\t\t\t\tpower_freq_scaleup_heuristic(lcore_id,\n\t\t\t\t\t\t\tportid, queueid);", "rx_queue->freq_up_hint = FREQ_CURRENT;", 1)
    return text


def validate(text):
    required = [
        "#define MIN_ZERO_POLL_COUNT 10",
        "#define MINIMUM_SLEEP_TIME         10",
        "#define SUSPEND_THRESHOLD          300",
        "#define FREQ_GEAR1_RX_PACKET_THRESHOLD             96",
        "#define FREQ_GEAR2_RX_PACKET_THRESHOLD             64",
        "#define FREQ_GEAR3_RX_PACKET_THRESHOLD             32",
        "#define FREQ_UP_TREND1_ACC   250",
        "#define FREQ_UP_TREND2_ACC   3",
        "#define FREQ_UP_THRESHOLD    10000",
        "SCALING_DOWN_TIME_RATIO_THRESHOLD 0.25",
        "rte_epoll_wait(RTE_EPOLL_PER_THREAD, event, num, 10)",
        "GNB_CONFIG"
    ]
    missing = [v for v in required if v not in text]
    if missing:
        raise RuntimeError("paper configuration check failed: " + ", ".join(missing))


def main():
    if not SRC.exists():
        raise SystemExit("missing dpdk/upstream/gNB_power_aware.c; run ./scripts/fetch_upstream.sh")
    original = SRC.read_text()
    pa = prepare_power_aware(original)
    validate(pa)
    bw = prepare_busy_wait(pa)
    OUT_PA.parent.mkdir(parents=True, exist_ok=True)
    OUT_BW.parent.mkdir(parents=True, exist_ok=True)
    OUT_PA.write_text(pa)
    OUT_BW.write_text(bw)
    shutil.copy2(ROOT / "dpdk" / "config" / "power-paper.conf", OUT_PA.parent / "power-paper.conf")


if __name__ == "__main__":
    main()
