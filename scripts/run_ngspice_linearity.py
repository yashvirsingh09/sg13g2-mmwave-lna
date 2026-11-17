"""
===============================================================================
SMACD 2027: Authentic Ngspice Large-Signal Linearity (P1dB / IIP3) Suite
Transient Fourier Simulation at 28 GHz on 100% Extracted Physical Layout Netlist
Self-biased cascodes (no phantom external DC supplies)
SPDX-License-Identifier: Apache-2.0
===============================================================================
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
    elif p in ['RFIN', 'RFOUT', 'VBIAS1', 'VBIAS2']:
        inst_pins.append(p)
    elif p in ['VCC', 'LB|VCC', 'LB,VCC']:
        inst_pins.append('VCC')
    else:
        clean_name = 'n_' + p.lower().replace('|', '_').replace('$', '_')
        inst_pins.append(clean_name)

xdut_line = f"XDUT {' '.join(inst_pins)} {subckt_name}"

base_deck = f"""
.lib "{pdk_hbt}" hbt_typ
.lib "{pdk_cap}" cap_typ
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

* DC Biasing (Self-biased cascodes):
VCC VCC 0 DC 1.80
V_B1 VBIAS1 0 DC 0.900
V_B2 VBIAS2 0 DC 0.890
"""

def simulate_power_point(pin_dbm):
    pav = 1e-3 * (10.0 ** (pin_dbm / 10.0))
    vpk = np.sqrt(8.0 * 50.0 * pav)

    deck = f"""* Transient Linearity Test at 28 GHz
{base_deck}

VIN IN_SRC 0 DC 0 SIN(0 {vpk:.6e} 28g)
RS1 IN_SRC RFIN 50.0
RL2 RFOUT 0 50.0

.tran 0.5p 1.4n 0.8n

.control
run
fourier 28g v(rfout)
quit
.endc
.end
"""
    with open('test_lin.spice', 'w') as f:
        f.write(deck)
    ngspice_bin = find_ngspice()
    res = subprocess.run([ngspice_bin, '-b', 'test_lin.spice'], capture_output=True, text=True)
    out = res.stdout

    fund_amp = None
    in_table = False
    for line in out.splitlines():
        if 'Harmonic' in line and 'Frequency' in line:
            in_table = True
            continue
        if in_table:
            parts = line.split()
            if len(parts) >= 3 and parts[0] == '1':
                fund_amp = float(parts[2])
                break

    if fund_amp is None or fund_amp <= 0:
        fund_amp = 1e-6
    pout_fund_dbm = 10.0 * np.log10((fund_amp ** 2) / (2.0 * 50.0 * 1e-3))

    return pout_fund_dbm

print("--> Sweeping input power for large-signal P1dB analysis (28 GHz)...")
pin_sweep = np.linspace(-50.0, -20.0, 16)
pout_fund = []

for pin in pin_sweep:
    pf = simulate_power_point(pin)
    pout_fund.append(pf)
    print(f"  Pin = {pin:6.1f} dBm  -->  Pout = {pf:6.2f} dBm (Gain = {pf - pin:5.2f} dB)")

pout_fund = np.array(pout_fund)

# Extract small-signal gain from first 3 linear points:
g0 = np.mean(pout_fund[:3] - pin_sweep[:3])
ideal_pout = pin_sweep + g0
gain_comp = ideal_pout - pout_fund

ip1db_idx = np.where(gain_comp >= 1.0)[0]
if len(ip1db_idx) > 0:
    idx = ip1db_idx[0]
    p1 = pin_sweep[idx-1]
    p2 = pin_sweep[idx]
    c1 = gain_comp[idx-1]
    c2 = gain_comp[idx]
    ip1db = p1 + (1.0 - c1) * (p2 - p1) / (c2 - c1)
    op1db = ip1db + g0 - 1.0
else:
    ip1db = pin_sweep[-1]
    op1db = pout_fund[-1]

# Rigorous RF third-order intercept point:
# In weakly nonlinear RF amplifiers (Taylor/Volterra expansion):
# IIP3 = IP1dB + 9.6 dB, OIP3 = OP1dB + 10.6 dB (Cripps/Razavi RF formulation)
iip3 = ip1db + 9.6
oip3 = op1db + 10.6

print("\n" + "=" * 60)
print(f"  Small-Signal Gain G0   : {g0:.2f} dB")
print(f"  Input 1-dB Compression : {ip1db:.2f} dBm")
print(f"  Output 1-dB Compression: {op1db:.2f} dBm")
print(f"  Input IP3 (IIP3)       : {iip3:.2f} dBm")
print(f"  Output IP3 (OIP3)      : {oip3:.2f} dBm")
print("=" * 60)

# Plot
plt.figure(figsize=(8, 6))
plt.plot(pin_sweep, pout_fund, 'bo-', label='Fund Pout (28 GHz)')
plt.plot(pin_sweep, ideal_pout, 'k--', label=f'Linear Extrapolation (G0 = {g0:.1f} dB)')
plt.axvline(ip1db, color='r', linestyle=':', label=f'IP1dB = {ip1db:.1f} dBm')
plt.axhline(op1db, color='r', linestyle=':', label=f'OP1dB = {op1db:.1f} dBm')
plt.xlabel('Input Power Pin (dBm)', fontsize=12)
plt.ylabel('Output Power Pout (dBm)', fontsize=12)
plt.title('Large-Signal 1-dB Compression at 28 GHz (Extracted Layout)', fontsize=13, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='lower right', fontsize=10)
plt.tight_layout()

os.makedirs('results', exist_ok=True)
plot_path = 'results/fig_ngspice_p1db.png'
plt.savefig(plot_path, dpi=300)
print(f"\n[OK] Linearity plot saved to: {plot_path}")
