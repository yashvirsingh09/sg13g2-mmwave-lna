# ==============================================================================
# Makefile for SMACD 2027 Open-Source Design Challenge
# Design: 20-Gbps SiGe-BiCMOS Optical TIA Front-End (IHP SG13G2)
# SPDX-License-Identifier: Apache-2.0
# ==============================================================================

PYTHON ?= python
KLAYOUT ?= klayout

.PHONY: all reproduce size sim layout drc lvs clean help

all: reproduce

## Run the full end-to-end reproduction pipeline
reproduce:
	$(PYTHON) reproduce.py

## Run analytical sizing and parameter optimization
size:
	$(PYTHON) scripts/size_tia.py

## Run SPICE simulations and generate paper figures
sim:
	$(PYTHON) scripts/sim_runner.py

## Generate physical GDSII layout
layout:
	$(KLAYOUT) -b -r layout/generate_layout.py
	$(PYTHON) scripts/plot_floorplan.py

## Run DRC physical rule check
drc:
	$(PYTHON) -c "from scripts.run_verification import run_drc; run_drc()"

## Run LVS layout vs schematic check
lvs:
	$(PYTHON) -c "from scripts.run_verification import run_lvs; run_lvs()"

## Clean temporary simulation and test logs
clean:
	rm -rf *.raw *.log results/*.tmp

help:
	@echo "SMACD 2027 Open-Source Design Challenge Build Commands:"
	@echo "  make reproduce  - Execute full end-to-end verification and report"
	@echo "  make size       - Execute analytical transistor and noise sizing"
	@echo "  make sim        - Run simulations and generate publication plots"
	@echo "  make layout     - Generate physical GDSII layout"
	@echo "  make drc        - Run KLayout DRC check"
	@echo "  make lvs        - Run KLayout LVS check"
