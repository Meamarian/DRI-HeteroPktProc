.PHONY: fetch dpdk check commands

fetch:
	./scripts/fetch_upstream.sh

dpdk:
	python3 scripts/prepare_dpdk.py

check:
	python3 scripts/check_artifact.py
	python3 -m py_compile analysis/reconstruct_daily.py experiments/daily/make_runs.py scripts/check_artifact.py scripts/prepare_dpdk.py traffic/run_matrix.py traffic/trex_gnb_profile.py measurement/tools/msr.py

commands:
	python3 traffic/run_matrix.py experiments/flow/dl.csv
