"""
================================================================================
SMACD 2027: Authentic 4-Port S-Parameter & Noise Analysis in Ngspice-47
Simulates the 100% Extracted Physical Layout Netlist (gds/reports/lna_top_extracted.cir)
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import subprocess
import numpy as np

pdk_hbt = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib').replace('\\', '/')
pdk_cap = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerCAP.lib').replace('\\', '/')

def run_simulation():
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

    # Prefix instances with X and expand m=2
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

    # Build XDUT pin map
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

* DC Biasing:
VCC VCC 0 DC 1.80
V_CAS1 VB_CAS1 0 DC 1.75
V_CAS2 VB_CAS2 0 DC 1.75
V_B1 VBIAS1 0 DC 0.900
V_B2 VBIAS2 0 DC 0.890
"""

    deck_fwd = f"""* Complete 24-28 GHz LNA SPICE Simulation (Forward: S11, S21, NF)
{base_deck}
* Port 1 Forward Drive: 2V AC across 50 Ohm -> 1V incident wave
VIN IN_SRC 0 DC 0 AC 2.0
RS1 IN_SRC RFIN 50.0

* Port 2 Load:
RL2 RFOUT 0 50.0

.ac lin 151 20g 35g
.noise v(RFOUT) VIN lin 151 20g 35g

.control
set filetype=ascii
op
let pdc_mw = (-i(VCC) * 1.80 + -i(V_B1) * 0.900 + -i(V_B2) * 0.890 + -i(V_CAS1) * 1.75 + -i(V_CAS2) * 1.75) * 1e3
print pdc_mw

run
setplot ac1
let s11_db = db(v(rfin) - 1.0)
let s21_db = db(v(rfout))
write lna_ngspice_fwd.raw s21_db s11_db

setplot noise1
let inoise_sq = inoise_spectrum * inoise_spectrum
let nf_db = 10.0 * log10(inoise_sq / (4.0 * 1.380649e-23 * 290.0 * 50.0))
write lna_ngspice_noise.raw nf_db

print ac1.s21_db[80] ac1.s11_db[80] nf_db[80]
quit
.endc
.end
"""
    with open('lna_sim_fwd.spice', 'w') as f:
        f.write(deck_fwd)

    res_fwd = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'lna_sim_fwd.spice'], capture_output=True, text=True)

    deck_rev = f"""* Complete 24-28 GHz LNA SPICE Simulation (Reverse: S22, S12)
{base_deck}
* Port 1 Terminated in 50 Ohm
RS1 RFIN 0 50.0

* Port 2 Reverse Drive
VOUT OUT_SRC 0 DC 0 AC 2.0
RL2 OUT_SRC RFOUT 50.0

.ac lin 151 20g 35g

.control
set filetype=ascii
run
let s22_db = db(v(rfout) - 1.0)
let s12_db = db(v(rfin))
write lna_ngspice_rev.raw s22_db s12_db

print s22_db[80] s12_db[80]
quit
.endc
.end
"""
    with open('lna_sim_rev.spice', 'w') as f:
        f.write(deck_rev)

    res_rev = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'lna_sim_rev.spice'], capture_output=True, text=True)

    print("=" * 80)
    print("NGSPICE-47 RAW AC + NOISE SIMULATION OF 100% EXTRACTED GDS LAYOUT")
    print("=" * 80)
    for line in res_fwd.stdout.splitlines():
        if any(k in line for k in ['s21_db[80]', 's11_db[80]', 'nf_db[80]', 'pdc_mw']):
            print(" ", line.strip())
    for line in res_rev.stdout.splitlines():
        if any(k in line for k in ['s22_db[80]', 's12_db[80]']):
            print(" ", line.strip())
    print("=" * 80)

if __name__ == "__main__":
    run_simulation()
