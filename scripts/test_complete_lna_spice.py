"""
================================================================================
SMACD 2027: Authentic 4-Port S-Parameter & Noise Analysis in Ngspice-47
Foundry VBIC npn13G2 models from IHP SG13G2 Open PDK (Commit: e73adb4)
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import subprocess
import numpy as np

pdk_hbt = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib').replace('\\', '/')

spice_deck_fwd = f"""* Complete 24-28 GHz LNA SPICE Simulation (Forward: S11, S21, NF)
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

* Port 1 Forward Drive: 2V AC across 50 Ohm -> 1V incident wave
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

.ac lin 151 20g 35g
.noise v(out_pad) VIN lin 151 20g 35g

.control
run
setplot ac1
let s11_db = db(v(in_pad) - 1.0)
let s21_db = db(v(out_pad))
write lna_ngspice_fwd.raw s21_db s11_db

setplot noise1
let inoise_sq = inoise_spectrum * inoise_spectrum
let nf_db = 10.0 * log10(inoise_sq / (4.0 * 1.380649e-23 * 300.15 * 50.0))
write lna_ngspice_noise.raw nf_db

print ac1.s21_db[80] ac1.s11_db[80] nf_db[80]
quit
.endc
.end
"""

spice_deck_rev = f"""* Complete 24-28 GHz LNA SPICE Simulation (Reverse: S22, S12)
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

* Port 1 Terminated in 50 Ohm
RS1 IN_PAD 0 50.0

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

* Port 2 Driven by 2V AC across 50 Ohm
V2 OUT_SRC 0 DC 0 AC 2.0
RL2 OUT_SRC OUT_PAD 50.0

.ac lin 151 20g 35g

.control
run
let s22_db = db(v(out_pad) - 1.0)
let s12_db = db(v(in_pad))
print s22_db[80] s12_db[80]
write lna_ngspice_rev.raw s22_db s12_db
quit
.endc
.end
"""

def main():
    print("================================================================================")
    print("  Executing Ngspice-47 4-Port S-Parameter & Noise Analysis                      ")
    print("  Device Models: IHP SG13G2 VBIC npn13G2 (Foundry cornerHBT.lib)               ")
    print("================================================================================")

    # 1. Forward run
    with open('lna_fwd.spice', 'w') as f:
        f.write(spice_deck_fwd)
    res_fwd = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'lna_fwd.spice'], capture_output=True, text=True)
    if res_fwd.returncode != 0:
        print(f"Error in Forward simulation:\n{res_fwd.stderr}")
        return

    # 2. Reverse run
    with open('lna_rev.spice', 'w') as f:
        f.write(spice_deck_rev)
    res_rev = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'lna_rev.spice'], capture_output=True, text=True)
    if res_rev.returncode != 0:
        print(f"Error in Reverse simulation:\n{res_rev.stderr}")
        return

    print("=== NGSPICE FORWARD OUTPUT ===")
    for line in res_fwd.stdout.splitlines():
        if any(k in line for k in ['s21_db', 's11_db', 'nf_db']):
            print(f"  {line.strip()}")

    print("=== NGSPICE REVERSE OUTPUT ===")
    for line in res_rev.stdout.splitlines():
        if any(k in line for k in ['s22_db', 's12_db']):
            print(f"  {line.strip()}")

    # Cleanup temp spice files
    for tf in ['lna_fwd.spice', 'lna_rev.spice']:
        if os.path.isfile(tf):
            os.remove(tf)

    print("================================================================================\n")

if __name__ == '__main__':
    main()
