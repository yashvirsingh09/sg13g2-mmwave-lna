"""
================================================================================
SMACD 2027: Automated Ngspice Simulation Runner & Parser
Executes SPICE testbenches against IHP SG13G2 PDK compact models.
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import sys
import shutil
import subprocess

def find_ngspice():
    # 1. Check PATH
    which_ng = shutil.which("ngspice")
    if which_ng:
        return [which_ng]
    
    which_ng_con = shutil.which("ngspice_con")
    if which_ng_con:
        return [which_ng_con]

    # 2. Check common Windows installation paths
    common_paths = [
        r"C:\Spice64\bin\ngspice.exe",
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\Spice64\bin\ngspice.exe",
        r"C:\Program Files\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Spice64\bin\ngspice.exe")
    ]
    for p in common_paths:
        if os.path.isfile(p):
            return [p]

    # 3. Check WSL
    which_wsl = shutil.which("wsl")
    if which_wsl:
        try:
            res = subprocess.run(["wsl", "which", "ngspice"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return ["wsl", "ngspice"]
        except Exception:
            pass

    return None

def main():
    print("================================================================================")
    print("        SMACD 2027: IHP SG13G2 Ngspice Simulation Suite Execution               ")
    print("================================================================================")

    ng_cmd = find_ngspice()
    if not ng_cmd:
        print("\n[INFO] Ngspice executable was not detected in PATH, standard Windows folders, or WSL.")
        print("Once installed, re-run this script: python scripts/run_ngspice.py")
        sys.exit(0)

    print(f"Detected Ngspice: {' '.join(ng_cmd)}")

    testbenches = [
        "netlist/testbenches/tb_sparam.spice",
        "netlist/testbenches/tb_noise_figure.spice",
        "netlist/testbenches/tb_linearity.spice",
        "netlist/testbenches/tb_corners.spice"
    ]

    for tb in testbenches:
        if not os.path.isfile(tb):
            print(f"Skipping missing testbench: {tb}")
            continue

        tb_dir = os.path.dirname(os.path.abspath(tb))
        tb_file = os.path.basename(tb)

        print(f"\n--> Running testbench: {tb_file}...")
        cmd = ng_cmd + ["-b", tb_file]
        res = subprocess.run(cmd, cwd=tb_dir, capture_output=True, text=True)

        if res.returncode == 0:
            print(f"    [PASS] {tb_file} completed successfully.")
        else:
            print(f"    [FAIL] {tb_file} exited with code {res.returncode}")
            if res.stderr:
                print(f"    Error: {res.stderr[:300]}")

    print("\n================================================================================")
    print("  Ngspice simulation run complete. Raw dumps saved in netlist/testbenches/       ")
    print("================================================================================")

if __name__ == '__main__':
    main()
