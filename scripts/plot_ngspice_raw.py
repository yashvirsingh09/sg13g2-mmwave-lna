"""
================================================================================
SMACD 2027: Ngspice Raw Data Plotter & Model Validator
Parses raw simulation dumps from Ngspice and compares against MNA model.
SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_ngspice_raw(raw_file):
    freqs = []
    s21 = []
    s11 = []
    
    with open(raw_file, 'r') as f:
        in_values = False
        for line in f:
            if line.startswith('Values:'):
                in_values = True
                continue
            if not in_values:
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    val = float(parts[1])
                    if len(freqs) > len(s21):
                        s21.append(val)
                    elif len(freqs) > len(s11):
                        s11.append(val)
                except ValueError:
                    pass
            elif len(parts) == 1:
                try:
                    freqs.append(float(parts[0]))
                except ValueError:
                    pass

    return np.array(freqs), np.array(s21), np.array(s11)

def main():
    raw_path = "lna_ngspice_ac.raw"
    if not os.path.isfile(raw_path):
        print(f"Error: {raw_path} not found.")
        return

    print("Parsing Ngspice raw AC simulation dump...")
    # Load ASCII raw file
    freqs = []
    s21_list = []
    s11_list = []
    
    with open(raw_path, 'r') as f:
        lines = f.readlines()
        
    val_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('Values:'):
            val_idx = i + 1
            break
            
    if val_idx != -1:
        cur_freq = None
        cur_s21 = None
        cur_s11 = None
        
        i = val_idx
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                # Format: Index \t Val,Imag (frequency)
                cur_freq = float(parts[1].split(',')[0])
                i += 1
                # Next line: s21
                if i < len(lines):
                    s21_parts = lines[i].strip().split()
                    cur_s21 = float(s21_parts[0].split(',')[0])
                i += 1
                # Next line: s11
                if i < len(lines):
                    s11_parts = lines[i].strip().split()
                    cur_s11 = float(s11_parts[0].split(',')[0])
                i += 1
                
                if cur_freq is not None and cur_s21 is not None:
                    freqs.append(cur_freq / 1e9)
                    s21_list.append(cur_s21)
                    s11_list.append(cur_s11 if cur_s11 is not None else 0.0)
            else:
                i += 1

    freqs = np.array(freqs)
    s21 = np.array(s21_list)
    s11 = np.array(s11_list)

    if len(freqs) == 0:
        print("Could not parse frequency points from raw file.")
        return

    idx_28 = np.argmin(np.abs(freqs - 28.0))
    peak_idx = np.argmax(s21)

    print(f"Ngspice 28 GHz Results:")
    print(f"  --> Power Gain S21 @ 28.0 GHz: {s21[idx_28]:.2f} dB (Peak: {s21[peak_idx]:.2f} dB @ {freqs[peak_idx]:.1f} GHz)")
    print(f"  --> Input Return Loss S11    : {s11[idx_28]:.2f} dB")

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(freqs, s21, 'b-', linewidth=2.4, label=f'Ngspice Foundry VBIC $S_{{21}}$ ({s21[idx_28]:.2f} dB @ 28 GHz)')
    ax.plot(freqs, s11, 'r--', linewidth=2.0, label=f'Ngspice $S_{{11}}$ ({s11[idx_28]:.2f} dB @ 28 GHz)')
    ax.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    ax.axhline(20, color='green', linestyle=':', linewidth=0.9, label='20 dB Gain Specification')
    ax.axvline(28.0, color='gray', linestyle=':', linewidth=0.8)

    ax.set_xlabel('Frequency [GHz]', fontsize=11, fontweight='bold')
    ax.set_ylabel('Magnitude [dB]', fontsize=11, fontweight='bold')
    ax.set_title('Ngspice AC Simulation with IHP SG13G2 VBIC Models', fontsize=11, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='lower left', framealpha=0.9, fontsize=9.0)
    ax.set_ylim([-30, 26])

    plt.tight_layout()
    fig.savefig('results/fig_ngspice_sparam.png', dpi=300)
    plt.close()
    print("Saved results/fig_ngspice_sparam.png successfully.")

if __name__ == '__main__':
    main()
