"""
================================================================================
SMACD 2027: Authentic Ngspice Noise Figure Simulation Runner
Executes .noise analysis in Ngspice-47 against IHP SG13G2 HBT compact models.
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import sys
import shutil
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def find_ngspice():
    candidates = [
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\Spice64\bin\ngspice_con.exe",
        r"C:\Spice\bin\ngspice.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    which = shutil.which("ngspice") or shutil.which("ngspice_con")
    if which:
        return which
    return "ngspice"

pdk_hbt = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib').replace('\\', '/')

spice_deck = f"""* Ngspice Noise Figure Analysis with Foundry VBIC npn13G2
.lib "{pdk_hbt}" hbt_typ

.param r_high_r = '1800.0 * (0.96 / 0.5)'
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
V_B1 VB_BASE1 0 DC 0.930
V_C1 VB_CAS1 0 DC 1.75
V_B2 VB_BASE2 0 DC 0.890
V_C2 VB_CAS2 0 DC 1.75

VIN IN_SRC 0 DC 0 AC 2.0
RS1 IN_SRC IN_PAD 50.0

XC_IN IN_PAD LA 0 rfcmim w=13.66u l=13.66u
XL_G1 LA LC1 LB 0 inductor3 L=1170p Q=18.0
XR_BIAS1 LB VB_BASE1 0 rhigh

R_LE1 E1 0 0.05
L_LE1 E1 0 18.5p

XQ1 CAS1_MID LB E1 0 npn13G2 Nx=2
XQ3 OUT1 VB_CAS1 CAS1_MID 0 npn13G2 Nx=2
C_BYP1 VB_CAS1 0 300f

XL_INT OUT1 LC2 VCC 0 inductor3 L=450p Q=18.0
XC_INT OUT1 B2 0 rfcmim w=7.3u l=7.3u
XR_BIAS2 B2 VB_BASE2 0 rhigh

XQ2 CAS2_MID B2 0 0 npn13G2 Nx=1
XQ4 OUT2 VB_CAS2 CAS2_MID 0 npn13G2 Nx=1
C_BYP2 VB_CAS2 0 300f

XL_D2 OUT2 LC3 VCC 0 inductor3 L=550p Q=18.0
XC_POUT OUT2 0 0 rfcmim w=4.47u l=4.47u
XC_OUT OUT2 OUT_PAD 0 rfcmim w=3.65u l=3.65u

RL2 OUT_PAD 0 50.0

.noise v(out_pad) VIN lin 151 20g 35g

.control
run
setplot noise1
* inoise_spectrum is in V/sqrt(Hz)
* Input thermal noise reference for 50 Ohm: 4 * k * T * 50 = 8.2878e-19 V^2/Hz at 300.15K
let inoise_sq = inoise_spectrum * inoise_spectrum
let nf_db = 10.0 * log10(inoise_sq / (4.0 * 1.380649e-23 * 300.15 * 50.0))
print nf_db[0] nf_db[80]
write ngspice_noise.raw nf_db frequency
quit
.endc
.end
"""

def main():
    print("================================================================================")
    print("  Executing Ngspice-47 Physical Noise Figure (.noise) Simulation Suite           ")
    print("================================================================================")

    with open('noise_temp.spice', 'w') as f:
        f.write(spice_deck)

    ngspice_bin = find_ngspice()
    res = subprocess.run([ngspice_bin, '-b', 'noise_temp.spice'], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error during noise analysis:\n{res.stderr}")
        return

    # Parse ASCII raw file
    freqs = []
    nf_list = []
    with open('ngspice_noise.raw', 'r') as f:
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
                if i < len(lines):
                    nf_val = float(lines[i].strip().split()[0].split(',')[0])
                    freqs.append(cur_f)
                    nf_list.append(nf_val)
                i += 1
            else:
                i += 1

    freqs = np.array(freqs)
    nf_arr = np.array(nf_list)

    if len(freqs) == 0:
        print("Could not parse noise figure data.")
        return

    idx28 = np.argmin(np.abs(freqs - 28.0))
    min_nf = np.min(nf_arr)

    print(f"  [Ngspice-47 Noise Figure Analysis]:")
    print(f"    --> Noise Figure @ 28.0 GHz: {nf_arr[idx28]:.2f} dB")
    print(f"    --> Minimum Noise Figure   : {min_nf:.2f} dB @ {freqs[np.argmin(nf_arr)]:.1f} GHz")

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.plot(freqs, nf_arr, 'darkgreen', linewidth=2.4, label=f'Ngspice VBIC Noise Figure ({nf_arr[idx28]:.2f} dB @ 28 GHz)')
    ax.axhline(5.0, color='gray', linestyle='--', linewidth=0.9, label='5.0 dB Specification Ceiling')
    ax.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
    ax.axvspan(24.25, 29.5, alpha=0.15, color='green', label='5G mmWave Band (n257/n258/n261)')

    ax.set_xlabel('Frequency [GHz]', fontsize=11, fontweight='bold')
    ax.set_ylabel('Noise Figure [dB]', fontsize=11, fontweight='bold')
    ax.set_title('Ngspice-47 Physical Noise Figure across 20-35 GHz (IHP SG13G2)', fontsize=11, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9.0)
    ax.set_ylim([2.0, 8.0])

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    fig.savefig('results/fig_ngspice_noise_figure.png', dpi=300)
    plt.close()

    # Cleanup temp
    for f in ['noise_temp.spice', 'ngspice_noise.raw']:
        if os.path.isfile(f):
            os.remove(f)

    print("  Saved authentic Ngspice noise figure plot to: results/fig_ngspice_noise_figure.png")
    print("================================================================================\n")

if __name__ == '__main__':
    main()
