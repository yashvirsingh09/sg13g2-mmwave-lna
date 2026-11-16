# ==============================================================================
# Makefile: 24-28 GHz mmWave SiGe-BiCMOS LNA
# SMACD 2027 Open-Source Design Challenge
# SPDX-License-Identifier: Apache-2.0
# ==============================================================================

PYTHON ?= python
KLAYOUT ?= klayout

.PHONY: all reproduce size sim layout drc lvs clean help

all: reproduce

## Run the full end-to-end verification pipeline
reproduce:
	$(PYTHON) reproduce.py

## Run analytical RF sizing & transistor calculations
size:
	$(PYTHON) scripts/size_lna.py

## Run S-parameter, noise figure, and linearity characterization
sim:
	$(PYTHON) scripts/sim_runner.py

## Generate physical GDSII layout in KLayout
layout:
	$(KLAYOUT) -b -r layout/generate_lna_layout.py
	$(PYTHON) scripts/plot_floorplan.py

## Run DRC physical check against official IHP deck
drc:
	$(PYTHON) -c "from scripts.run_verification import run_drc; run_drc()"

## Run LVS netlist check against official IHP deck
lvs:
	$(PYTHON) -c "from scripts.run_verification import run_lvs; run_lvs()"

clean:
	rm -rf *.raw *.log results/*.tmp

help:
	@echo "Available commands:"
	@echo "  make reproduce  - Run full verification pipeline"
	@echo "  make size       - Calculate transistor sizing and component values"
	@echo "  make sim        - Run S-parameter & Noise Figure simulations"
	@echo "  make layout     - Synthesize GDSII layout mask"
	@echo "  make drc        - Run KLayout DRC check"
	@echo "  make lvs        - Run KLayout LVS check"
