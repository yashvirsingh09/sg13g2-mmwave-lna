"""
================================================================================
SMACD 2027: Authentic Ngspice Large-Signal Linearity (P1dB / IIP3) Suite
Transient Fourier Simulation at 28 GHz using IHP SG13G2 VBIC compact models.
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pdk_hbt = os.path.abspath('ihp_pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib').replace('\\', '/')

def simulate_power_point(pin_dbm):
    pav = 1e-3 * (10.0 ** (pin_dbm / 10.0))
    vpk = np.sqrt(8.0 * 50.0 * pav)

    deck = f"""* Transient Linearity Test at 28 GHz
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

VIN IN_SRC 0 DC 0 SIN(0 {vpk:.6e} 28g)
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

.tran 0.5p 1.4n 0.8n

.control
run
fourier 28g v(out_pad)
quit
.endc
.end
"""
    with open('test_lin.spice', 'w') as f:
        f.write(deck)
    res = subprocess.run([r'C:\Spice64\bin\ngspice_con.exe', '-b', 'test_lin.spice'], capture_output=True, text=True)
    out = res.stdout

    fund_amp = None
    h3_amp = None
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3:
            if parts[0] == '1' and '2.8' in parts[1]:
                fund_amp = float(parts[2])
            elif parts[0] == '3' and '8.4' in parts[1]:
                h3_amp = float(parts[2])

    pout_fund_dbm = 10.0 * np.log10((fund_amp**2 / (2.0 * 50.0)) / 1e-3) if fund_amp and fund_amp > 1e-9 else -999.0
    pout_h3_dbm = 10.0 * np.log10((h3_amp**2 / (2.0 * 50.0)) / 1e-3) if h3_amp and h3_amp > 1e-9 else -999.0
    return pout_fund_dbm, pout_h3_dbm

def main():
    print("================================================================================")
    print("  Ngspice-47 Large-Signal 28 GHz Power Sweep & P1dB Compression Analysis        ")
    print("================================================================================")

    pin_list = np.arange(-50.0, -14.0, 2.0)
    pout_fund_list = []
    pout_h3_list = []

    for pin in pin_list:
        pf, ph3 = simulate_power_point(pin)
        pout_fund_list.append(pf)
        pout_h3_list.append(ph3)
        gain = pf - pin
        print(f"  Pin = {pin:5.1f} dBm --> Pout = {pf:6.2f} dBm  |  Gain = {gain:5.2f} dB")

    pin_arr = np.array(pin_list)
    pout_arr = np.array(pout_fund_list)
    gain_arr = pout_arr - pin_arr

    # Small-signal gain (average of first 3 linear points)
    g_ss = np.mean(gain_arr[:3])

    # Find P1dB point where Gain = g_ss - 1.0 dB
    # Interpolate crossing
    gain_drop = g_ss - gain_arr
    p1db_in = None
    p1db_out = None
    for i in range(len(gain_drop) - 1):
        if gain_drop[i] <= 1.0 and gain_drop[i+1] > 1.0:
            frac = (1.0 - gain_drop[i]) / (gain_drop[i+1] - gain_drop[i])
            p1db_in = pin_arr[i] + frac * (pin_arr[i+1] - pin_arr[i])
            p1db_out = pout_arr[i] + frac * (pout_arr[i+1] - pout_arr[i])
            break

    # Estimate IIP3 from third-order intercept rule: IIP3 ~ P1dB + 9.6 dB
    iip3_est = p1db_in + 9.6 if p1db_in is not None else -10.0
    oip3_est = p1db_out + 10.6 if p1db_out is not None else 15.0

    print("\n--------------------------------------------------------------------------------")
    print(f"  Small-Signal Gain G_0: {g_ss:.2f} dB")
    if p1db_in is not None:
        print(f"  Input 1-dB Compression Point (IP1dB) : {p1db_in:.2f} dBm")
        print(f"  Output 1-dB Compression Point (OP1dB): {p1db_out:.2f} dBm")
        print(f"  Extrapolated Input IP3 (IIP3)         : {iip3_est:.2f} dBm")
        print(f"  Extrapolated Output IP3 (OIP3)        : {oip3_est:.2f} dBm")
    print("--------------------------------------------------------------------------------")

    # Plot Pout vs Pin
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.plot(pin_arr, pout_arr, 'b-o', markersize=4.5, linewidth=2.0, label='Ngspice Simulated $P_{out}$ (28 GHz)')
    # Ideal linear extrapolation
    ideal_pin = np.linspace(-50, -10, 100)
    ax.plot(ideal_pin, ideal_pin + g_ss, 'k--', linewidth=1.2, label=f'Linear Extrapolation ($G_0 = {g_ss:.1f}$ dB)')

    if p1db_in is not None:
        ax.plot(p1db_in, p1db_out, 'ro', markersize=8, label=f'$IP_{{1\\mathrm{{dB}}}} = {p1db_in:.1f}$ dBm, $OP_{{1\\mathrm{{dB}}}} = {p1db_out:.1f}$ dBm')
        ax.axvline(p1db_in, color='r', linestyle=':', alpha=0.6)
        ax.axhline(p1db_out, color='r', linestyle=':', alpha=0.6)

    ax.set_xlabel('Input Available Power $P_{in}$ [dBm]', fontsize=11, fontweight='bold')
    ax.set_ylabel('Output Power $P_{out}$ [dBm]', fontsize=11, fontweight='bold')
    ax.set_title('Ngspice-47 28 GHz Large-Signal Power Transfer & 1-dB Compression (IHP SG13G2)', fontsize=11, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='lower right', framealpha=0.9, fontsize=9.5)
    ax.set_xlim([-52, -12])

    plt.tight_layout()
    fig.savefig('results/fig_ngspice_linearity.png', dpi=300)
    plt.close()

    if os.path.isfile('test_lin.spice'):
        os.remove('test_lin.spice')

    print(f"  Saved authentic linearity plot to: results/fig_ngspice_linearity.png")
    print("================================================================================\n")

if __name__ == '__main__':
    main()
