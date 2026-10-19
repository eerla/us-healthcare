"""
Generate CT Provider Funnel Chart
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load funnel data
df = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "ct_provider_funnel.csv")

# Create funnel chart
fig, ax = plt.subplots(figsize=(10, 6))

# Colors for each stage
colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#CCB974']

# Bar width proportional to count
max_count = df['count'].max()
bars = ax.barh(range(len(df)), df['count'], color=colors[:len(df)], edgecolor='white', height=0.6)

# Add labels
for i, (bar, row) in enumerate(zip(bars, df.itertuples())):
    # Stage name on left
    ax.text(-max_count * 0.02, bar.get_y() + bar.get_height()/2,
            row.stage, ha='right', va='center', fontsize=11, fontweight='bold')
    # Count in bar
    ax.text(bar.get_width() + max_count * 0.01, bar.get_y() + bar.get_height()/2,
            f"{row.count:,}", ha='left', va='center', fontsize=11)
    # Percentage of total
    ax.text(max_count * 0.98, bar.get_y() + bar.get_height()/2,
            f"{row.pct_of_total:.1f}%", ha='right', va='center', fontsize=10, color='white', fontweight='bold')

ax.set_xlim(0, max_count * 1.15)
ax.set_ylim(-0.5, len(df) - 0.5)
ax.invert_yaxis()  # Top to bottom
ax.set_xlabel('Count', fontsize=12)
ax.set_title('Healthcare Provider Funnel in Connecticut\n(From Sample NPPES Data)', fontsize=14, fontweight='bold', pad=20)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.get_yaxis().set_ticks([])

# Add methodology note
plt.figtext(0.5, 0.01,
    'Source: NPPES September 2026 V2 (sample 100k rows). '
    'Medicare enrollment and network matching not yet applied (Sprints 2-4).',
    ha='center', fontsize=9, style='italic', color='gray')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'ct_provider_funnel.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"Chart saved to {OUTPUT_DIR / 'ct_provider_funnel.png'}")