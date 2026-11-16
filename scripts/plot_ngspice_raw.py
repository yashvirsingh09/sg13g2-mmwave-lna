"""
================================================================================
SMACD 2027: Authentic Ngspice 4-Port S-Parameter & Noise Figure Plotter
Parses raw simulation dumps from Ngspice-47 and generates publication figures.
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_ascii_raw_1vec(raw_path):
    """Parses an ASCII raw file containing 1 simulation vector vs frequency."""
    freqs = []
    vec = []

    if not os.path.isfile(raw_path):
        return np.array([]), np.array([])

    with open(raw_path, 'r') as f:
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
                v_val = None
                if i < len(lines):
                    v_val = float(lines[i].strip().split()[0].split(',')[0])
                i += 1
                if v_val is not None:
                    freqs.append(cur_f)
                    vec.append(v_val)
            else:
                i += 1

    return np.array(freqs), np.array(vec)

def parse_ascii_raw_2vecs(raw_path):
    """Parses an ASCII raw file containing 2 simulation vectors vs frequency."""
    freqs = []
    vec1 = []
    vec2 = []

    if not os.path.isfile(raw_path):
        return np.array([]), np.array([]), np.array([])

    with open(raw_path, 'r') as f:
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
                v1_val = None
                v2_val = None
                if i < len(lines):
                    v1_val = float(lines[i].strip().split()[0].split(',')[0])
                i += 1
                if i < len(lines):
                    v2_val = float(lines[i].strip().split()[0].split(',')[0])
                i += 1
                if v1_val is not None and v2_val is not None:
                    freqs.append(cur_f)
                    vec1.append(v1_val)
                    vec2.append(v2_val)
            else:
                i += 1

    return np.array(freqs), np.array(vec1), np.array(vec2)

def main():
    fwd_raw = "lna_ngspice_fwd.raw"
    rev_raw = "lna_ngspice_rev.raw"
    noise_raw = "lna_ngspice_noise.raw"

    if not os.path.isfile(fwd_raw):
        print(f"Error: {fwd_raw} not found.")
        return

    freqs, s21, s11 = parse_ascii_raw_2vecs(fwd_raw)
    freqs_rev, s22, s12 = parse_ascii_raw_2vecs(rev_raw)
    freqs_nf, nf = parse_ascii_raw_1vec(noise_raw)

    if len(freqs) == 0:
        print("Error: Could not parse forward data.")
        return

    idx28 = np.argmin(np.abs(freqs - 28.0))
    s21_28 = s21[idx28]
    s11_28 = s11[idx28]
    nf_28 = nf[idx28] if len(nf) > idx28 else 0.0
    s22_28 = s22[idx28] if len(s22) > idx28 else 0.0
    s12_28 = s12[idx28] if len(s12) > idx28 else 0.0

    print("================================================================================")
    print("  Ngspice-47 Physical Simulation Metrics @ 28.0 GHz (IHP SG13G2 HBT Models):     ")
    print("================================================================================")
    print(f"  Power Gain (S21)        : {s21_28:6.2f} dB (Peak: {np.max(s21):.2f} dB @ {freqs[np.argmax(s21)]:.1f} GHz)")
    print(f"  Input Return Loss (S11) : {s11_28:6.2f} dB")
    print(f"  Output Return Loss (S22): {s22_28:6.2f} dB")
    print(f"  Reverse Isolation (S12) : {s12_28:6.2f} dB")
    print(f"  Noise Figure (NF)       : {nf_28:6.2f} dB")
    print("--------------------------------------------------------------------------------")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10.0, 7.5))

    # Panel 1: S21
    ax1.plot(freqs, s21, 'b-', linewidth=2.2, label=f'Ngspice S21 ({s21_28:.2f} dB @ 28 GHz)')
    ax1.axhline(20.0, color='gray', linestyle='--', linewidth=0.9, label='20 dB Spec Target')
    ax1.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
    ax1.axvspan(24.25, 29.5, alpha=0.15, color='green', label='5G mmWave Band (n257/n258)')
    ax1.set_xlabel('Frequency [GHz]', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Power Gain $S_{21}$ [dB]', fontsize=10, fontweight='bold')
    ax1.set_title('Power Gain ($S_{21}$) across 20-35 GHz', fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='lower left', fontsize=8.5)
    ax1.set_ylim([-5, 36])

    # Panel 2: S11 & S22
    ax2.plot(freqs, s11, 'r-', linewidth=2.0, label=f'$S_{{11}}$ ({s11_28:.2f} dB @ 28 GHz)')
    if len(s22) > 0:
        ax2.plot(freqs_rev, s22, 'm--', linewidth=2.0, label=f'$S_{{22}}$ ({s22_28:.2f} dB @ 28 GHz)')
    ax2.axhline(-10.0, color='gray', linestyle='--', linewidth=0.9, label='-10 dB Match Threshold')
    ax2.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
    ax2.axvspan(24.25, 29.5, alpha=0.15, color='green')
    ax2.set_xlabel('Frequency [GHz]', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Return Loss [dB]', fontsize=10, fontweight='bold')
    ax2.set_title('Matching Performance ($S_{11}$, $S_{22}$)', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.set_ylim([-35, 0])

    # Panel 3: Noise Figure
    if len(nf) > 0:
        ax3.plot(freqs_nf, nf, 'darkgreen', linewidth=2.2, label=f'Ngspice NF ({nf_28:.2f} dB @ 28 GHz)')
        ax3.axhline(5.0, color='gray', linestyle='--', linewidth=0.9, label='5.0 dB Target')
        ax3.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
        ax3.axvspan(24.25, 29.5, alpha=0.15, color='green')
        ax3.set_xlabel('Frequency [GHz]', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Noise Figure [dB]', fontsize=10, fontweight='bold')
        ax3.set_title('Physical Noise Figure across 20-35 GHz', fontsize=11, fontweight='bold')
        ax3.grid(True, linestyle=':', alpha=0.6)
        ax3.legend(loc='upper right', fontsize=8.5)
        ax3.set_ylim([2.0, 8.0])

    # Panel 4: Reverse Isolation
    if len(s12) > 0:
        ax4.plot(freqs_rev, s12, 'purple', linewidth=2.0, label=f'Reverse Isolation $S_{{12}}$ ({s12_28:.1f} dB)')
        ax4.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)
        ax4.axvspan(24.25, 29.5, alpha=0.15, color='green')
        ax4.set_xlabel('Frequency [GHz]', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Reverse Isolation $S_{12}$ [dB]', fontsize=10, fontweight='bold')
        ax4.set_title('Reverse Isolation ($S_{12}$)', fontsize=11, fontweight='bold')
        ax4.grid(True, linestyle=':', alpha=0.6)
        ax4.legend(loc='lower left', fontsize=8.5)
        ax4.set_ylim([-140, -80])

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    fig.savefig('results/fig_ngspice_sparam.png', dpi=300)
    plt.close()
    print("  Saved 4-port S-parameter figure to: results/fig_ngspice_sparam.png")
    print("================================================================================\n")

if __name__ == '__main__':
    main()
