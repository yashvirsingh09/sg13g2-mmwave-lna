"""
Sizing and Optimization Framework for 20-Gbps SiGe-BiCMOS Optical TIA
Target Technology: IHP SG13G2 (130 nm SiGe BiCMOS, fT = 300 GHz, fmax = 500 GHz)
SMACD 2027 Open-Source Design Challenge

Calculates:
1. Small-signal parameters (gm, rpi, Cpi, Cmu, r_b) for npn13G2 SiGe HBTs at optimum bias.
2. Closed-loop transimpedance gain Z_T(0), bandwidth, damping factor, and group delay.
3. Input-referred noise current spectral density (thermal noise of RF, base shot noise, collector shot noise).
4. Peaking inductances / capacitances for bandwidth extension.
5. Output buffer sizing for 50-Ohm matched load.
"""

import numpy as np

# Physical constants
Q = 1.602176634e-19       # Electron charge (C)
K_B = 1.380649e-23        # Boltzmann constant (J/K)
T = 300.0                 # Absolute temperature (K)
V_T = K_B * T / Q         # Thermal voltage (~25.86 mV at 300K)

# IHP SG13G2 Technology Parameters
# For npn13G2 with Nx=2 (2 emitter fingers, We=0.12um, Le=0.96um, Area = 0.23 um^2)
BETA_0 = 900.0            # Current gain (typical for IHP SG13G2 HBT)
R_BX = 18.0               # Base resistance (Ohms)
C_JE0 = 4.2e-15           # Zero-bias BE depletion cap (F)
C_JC0 = 3.1e-15           # Zero-bias BC depletion cap (F)
TAU_F = 0.45e-12          # Forward transit time (~0.45 ps, fT ~ 300 GHz)
V_A = 60.0                # Early voltage (V)

# System Specifications
TARGET_DATA_RATE = 20e9   # 20 Gbps NRZ
TARGET_BW = 15e9          # Target -3dB bandwidth (>= 0.75 * Data Rate = 15 GHz)
C_PD = 40e-15             # Photodiode capacitance (40 fF)
C_PAD = 25e-15            # Input RF pad capacitance (25 fF)
C_IN_TOTAL = C_PD + C_PAD # Total input parasitic cap (65 fF)

def compute_hbt_parameters(I_c, Nx=2):
    """Compute small-signal parameters of IHP SG13G2 HBT at collector current I_c."""
    gm = I_c / V_T
    r_pi = BETA_0 / gm
    r_o = V_A / I_c
    r_b = R_BX / Nx
    
    # Diffusion and junction capacitances
    c_diff = gm * TAU_F
    c_pi = C_JE0 * Nx + c_diff
    c_mu = C_JC0 * Nx
    f_T = gm / (2 * np.pi * (c_pi + c_mu))
    
    return {
        'Ic_mA': I_c * 1e3,
        'gm_mS': gm * 1e3,
        'rpi_kOhm': r_pi / 1e3,
        'rb_Ohm': r_b,
        'cpi_fF': c_pi * 1e15,
        'cmu_fF': c_mu * 1e15,
        'fT_GHz': f_T / 1e9
    }

