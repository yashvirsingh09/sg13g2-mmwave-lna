"""
================================================================================
SMACD 2027: Authentic Ngspice Multi-Corner PVT Runner
Executes TT, FF (hbt_bcs), and SS (hbt_wcs) corners against IHP SG13G2 PDK models.
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

corners = {
    'TT (Typ, 27°C, 1.80V)': {'lib': 'hbt_typ', 'temp': 27, 'vcc': 1.80, 'color': 'black', 'ls': '-'},
    'FF (Fast, -40°C, 1.98V)': {'lib': 'hbt_bcs', 'temp': -40, 'vcc': 1.98, 'color': 'red', 'ls': '--'},
    'SS (Slow, 85°C, 1.62V)': {'lib': 'hbt_wcs', 'temp': 85, 'vcc': 1.62, 'color': 'blue', 'ls': '-.'}
}

results = {}

for cname, ccfg in corners.items():
    print(f"\n--> Simulating Corner: {cname} in Ngspice-47...")
    spice_deck = f"""* PVT Corner: {cname}
.lib "{pdk_hbt}" {ccfg['lib']}

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

VCC VCC 0 DC {ccfg['vcc']}
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

.temp {ccfg['temp']}
.ac lin 151 20g 35g

.control
run
let s21_db = db(v(out_pad))
let s11_db = db(v(in_pad) - 1.0)
write corner_sim.raw s21_db s11_db
quit
.endc
.end
"""
    with open('corner_temp.spice', 'w') as f:
        f.write(spice_deck)

    res = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'corner_temp.spice'], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error simulating corner {cname}:\n{res.stderr}")
        continue

    # Parse ASCII raw file
    freqs = []
    s21_list = []
    s11_list = []
    with open('corner_sim.raw', 'r') as f:
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

    freqs = np.array(freqs)
    s21_arr = np.array(s21_list)
    s11_arr = np.array(s11_list)
    results[cname] = {'freqs': freqs, 's21': s21_arr, 's11': s11_arr, 'cfg': ccfg}

    idx28 = np.argmin(np.abs(freqs - 28.0))
    print(f"  --> S21 @ 28.0 GHz: {s21_arr[idx28]:.2f} dB (Peak: {np.max(s21_arr):.2f} dB @ {freqs[np.argmax(s21_arr)]:.1f} GHz)")
    print(f"  --> S11 @ 28.0 GHz: {s11_arr[idx28]:.2f} dB")

# Generate Corner Comparison Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8))

for cname, data in results.items():
    cfg = data['cfg']
    f = data['freqs']
    s21 = data['s21']
    s11 = data['s11']
    idx28 = np.argmin(np.abs(f - 28.0))
    lbl_s21 = f"{cname}: {s21[idx28]:.1f} dB"
    lbl_s11 = f"{cname}: {s11[idx28]:.1f} dB"
    ax1.plot(f, s21, color=cfg['color'], linestyle=cfg['ls'], linewidth=2.0, label=lbl_s21)
    ax2.plot(f, s11, color=cfg['color'], linestyle=cfg['ls'], linewidth=2.0, label=lbl_s11)

ax1.axhline(20.0, color='gray', linestyle='--', linewidth=0.9, label='20 dB Spec Target')
ax1.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
ax1.axvspan(24.25, 29.5, alpha=0.15, color='green', label='5G mmWave Band')
ax1.set_xlabel('Frequency [GHz]', fontsize=11, fontweight='bold')
ax1.set_ylabel('Power Gain $S_{21}$ [dB]', fontsize=11, fontweight='bold')
ax1.set_title('Ngspice PVT Corners: Power Gain ($S_{21}$)', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(loc='lower left', framealpha=0.9, fontsize=8.5)
ax1.set_ylim([-5, 38])

ax2.axhline(-10.0, color='gray', linestyle='--', linewidth=0.9, label='-10 dB Match Threshold')
ax2.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
ax2.axvspan(24.25, 29.5, alpha=0.15, color='green')
ax2.set_xlabel('Frequency [GHz]', fontsize=11, fontweight='bold')
ax2.set_ylabel('Input Match $S_{11}$ [dB]', fontsize=11, fontweight='bold')
ax2.set_title('Ngspice PVT Corners: Input Match ($S_{11}$)', fontsize=12, fontweight='bold')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(loc='lower right', framealpha=0.9, fontsize=8.5)
ax2.set_ylim([-30, 0])

plt.tight_layout()
fig.savefig('results/fig_ngspice_corners.png', dpi=300)
plt.close()

# Cleanup
for f in ['corner_temp.spice', 'corner_sim.raw']:
    if os.path.isfile(f):
        os.remove(f)

print("\nSaved authentic Ngspice multi-corner PVT plot to: results/fig_ngspice_corners.png")
print("================================================================================\n")
