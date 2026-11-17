"""
================================================================================
SMACD 2027: Authentic Ngspice Monte Carlo Process & Yield Analysis
Performs 30-run statistical analysis with physical PDK component tolerances:
- MIM Capacitances: +/- 10% (3-sigma normal)
- Planar Inductances: +/- 5% (3-sigma normal)
- Poly Resistors: +/- 15% (3-sigma normal)
- Base Bias Voltage: +/- 10 mV (3-sigma normal)
Simulates the 100% Extracted Physical Layout Netlist (gds/reports/lna_top_extracted.cir)
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
pdk_cap = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerCAP.lib').replace('\\', '/')

ext_path = os.path.abspath('gds/reports/lna_top_extracted.cir')
if not os.path.exists(ext_path):
    raise FileNotFoundError(f"Extracted netlist not found at {ext_path}")

with open(ext_path) as f:
    extracted = f.read()

subckt_lines = []
for line in extracted.splitlines():
    if line.startswith('.SUBCKT') or (subckt_lines and line.startswith('+')):
        subckt_lines.append(line)
    elif subckt_lines:
        break

subckt_header = ' '.join(subckt_lines)
tokens = subckt_header.split()
subckt_name = tokens[1]
subckt_pins = [p for p in tokens[2:] if p != '+']

mod_lines = []
for line in extracted.splitlines():
    s = line.strip()
    if s.startswith(('Q$', 'R$', 'C$', 'L$')):
        t = s.split()
        name = t[0]
        rest = ' '.join(x for x in t[1:] if not x.startswith('m='))
        if s.startswith('Q$') and 'm=2' in s:
            mod_lines.append(f'X{name}_A {rest}')
            mod_lines.append(f'X{name}_B {rest}')
        else:
            mod_lines.append(f'X{name} {rest}')
    else:
        mod_lines.append(line)

dut_deck = '\n'.join(mod_lines)

inst_pins = []
for p in subckt_pins:
    if p == 'GND':
        inst_pins.append('0')
    elif p in ['RFIN', 'RFOUT', 'VBIAS1', 'VBIAS2', 'VB_CAS1', 'VB_CAS2']:
        inst_pins.append(p)
    elif p == 'LB|VCC':
        inst_pins.append('VCC')
    else:
        clean_name = 'n_' + p.lower().replace('|', '_').replace('$', '_')
        inst_pins.append(clean_name)

xdut_line = f"XDUT {' '.join(inst_pins)} {subckt_name}"

def run_mc_iteration(iter_idx, rng):
    d_c = rng.normal(1.0, 0.033)      # 10% 3-sigma -> 3.3% std
    d_l = rng.normal(1.0, 0.0167)     # 5% 3-sigma -> 1.67% std
    d_r = rng.normal(1.0, 0.05)       # 15% 3-sigma -> 5% std
    d_vb1 = rng.normal(0.0, 0.0033)   # 10 mV 3-sigma -> 3.3 mV std

    l_val_p = 221.5 * d_l
    r_high_val = 1360.0 * (0.96 / 0.5) * d_r
    vb1 = 0.900 + d_vb1

    deck = f"""* Monte Carlo Iteration {iter_idx}
.lib "{pdk_hbt}" hbt_typ
.lib "{pdk_cap}" cap_typ
.options rshunt=1e12

.param r_high_r = {r_high_val:.2f}
.subckt rhigh 1 2 bn w=0.5u l=0.96u ps=0u b=0 m=1
R1 1 2 'r_high_r'
Csub1 1 bn 0.5f
Csub2 2 bn 0.5f
.ends rhigh

.subckt rfcmim 1 2 bn w=7u l=7u A=49p P=28u m=1 wfeed=3u
.param c_scale = {d_c:.4f}
Xcap 1 2 bn cap_rfcmim w='w*sqrt(c_scale)' l='l*sqrt(c_scale)' wfeed=wfeed
.ends rfcmim

.subckt inductor3 1 2 3 sub w=2u s=2.1u d=25.85u nr_r=2
.param L_val = {l_val_p:.2f}p
.param r_ser = 1.386
.param l_half = 'L_val / 2'
Rser1 1 1a 'r_ser/2'
L1 1a 2 'l_half'
Rser2 2 2a 'r_ser/2'
L2 2a 3 'l_half'
Cox1 1 sub 4.0f
Cox2 3 sub 4.0f
Cp 1 3 2.0f
.ends inductor3

* Extracted DUT:
{dut_deck}

