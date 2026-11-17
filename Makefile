# ==============================================================================
# Makefile: 24-28 GHz mmWave SiGe-BiCMOS LNA
# SMACD 2027 Open-Source Design Challenge
# SPDX-License-Identifier: Apache-2.0
# ==============================================================================

PYTHON ?= python
KLAYOUT ?= klayout

.PHONY: all reproduce size mna sim layout drc lvs paper clean help

all: reproduce

## Run the full end-to-end verification pipeline
reproduce:
	$(PYTHON) reproduce.py

## Compile IEEE 4-page paper to PDF
paper:
	cd doc && pdflatex -interaction=nonstopmode smacd2027_paper.tex && pdflatex -interaction=nonstopmode smacd2027_paper.tex

## Run analytical RF sizing & transistor calculations
size:
	$(PYTHON) scripts/size_lna.py

## Run complete Ngspice-47 simulation suite
sim:
	$(PYTHON) scripts/run_ngspice.py

## Run first-principles MNA complex admittance solver
mna:
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
	@echo "  make reproduce  - Run full end-to-end reproduction pipeline"
	@echo "  make size       - Calculate transistor sizing and component values"
	@echo "  make mna        - Solve analytical MNA admittance matrix"
	@echo "  make sim        - Run complete Ngspice-47 simulation suite"
	@echo "  make layout     - Synthesize GDSII layout mask & plot floorplan"
	@echo "  make drc        - Run KLayout DRC check (0 violations)"
	@echo "  make lvs        - Run KLayout LVS check (100% matched)"
	@echo "  make paper      - Compile IEEE 4-page paper to PDF"
	@echo "  make clean      - Clean intermediate simulation and log artifacts"
