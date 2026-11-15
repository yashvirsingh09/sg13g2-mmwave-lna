"""
Generates publication-quality annotated IC floorplan and layout diagram
for the SMACD 2027 IEEE 4-page paper and repository README.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_chip_floorplan():
    fig, ax = plt.subplots(figsize=(8, 6.2))
    
    # Chip Boundary (800 um x 600 um)
    die_rect = patches.Rectangle((0, 0), 800, 600, linewidth=2.5, edgecolor='#1a237e', facecolor='#f5f5f5')
    ax.add_patch(die_rect)
    
    # Guard Ring / Sealring (Substrate/Metal1)
    ring = patches.Rectangle((10, 10), 780, 580, linewidth=1.5, edgecolor='#424242', facecolor='none', linestyle='--')
    ax.add_patch(ring)
    
    # Power Rings (TopMetal1 & TopMetal2)
    vdd_bus = patches.Rectangle((190, 330), 280, 20, linewidth=1.0, edgecolor='#b71c1c', facecolor='#ef9a9a', alpha=0.8)
    vss_bus = patches.Rectangle((190, 90), 280, 20, linewidth=1.0, edgecolor='#0d47a1', facecolor='#90caf9', alpha=0.8)
    ax.add_patch(vdd_bus)
    ax.add_patch(vss_bus)
    ax.text(330, 335, 'VDD Power Bus (TopMetal2, 20 um)', color='#b71c1c', fontweight='bold', fontsize=8.5, ha='center')
    ax.text(330, 95, 'VSS Ground Bus (TopMetal1, 20 um)', color='#0d47a1', fontweight='bold', fontsize=8.5, ha='center')
    
    # Core Circuit Blocks
    # 1. Main TIA Core
    tia_core = patches.Rectangle((230, 180), 90, 80, linewidth=1.8, edgecolor='#004d40', facecolor='#80cbc4', alpha=0.9)
    ax.add_patch(tia_core)
    ax.text(275, 225, 'Main TIA Core\n(npn13G2 HBTs\nRF = 1.25k, CF)', color='#004d40', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # 2. Replica TIA Core
    rep_core = patches.Rectangle((370, 180), 90, 80, linewidth=1.8, edgecolor='#311b92', facecolor='#b39ddb', alpha=0.8)
    ax.add_patch(rep_core)
    ax.text(415, 225, 'Replica TIA\n(Dummy Stage\nBalanced Bias)', color='#311b92', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # 3. DCOC Servo Loop & Large MIM Integrating Capacitor
    dcoc_box = patches.Rectangle((280, 115), 140, 50, linewidth=1.8, edgecolor='#e65100', facecolor='#ffcc80', alpha=0.9)
    ax.add_patch(dcoc_box)
    ax.text(350, 140, 'Active DCOC Servo Loop\n(PMOS OTA & 8-pF MIM Caps)', color='#e65100', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # 4. 50-Ohm CML Output Buffer
    buf_box = patches.Rectangle((290, 270), 110, 50, linewidth=1.8, edgecolor='#880e4f', facecolor='#f48fb1', alpha=0.9)
    ax.add_patch(buf_box)
    ax.text(345, 295, '50-Ohm CML Driver\n(npn13G2, R_L=50 Ohm)', color='#880e4f', fontweight='bold', fontsize=8.5, ha='center', va='center')
    
    # Bondpads (70 um x 70 um)
    pads = [
        # Input GSG Pads (West)
        (60, 80, 'GND (RF)', '#616161'),
        (60, 200, 'IN (Opt)', '#d84315'),
        (60, 320, 'GND (RF)', '#616161'),
        # Output GSG Pads (East)
        (660, 80, 'OUT_N', '#1565c0'),
        (660, 200, 'GND (RF)', '#616161'),
        (660, 320, 'OUT_P', '#1565c0'),
        # Supply Pads (North & South)
        (330, 480, 'VDD (2.5V)', '#c62828'),
        (330, 30, 'VSS (0V)', '#2e7d32')
    ]
    
    for px, py, label, col in pads:
        rect = patches.Rectangle((px - 35, py - 35), 70, 70, linewidth=1.5, edgecolor='#212121', facecolor='#e0e0e0')
        ax.add_patch(rect)
        inner = patches.Rectangle((px - 25, py - 25), 50, 50, linewidth=1.0, edgecolor=col, facecolor='#fff59d')
        ax.add_patch(inner)
        ax.text(px, py, label, color='#212121', fontweight='bold', fontsize=7.5, ha='center', va='center')
        
    # RF Input & Output Interconnect traces
    ax.annotate('', xy=(230, 220), xytext=(95, 200),
                arrowprops=dict(arrowstyle="->", lw=2.2, color='#d84315'))
    ax.annotate('', xy=(625, 320), xytext=(400, 305),
                arrowprops=dict(arrowstyle="->", lw=2.2, color='#1565c0'))
    ax.annotate('', xy=(625, 80), xytext=(400, 285),
                arrowprops=dict(arrowstyle="->", lw=2.2, color='#1565c0'))
                
    # Labels and Dimensions
    ax.text(400, 560, 'IHP SG13G2 130-nm SiGe BiCMOS Tapeout Layout', fontsize=13, fontweight='bold', ha='center', color='#1a237e')
    ax.text(400, 538, 'Die Size: 800 um x 600 um (Area: 0.48 mm^2 < 5 mm^2 limit)', fontsize=10, ha='center', style='italic', color='#424242')
    
    # Scale bar & Grid
    ax.set_xlim([-20, 820])
    ax.set_ylim([-20, 620])
    ax.set_xlabel(r'X Coordinate [$\mu\mathrm{m}$]', fontsize=11, fontweight='bold')
    ax.set_ylabel(r'Y Coordinate [$\mu\mathrm{m}$]', fontsize=11, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    fig.savefig('doc/paper/figures/fig_layout.pdf')
    fig.savefig('doc/paper/figures/fig_layout.png', dpi=300)
    fig.savefig('results/fig_layout.png', dpi=300)
    plt.close()
    print("--> Successfully saved layout floorplan figure: doc/paper/figures/fig_layout.png")

if __name__ == '__main__':
    draw_chip_floorplan()