* Connect DUT:
{xdut_line}

VCC VCC 0 DC 1.80
V_CAS1 VB_CAS1 0 DC 1.75
V_CAS2 VB_CAS2 0 DC 1.75
V_B1 VBIAS1 0 DC {vb1:.4f}
V_B2 VBIAS2 0 DC 0.890

VIN IN_SRC 0 DC 0 AC 2.0
RS1 IN_SRC RFIN 50.0
RL2 RFOUT 0 50.0

.ac lin 151 20g 35g

.control
set filetype=ascii
run
let s21_db = db(v(rfout))
let s11_db = db(v(rfin) - 1.0)
write mc_temp.raw s21_db s11_db
quit
.endc
.end
"""
    with open('test_mc.spice', 'w') as f:
        f.write(deck)
    subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'test_mc.spice'], capture_output=True, text=True)

    freqs, s21, s11 = [], [], []
    with open('mc_temp.raw', 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith('Values:'):
            val_idx = i + 1
            break
    i = val_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit():
            freqs.append(float(parts[1].split(',')[0]) / 1e9)
            i += 1
            s21.append(float(lines[i].strip().split()[0].split(',')[0]))
            i += 1
            s11.append(float(lines[i].strip().split()[0].split(',')[0]))
            i += 1
        else:
            i += 1

    return np.array(freqs), np.array(s21), np.array(s11)

print("--> Executing 30-Run Monte Carlo Statistical Yield Analysis on Extracted Layout...")
rng = np.random.RandomState(42)
N_RUNS = 30
all_s21_28 = []
all_s11_28 = []
mc_curves = []

for idx in range(1, N_RUNS + 1):
    f_arr, s21_arr, s11_arr = run_mc_iteration(idx, rng)
    s21_val = s21_arr[80]
    s11_val = s11_arr[80]
    all_s21_28.append(s21_val)
    all_s11_28.append(s11_val)
    mc_curves.append((f_arr, s21_arr, s11_arr))
    if idx % 5 == 0 or idx == 1:
        print(f"  Run {idx:2d}/{N_RUNS}: S21(28G) = {s21_val:5.2f} dB, S11(28G) = {s11_val:6.2f} dB")

all_s21_28 = np.array(all_s21_28)
all_s11_28 = np.array(all_s11_28)

yield_count = np.sum((all_s21_28 >= 20.0) & (all_s11_28 < -10.0))
yield_pct = 100.0 * yield_count / N_RUNS

print("\n" + "=" * 60)
print(f"  Monte Carlo Statistical Yield Results ({N_RUNS} Runs @ 28 GHz):")
print(f"  S21 Mean +/- Std: {np.mean(all_s21_28):.2f} +/- {np.std(all_s21_28):.2f} dB")
print(f"  S11 Mean +/- Std: {np.mean(all_s11_28):.2f} +/- {np.std(all_s11_28):.2f} dB")
print(f"  Yield (S21 >= 20 dB, S11 < -10 dB): {yield_count}/{N_RUNS} ({yield_pct:.1f}%)")
print("=" * 60)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
for f_arr, s21_arr, s11_arr in mc_curves:
    ax1.plot(f_arr, s21_arr, color='green', alpha=0.35, linewidth=1)
    ax2.plot(f_arr, s11_arr, color='navy', alpha=0.35, linewidth=1)

ax1.axvline(28.0, color='gray', linestyle=':', label='28 GHz Target')
ax1.axhline(20.0, color='red', linestyle='--', label='20 dB Gain Spec')
ax1.set_ylabel('|S21| Gain (dB)', fontsize=12)
ax1.set_title(f'30-Run Monte Carlo Statistical Yield Analysis (Yield: {yield_pct:.0f}%)', fontsize=14, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower left', fontsize=10)

ax2.axvline(28.0, color='gray', linestyle=':')
ax2.axhline(-10.0, color='red', linestyle='--', label='-10 dB Return Loss Spec')
ax2.set_xlabel('Frequency (GHz)', fontsize=12)
ax2.set_ylabel('|S11| Return Loss (dB)', fontsize=12)
ax2.set_xlim(20, 35)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='lower left', fontsize=10)

plt.tight_layout()
os.makedirs('results', exist_ok=True)
plot_path = 'results/fig_ngspice_monte_carlo.png'
plt.savefig(plot_path, dpi=300)
print(f"\n[OK] Monte Carlo plot saved to: {plot_path}")
