.PHONY: fetch dpdk check sweep

fetch:
	./scripts/fetch_upstream.sh

dpdk:
	python3 scripts/prepare_dpdk.py

check:
	python3 scripts/check_repo.py
	python3 -m py_compile scripts/check_repo.py scripts/prepare_dpdk.py traffic/experiment_sweep.py traffic/trex_gnb_profile.py measurement/tools/msr.py

sweep:
	python3 traffic/experiment_sweep.py --suite daily --dry-run
