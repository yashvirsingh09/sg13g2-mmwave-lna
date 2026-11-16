"""
Generates publication-quality annotated IC floorplan and layout diagram
for the 24-28 GHz mmWave SiGe-BiCMOS LNA.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_lna_floorplan():
    fig, ax = plt.subplots(figsize=(8.2, 5.8))
    
    # Chip Boundary (700 um x 500 um)
    die_rect = patches.Rectangle((0, 0), 700, 500, linewidth=2.5, edgecolor='#0d47a1', facecolor='#fafafa')
    ax.add_patch(die_rect)
    
    # Perimeter Guard Ring
    ring = patches.Rectangle((8, 8), 684, 484, linewidth=1.5, edgecolor='#424242', facecolor='none', linestyle='--')
    ax.add_patch(ring)
    
    # Power Buses (TopMetal1 & TopMetal2)
    vcc_bus = patches.Rectangle((140, 415), 420, 20, linewidth=1.0, edgecolor='#b71c1c', facecolor='#ef9a9a', alpha=0.85)
    gnd_bus = patches.Rectangle((140, 65), 420, 25, linewidth=1.0, edgecolor='#0d47a1', facecolor='#90caf9', alpha=0.85)
    ax.add_patch(vcc_bus)
    ax.add_patch(gnd_bus)
    ax.text(350, 422, 'VCC Power Bus (TopMetal2, 20 um, 1.8V)', color='#b71c1c', fontweight='bold', fontsize=8.5, ha='center')
    ax.text(350, 74, 'GND Return Plane (TopMetal1, 25 um)', color='#0d47a1', fontweight='bold', fontsize=8.5, ha='center')
    
    # Circuit Blocks
    # 1. Base Matching Spiral Inductor Lg1 (544 pH)
    ind1 = patches.Circle((180, 210), 38, linewidth=1.8, edgecolor='#e65100', facecolor='#ffe0b2')
    ax.add_patch(ind1)
    ax.text(180, 210, 'L_g1\n(544 pH)', color='#e65100', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # 2. Stage 1 Cascode Core (Q1, Q2, Le1)
    stg1 = patches.Rectangle((230, 220), 65, 75, linewidth=1.8, edgecolor='#004d40', facecolor='#80cbc4')
    ax.add_patch(stg1)
    ax.text(262, 257, 'Stage 1 Core\n(npn13G2 CE/CB\nL_e1 = 22 pH)', color='#004d40', fontweight='bold', fontsize=8.0, ha='center', va='center')
    
    # 3. Interstage Matching Spiral Inductor Lint (397 pH)
    ind2 = patches.Circle((340, 280), 32, linewidth=1.8, edgecolor='#e65100', facecolor='#ffe0b2')
    ax.add_patch(ind2)
    ax.text(340, 280, 'L_int\n(397 pH)', color='#e65100', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # 4. Stage 2 Cascode Core (Q3, Q4, Le2)
    stg2 = patches.Rectangle((400, 220), 65, 75, linewidth=1.8, edgecolor='#4a148c', facecolor='#ce93d8')
    ax.add_patch(stg2)
    ax.text(432, 257, 'Stage 2 Core\n(npn13G2 CE/CB\nNx = 3)', color='#4a148c', fontweight='bold', fontsize=8.0, ha='center', va='center')
    
    # 5. Output Load Inductor Ld2 (350 pH)
    ind3 = patches.Circle((520, 210), 30, linewidth=1.8, edgecolor='#e65100', facecolor='#ffe0b2')
    ax.add_patch(ind3)
    ax.text(520, 210, 'L_d2\n(350 pH)', color='#e65100', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # 6. Bias Generator & Decoupling
    bias_box = patches.Rectangle((280, 110), 140, 45, linewidth=1.5, edgecolor='#37474f', facecolor='#cfd8dc')
    ax.add_patch(bias_box)
    ax.text(350, 132, 'Bias Mirror & Decoupling\n(rhigh, cap_cmim 40 um)', color='#263238', fontweight='bold', fontsize=8.0, ha='center', va='center')
    
    # RF GSG Probe Pads
    pads = [
        # West: Input GSG
        (60, 130, 'GND (RF)', '#616161'),
        (60, 250, 'RF_IN', '#d84315'),
        (60, 370, 'GND (RF)', '#616161'),
        # East: Output GSG
        (640, 130, 'GND (RF)', '#616161'),
        (640, 250, 'RF_OUT', '#1565c0'),
        (640, 370, 'GND (RF)', '#616161'),
        # North & South DC
        (350, 450, 'VCC (1.8V)', '#c62828'),
        (350, 50, 'GND (DC)', '#2e7d32')
    ]
    
    for px, py, label, col in pads:
        rect = patches.Rectangle((px - 30, py - 30), 60, 60, linewidth=1.5, edgecolor='#212121', facecolor='#e0e0e0')
        ax.add_patch(rect)
        inner = patches.Rectangle((px - 20, py - 20), 40, 40, linewidth=1.0, edgecolor=col, facecolor='#fff59d')
        ax.add_patch(inner)
        ax.text(px, py, label, color='#212121', fontweight='bold', fontsize=7.0, ha='center', va='center')
        
    # RF Signal Arrows
    ax.annotate('', xy=(142, 220), xytext=(90, 250),
                arrowprops=dict(arrowstyle="->", lw=2.2, color='#d84315'))
    ax.annotate('', xy=(610, 250), xytext=(550, 220),
                arrowprops=dict(arrowstyle="->", lw=2.2, color='#1565c0'))
                
    # Labels & Scale
    ax.text(350, 475, 'IHP SG13G2 24-28 GHz mmWave LNA Physical Mask Layout', fontsize=12, fontweight='bold', ha='center', color='#0d47a1')
    ax.text(350, 20, 'Die Dimensions: 700 um x 500 um (Area: 0.35 mm^2 <= 5 mm^2 limit)', fontsize=9.5, ha='center', style='italic', color='#424242')
    
    ax.set_xlim([-10, 710])
    ax.set_ylim([-10, 510])
    ax.set_xlabel(r'X Coordinate [$\mu\mathrm{m}$]', fontsize=10.5, fontweight='bold')
    ax.set_ylabel(r'Y Coordinate [$\mu\mathrm{m}$]', fontsize=10.5, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    fig.savefig('results/fig_lna_layout.png', dpi=300)
    plt.close()
    print("--> Successfully generated layout floorplan plot: results/fig_lna_layout.png")

if __name__ == '__main__':
    draw_lna_floorplan()
