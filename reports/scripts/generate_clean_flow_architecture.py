import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_professional_flow():
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    fig, ax = plt.subplots(figsize=(10, 9.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    box_ec = '#1A1A1A'
    bg_main = '#FFFFFF'
    bg_sub = '#F8F9FA'
    bg_highlight = '#EFEFEF'
    
    def draw_box(x, y_center, width, height, title, subtitle_list, bg_color=bg_main, lw=1.5):
        # Draw box from (x - width/2, y_center - height/2) to (x + width/2, y_center + height/2)
        rect = patches.FancyBboxPatch(
            (x - width/2, y_center - height/2), width, height,
            boxstyle="round,pad=0.5,rounding_size=1.5",
            edgecolor=box_ec, facecolor=bg_color, linewidth=lw
        )
        ax.add_patch(rect)
        
        # Top of box is y_center + height/2
        top_y = y_center + height/2
        
        # Title
        ax.text(x, top_y - 3.5, title, ha='center', va='top', 
                fontsize=11.5, fontweight='bold', color='#000000')
        
        # Divider line under title
        ax.plot([x - width/2 + 4, x + width/2 - 4], 
                [top_y - 6.5, top_y - 6.5], 
                color='#777777', linewidth=0.8)
        
        # Subtitle items starting below divider line
        start_y = top_y - 9.5
        for i, text in enumerate(subtitle_list):
            ax.text(x, start_y - i*5.5, text, ha='center', va='top', 
                    fontsize=9.5, color='#222222')

    # 1. Top Block: center y=88, height=18 -> top_y=97, bottom_y=79
    draw_box(50, 88, 70, 18, 
             "124 Total Physical LFP Batteries (Stanford / MIT / TRI)", 
             ["Nominal Capacity: 1.1 Ah | Fast-Charging Protocols: 1C to 6C",
              "Leakage-Free GroupShuffleSplit at Physical Cell Level"])
    
    # Arrows from Top Block (y=79) to Middle Blocks (y=66)
    ax.annotate("", xy=(26, 66), xytext=(40, 78),
                arrowprops=dict(arrowstyle="->", lw=1.5, color=box_ec, connectionstyle="arc3,rad=0.05"))
    ax.annotate("", xy=(74, 66), xytext=(60, 78),
                arrowprops=dict(arrowstyle="->", lw=1.5, color=box_ec, connectionstyle="arc3,rad=-0.05"))
    
    # Split annotations
    ax.text(28, 73, "80.6% Split", ha='center', va='center', fontsize=9.5, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', pad=1))
    ax.text(72, 73, "19.4% Split", ha='center', va='center', fontsize=9.5, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', pad=1))

    # 2. Left Block: Training Vault center y=54, height=24 -> top_y=66, bottom_y=42
    draw_box(26, 54, 44, 24, 
             "Training Vault (100 Cells)", 
             ["100 Commercial LFP Batteries",
              "18,240 Operational Checkpoints"], bg_color=bg_sub)

    # 3. Right Block: Testing Vault center y=54, height=24 -> top_y=66, bottom_y=42
    draw_box(74, 54, 44, 24, 
             "Testing Vault (24 Cells)", 
             ["24 Unseen Test Batteries",
              "4,234 Operational Checkpoints"], bg_color=bg_sub)

    # Arrow ONLY from Right Block (Testing Vault, y=42) to Bottom Block (y=30)
    ax.annotate("", xy=(62, 30), xytext=(74, 41),
                arrowprops=dict(arrowstyle="->", lw=1.5, color=box_ec, connectionstyle="arc3,rad=0.1"))

    # 4. Bottom Block: Conformal Prediction center y=19, height=22 -> top_y=30, bottom_y=8
    draw_box(50, 19, 74, 22, 
             "Split-Conformal Prediction Safety Brackets", 
             ["Calibrated from Strictly Unseen Out-of-Sample Data",
              "90% Safety Bracket: Maximum Error Bounded within ±122 Cycles"], bg_color=bg_highlight)

    plt.tight_layout()
    output_path = r"reports\figures\flow_architecture.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Flawless monochrome flow chart generated.")

if __name__ == "__main__":
    generate_professional_flow()

