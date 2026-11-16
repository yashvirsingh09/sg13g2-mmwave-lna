"""
Test Complete LNA in Ngspice-47 with Proper DC Biasing and Foundry HBT Models
"""
import subprocess
import os

pdk_hbt = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib').replace('\\', '/')

spice_deck = f"""* Complete 24-28 GHz LNA SPICE Simulation with Foundry VBIC npn13G2
.lib "{pdk_hbt}" hbt_typ

* --- Physical Subcircuit Models for Passives ---
.subckt rhigh 1 2 bn w=0.5u l=0.96u
.param r_val = '1800.0 * (l / w)'
R1 1 2 'r_val'
Csub1 1 bn 0.5f
Csub2 2 bn 0.5f
.ends rhigh

.subckt rfcmim 1 2 bn w=7u l=7u
.param c_val = '1.5e-15 * (w*1e6) * (l*1e6)'
C1 1 2 'c_val'
Csub 2 bn 2.0f
.ends rfcmim

.subckt inductor3 1 2 3 sub w=2u s=2.1u d=25.85u nr_r=2 L=400p Q=18.0
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

* --- Circuit Under Test: 2-Stage Cascode LNA ---
VCC VCC 0 DC 1.8
V_B1 VB_BASE1 0 DC 0.885
V_C1 VB_CAS1 0 DC 1.75
V_B2 VB_BASE2 0 DC 0.890
V_C2 VB_CAS2 0 DC 1.75

* Port 1 Drive: 50 Ohm source with 2V AC (1V incident wave)
VIN IN_SRC 0 DC 0 AC 2.0
RS1 IN_SRC IN_PAD 50.0

* Input Matching: Cin = 280 fF, Lg1 = 1.17 nH
XC_IN IN_PAD LA 0 rfcmim w=12.8u l=12.8u
XL_G1 LA LC1 LB 0 inductor3 L=1170p Q=18.0

* Bias Resistor 1: 3.6 kOhm
XR_BIAS1 LB VB_BASE1 0 rhigh w=0.5u l=0.96u

* Stage 1 Cascode: Q1 (CE), Q3 (CB)
* Emitter degeneration: Le1 = 18.5 pH
R_LE1 E1 0 0.1
L_LE1 E1 0 18.5p

XQ1 CAS1_MID LB E1 0 npn13G2 Nx=1
XQ3 OUT1 VB_CAS1 CAS1_MID 0 npn13G2 Nx=1
C_BYP1 VB_CAS1 0 300f

* Interstage Match: Lint = 450 pH to VCC, Cint = 80 fF
XL_INT OUT1 LC2 VCC 0 inductor3 L=450p Q=18.0
XC_INT OUT1 B2 0 rfcmim w=7.3u l=7.3u
XR_BIAS2 B2 VB_BASE2 0 rhigh w=0.5u l=0.96u

* Stage 2 Cascode: Q2 (CE), Q4 (CB)
XQ2 CAS2_MID B2 0 0 npn13G2 Nx=1
XQ4 OUT2 VB_CAS2 CAS2_MID 0 npn13G2 Nx=1
C_BYP2 VB_CAS2 0 300f

* Output Load Tank: Ld2 = 500 pH to VCC, Cp_out = 40 fF, Cout = 20 fF
XL_D2 OUT2 LC3 VCC 0 inductor3 L=500p Q=18.0
XC_POUT OUT2 0 0 rfcmim w=5.1u l=5.1u
XC_OUT OUT2 OUT_PAD 0 rfcmim w=3.6u l=3.6u

* Port 2 Termination: 50 Ohm Load
RL2 OUT_PAD 0 50.0

* Frequency Sweep from 20 GHz to 35 GHz
.ac lin 151 20g 35g

.control
run
* S-parameter extraction:
let s11_db = db(v(in_pad) - 1.0)
let s21_db = db(v(out_pad))

print s21_db[0] s21_db[80] s11_db[80]
write lna_ngspice_ac.raw s21_db s11_db frequency
quit
.endc
.end
"""

with open('lna_ngspice_test.spice', 'w') as f:
    f.write(spice_deck)

print("Executing Ngspice on full LNA with IHP VBIC npn13G2 models...")
res = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'lna_ngspice_test.spice'], capture_output=True, text=True)
print("=== NGSPICE OUTPUT ===")
print(res.stdout)
if res.stderr:
    print("=== NGSPICE STDERR ===")
    print(res.stderr)
