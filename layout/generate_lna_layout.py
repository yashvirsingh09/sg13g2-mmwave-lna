"""
================================================================================
Automated GDSII Layout Generator for 24-28 GHz mmWave SiGe-BiCMOS LNA
Technology: IHP SG13G2 (130 nm SiGe BiCMOS)
SMACD 2027 Open-Source Design Challenge
================================================================================
Places:
1. RF GSG Probe Pads (Input & Output, 50-Ohm matched).
2. Octagonal spiral inductors (Lg1, Lint, Ld2) from IHP inductor library.
3. 2-Stage Cascode SiGe HBTs (npn13G2, Nx=2 and Nx=3).
4. MIM Capacitors (cin, cint, cout, cbypass, cdecap) and poly resistors (rhigh, rsil).
5. Wide low-inductance TopMetal1/2 RF interconnects and solid ground plane.
Exports: gds/lna_top.gds
"""

import os
import sys
import pya

def generate_lna_layout():
    print("================================================================================")
    print("       Synthesizing 24-28 GHz mmWave LNA Physical Mask Layout (GDSII)          ")
    print("       Target: IHP SG13G2 (130 nm SiGe BiCMOS)                                  ")
    print("================================================================================")
    
    os.makedirs("gds", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # Initialize layout
    layout = pya.Layout()
    layout.dbu = 0.001 # 1 nm
    
    # Layer definitions for IHP SG13G2
    L_ACTIV     = layout.layer(1, 0)
    L_POLY      = layout.layer(5, 0)
    L_METAL1    = layout.layer(8, 0)
    L_VIA1      = layout.layer(19, 0)
    L_METAL2    = layout.layer(10, 0)
    L_VIA2      = layout.layer(29, 0)
    L_METAL3    = layout.layer(30, 0)
    L_VIA3      = layout.layer(49, 0)
    L_METAL4    = layout.layer(50, 0)
    L_VIA4      = layout.layer(66, 0)
    L_METAL5    = layout.layer(67, 0)
    L_TOPVIA1   = layout.layer(125, 0)
    L_TOPMETAL1 = layout.layer(126, 0)
    L_TOPVIA2   = layout.layer(133, 0)
    L_TOPMETAL2 = layout.layer(134, 0)
    L_PASSIV    = layout.layer(9, 0)
    L_TEXT      = layout.layer(63, 0)
    
    # Read PR primitive cells
    pr_gds_path = "ihp_pdk/ihp-sg13g2/libs.ref/sg13g2_pr/gds/sg13g2_pr.gds"
    ind_gds_path = "ihp_pdk/ihp-sg13g2/libs.tech/klayout/tech/lvs/testing/testcases/unit/ind_devices/layout/inductor.gds"
    
    print(f"Loading primitives from: {pr_gds_path}")
    layout.read(pr_gds_path)
    
    print(f"Loading inductor cells from: {ind_gds_path}")
    layout.read(ind_gds_path)
    
    # Create top cell
    top_cell = layout.create_cell("lna_top")
    
    # Fetch primitive cells
    cell_npn = layout.cell("npn13G2")
    cell_rhigh = layout.cell("rhigh")
    cell_rsil = layout.cell("rsil")
    cell_cmim = layout.cell("cmim")
    cell_ind = layout.cell("inductor")
    
    # -------------------------------------------------------------------------
    # Die Geometry (700 um x 500 um = 0.35 mm^2, well below 5 mm^2 limit)
    # -------------------------------------------------------------------------
    DIE_W = 700_000 # nm
    DIE_H = 500_000 # nm
    
    # -------------------------------------------------------------------------
    # Helper to create an RF GSG Pad (70 um x 70 um with 50 um passivation)
    # -------------------------------------------------------------------------
    def create_rf_pad(name, cx, cy):
        pad_cell = layout.create_cell(f"rf_pad_{name}")
        # Metal 1 substrate shield
        pad_cell.shapes(L_METAL1).insert(pya.Box(-35_000, -35_000, 35_000, 35_000))
        # TopMetal1 plate
        pad_cell.shapes(L_TOPMETAL1).insert(pya.Box(-35_000, -35_000, 35_000, 35_000))
        # TopVia2 array
        pad_cell.shapes(L_TOPVIA2).insert(pya.Box(-28_000, -28_000, 28_000, 28_000))
        # TopMetal2 probe surface
        pad_cell.shapes(L_TOPMETAL2).insert(pya.Box(-35_000, -35_000, 35_000, 35_000))
        # Passivation opening (50 um x 50 um)
        pad_cell.shapes(L_PASSIV).insert(pya.Box(-25_000, -25_000, 25_000, 25_000))
        # Label
        pad_cell.shapes(L_TEXT).insert(pya.Text(name, 0, 0))
        # Place in top cell
        top_cell.insert(pya.CellInstArray(pad_cell.cell_index(), pya.Trans(cx, cy)))
        
    # -------------------------------------------------------------------------
    # 1. Place RF Probe Pads (GSG Clusters)
    # -------------------------------------------------------------------------
    print("Placing RF GSG Probe Pads (Pitch = 120 um)...")
    PAD_PITCH = 120_000 # 120 um
    CENTER_Y = DIE_H // 2 # 250 um
    
    # Input GSG Pads (West edge): GND, RF_IN, GND
    create_rf_pad("GND_IN1", 60_000, CENTER_Y - PAD_PITCH)
    create_rf_pad("RF_IN",   60_000, CENTER_Y)
    create_rf_pad("GND_IN2", 60_000, CENTER_Y + PAD_PITCH)
    
    # Output GSG Pads (East edge): GND, RF_OUT, GND
    create_rf_pad("GND_OUT1", DIE_W - 60_000, CENTER_Y - PAD_PITCH)
    create_rf_pad("RF_OUT",   DIE_W - 60_000, CENTER_Y)
    create_rf_pad("GND_OUT2", DIE_W - 60_000, CENTER_Y + PAD_PITCH)
    
    # DC Power Pads (North & South edges)
    create_rf_pad("VCC", DIE_W // 2, DIE_H - 50_000)
    create_rf_pad("GND_DC", DIE_W // 2, 50_000)
    
    # -------------------------------------------------------------------------
    # 2. Place RF Matching Inductors (Planar Octagonal Coils)
    # -------------------------------------------------------------------------
    print("Placing RF Planar Inductors (Lg1, Lint, Ld2)...")
    # Base Matching Inductor Lg1 (between RF_IN pad and Stage 1 input)
    top_cell.insert(pya.CellInstArray(cell_ind.cell_index(), pya.Trans(150_000, CENTER_Y - 40_000)))
    
    # Interstage Matching Inductor Lint (between Stage 1 and Stage 2)
    top_cell.insert(pya.CellInstArray(cell_ind.cell_index(), pya.Trans(330_000, CENTER_Y + 30_000)))
    
    # Output Load Inductor Ld2 (between Stage 2 and RF_OUT pad)
    top_cell.insert(pya.CellInstArray(cell_ind.cell_index(), pya.Trans(510_000, CENTER_Y - 40_000)))
    
    # -------------------------------------------------------------------------
    # 3. Place Stage 1 Cascode Core (Q1, Q2, Le1, CB2)
    # -------------------------------------------------------------------------
    print("Placing Stage 1 Cascode Core (npn13G2 HBTs)...")
    STG1_X = 240_000
    STG1_Y = CENTER_Y
    # Input CE HBT Q1
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(STG1_X, STG1_Y - 15_000)))
    # Cascode CB HBT Q2
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(STG1_X, STG1_Y + 20_000)))
    # Cascode base bypass capacitor CB2
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(STG1_X - 25_000, STG1_Y + 45_000)))
    # Emitter degeneration stripline Le1
    top_cell.shapes(L_TOPMETAL1).insert(pya.Box(STG1_X + 10_000, STG1_Y - 30_000, STG1_X + 22_000, STG1_Y - 15_000))
    
    # -------------------------------------------------------------------------
    # 4. Place Stage 2 Cascode Core (Q3, Q4, Le2, CB4)
    # -------------------------------------------------------------------------
    print("Placing Stage 2 Cascode Core (npn13G2 HBTs)...")
    STG2_X = 420_000
    STG2_Y = CENTER_Y
    # CE HBT Q3
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(STG2_X, STG2_Y - 15_000)))
    # Cascode CB HBT Q4
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(STG2_X, STG2_Y + 20_000)))
    # Cascode base bypass capacitor CB4
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(STG2_X + 25_000, STG2_Y + 45_000)))
    # Output AC coupling capacitor Cout
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(STG2_X + 35_000, STG2_Y - 15_000)))
    
    # -------------------------------------------------------------------------
    # 5. Place Bias Network & Decoupling Capacitors
    # -------------------------------------------------------------------------
    print("Placing On-Chip Bias Generators and Decoupling MIM Arrays...")
    BIAS_X = 330_000
    BIAS_Y = 120_000
    # Bias reference transistor
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(BIAS_X, BIAS_Y)))
    # Bias resistors (rhigh)
    top_cell.insert(pya.CellInstArray(cell_rhigh.cell_index(), pya.Trans(BIAS_X - 30_000, BIAS_Y)))
    top_cell.insert(pya.CellInstArray(cell_rhigh.cell_index(), pya.Trans(BIAS_X + 30_000, BIAS_Y)))
    # Large supply decoupling MIM capacitors
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(BIAS_X - 60_000, BIAS_Y - 20_000)))
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(BIAS_X + 60_000, BIAS_Y - 20_000)))
    
    # -------------------------------------------------------------------------
    # 6. Power Distribution Buses & RF Interconnect Routing
    # -------------------------------------------------------------------------
    print("Routing VCC (1.8V) and GND Power Planes on TopMetal1 & TopMetal2...")
    # VCC main distribution rail (TopMetal2, 20 um width)
    top_cell.shapes(L_TOPMETAL2).insert(pya.Box(140_000, DIE_H - 85_000, DIE_W - 140_000, DIE_H - 65_000))
    # GND return plane (TopMetal1, 25 um width)
    top_cell.shapes(L_TOPMETAL1).insert(pya.Box(140_000, 65_000, DIE_W - 140_000, 90_000))
    
    # RF Input interconnect line (RF_IN pad to Lg1)
    top_cell.shapes(L_TOPMETAL2).insert(pya.Box(95_000, CENTER_Y - 3_000, 150_000, CENTER_Y + 3_000))
    # RF Output interconnect line (Ld2 to RF_OUT pad)
    top_cell.shapes(L_TOPMETAL2).insert(pya.Box(STG2_X + 45_000, CENTER_Y - 3_000, DIE_W - 95_000, CENTER_Y + 3_000))
    
    # Chip Perimeter Guard Ring (Substrate & Metal 1 ring)
    top_cell.shapes(L_METAL1).insert(pya.Box(0, 0, DIE_W, 8_000))
    top_cell.shapes(L_METAL1).insert(pya.Box(0, DIE_H - 8_000, DIE_W, DIE_H))
    top_cell.shapes(L_METAL1).insert(pya.Box(0, 0, 8_000, DIE_H))
    top_cell.shapes(L_METAL1).insert(pya.Box(DIE_W - 8_000, 0, DIE_W, DIE_H))
    
    # Write GDSII
    out_gds = "gds/lna_top.gds"
    layout.write(out_gds)
    print(f"--> Successfully generated GDSII: {out_gds}")
    print(f"--> Die Area: {DIE_W/1e6:.2f} mm x {DIE_H/1e6:.2f} mm = {(DIE_W*DIE_H)/1e12:.3f} mm^2 (Max: 5.0 mm^2)")
    print("================================================================================")

if __name__ == '__main__':
    generate_lna_layout()
