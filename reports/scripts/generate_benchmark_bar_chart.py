import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs(r"results\benchmarks", exist_ok=True)

def generate_benchmark_bar_chart():
    models = ["Linear Regression", "Random Forest", "XGBoost", "LightGBM (Ours)"]
    mae_cycles = [152.9, 80.2, 82.5, 79.9]
    r2_accuracy = [56.1, 79.2, 80.3, 81.6]

    x = np.arange(len(models))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 5.8), dpi=300)

    # Left Axis: Mean Absolute Error (Cycles) -> Uniform Deep Slate Blue (#2980B9)
    color_mae = '#2980B9'
    rects1 = ax1.bar(x - width/2, mae_cycles, width, label='Mean Absolute Error (Cycles)', color=color_mae, alpha=0.9, edgecolor='white', linewidth=1.2)
    ax1.set_ylabel('Mean Absolute Error (Cycles)', fontsize=12, fontweight='bold', color=color_mae)
    ax1.tick_params(axis='y', labelcolor=color_mae, labelsize=11)
    ax1.set_ylim(0, 175)

    # Right Axis: R2 Accuracy Score (%) -> Uniform Purple (#8E44AD)
    ax2 = ax1.twinx()
    color_r2 = '#8E44AD'
    rects2 = ax2.bar(x + width/2, r2_accuracy, width, label='R2 Accuracy Score (%)', color=color_r2, alpha=0.9, edgecolor='white', linewidth=1.2)
    ax2.set_ylabel('R2 Accuracy Score (%)', fontsize=12, fontweight='bold', color=color_r2)
    ax2.tick_params(axis='y', labelcolor=color_r2, labelsize=11)
    ax2.set_ylim(0, 110)

    # X Axis
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=11, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    # Value labels on top of bars
    for rect in rects1:
        height = rect.get_height()
        ax1.annotate(f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 4),  # 4 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color='#1A5276')

    for rect in rects2:
        height = rect.get_height()
        ax2.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 4),  # 4 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color='#5B2C6F')

    plt.title("Empirical Benchmark: LightGBM vs Linear Regression, Random Forest & XGBoost", fontsize=13, fontweight='bold', pad=15)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 0.96), ncol=2, fontsize=10, framealpha=0.95)

    plt.tight_layout()
    out_path = r"results\benchmarks\model_comparison_bar_chart.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved clean model_comparison_bar_chart.png with correct model order!")

if __name__ == "__main__":
    generate_benchmark_bar_chart()
