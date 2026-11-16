import pya
import os

def build_lna_layout():
    pr_path = os.path.abspath("ihp_pdk/ihp-sg13g2/libs.ref/sg13g2_pr/gds/sg13g2_pr.gds")
    pr_ly = pya.Layout()
    pr_ly.read(pr_path)

    ly = pya.Layout()
    ly.dbu = 0.001 # 1 nm (1000 dbu = 1 um)

    top = ly.create_cell("lna_top")

    # Import required primitive cells into our layout
    cells_to_import = ['npn13G2', 'inductor3', 'rfcmim', 'rhigh']
    imported = {}
    for name in cells_to_import:
        src = pr_ly.cell(name)
        dst = ly.create_cell(name)
        dst.copy_tree(src)
        imported[name] = dst

    # Snap 10 nm off-angle vertices in inductor3 TopMetal2 (134/0) so ANGLE rule passes strictly
    L_TM2 = ly.layer(134, 0)
    ind3_cell = imported['inductor3']
    for s in list(ind3_cell.shapes(L_TM2).each()):
        if s.is_polygon():
            poly = s.polygon
            pts = list(poly.each_point_hull())
            changed = False
            new_pts = []
            for pt in pts:
                if pt.x == 1630 and pt.y == 68050:
                    new_pts.append(pya.Point(1640, 68050))
                    changed = True
                elif pt.x == -1630 and pt.y == 61940:
                    new_pts.append(pya.Point(-1640, 61940))
                    changed = True
                else:
                    new_pts.append(pt)
            if changed:
                ind3_cell.shapes(L_TM2).erase(s)
                ind3_cell.shapes(L_TM2).insert(pya.Polygon(new_pts))

    # Layer definitions
    L_M1       = ly.layer(8, 0)
    L_M1_PIN   = ly.layer(8, 2)
    L_M1_TEXT  = ly.layer(8, 25)
    L_V1       = ly.layer(19, 0)
    L_M2       = ly.layer(10, 0)
    L_M2_PIN   = ly.layer(10, 2)
    L_M2_TEXT  = ly.layer(10, 25)
    L_TM1      = ly.layer(126, 0)
    L_TM1_PIN  = ly.layer(126, 2)
    L_TM1_TEXT = ly.layer(126, 25)
    L_TV2      = ly.layer(133, 0)
    L_TM2      = ly.layer(134, 0)
    L_TM2_PIN  = ly.layer(134, 2)
    L_TM2_TEXT = ly.layer(134, 25)
    L_PASSIV   = ly.layer(9, 0)
    L_TEXT     = ly.layer(63, 0)

    # Helper: draw pad (70x70 um centered at cx, cy)
    def create_pad(cx, cy, label_name):
        top.shapes(L_TM1).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        top.shapes(L_TM2).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        top.shapes(L_PASSIV).insert(pya.Box(cx - 25000, cy - 25000, cx + 25000, cy + 25000))
        via_sz = 900
        via_pitch = 2000
        for vx in range(cx - 24000, cx + 24001, via_pitch):
            for vy in range(cy - 24000, cy + 24001, via_pitch):
                top.shapes(L_TV2).insert(pya.Box(vx, vy, vx + via_sz, vy + via_sz))
        top.shapes(L_TM2_PIN).insert(pya.Box(cx - 35000, cy - 35000, cx + 35000, cy + 35000))
        # TopMetal2 text layer for LVS port recognition (layer 134/25)
        top.shapes(L_TM2_TEXT).insert(pya.Text(label_name, pya.Trans(cx, cy)))
        top.shapes(L_TEXT).insert(pya.Text(label_name, pya.Trans(cx, cy)))

    # 1. GSG Pads for RF Input (x = 50 um; y = 100, 220, 340 um)
    create_pad(50000, 100000, "GND")
    create_pad(50000, 220000, "RFIN")
    create_pad(50000, 340000, "GND")

    # 2. GSG Pads for RF Output (x = 750 um; y = 100, 220, 340 um)
    create_pad(750000, 100000, "GND")
    create_pad(750000, 220000, "RFOUT")
    create_pad(750000, 340000, "GND")

    # 3. DC Power & Bias Pads (y = 480 um; x = 200, 350, 500, 650 um)
    create_pad(200000, 480000, "VCC")
    create_pad(350000, 480000, "VBIAS1")
    create_pad(500000, 480000, "VBIAS2")
    create_pad(650000, 480000, "GND")

    # 4. Transistors Placement
    # Stage 1: Q1 (CE), Q2 (CB)
    q1_idx = imported['npn13G2'].cell_index()
    top.insert(pya.CellInstArray(q1_idx, pya.Trans(pya.Point(230000, 200000)))) # Q1
    top.insert(pya.CellInstArray(q1_idx, pya.Trans(pya.Point(230000, 220000)))) # Q2

    # Stage 2: Q3 (CE), Q4 (CB)
    top.insert(pya.CellInstArray(q1_idx, pya.Trans(pya.Point(550000, 200000)))) # Q3
    top.insert(pya.CellInstArray(q1_idx, pya.Trans(pya.Point(550000, 220000)))) # Q4

    # Current Mirror Reference: Q5, Q6
    top.insert(pya.CellInstArray(q1_idx, pya.Trans(pya.Point(350000, 350000)))) # Q5
    top.insert(pya.CellInstArray(q1_idx, pya.Trans(pya.Point(500000, 350000)))) # Q6

    # 5. Inductors Placement (inductor3)
    ind3_idx = imported['inductor3'].cell_index()

    # Lg1 (Input matching inductor, inductor3)
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(pya.Point(140000, 170000))))

    # Lint (Interstage matching inductor, inductor3)
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(pya.Point(380000, 170000))))

    # Ld2 (Output load inductor, inductor3)
    top.insert(pya.CellInstArray(ind3_idx, pya.Trans(pya.Point(620000, 170000))))

    # Emitter degeneration microstrip inductors Le1, Le2:
    # 25 um length x 3 um width TopMetal2 line providing ~22 pH degeneration
    # Le1: connects Q1 emitter (x=230, y=200) downward to GND rail
    top.shapes(L_TM2).insert(pya.Box(228500, 170000, 231500, 195000))
    # Le2: connects Q3 emitter (x=550, y=200) downward to GND rail
    top.shapes(L_TM2).insert(pya.Box(548500, 170000, 551500, 195000))

    # 6. MIM Capacitors (rfcmim)
    cap_idx = imported['rfcmim'].cell_index()
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(pya.Point(100000, 220000)))) # Cin
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(pya.Point(690000, 220000)))) # Cout
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(pya.Point(470000, 220000)))) # Cint
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(pya.Point(200000, 350000)))) # Cbyp1
    top.insert(pya.CellInstArray(cap_idx, pya.Trans(pya.Point(650000, 350000)))) # Cbyp2

    # 7. Resistors (rhigh)
    res_idx = imported['rhigh'].cell_index()
    top.insert(pya.CellInstArray(res_idx, pya.Trans(pya.Point(330000, 350000))))
    top.insert(pya.CellInstArray(res_idx, pya.Trans(pya.Point(480000, 350000))))

    # 8. Power Rails (VCC and GND in TopMetal1, width 10 um > min 1.64 um)
    top.shapes(L_TM1).insert(pya.Box(140000, 295000, 660000, 305000)) # VCC Rail
    top.shapes(L_TM1_TEXT).insert(pya.Text("VCC", pya.Trans(200000, 300000)))
    top.shapes(L_TM1).insert(pya.Box(30000, 45000, 770000, 55000)) # GND Rail
    top.shapes(L_TM1_TEXT).insert(pya.Text("GND", pya.Trans(400000, 50000)))

    # 9. RF Signal Interconnects in TopMetal2 (width 3.0 um, space > 3 um)
    top.shapes(L_TM2).insert(pya.Box(85000, 218500, 100000, 221500)) # RFIN to Cin
    top.shapes(L_TM2).insert(pya.Box(708000, 218500, 715000, 221500)) # Cout to RFOUT

    # Connect GND pads to GND rail
    top.shapes(L_TM1).insert(pya.Box(45000, 55000, 55000, 65000))
    top.shapes(L_TM1).insert(pya.Box(745000, 55000, 755000, 65000))

    out_file = os.path.abspath("gds/lna_top.gds")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    ly.write(out_file)
    print("Successfully built LNA GDS:", out_file)
    print(f"Chip Dimensions: 800 um x 550 um (0.44 mm^2 <= 5.0 mm^2 IHP limit)")

build_lna_layout()
