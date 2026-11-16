"""
================================================================================
SMACD 2027: Authentic Ngspice Monte Carlo Process & Yield Analysis
Performs 30-run statistical analysis with physical PDK component tolerances:
- MIM Capacitances: +/- 10% (3-sigma normal)
- Planar Inductances: +/- 5% (3-sigma normal)
- Poly Resistors: +/- 15% (3-sigma normal)
- Base Bias Voltage: +/- 10 mV (3-sigma normal)
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import sys
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pdk_hbt = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib').replace('\\', '/')

def run_mc_iteration(iter_idx, rng):
    # Sample variations
    d_c = rng.normal(1.0, 0.033)      # 10% 3-sigma -> 3.3% std
    d_l = rng.normal(1.0, 0.0167)     # 5% 3-sigma -> 1.67% std
    d_r = rng.normal(1.0, 0.05)       # 15% 3-sigma -> 5% std
    d_vb1 = rng.normal(0.0, 0.0033)   # 10 mV 3-sigma -> 3.3 mV std

    cin_w = 13.66 * np.sqrt(d_c)
    cint_w = 7.30 * np.sqrt(d_c)
    cout_w = 3.65 * np.sqrt(d_c)
    cpout_w = 4.47 * np.sqrt(d_c)

    lg1_p = 1170.0 * d_l
    lint_p = 450.0 * d_l
    ld2_p = 550.0 * d_l

    rbias = 3456.0 * d_r
    vb1 = 0.930 + d_vb1

    deck = f"""* Monte Carlo Iteration {iter_idx}
.lib "{pdk_hbt}" hbt_typ

.param r_high_r = {rbias:.2f}
.subckt rhigh 1 2 bn
R1 1 2 'r_high_r'
Csub1 1 bn 0.5f
Csub2 2 bn 0.5f
.ends rhigh

.subckt rfcmim 1 2 bn w=7u l=7u
.param c_val = '1.5e-15 * (w*1e6) * (l*1e6)'
C1 1 2 'c_val'
Csub 2 bn 2.0f
.ends rfcmim

.subckt inductor3 1 2 3 sub L=400p Q=18.0
.param w0 = '2 * 3.14159265 * 28e9'
.param r_ser = 'w0 * L / Q'
.param l_half = 'L / 2'
Rser1 1 1a 'r_ser/2'
L1 1a 2 'l_half'
Rser2 2 2a 'r_ser/2'
L2 2a 3 'l_half'
Cox1 1 sub 4.0f
Cox2 3 sub 4.0f
Cp 1 3 2.0f
.ends inductor3

VCC VCC 0 DC 1.8
V_B1 VB_BASE1 0 DC {vb1:.4f}
V_C1 VB_CAS1 0 DC 1.75
V_B2 VB_BASE2 0 DC 0.890
V_C2 VB_CAS2 0 DC 1.75

VIN IN_SRC 0 DC 0 AC 2.0
RS1 IN_SRC IN_PAD 50.0

XC_IN IN_PAD LA 0 rfcmim w={cin_w:.2f}u l={cin_w:.2f}u
XL_G1 LA LC1 LB 0 inductor3 L={lg1_p:.1f}p Q=18.0
XR_BIAS1 LB VB_BASE1 0 rhigh

R_LE1 E1 0 0.05
L_LE1 E1 0 18.5p

XQ1 CAS1_MID LB E1 0 npn13G2 Nx=2
XQ3 OUT1 VB_CAS1 CAS1_MID 0 npn13G2 Nx=2
C_BYP1 VB_CAS1 0 300f

XL_INT OUT1 LC2 VCC 0 inductor3 L={lint_p:.1f}p Q=18.0
XC_INT OUT1 B2 0 rfcmim w={cint_w:.2f}u l={cint_w:.2f}u
XR_BIAS2 B2 VB_BASE2 0 rhigh

XQ2 CAS2_MID B2 0 0 npn13G2 Nx=1
XQ4 OUT2 VB_CAS2 CAS2_MID 0 npn13G2 Nx=1
C_BYP2 VB_CAS2 0 300f

XL_D2 OUT2 LC3 VCC 0 inductor3 L={ld2_p:.1f}p Q=18.0
XC_POUT OUT2 0 0 rfcmim w={cpout_w:.2f}u l={cpout_w:.2f}u
XC_OUT OUT2 OUT_PAD 0 rfcmim w={cout_w:.2f}u l={cout_w:.2f}u

RL2 OUT_PAD 0 50.0

.ac lin 151 20g 35g

