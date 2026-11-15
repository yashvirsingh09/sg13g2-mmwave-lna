# 20-Gbps SiGe-BiCMOS Optical TIA Front-End: Circuit Architecture & Theory

## 1. System Overview
The optical receiver analog front-end translates high-speed unipolar optical pulses into low-jitter differential voltage signals suitable for downstream clock-and-data recovery (CDR) or deserializer circuits.

```
       +-------------------------------------------------------+
       |                  Active DCOC Servo Loop               |
       |             [OTA + Integrator + Sink Transistor]      |
       +-------------------------+-----------------------------+
                                 |  (IDC_CANCEL)
                                 v
[PIN Photodiode] --> [Pad] ---> [SF-TIA Core] ---> [CML Output Buffer] ---> [50-Ohm Loads]
  (CPD = 40 fF)                   ^                      |
                                  |                      v
                              [Replica] --------> [Differential]
```

---

## 2. Circuit Blocks & Design Equations

### 2.1 Shunt-Feedback TIA Core (SF-TIA)
- **Input Common-Emitter Transistor ($Q_1$)**:
  - Device: `npn13G2` ($N_x=2$, $W_e=0.12\,\mu\text{m}$, $L_e=0.96\,\mu\text{m}$).
  - Bias: $I_{C1} = 2.5\,\text{mA}$ ($g_{m1} = 96.7\,\text{mS}$, $r_b = 9\,\Omega$).
  - Collector load: $R_{C1} = 300\,\Omega$ (`rhigh`).
- **Emitter-Follower Buffer ($Q_2$)**:
  - Device: `npn13G2` ($N_x=3$, $I_{C2} = 3.0\,\text{mA}$).
- **Feedback Network ($R_F, C_F$)**:
  - $R_F = 1.25\,\text{k}\Omega$ (`rhigh`).
  - $C_F = 20\,\text{fF}$ (`cap_cmim`).
  - Closed-loop gain:
    $$Z_T(0) = R_F \frac{A_0}{1 + A_0} \approx 1220\,\Omega \; (61.73\,\text{dB}\Omega)$$
  - Closed-loop input resistance:
    $$R_{\text{in}} = \frac{R_F}{1 + A_0} \approx 42.4\,\Omega$$

### 2.2 Active DC-Offset Cancellation (DCOC) Loop
The active DCOC circuit senses the differential output offset voltage between the main TIA and an identical dummy replica stage, integrates the error, and sinks an equivalent current from the input node.
- **Low-Transconductance Differential OTA**:
  - PMOS input pair: `sg13_lv_pmos` ($W=8\,\mu\text{m}$, $L=1\,\mu\text{m}$).
  - Transconductance: $g_{m,\text{OTA}} \approx 65\,\mu\text{S}$.
- **Loop Filter Integrator**:
  - On-chip MIM capacitor: $C_{\text{int}} = 8\,\text{pF}$ (`cap_cmim`).
  - Resistor: $R_{\text{int}} = 500\,\text{k}\Omega$ (`rhigh`).
- **Low-Frequency Cutoff**:
  $$f_{\text{low}} = \frac{g_{m,\text{OTA}} g_{m,\text{cancel}} R_F}{2\pi C_{\text{int}}} \approx 45\,\text{kHz}$$
  Phase margin of the servo loop exceeds $82^\circ$, ensuring absolute stability across all input optical power levels.

### 2.3 50-$\Omega$ Matched CML Output Driver
- Differential pair: `npn13G2` ($N_x=4$, $I_{\text{tail}} = 10\,\text{mA}$).
- Degeneration resistor: $R_{\text{deg}} = 10\,\Omega$ (`rsil`).
- Back-termination load: $R_L = 50\,\Omega$ (`rsil`).
- Output return loss: $S_{22} < -14\,\text{dB}$ from DC to $30\,\text{GHz}$.

---

## 3. Technology Parameters: IHP SG13G2 (130-nm SiGe BiCMOS)
- **HBT Cutoff Frequency**: $f_T = 300\,\text{GHz}$, $f_{\max} = 500\,\text{GHz}$.
- **HBT Breakdown Voltage**: $BV_{CEO} = 1.6\,\text{V}$, $BV_{CBO} = 5.0\,\text{V}$.
- **CMOS Supply**: 1.2 V core, 3.3 V IO.
- **Interconnect Stack**: 5 Thin Metal layers + 2 Thick Top Metal layers (TopMetal1: $2\,\mu\text{m}$, TopMetal2: $3\,\mu\text{m}$).
- **Passive Components**:
  - `cap_cmim`: $1.5\,\text{fF}/\mu\text{m}^2$.
  - `rhigh`: $1350\,\Omega/\square$.
  - `rsil`: $7\,\Omega/\square$.
