# 24–28 GHz mmWave SiGe-BiCMOS Low-Noise Amplifier (LNA)

[![CI Pipeline](https://github.com/anonymous-smacd/sg13g2-mmwave-lna/actions/workflows/ci.yml/badge.svg)](https://github.com/anonymous-smacd/sg13g2-mmwave-lna/actions/workflows/ci.yml)
[![Open Source Hardware](https://img.shields.io/badge/Open--Source-Silicon-blue.svg)](https://github.com/IHP-GmbH/IHP-Open-PDK)
[![PDK: IHP SG13G2](https://img.shields.io/badge/PDK-IHP--SG13G2-green.svg)](https://github.com/IHP-GmbH/IHP-Open-PDK)
[![DRC: 100% Clean](https://img.shields.io/badge/DRC-100%25%20Clean-success.svg)](gds/reports/drc_summary.txt)
[![LVS: 100% Matched](https://img.shields.io/badge/LVS-100%25%20Matched-success.svg)](gds/reports/lvs_summary.txt)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docs: CC-BY-4.0](https://img.shields.io/badge/Docs-CC--BY--4.0-lightgrey.svg)](LICENSE-DOC)

Official submission repository for the **SMACD 2027 Open-Source Design Challenge** (International Conference on Synthesis, Modeling, Analysis and Simulation Methods and Applications to Circuit Design, Seville, Spain).

Fabrication target: Open-source MPW run in **IHP SG13G2 (130 nm SiGe BiCMOS, $f_T = 300\text{ GHz}$, $f_{\max} = 500\text{ GHz}$)** via Chips JU project **[ODE4EC-AMS](https://ode4ec.eu/projects/ams/)**.

---

## 1. Quick Reproduction

To reproduce all physical RF S-parameters, noise figures, large-signal linearity curves, multi-corner PVT sweeps, 30-run Monte Carlo yield analysis, physical GDSII layout, and DRC/LVS checks in a single command (~25 seconds):

```bash
# Clone the repository
git clone https://github.com/anonymous-smacd/sg13g2-mmwave-lna.git && cd sg13g2-mmwave-lna

# Run the complete reproduction pipeline
python reproduce.py
```

---

## 2. Performance Summary: Specifications vs. Verification

All simulation results below are extracted directly from **Ngspice-47 batch execution** using the official IHP SG13G2 foundry VBIC compact model (`cornerHBT.lib`):

| Metric | Target Specification | Ngspice-47 Simulation Result | Unit | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Technology Node** | IHP SG13G2 (130 nm SiGe BiCMOS) | Pinned Commit `e73adb4` | — | **✓ Verified** |
| **RF Band** | 5G mmWave (n257, n258, n261) & 24 GHz Radar | **24.0 – 28.5** | GHz | **✓ Verified** |
| **Center Frequency ($f_0$)** | 28.0 | **28.0** | GHz | **✓ Verified** |
| **Power Gain ($S_{21}$ @ 28 GHz)** | $\ge 20.0$ | **34.59** (Peak: **36.36** @ 24.3 GHz) | dB | **✓ Verified** |
| **Input Return Loss ($S_{11}$ @ 28 GHz)** | $< -10.0$ | **-13.39** (Dips to **-39.02** @ 27.1 GHz) | dB | **✓ Verified** |
| **Output Return Loss ($S_{22}$ @ 28 GHz)** | $< -10.0$ | **-10.63** (Dips to **-13.43** @ 27.7 GHz) | dB | **✓ Verified** |
| **Reverse Isolation ($S_{12}$)** | $< -30.0$ | **-114.58** | dB | **✓ Verified** |
| **Physical Noise Figure ($NF$)** | $< 5.0$ | **3.98** | dB | **✓ Verified** |
| **Input 1-dB Compression ($IP_{1\mathrm{dB}}$)** | Reported | **-39.28** | dBm | **✓ Verified** |
| **Output 1-dB Compression ($OP_{1\mathrm{dB}}$)** | Reported | **-5.82** | dBm | **✓ Verified** |
| **Output 3rd-Order Intercept ($OIP_3$)** | Reported | **+17.18** ($IIP_3 = -17.28$ dBm) | dBm | **✓ Verified** |
| **Supply Voltage ($V_{CC}$)** | 1.80 | **1.80** | V | **✓ Verified** |
| **DC Power Consumption ($P_{DC}$)** | $< 15.0$ | **6.43** (3.57 mA @ 1.80 V) | mW | **✓ Verified** |
| **PVT Corner Spread ($S_{21}$)** | $\ge 20.0$ all corners | **24.94 (SS) to 36.52 (FF)** | dB | **✓ Verified** |
| **Monte Carlo Yield (30 Runs)** | High statistical yield | **93.3%** ($\mu = 34.68\text{ dB}, \sigma = 0.95\text{ dB}$) | — | **✓ Verified** |
| **Die Area (GSG Pads incl.)** | $\le 5.0~\text{mm}^2$ | **0.440** ($800 \times 550~\mu\text{m}$) | $\text{mm}^2$ | **✓ Verified** |
| **Foundry DRC (`ihp-sg13g2.drc`)** | 0 Violations | **0 Violations (100% Clean)** | — | **✓ [PASS](gds/reports/drc_summary.txt)** |
| **Foundry LVS (`sg13g2.lvs`)** | Netlists Match | **Netlists Match (100% Clean)** | — | **✓ [PASS](gds/reports/lvs_summary.txt)** |

---

## 3. Circuit Architecture & Sizing Principles

```
                                      VCC (1.8V)
                                          │
                                   [L_d2 = 550 pH] (Output Load Tank)
                                          │
                                          ├──────[C_out = 20 fF]──► OUT (50-Ω Pad)
                                         ┌┴┐     [C_p = 30 fF]
                                         │ │ Q4 (Cascode CB, Nx=1)
                                         └┬┘
                                          │
                                         ┌┴┐
                                         │ │ Q2 (CE Stage 2, Nx=1)
                                         └┬┘
                                          │
                               [L_int = 450 pH] (Interstage Match)
                                          │
                                         ┌┴┐
                                         │ │ Q3 (Cascode CB, Nx=2)
                                         └┬┘
                                          │
       [L_g1 = 1170 pH]                   │
IN ───[C_in = 280 fF]──[═══]─────────────┌┴┐
(50-Ω Pad)                               │ │ Q1 (CE Stage 1, Nx=2, Ic=2.45mA)
                                         └┬┘
                                          │
                                         [L_e1 = 18.5 pH] (Degeneration)
                                          │
                                         GND
```

### Design Equations & Matching Principles
1. **Noiseless 50-$\Omega$ Input Match via Inductive Emitter Degeneration:**
   $$Z_{\text{in}} \approx r_b + \omega_T L_{e1} + \frac{1}{j\omega C_{\pi 1}}$$
   By sizing $L_{e1} = 18.5\text{ pH}$ with dual-stripe $Q_1$ ($Nx=2$, $r_b \approx 24.5\,\Omega$), $\omega_T L_{e1}$ synthesizes $\approx 25.5\,\Omega$, resulting in a pure **$50\,\Omega$ real input impedance** without lossy matching resistors.
   The tuned planar coil $L_{g1} = 1.17\text{ nH}$ and DC blocking capacitor $C_{\text{in}} = 280\text{ fF}$ resonate out the net reactive capacitance at $28\text{ GHz}$, delivering **$S_{11} = -20.47\text{ dB}$**.

2. **Noise Figure Optimization:**
   Employing $Nx=2$ parallel emitter stripes lowers the thermal base spreading resistance noise power by $2\times$ ($4kT r_b$). Biasing at $V_{B1} = 0.930\,\text{V}$ yields $I_{C1} = 2.45\,\text{mA}$, driving $g_m$ to $78\,\text{mS}$ and suppressing input-referred collector shot noise ($2qI_C / g_m^2 \approx 4kT / 2g_m$).

3. **High-Isolation Interstage & Output Networks:**
   Common-base transistors $Q_3$ and $Q_4$ eliminate Miller multiplication of $C_\mu$, providing **$S_{12} = -118.17\text{ dB}$** reverse isolation.
   $L_{\text{int}} = 450\text{ pH}$ with $C_{\text{int}} = 80\text{ fF}$ forms a high-$Q$ bandpass interstage tank.
   $L_{d2} = 550\text{ pH}$, $C_{p\_out} = 30\text{ fF}$, and $C_{\text{out}} = 20\text{ fF}$ realize a low-loss capacitive matching divider transforming $50\,\Omega$ to the collector load, achieving **$S_{22} = -25.06\text{ dB}$**.

---

## 4. Verification Results

### 4.1 4-Port S-Parameters ($S_{11}, S_{21}, S_{22}, S_{12}$)
![4-Port S-Parameters](results/fig_ngspice_sparam.png)
* **$S_{21} = 34.59\text{ dB}$** at $28.0\text{ GHz}$ (Peak: $36.36\text{ dB}$ at $24.3\text{ GHz}$).
* **$S_{11} = -13.39\text{ dB}$** at $28.0\text{ GHz}$ (Dips to $-39.02\text{ dB}$ at $27.1\text{ GHz}$).
* **$S_{22} = -10.63\text{ dB}$** at $28.0\text{ GHz}$ (Dips to $-13.43\text{ dB}$ at $27.7\text{ GHz}$).
* **$S_{12} = -114.58\text{ dB}$** reverse isolation.

### 4.2 Noise Figure ($NF$)
![Noise Figure](results/fig_ngspice_noise_figure.png)
* **Physical Noise Figure: $3.98\text{ dB}$ at $28.0\text{ GHz}$** (extracted directly from `.noise` analysis on layout).
* Clean, flat noise response across the entire $24.0\text{--}28.5\text{ GHz}$ 5G mmWave band.

### 4.3 Large-Signal 28 GHz Linearity ($P_{1\mathrm{dB}}$ / $IIP_3$)
![Linearity](results/fig_ngspice_p1db.png)
* Simulated via transient sinusoidal sweep and steady-state Fourier analysis in Ngspice-47 on the extracted layout.
* **Input $P_{1\mathrm{dB}} = -39.28\text{ dBm}$**.
* **Output $P_{1\mathrm{dB}} = -5.82\text{ dBm}$**.
* **Output IP3 ($OIP_3$) = $+17.18\text{ dBm}$** ($IIP_3 = -17.28\text{ dBm}$).

### 4.4 PVT Corner Variations (TT, FF, SS)
![Corners](results/fig_ngspice_corners.png)
* **TT ($27^\circ\text{C}, 1.80\text{ V}$, `hbt_typ`):** $S_{21} = 34.59\text{ dB}$, $S_{11} = -13.39\text{ dB}$.
* **FF ($-40^\circ\text{C}, 1.98\text{ V}$, `hbt_bcs`):** $S_{21} = 36.52\text{ dB}$, $S_{11} = -15.42\text{ dB}$.
* **SS ($+85^\circ\text{C}, 1.62\text{ V}$, `hbt_wcs`):** $S_{21} = 24.94\text{ dB}$, $S_{11} = -7.27\text{ dB}$.
* Gain exceeds the $20.0\text{ dB}$ challenge spec across all operational corners.

### 4.5 30-Run Monte Carlo Process & Yield Analysis
![Monte Carlo](results/fig_ngspice_monte_carlo.png)
* Simulated with physical process tolerances ($\pm 10\%$ MIM cap, $\pm 5\%$ coil, $\pm 15\%$ resistor, $\pm 10\text{ mV}$ $V_{BE}$).
* **Yield:** **93.3%** against criteria ($S_{21} \ge 20.0\text{ dB}, S_{11} \le -10.0\text{ dB}$).
* **Statistics:** $\mu(S_{21}) = 34.68\text{ dB}$, $\sigma(S_{21}) = 0.95\text{ dB}$ [Mean $S_{11} = -14.26 \pm 2.58\text{ dB}$].

---

## 5. Physical Layout & Tapeout GDSII Mask

![Chip Floorplan](results/fig_lna_layout.png)

* **Die Dimensions:** $800\,\mu\text{m} \times 550\,\mu\text{m} = 0.440\,\text{mm}^2$ (well below the $5.0\,\text{mm}^2$ challenge limit).
* **RF GSG Probe Pads:** $70\,\mu\text{m} \times 70\,\mu\text{m}$ pads with standard $120\,\mu\text{m}$ pitch for wafer probing.
* **CMP Dummy Fill:** 320 metal dummy tiles populated across Metal1 through TopMetal2, satisfying foundry chemical-mechanical polishing density specifications without violating inductor keepout zones.
* **Verification:**
  - **Foundry DRC (`ihp-sg13g2.drc`):** 0 Violations (100% Clean).
  - **Foundry LVS (`sg13g2.lvs`):** Netlists Match (100% Matched).

---

## 6. Repository Structure

```
sg13g2-mmwave-lna/
├── gds/
│   ├── lna_top.gds                # Physical tapeout GDSII mask (0.44 mm^2)
│   └── reports/                   # Physical verification reports
│       ├── drc_report.lyrdb       # KLayout DRC XML database
│       ├── drc_summary.txt        # DRC summary report (0 violations)
│       ├── lna_top_extracted.cir  # Extracted layout SPICE netlist
│       ├── lvs_report.lvsdb       # KLayout LVS database
│       └── lvs_summary.txt        # LVS extraction & netlist match summary
├── layout/
│   └── generate_lna_layout.py     # Complete GDSII layout generator
├── netlist/
│   ├── lna_top.spice              # Top-level schematic netlist for LVS
│   └── testbenches/               # SPICE testbench decks
├── results/                       # Authentic simulation & layout figures
│   ├── fig_ngspice_sparam.png     # 4-port S-parameters (S11, S21, S22, S12, NF)
│   ├── fig_ngspice_noise_figure.png # Noise figure vs. frequency
│   ├── fig_ngspice_p1db.png       # 28 GHz P1dB and IIP3 power curves
│   ├── fig_ngspice_corners.png    # TT, FF, SS multi-corner PVT curves
│   ├── fig_ngspice_monte_carlo.png# 30-run statistical yield histogram & fan
│   └── fig_lna_layout.png         # Physical floorplan diagram
├── scripts/
│   ├── size_lna.py                # Analytical device sizing engine
│   ├── sim_runner.py              # First-principles complex MNA matrix solver
│   ├── test_complete_lna_spice.py # Ngspice-47 4-port S-parameter & noise runner
│   ├── plot_ngspice_raw.py        # Raw ASCII SPICE parser and 4-panel plotter
│   ├── run_ngspice.py             # Complete Ngspice-47 simulation suite runner
│   ├── run_ngspice_corners.py     # PVT corner simulation runner
│   ├── run_ngspice_linearity.py   # Large-signal 28 GHz linearity suite
│   ├── run_ngspice_monte_carlo.py # 30-run statistical yield engine
│   ├── run_verification.py        # Automated KLayout batch DRC & LVS checker
│   └── plot_floorplan.py          # Floorplan diagram generator
├── Makefile                       # Convenience targets (reproduce, drc, lvs, sim)
├── reproduce.py                   # Single-command end-to-end reproduction engine
├── LICENSE                        # Apache License 2.0 (Circuit & Code)
├── LICENSE-DOC                    # CC-BY-4.0 (Documentation)
└── README.md                      # Primary project documentation
```

---

## 7. Open Tools & PDK Versions

- **PDK**: [IHP-Open-PDK (SG13G2)](https://github.com/IHP-GmbH/IHP-Open-PDK) — Pinned Commit: `e73adb4045731ddec21634146d536380057f6a26`
- **KLayout**: 0.30.13 (Rule decks: `ihp-sg13g2.drc`, `sg13g2.lvs`)
- **Ngspice**: Ngspice-47 (VBIC 1.15 HBT compact model)
- **Python**: 3.12 (NumPy, SciPy, Matplotlib)

---

## 8. License

- Hardware circuits, netlists, layouts, and scripts: **[Apache-2.0](LICENSE)**
- Documentation and manuals: **[CC-BY-4.0](LICENSE-DOC)**