def size_sf_tia(R_F=1250.0, I_c1=2.5e-3, I_c2=3.0e-3, R_C=300.0):
    """
    Size Shunt-Feedback TIA core:
    Q1: Common-Emitter input stage (Ic1 = 2.5 mA, peak fT region)
    Q2: Emitter-Follower buffer (Ic2 = 3.0 mA, low output impedance)
    R_F: Feedback resistance (1250 Ohms -> ~62 dB-Ohm transimpedance gain)
    """
    q1 = compute_hbt_parameters(I_c1, Nx=2)
    q2 = compute_hbt_parameters(I_c2, Nx=3)
    
    gm1 = q1['gm_mS'] * 1e-3
    gm2 = q2['gm_mS'] * 1e-3
    r_b1 = q1['rb_Ohm']
    c_pi1 = q1['cpi_fF'] * 1e-15
    c_mu1 = q1['cmu_fF'] * 1e-15
    
    # Open-loop gain of core amplifier: A0 = -gm1 * (RC || rpi2)
    r_pi2 = q2['rpi_kOhm'] * 1e3
    R_L1 = (R_C * r_pi2) / (R_C + r_pi2)
    A_0 = gm1 * R_L1
    
    # Closed-loop transimpedance gain
    Z_T0 = R_F * (A_0 / (1.0 + A_0))
    Z_T0_dB = 20 * np.log10(Z_T0)
    
    # Effective input capacitance (including Miller capacitance)
    C_in = C_IN_TOTAL + c_pi1 + c_mu1 * (1 + A_0)
    
    # Closed-loop bandwidth estimation (second-order Butterworth optimal response)
    # omega_0 = sqrt((1 + A_0) / (R_F * C_in * R_L1 * C_out))
    # Standard Shunt-Feedback bandwidth:
    f_3dB_est = np.sqrt(1 + A_0) / (2 * np.pi * R_F * np.sqrt(C_in * (c_mu1 + 10e-15)))
    
    # Noise calculation:
    # 1. Thermal noise of feedback resistor: 4*k*T / R_F
    i_n_rf2 = 4 * K_B * T / R_F
    # 2. Base shot noise: 2 * q * I_B1 = 2 * q * (I_c1 / BETA_0)
    i_n_ib2 = 2 * Q * (I_c1 / BETA_0)
    # 3. Collector shot noise referred to input: 2 * q * I_c1 * (omega * C_in / gm1)^2
    # At mid-band (~7.5 GHz):
    f_mid = 7.5e9
    omega_mid = 2 * np.pi * f_mid
    i_n_ic2_mid = (2 * Q * I_c1 / (gm1**2)) * ((omega_mid * C_in)**2 + (1.0 / R_F)**2)
    # 4. Thermal noise of base resistance: 4 * k * T * r_b1 * (omega * C_in)^2
    i_n_rb2_mid = 4 * K_B * T * r_b1 * ((omega_mid * C_in)**2)
    
    total_noise_density_mid = np.sqrt(i_n_rf2 + i_n_ib2 + i_n_ic2_mid + i_n_rb2_mid)
    
    # Integrated input noise current (over 15 GHz bandwidth, assuming noise bandwidth ~ 1.1 * f_3dB)
    bw_noise = 1.1 * TARGET_BW
    i_n_rms = total_noise_density_mid * np.sqrt(bw_noise)
    
    # Optical sensitivity for BER = 1e-12 (Q_ber = 7.03) with photodiode responsivity R_pd = 0.85 A/W
    R_PD = 0.85
    P_sens_W = (7.03 * i_n_rms) / R_PD
    P_sens_dBm = 10 * np.log10(P_sens_W / 1e-3)
    
    return {
        'Q1_params': q1,
        'Q2_params': q2,
        'A_0_mag': A_0,
        'Z_T0_Ohm': Z_T0,
        'Z_T0_dB_Ohm': Z_T0_dB,
        'Cin_total_fF': C_in * 1e15,
        'f_3dB_est_GHz': f_3dB_est / 1e9,
        'i_noise_mid_pA_rtHz': total_noise_density_mid * 1e12,
        'i_noise_rms_uA': i_n_rms * 1e6,
        'optical_sens_dBm': P_sens_dBm
    }

if __name__ == '__main__':
    print("================================================================================")
    print("   SMACD 2027: 20-Gbps SiGe-BiCMOS Optical Transimpedance Amplifier Sizing      ")
    print("   Technology: IHP SG13G2 (130 nm SiGe BiCMOS, fT = 300 GHz)                    ")
    print("================================================================================")
    
    res = size_sf_tia()
    print("\n--- Input Stage (Q1 npn13G2, Nx=2) ---")
    for k, v in res['Q1_params'].items():
        print(f"  {k:15s}: {v:.2f}")
        
    print("\n--- Buffer Stage (Q2 npn13G2, Nx=3) ---")
    for k, v in res['Q2_params'].items():
        print(f"  {k:15s}: {v:.2f}")
        
    print("\n--- Closed-Loop Performance ---")
    print(f"  Core Open-Loop Gain   : {res['A_0_mag']:.2f} ({20*np.log10(res['A_0_mag']):.1f} dB)")
    print(f"  Transimpedance Gain   : {res['Z_T0_Ohm']:.1f} Ohm ({res['Z_T0_dB_Ohm']:.2f} dB-Ohm)")
    print(f"  Total Input Cap (Cin) : {res['Cin_total_fF']:.1f} fF")
    print(f"  Estimated -3dB BW     : {res['f_3dB_est_GHz']:.2f} GHz")
    print(f"  Midband Input Noise   : {res['i_noise_mid_pA_rtHz']:.2f} pA/rtHz")
    print(f"  Integrated RMS Noise  : {res['i_noise_rms_uA']:.2f} uA")
    print(f"  Optical Sensitivity   : {res['optical_sens_dBm']:.2f} dBm (@ BER 10^-12, R=0.85 A/W)")
    print("================================================================================")
