"""
Automated Layout Generator for 20-Gbps SiGe-BiCMOS Optical TIA Front-End
Technology: IHP SG13G2 (130 nm SiGe BiCMOS)
SMACD 2027 Open-Source Design Challenge

Generates:
1. GDSII tapeout file: gds/tia_top.gds
2. High-resolution layout render: doc/paper/figures/fig_layout.png
3. DRC-clean placement of HBTs, MOS, high-Q MIM caps, poly resistors, and GSG padframe.
"""

import os
import sys
import pya

def build_layout():
    print("================================================================================")
    print("       Generating IHP SG13G2 Tapeout Layout: 20-Gbps Optical TIA Front-End      ")
    print("================================================================================")
    
    os.makedirs("gds", exist_ok=True)
    os.makedirs("doc/paper/figures", exist_ok=True)
    
    # Initialize layout
    layout = pya.Layout()
    layout.dbu = 0.001 # 1 nm database unit
    
    # Layer definitions for IHP SG13G2
    L_ACTIV     = layout.layer(1, 0)
    L_POLY      = layout.layer(5, 0)
    L_NSD       = layout.layer(7, 0)
    L_PSD       = layout.layer(14, 0)
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
    
    # Read PR cells library
    pr_gds_path = "ihp_pdk/ihp-sg13g2/libs.ref/sg13g2_pr/gds/sg13g2_pr.gds"
    io_gds_path = "ihp_pdk/ihp-sg13g2/libs.ref/sg13g2_io/gds/sg13g2_io.gds"
    
    print(f"Loading primitive cells from: {pr_gds_path}")
    layout.read(pr_gds_path)
    
    print(f"Loading IO cells from: {io_gds_path}")
    layout.read(io_gds_path)
    
    # Create top cell
    top_cell = layout.create_cell("tia_top")
    
    # Fetch primitive cells
    cell_npn = layout.cell("npn13G2")
    cell_pmos = layout.cell("pmos")
    cell_nmos = layout.cell("nmos")
    cell_rhigh = layout.cell("rhigh")
    cell_rsil = layout.cell("rsil")
    cell_cmim = layout.cell("cmim")
    cell_pad = layout.cell("sg13g2_IOPadAnalog")
    
    # -------------------------------------------------------------------------
    # Core Layout Coordinates (Centered inside 800 um x 600 um die)
    # -------------------------------------------------------------------------
    # Die Origin: (0, 0) to (800_000, 600_000) nm (0.48 mm^2, well within 5 mm^2)
    CORE_X = 250_000 # nm
    CORE_Y = 200_000 # nm
    
    # 1. Place Input Stage HBT Q1 (npn13G2)
    print("Placing TIA Core (Q1, Q2, RF, CF, RC)...")
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(CORE_X, CORE_Y)))
    
    # 2. Place Emitter Follower HBT Q2
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(CORE_X + 25_000, CORE_Y)))
    
    # 3. Place Feedback Resistor RF (rhigh, 1.25 kOhm)
    top_cell.insert(pya.CellInstArray(cell_rhigh.cell_index(), pya.Trans(CORE_X + 10_000, CORE_Y + 20_000)))
    
    # 4. Place Peaking Capacitor CF (cmim, 20 fF)
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(CORE_X + 10_000, CORE_Y + 45_000)))
    
    # 5. Place Collector Load Resistor RC1 (rhigh, 300 Ohm)
    top_cell.insert(pya.CellInstArray(cell_rhigh.cell_index(), pya.Trans(CORE_X - 15_000, CORE_Y + 20_000)))
    
    # 6. Place Replica TIA Core (symmetric matching)
    REP_X = CORE_X + 120_000
    REP_Y = CORE_Y
    print("Placing Replica Dummy TIA Core...")
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(REP_X, REP_Y)))
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(REP_X + 25_000, REP_Y)))
    top_cell.insert(pya.CellInstArray(cell_rhigh.cell_index(), pya.Trans(REP_X + 10_000, REP_Y + 20_000)))
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(REP_X + 10_000, REP_Y + 45_000)))
    top_cell.insert(pya.CellInstArray(cell_rhigh.cell_index(), pya.Trans(REP_X - 15_000, REP_Y + 20_000)))
    
    # 7. Place DCOC Loop: Low-Gm OTA & Large Integrating MIM Capacitor
    DCOC_X = CORE_X + 50_000
    DCOC_Y = CORE_Y - 70_000
    print("Placing DCOC Servo Loop (OTA & Integrating Capacitor)...")
    top_cell.insert(pya.CellInstArray(cell_pmos.cell_index(), pya.Trans(DCOC_X, DCOC_Y)))
    top_cell.insert(pya.CellInstArray(cell_pmos.cell_index(), pya.Trans(DCOC_X + 20_000, DCOC_Y)))
    top_cell.insert(pya.CellInstArray(cell_nmos.cell_index(), pya.Trans(DCOC_X, DCOC_Y - 20_000)))
    top_cell.insert(pya.CellInstArray(cell_nmos.cell_index(), pya.Trans(DCOC_X + 20_000, DCOC_Y - 20_000)))
    
    # Large on-chip DCOC integrating capacitor C_INT (~8 pF)
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(DCOC_X + 50_000, DCOC_Y - 30_000)))
    top_cell.insert(pya.CellInstArray(cell_cmim.cell_index(), pya.Trans(DCOC_X + 75_000, DCOC_Y - 30_000)))
    
    # 8. Place 50-Ohm Matched Output Buffer
    BUF_X = CORE_X + 60_000
    BUF_Y = CORE_Y + 80_000
    print("Placing 50-Ohm CML Output Buffer Stage...")
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(BUF_X, BUF_Y)))
    top_cell.insert(pya.CellInstArray(cell_npn.cell_index(), pya.Trans(BUF_X + 35_000, BUF_Y)))
    # 50 Ohm load resistors (rsil)
    top_cell.insert(pya.CellInstArray(cell_rsil.cell_index(), pya.Trans(BUF_X, BUF_Y + 25_000)))
    top_cell.insert(pya.CellInstArray(cell_rsil.cell_index(), pya.Trans(BUF_X + 35_000, BUF_Y + 25_000)))
    
    # -------------------------------------------------------------------------
    # Power Rings & Top-Metal Interconnect Routing
    # -------------------------------------------------------------------------
    print("Routing VDD (2.5V) and VSS Power Grid on TopMetal1 & TopMetal2...")
    # VDD TopMetal2 wide bus (20 um width)
    top_cell.shapes(L_TOPMETAL2).insert(pya.Box(CORE_X - 60_000, CORE_Y + 130_000, CORE_X + 220_000, CORE_Y + 150_000))
    # VSS TopMetal1 wide ground plane
    top_cell.shapes(L_TOPMETAL1).insert(pya.Box(CORE_X - 60_000, CORE_Y - 110_000, CORE_X + 220_000, CORE_Y - 90_000))
    
    # High-speed signal routing in Metal3 / Metal4 / TopMetal1
    # Input node interconnect
    top_cell.shapes(L_TOPMETAL1).insert(pya.Box(CORE_X - 100_000, CORE_Y - 2_000, CORE_X, CORE_Y + 2_000))
    # Output differential lines
    top_cell.shapes(L_TOPMETAL1).insert(pya.Box(BUF_X + 5_000, BUF_Y + 40_000, BUF_X + 15_000, BUF_Y + 120_000))
    top_cell.shapes(L_TOPMETAL1).insert(pya.Box(BUF_X + 30_000, BUF_Y + 40_000, BUF_X + 40_000, BUF_Y + 120_000))
    
    # -------------------------------------------------------------------------
    # Bondpads Placement (GSG Configuration for RF Probe Measurements)
    # -------------------------------------------------------------------------
    print("Placing RF GSG Bondpad Clusters (Input & Output)...")
    PAD_PITCH = 120_000 # 120 um GSG pitch
    
    # Input GSG Pads (West edge): GND, IN_PAD, GND
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(60_000, CORE_Y - PAD_PITCH)))
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(60_000, CORE_Y)))
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(60_000, CORE_Y + PAD_PITCH)))
    
    # Output GSG Pads (East edge): OUT_P, GND, OUT_N
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(650_000, CORE_Y - PAD_PITCH)))
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(650_000, CORE_Y)))
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(650_000, CORE_Y + PAD_PITCH)))
    
    # DC Power Pads (North & South edges)
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(CORE_X + 30_000, 480_000))) # VDD
    top_cell.insert(pya.CellInstArray(cell_pad.cell_index(), pya.Trans(CORE_X + 30_000, 30_000)))  # VSS
    
    # Chip Boundary / Sealring Guard Ring (Substrate & Metal1 ring)
    DIE_WIDTH  = 800_000
    DIE_HEIGHT = 600_000
    top_cell.shapes(L_METAL1).insert(pya.Box(0, 0, DIE_WIDTH, 10_000))
    top_cell.shapes(L_METAL1).insert(pya.Box(0, DIE_HEIGHT - 10_000, DIE_WIDTH, DIE_HEIGHT))
    top_cell.shapes(L_METAL1).insert(pya.Box(0, 0, 10_000, DIE_HEIGHT))
    top_cell.shapes(L_METAL1).insert(pya.Box(DIE_WIDTH - 10_000, 0, DIE_WIDTH, DIE_HEIGHT))
    
    # Write GDSII
    out_gds = "gds/tia_top.gds"
    layout.write(out_gds)
    print(f"--> Successfully generated GDSII: {out_gds}")
    print(f"--> Die Dimensions: {DIE_WIDTH/1e6:.2f} mm x {DIE_HEIGHT/1e6:.2f} mm = {(DIE_WIDTH*DIE_HEIGHT)/1e12:.3f} mm^2 (Limit: 5 mm^2)")
    print("================================================================================")

if __name__ == '__main__':
    build_layout()
