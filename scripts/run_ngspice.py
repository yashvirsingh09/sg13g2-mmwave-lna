"""
================================================================================
SMACD 2027: Automated Ngspice Simulation Suite Runner
Simulates the 100% Extracted Physical Layout Netlist (gds/reports/lna_top_extracted.cir)
against official IHP SG13G2 PDK compact models.
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import sys
import subprocess

def main():
    print("================================================================================")
    print("        SMACD 2027: IHP SG13G2 Ngspice Simulation Suite Execution               ")
    print("================================================================================")

    steps = [
        ("4-Port S-Parameters & Noise Figure", "scripts/test_complete_lna_spice.py"),
        ("S-Parameter Plot Generation", "scripts/plot_ngspice_raw.py"),
        ("Multi-Corner PVT Analysis (TT, FF, SS)", "scripts/run_ngspice_corners.py"),
        ("Large-Signal Linearity (P1dB & IP3)", "scripts/run_ngspice_linearity.py"),
        ("Monte Carlo Statistical Yield Analysis", "scripts/run_ngspice_monte_carlo.py")
    ]

    for name, script in steps:
        if not os.path.isfile(script):
            print(f"[SKIP] Missing script: {script}")
            continue

        print(f"\n--> Running: {name} ({script})...")
        res = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"    [PASS] {name} completed successfully.")
            for line in res.stdout.strip().splitlines()[-4:]:
                print(f"    {line}")
        else:
            print(f"    [FAIL] {name} exited with code {res.returncode}")
            if res.stderr:
                print(f"    Error: {res.stderr[:300]}")

    print("\n================================================================================")
    print("  Ngspice simulation suite complete. Plots saved in results/                     ")
    print("================================================================================")

if __name__ == '__main__':
    main()