.control
run
let s21_db = db(v(out_pad))
let s11_db = db(v(in_pad) - 1.0)
write mc_temp.raw s21_db s11_db
quit
.endc
.end
"""
    with open('mc_run.spice', 'w') as f:
        f.write(deck)

    res = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'mc_run.spice'], capture_output=True, text=True)
    if res.returncode != 0:
        return None, None, None

    freqs = []
    s21_list = []
    s11_list = []
    with open('mc_temp.raw', 'r') as f:
        lines = f.readlines()

    val_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('Values:'):
            val_idx = i + 1
            break

    if val_idx != -1:
        i = val_idx
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                cur_f = float(parts[1].split(',')[0]) / 1e9
                i += 1
                cur_s21 = float(lines[i].strip().split()[0].split(',')[0]) if i < len(lines) else 0.0
                i += 1
                cur_s11 = float(lines[i].strip().split()[0].split(',')[0]) if i < len(lines) else 0.0
                i += 1
                freqs.append(cur_f)
                s21_list.append(cur_s21)
                s11_list.append(cur_s11)
            else:
                i += 1

    return np.array(freqs), np.array(s21_list), np.array(s11_list)

def main():
    print("================================================================================")
    print("  Executing 30-Run Monte Carlo Statistical Yield Analysis in Ngspice-47        ")
    print("  Technology: IHP SG13G2 (Compact VBIC npn13G2, cornerHBT.lib)                 ")
    print("================================================================================")

    rng = np.random.RandomState(42)  # Fixed seed for perfect reproducibility
    N_RUNS = 30

    all_s21_28 = []
    all_s11_28 = []
    all_s21_curves = []
    common_freqs = None

    for i in range(N_RUNS):
        f, s21, s11 = run_mc_iteration(i, rng)
        if f is not None and len(f) > 0:
            if common_freqs is None:
                common_freqs = f
            idx28 = np.argmin(np.abs(f - 28.0))
            all_s21_28.append(s21[idx28])
            all_s11_28.append(s11[idx28])
            all_s21_curves.append(s21)
            if (i + 1) % 5 == 0 or i == 0:
                print(f"  Run {i+1:2d}/{N_RUNS}: S21 = {s21[idx28]:5.2f} dB, S11 = {s11[idx28]:6.2f} dB")

    all_s21_28 = np.array(all_s21_28)
    all_s11_28 = np.array(all_s11_28)

    mean_s21 = np.mean(all_s21_28)
    std_s21 = np.std(all_s21_28)
    min_s21 = np.min(all_s21_28)
    max_s21 = np.max(all_s21_28)

    mean_s11 = np.mean(all_s11_28)
    std_s11 = np.std(all_s11_28)

    # Yield defined as S21 >= 25.0 dB and S11 <= -10.0 dB
    passing = np.sum((all_s21_28 >= 25.0) & (all_s11_28 <= -10.0))
    yield_pct = 100.0 * passing / N_RUNS

    print("\n--------------------------------------------------------------------------------")
    print(f"  Monte Carlo Statistics @ 28.0 GHz (N = {N_RUNS} runs):")
    print(f"    --> Power Gain (S21)    : Mean = {mean_s21:.2f} dB, Std = {std_s21:.2f} dB [Min: {min_s21:.2f}, Max: {max_s21:.2f}]")
    print(f"    --> Input Match (S11)   : Mean = {mean_s11:.2f} dB, Std = {std_s11:.2f} dB")
    print(f"    --> Statistical Yield   : {yield_pct:.1f}% (Criteria: S21 >= 25 dB, S11 <= -10 dB)")
    print("--------------------------------------------------------------------------------")

    # Plot Monte Carlo Figures
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8))

    # Panel 1: S21 curve fan
    for c in all_s21_curves:
        ax1.plot(common_freqs, c, color='steelblue', alpha=0.35, linewidth=1.0)
    ax1.plot(common_freqs, np.mean(all_s21_curves, axis=0), 'navy', linewidth=2.4, label=f'Mean $S_{{21}}$ ({mean_s21:.1f} dB @ 28 GHz)')
    ax1.axhline(20.0, color='red', linestyle='--', linewidth=1.0, label='20 dB Spec Minimum')
    ax1.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
    ax1.axvspan(24.25, 29.5, alpha=0.15, color='green', label='5G mmWave Band')
    ax1.set_xlabel('Frequency [GHz]', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Power Gain $S_{21}$ [dB]', fontsize=11, fontweight='bold')
    ax1.set_title(f'Monte Carlo $S_{{21}}$ Distribution (N = {N_RUNS})', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='lower left', fontsize=9.0)
    ax1.set_ylim([10, 36])

    # Panel 2: Histogram of S21 at 28 GHz
    n, bins, patches = ax2.hist(all_s21_28, bins=8, color='coral', edgecolor='darkred', alpha=0.8)
    ax2.axvline(mean_s21, color='darkred', linestyle='-', linewidth=2.0, label=f'Mean = {mean_s21:.1f} dB')
    ax2.axvline(mean_s21 - 3*std_s21, color='black', linestyle=':', linewidth=1.2, label=f'$-3\\sigma = {mean_s21 - 3*std_s21:.1f}$ dB')
    ax2.axvline(20.0, color='red', linestyle='--', linewidth=1.2, label='Spec Limit (20 dB)')
    ax2.set_xlabel('Power Gain $S_{21}$ @ 28 GHz [dB]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency Count', fontsize=11, fontweight='bold')
    ax2.set_title(rf'Yield Distribution ($\mu={mean_s21:.1f}$ dB, $\sigma={std_s21:.2f}$ dB)', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', fontsize=9.0)

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    fig.savefig('results/fig_ngspice_monte_carlo.png', dpi=300)
    plt.close()

    # Cleanup temp
    for f in ['mc_run.spice', 'mc_temp.raw']:
        if os.path.isfile(f):
            os.remove(f)

    print("  Saved Monte Carlo statistical plot to: results/fig_ngspice_monte_carlo.png")
    print("================================================================================\n")

if __name__ == '__main__':
    main()
