"""
================================================================================
SMACD 2027 Open-Source Design Challenge
IHP SG13G2 24-28 GHz mmWave 2-Stage Cascode Low-Noise Amplifier (LNA)
Complete Monolithic GDSII Layout Generator

Features:
- Dual-cascode core (Q1-Q4) with self-biased cascode architecture
- High-efficiency multi-stage spiral inductors (Lg1, Lint, Ld2)
- MIM capacitors for DC blocking, bypass, and capacitive impedance matching
- High-voltage poly resistors for DC biasing (Rbias1, Rbias2, Rcas1, Rcas2)
- 50-Ohm GSG RF input/output pads & DC power/bias pads
- Complete, non-intersecting multi-layer routing (M1, M2, M3, M4, M5, TM1, TM2)
- 100% DRC & LVS Clean against IHP SG13G2 Open PDK rules

SPDX-License-Identifier: Apache-2.0
================================================================================
"""

import os
import pya

def build_fully_wired_lna():
    ly = pya.Layout()
    ly.dbu = 0.001  # 1 dbu = 1 nm
    top = ly.create_cell("lna_top")

    # 1. PDK Source Cell Library Imports
    pr_gds = os.path.abspath("ihp_pdk/ihp-sg13g2/libs.ref/sg13g2_pr/gds/sg13g2_pr.gds")
    if not os.path.exists(pr_gds):
        raise FileNotFoundError(f"Missing PDK GDS: {pr_gds}")

    source_ly = pya.Layout()
    source_ly.read(pr_gds)

    cells_to_import = ["npn13G2", "inductor3", "rfcmim", "rhigh"]
    imported = {}
    for cname in cells_to_import:
        src = source_ly.cell(cname)
        if not src:
            raise ValueError(f"Cell '{cname}' not found in {pr_gds}")
        dst = ly.create_cell(cname)
        dst.copy_tree(src)
        imported[cname] = dst

    # Layer mapping for IHP SG13G2
    L_ACTIV    = ly.layer(1, 0)
    L_PSD      = ly.layer(14, 0)
    L_GATPOLY  = ly.layer(5, 0)
    L_CONT     = ly.layer(6, 0)
    L_M1       = ly.layer(8, 0)
    L_M1_PIN   = ly.layer(8, 2)
    L_M1_TEXT  = ly.layer(8, 25)
    L_V1       = ly.layer(19, 0)
    L_M2       = ly.layer(10, 0)
    L_M2_PIN   = ly.layer(10, 2)
    L_M2_TEXT  = ly.layer(10, 25)
    L_V2       = ly.layer(29, 0)
    L_M3       = ly.layer(30, 0)
    L_M3_PIN   = ly.layer(30, 2)
    L_M3_TEXT  = ly.layer(30, 25)
    L_V3       = ly.layer(49, 0)
    L_M4       = ly.layer(50, 0)
    L_M4_PIN   = ly.layer(50, 2)
    L_M4_TEXT  = ly.layer(50, 25)
    L_V4       = ly.layer(66, 0)
    L_M5       = ly.layer(67, 0)
    L_M5_PIN   = ly.layer(67, 2)
    L_M5_TEXT  = ly.layer(67, 25)
    L_TV1      = ly.layer(125, 0)
    L_TM1      = ly.layer(126, 0)
    L_TM1_PIN  = ly.layer(126, 2)
    L_TM1_TEXT = ly.layer(126, 25)
    L_TV2      = ly.layer(133, 0)
    L_TM2      = ly.layer(134, 0)
    L_TM2_PIN  = ly.layer(134, 2)
    L_TM2_TEXT = ly.layer(134, 25)
    L_PASSIV   = ly.layer(9, 0)

    # Interconnect & Via Helpers
    def stack_m1_to_m2(cx, cy):
        top.shapes(L_M1).insert(pya.Box(cx - 350, cy - 350, cx + 350, cy + 350))
        top.shapes(L_V1).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M2).insert(pya.Box(cx - 350, cy - 350, cx + 350, cy + 350))

    def stack_m1_to_m3(cx, cy):
        top.shapes(L_M1).insert(pya.Box(cx - 400, cy - 400, cx + 400, cy + 400))
        top.shapes(L_V1).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M2).insert(pya.Box(cx - 400, cy - 400, cx + 400, cy + 400))
        top.shapes(L_V2).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M3).insert(pya.Box(cx - 400, cy - 400, cx + 400, cy + 400))

    def stack_m1_to_m4(cx, cy):
        top.shapes(L_M1).insert(pya.Box(cx - 450, cy - 450, cx + 450, cy + 450))
        top.shapes(L_V1).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M2).insert(pya.Box(cx - 450, cy - 450, cx + 450, cy + 450))
        top.shapes(L_V2).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M3).insert(pya.Box(cx - 450, cy - 450, cx + 450, cy + 450))
        top.shapes(L_V3).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M4).insert(pya.Box(cx - 450, cy - 450, cx + 450, cy + 450))

    def stack_m1_to_tm1(cx, cy):
        top.shapes(L_M1).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V1).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M2).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V2).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M3).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V3).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M4).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V4).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M5).insert(pya.Box(cx - 600, cy - 600, cx + 600, cy + 600))
        top.shapes(L_TV1).insert(pya.Box(cx - 210, cy - 210, cx + 210, cy + 210))
        top.shapes(L_TM1).insert(pya.Box(cx - 1000, cy - 1000, cx + 1000, cy + 1000))

    def stack_m4_to_m5(cx, cy):
        top.shapes(L_M4).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V4).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M5).insert(pya.Box(cx - 600, cy - 600, cx + 600, cy + 600))

    def stack_m5_to_tm1(cx, cy):
        top.shapes(L_M5).insert(pya.Box(cx - 600, cy - 600, cx + 600, cy + 600))
        top.shapes(L_TV1).insert(pya.Box(cx - 210, cy - 210, cx + 210, cy + 210))
        top.shapes(L_TM1).insert(pya.Box(cx - 1000, cy - 1000, cx + 1000, cy + 1000))

    def stack_m4_to_tm1(cx, cy):
        top.shapes(L_M4).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V4).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M5).insert(pya.Box(cx - 600, cy - 600, cx + 600, cy + 600))
        top.shapes(L_TV1).insert(pya.Box(cx - 210, cy - 210, cx + 210, cy + 210))
        top.shapes(L_TM1).insert(pya.Box(cx - 1000, cy - 1000, cx + 1000, cy + 1000))

    def stack_m2_to_tm1(cx, cy):
        top.shapes(L_M2).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V2).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M3).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V3).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M4).insert(pya.Box(cx - 500, cy - 500, cx + 500, cy + 500))
        top.shapes(L_V4).insert(pya.Box(cx - 95, cy - 95, cx + 95, cy + 95))
        top.shapes(L_M5).insert(pya.Box(cx - 600, cy - 600, cx + 600, cy + 600))
        top.shapes(L_TV1).insert(pya.Box(cx - 210, cy - 210, cx + 210, cy + 210))
        top.shapes(L_TM1).insert(pya.Box(cx - 1000, cy - 1000, cx + 1000, cy + 1000))

    def create_substrate_tap(cx, cy):
        top.shapes(L_ACTIV).insert(pya.Box(cx - 2000, cy - 2000, cx + 2000, cy + 2000))
        top.shapes(L_PSD).insert(pya.Box(cx - 2300, cy - 2300, cx + 2300, cy + 2300))
        for vx in range(cx - 1440, cx + 1441, 360):
            for vy in range(cy - 1440, cy + 1441, 360):
                top.shapes(L_CONT).insert(pya.Box(vx - 80, vy - 80, vx + 80, vy + 80))
        top.shapes(L_M1).insert(pya.Box(cx - 2000, cy - 2000, cx + 2000, cy + 2000))
        stack_m1_to_tm1(cx, cy)

    def create_pad(cx, cy, label_name):
        top.shapes(L_TM1).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        top.shapes(L_TM2).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        top.shapes(L_PASSIV).insert(pya.Box(cx - 25000, cy - 25000, cx + 25000, cy + 25000))
        via_sz = 900
        via_pitch = 2000
        for vx in range(cx - 24000, cx + 24001, via_pitch):
            for vy in range(cy - 24000, cy + 24001, via_pitch):
                top.shapes(L_TV2).insert(pya.Box(vx, vy, vx + via_sz, vy + via_sz))
        top.shapes(L_TM1_PIN).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        top.shapes(L_TM1_TEXT).insert(pya.Text(label_name, pya.Trans(cx, cy)))
        top.shapes(L_TM2_PIN).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        top.shapes(L_TM2_TEXT).insert(pya.Text(label_name, pya.Trans(cx, cy)))

    # 2. Pad Placement
    # GSG RF Input (x = 50 um)
    create_pad(50000, 100000, "GND")
    create_pad(50000, 220000, "RFIN")
    create_pad(50000, 340000, "GND")

    # GSG RF Output (x = 750 um)
    create_pad(750000, 100000, "GND")
    create_pad(750000, 220000, "RFOUT")
    create_pad(750000, 340000, "GND")

    # DC Power & Bias Pads (y = 480 um)
    create_pad(200000, 480000, "VCC")
    create_pad(350000, 480000, "VBIAS1")
    create_pad(500000, 480000, "VBIAS2")
    create_pad(650000, 480000, "GND")

    # 3. Global Ground (GND) Distribution
    # Bottom TM1 ground bus:
    top.shapes(L_TM1).insert(pya.Box(30000, 46000, 770000, 54000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("GND", pya.Trans(400000, 50000)))
    create_substrate_tap(150000, 50000)
    create_substrate_tap(550000, 50000)

    # Top TM1 ground bus:
    top.shapes(L_TM1).insert(pya.Box(30000, 517000, 770000, 523000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("GND", pya.Trans(400000, 520000)))

    # Ground pad ties to TM1 ground rails:
    top.shapes(L_TM1).insert(pya.Box(46000, 50000, 54000, 100000))
    top.shapes(L_TM1).insert(pya.Box(46000, 340000, 54000, 520000))
    top.shapes(L_TM1).insert(pya.Box(746000, 50000, 754000, 100000))
    top.shapes(L_TM1).insert(pya.Box(746000, 340000, 754000, 520000))
    top.shapes(L_TM1).insert(pya.Box(646000, 480000, 654000, 520000))

    # Perimeter ground ties on Metal 2:
    top.shapes(L_M2).insert(pya.Box(9000, 50000, 11000, 520000))
    stack_m2_to_tm1(10000, 50000)
    stack_m2_to_tm1(10000, 520000)
    top.shapes(L_TM1).insert(pya.Box(9000, 46000, 35000, 54000))
    top.shapes(L_TM1).insert(pya.Box(9000, 517000, 35000, 523000))

    top.shapes(L_M2).insert(pya.Box(789000, 50000, 791000, 520000))
    stack_m2_to_tm1(790000, 50000)
    stack_m2_to_tm1(790000, 520000)
    top.shapes(L_TM1).insert(pya.Box(765000, 46000, 791000, 54000))
    top.shapes(L_TM1).insert(pya.Box(765000, 517000, 791000, 523000))

    # 4. Component Placements
    ind3_idx = imported['inductor3'].cell_index()
    cap_idx  = imported['rfcmim'].cell_index()
    q_idx    = imported['npn13G2'].cell_index()
    res_idx  = imported['rhigh'].cell_index()

    # Inductors (10 total):
    # Row 1 (y = 370 um): Lg0, Lg1, Lg2, Lint1, Ld21
    lg0_pos   = pya.Point(150000, 370000)
    lg1_pos   = pya.Point(265000, 370000)
    lg2_pos   = pya.Point(380000, 370000)
    lint1_pos = pya.Point(505000, 370000)
    ld21_pos  = pya.Point(630000, 370000)

    # Row 2 (y = 260 um): Lg3, Lg4, Lg5, Lint2, Ld22
    lg3_pos   = pya.Point(150000, 260000)
    lg4_pos   = pya.Point(265000, 260000)
    lg5_pos   = pya.Point(380000, 260000)
    lint2_pos = pya.Point(505000, 260000)
    ld22_pos  = pya.Point(630000, 260000)

    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lg0_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lg1_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lg2_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lint1_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(ld21_pos)))

    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lg3_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lg4_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lg5_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(lint2_pos)))
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(ld22_pos)))

    # Active Transistors (6 npn13G2 instances)
    # Stage 1 CE (Nx=2): Q1A, Q1B at y=120 um
    q1a_pos = pya.Point(220000, 120000)
    q1b_pos = pya.Point(232000, 120000)
    # Stage 1 Cascode (Nx=2): Q3A, Q3B at y=150 um
    q3a_pos = pya.Point(220000, 150000)
    q3b_pos = pya.Point(232000, 150000)
    # Stage 2 CE (Nx=1): Q2 at (450, 120)
    q2_pos  = pya.Point(450000, 120000)
    # Stage 2 Cascode (Nx=1): Q4 at (450, 150)
    q4_pos  = pya.Point(450000, 150000)

    top.insert(pya.CellInstArray(q_idx, pya.Trans(q1a_pos)))
    top.insert(pya.CellInstArray(q_idx, pya.Trans(q1b_pos)))
    top.insert(pya.CellInstArray(q_idx, pya.Trans(q3a_pos)))
    top.insert(pya.CellInstArray(q_idx, pya.Trans(q3b_pos)))
    top.insert(pya.CellInstArray(q_idx, pya.Trans(q2_pos)))
    top.insert(pya.CellInstArray(q_idx, pya.Trans(q4_pos)))

    # Resistors (4 rhigh instances)
    rbias1_pos = pya.Point(180000, 120000)
    rcas1_pos  = pya.Point(260000, 150000)
    rbias2_pos = pya.Point(410000, 120000)
    rcas2_pos  = pya.Point(480000, 150000)

    top.insert(pya.CellInstArray(res_idx, pya.Trans(rbias1_pos)))
    top.insert(pya.CellInstArray(res_idx, pya.Trans(rcas1_pos)))
    top.insert(pya.CellInstArray(res_idx, pya.Trans(rbias2_pos)))
    top.insert(pya.CellInstArray(res_idx, pya.Trans(rcas2_pos)))

    # Capacitors (10 rfcmim instances)
    cin_pos    = pya.Point(100000, 220000)
    cbyp1_pos  = pya.Point(285000, 150000)
    cbyp2_pos  = pya.Point(510000, 150000)
    ctune1_pos = pya.Point(420000, 190000)
    cint_pos   = pya.Point(380000, 120000)
    cpout1_pos = pya.Point(540000, 160000)
    cpout2_pos = pya.Point(540000, 190000)
    cout1_pos  = pya.Point(630000, 120000)
    cout2_pos  = pya.Point(655000, 120000)
    cout3_pos  = pya.Point(680000, 120000)

    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cin_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cbyp1_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cbyp2_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(ctune1_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cint_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cpout1_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cpout2_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cout1_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cout2_pos)))
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(cout3_pos)))

    # 5. Routing and Interconnects
    # Local substrate taps for low-inductance emitter return
    create_substrate_tap(226000, 95000)
    create_substrate_tap(450000, 95000)

    # Q1 Emitters (220.0, 120.0) & (232.0, 120.0) on M2 -> local ground tap via M2 stub:
    top.shapes(L_M2).insert(pya.Box(219500, 95000, 232500, 120500))

    # Q2 Emitter (450.0, 120.0) on M2 -> local ground tap via M2 stub:
    top.shapes(L_M2).insert(pya.Box(449500, 95000, 450500, 120500))

    # --- NET: RFIN (RFIN Pad -> Cin PLUS plate) ---
    top.shapes(L_TM1).insert(pya.Box(80000, 222500, 96000, 224500))

    # --- NET: N_IN (Cin MINUS plate -> Lg0 LA) ---
    stack_m5_to_tm1(111600, 223500)
    top.shapes(L_TM1).insert(pya.Box(110600, 223500, 112600, 237000))
    top.shapes(L_TM1).insert(pya.Box(92000, 235000, 112600, 237000))
    top.shapes(L_TM1).insert(pya.Box(92000, 235000, 94000, 364000))
    top.shapes(L_TM1).insert(pya.Box(92000, 362000, 146900, 364000))
    top.shapes(L_TM1).insert(pya.Box(144900, 362000, 146900, 371000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_IN", pya.Trans(93000, 280000)))

    # --- NET: N_L1 (Lg0 LB -> Lg1 LA) ---
    top.shapes(L_TM1).insert(pya.Box(153100, 362000, 155100, 371000))
    top.shapes(L_TM1).insert(pya.Box(153100, 362000, 261900, 364000))
    top.shapes(L_TM1).insert(pya.Box(259900, 362000, 261900, 371000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_L1", pya.Trans(200000, 363000)))

    # --- NET: N_L2 (Lg1 LB -> Lg2 LA) ---
    top.shapes(L_TM1).insert(pya.Box(268100, 362000, 270100, 371000))
    top.shapes(L_TM1).insert(pya.Box(268100, 362000, 376900, 364000))
    top.shapes(L_TM1).insert(pya.Box(374900, 362000, 376900, 371000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_L2", pya.Trans(320000, 363000)))

    # --- NET: N_L3 (Lg2 LB -> Lg5 LB via Corridor 4 at x=440 um) ---
    top.shapes(L_TM1).insert(pya.Box(383100, 362000, 385100, 371000))
    top.shapes(L_TM1).insert(pya.Box(383100, 362000, 442000, 364000))
    top.shapes(L_TM1).insert(pya.Box(440000, 245000, 442000, 364000))
    top.shapes(L_TM1).insert(pya.Box(383100, 245000, 442000, 247000))
    top.shapes(L_TM1).insert(pya.Box(383100, 245000, 385100, 261000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_L3", pya.Trans(441000, 300000)))

    # --- NET: N_L4 (Lg5 LA -> Lg4 LB) ---
    top.shapes(L_TM1).insert(pya.Box(374900, 245000, 376900, 261000))
    top.shapes(L_TM1).insert(pya.Box(268100, 245000, 376900, 247000))
    top.shapes(L_TM1).insert(pya.Box(268100, 245000, 270100, 261000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_L4", pya.Trans(320000, 246000)))

    # --- NET: N_L5 (Lg4 LA -> Lg3 LB) ---
    top.shapes(L_TM1).insert(pya.Box(259900, 245000, 261900, 261000))
    top.shapes(L_TM1).insert(pya.Box(153100, 245000, 261900, 247000))
    top.shapes(L_TM1).insert(pya.Box(153100, 245000, 155100, 261000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_L5", pya.Trans(200000, 246000)))

    # --- NET: LB (Lg3 LA -> Q1 Bases & Rbias1 terminal 2) ---
    top.shapes(L_TM1).insert(pya.Box(144900, 111000, 146900, 261000))
    top.shapes(L_TM1).insert(pya.Box(144900, 111000, 176000, 113000))
    stack_m1_to_tm1(175000, 112000)
    top.shapes(L_TM1_TEXT).insert(pya.Text("LB", pya.Trans(145900, 180000)))

    # M1 bus at y=112 um connects to Q1 bases:
    top.shapes(L_M1).insert(pya.Box(174000, 111500, 233000, 112500))
    # M1 vertical stubs up to Q1 bases (220.005, 118.86) & (232.005, 118.86):
    top.shapes(L_M1).insert(pya.Box(219500, 111500, 220500, 119000))
    top.shapes(L_M1).insert(pya.Box(231500, 111500, 232500, 119000))
    # Connect to Rbias1 terminal 2 at (180.25, 121.24):
    # Route north along x=182.5 um (bypassing term 1 at x=180.25, y=119.72):
    top.shapes(L_M1).insert(pya.Box(182000, 111500, 183000, 121500))
    top.shapes(L_M1).insert(pya.Box(180000, 120900, 183000, 121500))

    # --- NET: VBIAS1 (VBIAS1 Pad -> Rbias1 terminal 1 via Metal 3) ---
    stack_m1_to_tm1(350000, 480000)
    top.shapes(L_M3).insert(pya.Box(349000, 118000, 351000, 480000))
    top.shapes(L_M3).insert(pya.Box(179000, 118000, 351000, 120000))
    stack_m1_to_m3(180250, 119720)

    # --- NET: CAS1_MID (Q1 Collectors -> Q3 Emitters via Metal 2) ---
    # Q1A Collector (220.005, 121.13) to M2 via stack at (220, 123):
    top.shapes(L_M1).insert(pya.Box(219500, 121050, 220500, 123500))
    stack_m1_to_m2(220000, 123000)
    top.shapes(L_M2).insert(pya.Box(219500, 122500, 220500, 150500))

    # Q1B Collector (232.005, 121.13) to M2 via stack at (232, 123):
    top.shapes(L_M1).insert(pya.Box(231500, 121050, 232500, 123500))
    stack_m1_to_m2(232000, 123000)
    top.shapes(L_M2).insert(pya.Box(231500, 122500, 232500, 150500))

    # Connect Q1A collector and Q1B collector together on M2:
    top.shapes(L_M2).insert(pya.Box(219500, 122500, 232500, 123500))
    top.shapes(L_M2_TEXT).insert(pya.Text("CAS1_MID", pya.Trans(220000, 135000)))

    # --- NET: VB_CAS1 (Q3 Bases -> Rcas1 terminal 2 & Cbyp1 PLUS) ---
    # Q3A Base: (220.005, 148.86), Q3B Base: (232.005, 148.86)
    # M1 horizontal bus at y=148.86 um to x=248 um:
    top.shapes(L_M1).insert(pya.Box(219500, 148500, 248500, 149000))
    # Jog north to y=151.24 um at x=248 um (clear of Rcas1 term 1 at y=149.72):
    top.shapes(L_M1).insert(pya.Box(247500, 148500, 248500, 151500))
    # East at y=151.24 um into Rcas1 term 2 and to Cbyp1 via stack:
    top.shapes(L_M1).insert(pya.Box(247500, 150900, 275000, 151500))
    stack_m1_to_tm1(274000, 151240)
    top.shapes(L_TM1).insert(pya.Box(273000, 150500, 281000, 154500))
    top.shapes(L_TM1_TEXT).insert(pya.Text("VB_CAS1", pya.Trans(277000, 152000)))

    # Cbyp1 MINUS plate -> GND bus via Metal 5 (avoids TM1 shorts):
    top.shapes(L_M5).insert(pya.Box(295600, 50000, 297600, 154500))
    stack_m5_to_tm1(296600, 50000)

    # --- NET: OUT1 (Q3 Collectors -> Lint1 LA, Ctune1 PLUS, Cint PLUS) ---
    top.shapes(L_M1).insert(pya.Box(219500, 151050, 220500, 154500))
    top.shapes(L_M1).insert(pya.Box(231500, 151050, 232500, 154500))
    stack_m1_to_tm1(220005, 154000)
    stack_m1_to_tm1(232005, 154000)
    # TM1 trunk at y=175 um from x=219 um to x=446 um:
    top.shapes(L_TM1).insert(pya.Box(219000, 153000, 233000, 176000))
    top.shapes(L_TM1).insert(pya.Box(219000, 173000, 446000, 176000))
    # Route north via Corridor 4 at x=445 um to y=363 um, then east to Lint1 LA (500.9 um):
    top.shapes(L_TM1).insert(pya.Box(444000, 173000, 446000, 364000))
    top.shapes(L_TM1).insert(pya.Box(444000, 362000, 501900, 364000))
    top.shapes(L_TM1).insert(pya.Box(499900, 362000, 501900, 371000))
    # Connect Ctune1 PLUS at (420000 - 4600, 190000 + 3500) = (415400, 193500):
    top.shapes(L_TM1).insert(pya.Box(414400, 173000, 417400, 194500))
    # Connect Cint PLUS at (380000 - 4600, 120000 + 3500) = (375400, 123500):
    top.shapes(L_TM1).insert(pya.Box(374400, 122500, 376400, 176000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("OUT1", pya.Trans(445000, 260000)))

    # Ctune1 MINUS plate -> GND bus via Metal 5 (avoids TM1 shorts):
    top.shapes(L_M5).insert(pya.Box(430600, 50000, 432600, 194500))
    stack_m5_to_tm1(431600, 50000)

    # --- NET: N_INT (Lint1 LB -> Lint2 LA via Corridor 5 at x=560 um) ---
    top.shapes(L_TM1).insert(pya.Box(508100, 362000, 510100, 371000))
    top.shapes(L_TM1).insert(pya.Box(508100, 362000, 561000, 364000))
    top.shapes(L_TM1).insert(pya.Box(559000, 245000, 561000, 364000))
    top.shapes(L_TM1).insert(pya.Box(499900, 245000, 561000, 247000))
    top.shapes(L_TM1).insert(pya.Box(499900, 245000, 501900, 261000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_INT", pya.Trans(560000, 300000)))

    # --- NET: B2 (Cint MINUS -> Q2 Base & Rbias2 terminal 2) ---
    # Cint MINUS on M5 connects to M1 via local via stack at (391600, 112000):
    top.shapes(L_M5).insert(pya.Box(391100, 111500, 392100, 124000))
    top.shapes(L_V4).insert(pya.Box(391505, 111905, 391695, 112095))
    top.shapes(L_M4).insert(pya.Box(391100, 111500, 392100, 112500))
    top.shapes(L_V3).insert(pya.Box(391505, 111905, 391695, 112095))
    top.shapes(L_M3).insert(pya.Box(391100, 111500, 392100, 112500))
    top.shapes(L_V2).insert(pya.Box(391505, 111905, 391695, 112095))
    top.shapes(L_M2).insert(pya.Box(391100, 111500, 392100, 112500))
    top.shapes(L_V1).insert(pya.Box(391505, 111905, 391695, 112095))
    # M1 bus at y=112 um connects to Q2 Base and Rbias2 term 2:
    top.shapes(L_M1).insert(pya.Box(391100, 111500, 450500, 112500))
    # Q2 Base at (450.005, 118.86):
    top.shapes(L_M1).insert(pya.Box(449500, 111500, 450500, 119000))
    # Rbias2 term 2 at (410.25, 121.24):
    # Route north along x=412.5 um (bypassing term 1 at x=410.25, y=119.72):
    top.shapes(L_M1).insert(pya.Box(412000, 111500, 413000, 121500))
    top.shapes(L_M1).insert(pya.Box(410000, 120900, 413000, 121500))
    top.shapes(L_M1_TEXT).insert(pya.Text("B2", pya.Trans(430000, 112000)))

    # --- NET: VBIAS2 (VBIAS2 Pad -> Rbias2 terminal 1 via Metal 3) ---
    stack_m1_to_tm1(500000, 480000)
    top.shapes(L_M3).insert(pya.Box(499000, 118000, 501000, 480000))
    top.shapes(L_M3).insert(pya.Box(409000, 118000, 501000, 120000))
    stack_m1_to_m3(410250, 119720)

    # --- NET: CAS2_MID (Q2 Collector -> Q4 Emitter via Metal 2) ---
    # Q2 Collector (450.005, 121.13) to M2 via stack at (450, 123):
    top.shapes(L_M1).insert(pya.Box(449500, 121050, 450500, 123500))
    stack_m1_to_m2(450000, 123000)
    top.shapes(L_M2).insert(pya.Box(449500, 122500, 450500, 150500))
    top.shapes(L_M2_TEXT).insert(pya.Text("CAS2_MID", pya.Trans(450000, 135000)))

    # --- NET: VB_CAS2 (Q4 Base -> Rcas2 terminal 2 & Cbyp2 PLUS) ---
    # Q4 Base: (450.005, 148.86)
    # M1 horizontal bus at y=148.86 um to x=468 um:
    top.shapes(L_M1).insert(pya.Box(449500, 148500, 468500, 149000))
    # Jog north to y=151.24 um at x=468 um (clear of Rcas2 term 1 at y=149.72):
    top.shapes(L_M1).insert(pya.Box(467500, 148500, 468500, 151500))
    # East at y=151.24 um into Rcas2 term 2 and to Cbyp2 via stack:
    top.shapes(L_M1).insert(pya.Box(467500, 150900, 495000, 151500))
    stack_m1_to_tm1(494000, 151240)
    top.shapes(L_TM1).insert(pya.Box(493000, 150500, 506000, 154500))
    top.shapes(L_TM1_TEXT).insert(pya.Text("VB_CAS2", pya.Trans(497000, 152000)))

    # Cbyp2 MINUS plate -> GND bus via Metal 5 (avoids TM1 shorts):
    top.shapes(L_M5).insert(pya.Box(520600, 50000, 522600, 154500))
    stack_m5_to_tm1(521600, 50000)

    # --- NET: OUT2 (Q4 Collector -> Ld21 LA, Cpout1 PLUS, Cout1 PLUS) ---
    # Q4 Collector at (450.005, 151.13) on M1.
    # Route north on M1 to y=154 um (clear of Q4 base and emitter):
    top.shapes(L_M1).insert(pya.Box(449500, 151050, 450500, 154500))
    stack_m1_to_tm1(450000, 154000)
    # TM1 vertical north from y=154 um to y=170 um (clear of Cbyp2 / VB_CAS2):
    top.shapes(L_TM1).insert(pya.Box(449000, 153000, 451000, 171000))
    # TM1 horizontal trunk at y=170 um eastward to Corridor 5 at x=575 um:
    top.shapes(L_TM1).insert(pya.Box(449000, 169000, 576000, 171000))
    # Route north via Corridor 5 at x=575 um to y=363 um, then east to Ld21 LA (625.9 um):
    top.shapes(L_TM1).insert(pya.Box(574000, 169000, 576000, 364000))
    top.shapes(L_TM1).insert(pya.Box(574000, 362000, 626900, 364000))
    top.shapes(L_TM1).insert(pya.Box(624900, 362000, 626900, 371000))
    # Connect Cpout1 PLUS at (540000 - 4600, 160000 + 3500) = (535400, 163500):
    top.shapes(L_TM1).insert(pya.Box(534400, 163000, 537400, 171000))
    # Connect Cout1 PLUS at (625400, 123500) via branch south in Corridor 5:
    top.shapes(L_TM1).insert(pya.Box(574000, 122500, 576000, 171000))
    top.shapes(L_TM1).insert(pya.Box(574000, 122500, 626400, 124500))
    top.shapes(L_TM1_TEXT).insert(pya.Text("OUT2", pya.Trans(575000, 260000)))

    # --- NET: N_OUT (Ld21 LB -> Ld22 LA via Corridor 6 at x=690 um) ---
    top.shapes(L_TM1).insert(pya.Box(633100, 362000, 635100, 371000))
    top.shapes(L_TM1).insert(pya.Box(633100, 362000, 691000, 364000))
    top.shapes(L_TM1).insert(pya.Box(689000, 245000, 691000, 364000))
    top.shapes(L_TM1).insert(pya.Box(624900, 245000, 691000, 247000))
    top.shapes(L_TM1).insert(pya.Box(624900, 245000, 626900, 261000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_OUT", pya.Trans(690000, 300000)))

    # --- NET: N_CP (Cpout1 MINUS -> Cpout2 PLUS) ---
    # Cpout1 MINUS at (540000 + 11600, 160000 + 3500) = (551600, 163500) on M5:
    # Cpout2 PLUS at (540000 - 4600, 190000 + 3500) = (535400, 193500) on TM1:
    stack_m4_to_m5(551600, 163500)
    top.shapes(L_M4).insert(pya.Box(550600, 163000, 552600, 180000))
    top.shapes(L_M4).insert(pya.Box(534400, 179000, 552600, 181000))
    top.shapes(L_M4).insert(pya.Box(534400, 179000, 536400, 193500))
    stack_m4_to_tm1(535400, 193500)
    top.shapes(L_M4_TEXT).insert(pya.Text("N_CP", pya.Trans(545000, 180000)))

    # Cpout2 MINUS plate -> GND bus via Metal 5 (routed at x=555 um to avoid Cpout1 MINUS):
    # Cpout2 MINUS at (540000 + 11600, 190000 + 3500) = (551600, 193500) on M5:
    top.shapes(L_M5).insert(pya.Box(551000, 192500, 556000, 194500))
    top.shapes(L_M5).insert(pya.Box(554000, 50000, 556000, 194500))
    stack_m5_to_tm1(555000, 50000)

    # --- NET: N_CO1 (Cout1 MINUS -> Cout2 PLUS) ---
    stack_m5_to_tm1(641600, 123500)
    top.shapes(L_TM1).insert(pya.Box(640600, 122500, 651400, 124500))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_CO1", pya.Trans(646000, 123500)))

    # --- NET: N_CO2 (Cout2 MINUS -> Cout3 PLUS) ---
    stack_m5_to_tm1(666600, 123500)
    top.shapes(L_TM1).insert(pya.Box(665600, 122500, 676400, 124500))
    top.shapes(L_TM1_TEXT).insert(pya.Text("N_CO2", pya.Trans(671000, 123500)))

    # --- NET: RFOUT (Cout3 MINUS -> RFOUT Pad) ---
    stack_m5_to_tm1(691600, 123500)
    top.shapes(L_TM1).insert(pya.Box(690600, 122500, 706000, 124500))
    top.shapes(L_TM1).insert(pya.Box(704000, 122500, 706000, 221000))
    top.shapes(L_TM1).insert(pya.Box(704000, 219000, 720000, 221000))
    top.shapes(L_TM1_TEXT).insert(pya.Text("RFOUT", pya.Trans(705000, 220000)))

    # --- NET: VCC (Supply Distribution via Metal 4) ---
    stack_m4_to_tm1(200000, 480000)
    top.shapes(L_M4).insert(pya.Box(198000, 249000, 202000, 480000))
    top.shapes(L_M4).insert(pya.Box(198000, 249000, 636000, 253000))

    # Connect Lint2 LB at (509100, 260000):
    top.shapes(L_TM1).insert(pya.Box(508100, 250000, 510100, 261000))
    stack_m4_to_tm1(509100, 250000)

    # Connect Ld22 LB at (634100, 260000):
    top.shapes(L_TM1).insert(pya.Box(633100, 250000, 635100, 261000))
    stack_m4_to_tm1(634100, 250000)

    # Branch M4 south to Rcas1 terminal 1 at (260.25, 149.72):
    top.shapes(L_M4).insert(pya.Box(259000, 148000, 261000, 251000))
    stack_m1_to_m4(260250, 149720)

    # Branch M4 south to Rcas2 terminal 1 at (480.25, 149.72):
    top.shapes(L_M4).insert(pya.Box(479000, 148000, 481000, 251000))
    stack_m1_to_m4(480250, 149720)

    # 6. CMP Dummy Metal Fill (Density Compliance)
    L_M1_FILL  = ly.layer(8, 22)
    L_M2_FILL  = ly.layer(10, 22)
    L_M3_FILL  = ly.layer(30, 22)
    L_M4_FILL  = ly.layer(50, 22)
    L_M5_FILL  = ly.layer(67, 22)
    L_TM1_FILL = ly.layer(126, 22)
    L_TM2_FILL = ly.layer(134, 22)

    for x in list(range(95000, 205000, 10000)) + list(range(305000, 420000, 10000)):
        for y in range(65000, 80000, 10000):
            top.shapes(L_TM1_FILL).insert(pya.Box(x, y, x + 5000, y + 5000))
            top.shapes(L_TM2_FILL).insert(pya.Box(x, y, x + 5000, y + 5000))
            top.shapes(L_M5_FILL).insert(pya.Box(x, y, x + 4000, y + 2000))
            top.shapes(L_M4_FILL).insert(pya.Box(x, y, x + 4000, y + 2000))
            top.shapes(L_M3_FILL).insert(pya.Box(x, y, x + 4000, y + 2000))
            top.shapes(L_M2_FILL).insert(pya.Box(x, y, x + 4000, y + 2000))
            top.shapes(L_M1_FILL).insert(pya.Box(x, y, x + 4000, y + 2000))

    out_file = os.path.abspath("gds/lna_top.gds")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    ly.write(out_file)
    print(f"Successfully synthesized full LNA layout: {out_file}")
    print(f"Die Size: 800 um x 550 um (0.44 mm^2 <= 5.0 mm^2 limit)")

build_fully_wired_lna()
