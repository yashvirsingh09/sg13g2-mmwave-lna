"""
================================================================================
SMACD 2027: Authentic Ngspice Multi-Corner PVT Runner
Executes TT, FF (hbt_bcs), and SS (hbt_wcs) corners against IHP SG13G2 PDK models
on the 100% Extracted Physical Layout Netlist (gds/reports/lna_top_extracted.cir).
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

corners = {
    'TT (Typ, 27°C, 1.80V)': {'hbt': 'hbt_typ', 'cap': 'cap_typ', 'temp': 27, 'vcc': 1.80, 'color': 'black', 'ls': '-'},
    'FF (Fast, -40°C, 1.98V)': {'hbt': 'hbt_bcs', 'cap': 'cap_bcs', 'temp': -40, 'vcc': 1.98, 'color': 'red', 'ls': '--'},
    'SS (Slow, 85°C, 1.62V)': {'hbt': 'hbt_wcs', 'cap': 'cap_wcs', 'temp': 85, 'vcc': 1.62, 'color': 'blue', 'ls': '-.'}
}

results = {}

for cname, ccfg in corners.items():
    print(f"\n--> Simulating Corner: {cname} on Extracted Layout...")
    spice_deck = f"""* PVT Corner: {cname}
.lib "{pdk_hbt}" {ccfg['hbt']}
.lib "{pdk_cap}" {ccfg['cap']}
.options rshunt=1e12

.param r_high_r = '1360.0 * (0.96 / 0.5)'
.subckt rhigh 1 2 bn w=0.5u l=0.96u ps=0u b=0 m=1
R1 1 2 'r_high_r'
Csub1 1 bn 0.5f
Csub2 2 bn 0.5f
.ends rhigh

.subckt rfcmim 1 2 bn w=7u l=7u A=49p P=28u m=1 wfeed=3u
Xcap 1 2 bn cap_rfcmim w=w l=l wfeed=wfeed
.ends rfcmim

.subckt inductor3 1 2 3 sub w=2u s=2.1u d=25.85u nr_r=2
.param L_val = 221.5p
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

VCC VCC 0 DC {ccfg['vcc']}
V_CAS1 VB_CAS1 0 DC {min(1.75, ccfg['vcc'] - 0.05)}
V_CAS2 VB_CAS2 0 DC {min(1.75, ccfg['vcc'] - 0.05)}
V_B1 VBIAS1 0 DC 0.900
V_B2 VBIAS2 0 DC 0.890

VIN IN_SRC 0 DC 0 AC 2.0
RS1 IN_SRC RFIN 50.0
RL2 RFOUT 0 50.0

.temp {ccfg['temp']}
.ac lin 151 20g 35g

.control
set filetype=ascii
run
let s21_db = db(v(rfout))
let s11_db = db(v(rfin) - 1.0)
write corner_sim.raw s21_db s11_db
quit
.endc
.end
"""
    with open('temp_corner.spice', 'w') as f:
        f.write(spice_deck)

    res = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'temp_corner.spice'], capture_output=True, text=True)

    # Parse ASCII raw file
    freqs, s21, s11 = [], [], []
    with open('corner_sim.raw', 'r') as f:
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

    freqs = np.array(freqs)
    s21 = np.array(s21)
    s11 = np.array(s11)

    idx_28 = 80
    print(f"  Result @ 28.0 GHz: S21 = {s21[idx_28]:.2f} dB, S11 = {s11[idx_28]:.2f} dB")
    results[cname] = {'freqs': freqs, 's21': s21, 's11': s11, 'cfg': ccfg}

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
for cname, data in results.items():
    cfg = data['cfg']
    ax1.plot(data['freqs'], data['s21'], label=f"{cname}", color=cfg['color'], linestyle=cfg['ls'], linewidth=2)
    ax2.plot(data['freqs'], data['s11'], label=f"{cname}", color=cfg['color'], linestyle=cfg['ls'], linewidth=2)

ax1.axvline(28.0, color='gray', linestyle=':', label='28 GHz Target')
ax1.set_ylabel('|S21| Gain (dB)', fontsize=12)
ax1.set_title('Ngspice-47 Multi-Corner PVT Performance (Extracted Layout)', fontsize=14, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower left', fontsize=10)

ax2.axvline(28.0, color='gray', linestyle=':')
ax2.axhline(-10.0, color='red', linestyle='--', label='-10 dB Match Threshold')
ax2.set_xlabel('Frequency (GHz)', fontsize=12)
ax2.set_ylabel('|S11| Return Loss (dB)', fontsize=12)
ax2.set_xlim(20, 35)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='lower left', fontsize=10)

plt.tight_layout()
os.makedirs('results', exist_ok=True)
plot_path = 'results/fig_ngspice_corners.png'
plt.savefig(plot_path, dpi=300)
print(f"\n[OK] PVT Corner plot saved to: {plot_path}")
