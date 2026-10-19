"""
Generate Provider Concentration Bar Chart.

Shows top organizations by clinician count and utilization share.
"""

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from matplotlib.patches import Patch

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Generating Provider Concentration Bar Chart")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    query = """
    SELECT
        organization_name,
        state,
        provider_count,
        individual_count,
        org_count,
        total_medicare_services,
        total_medicare_beneficiaries,
        avg_services_per_provider,
        ROUND(total_medicare_services * 100.0 / SUM(total_medicare_services) OVER (), 2) AS pct_of_total_services,
        ROUND(SUM(total_medicare_services) OVER (ORDER BY total_medicare_services DESC) * 100.0 / SUM(total_medicare_services) OVER (), 2) AS cumulative_pct_services,
        provider_concentration_tier,
        utilization_concentration_tier
    FROM mart.mart_provider_concentration
    WHERE provider_count > 0
    ORDER BY provider_count DESC
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} organizations")

    if len(df) == 0:
        print("No data found!")
        return

    # Top 20 by provider count
    top20 = df.head(20).copy()

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))

    # Left: Top 20 by provider count
    top20_sorted = top20.sort_values('provider_count', ascending=True)
    bars1 = ax1.barh(range(len(top20_sorted)), top20_sorted['provider_count'].values,
                      color=top20_sorted['provider_concentration_tier'].map({
                          'Top 1%': '#d62728', 'Top 5%': '#ff7f0e',
                          'Top 10%': '#ffbb78', 'Other': '#1f77b4'
                      }).values, alpha=0.8)

    ax1.set_yticks(range(len(top20_sorted)))
    labels = [f"{row['organization_name'][:35]} ({row['state']})" for _, row in top20_sorted.iterrows()]
    ax1.set_yticklabels(labels, fontsize=9)
    ax1.set_xlabel('Number of Providers')
    ax1.set_title('Top 20 Organizations by Provider Count (Medicare 2023)')
    ax1.grid(axis='x', alpha=0.3)

    # Add tier legend
    legend_elements = [
        Patch(facecolor='#d62728', label='Top 1%'),
        Patch(facecolor='#ff7f0e', label='Top 5%'),
        Patch(facecolor='#ffbb78', label='Top 10%'),
        Patch(facecolor='#1f77b4', label='Other'),
    ]
    ax1.legend(handles=legend_elements, loc='lower right', fontsize=9)

    # Add value labels
    for i in range(len(top20_sorted)):
        row = top20_sorted.iloc[i]
        ax1.text(row['provider_count'] + 5, i, f"{int(row['provider_count']):,}", va='center', fontsize=8)

    # Right: Utilization share by top organizations
    # Sort by Medicare services
    top20_util = top20.sort_values('total_medicare_services', ascending=True)
    bars2 = ax2.barh(range(len(top20_util)), top20_util['total_medicare_services'].values / 1_000_000,
                      color=top20_util['utilization_concentration_tier'].map({
                          'Top 1%': '#d62728', 'Top 5%': '#ff7f0e',
                          'Top 10%': '#ffbb78', 'Other': '#1f77b4'
                      }).values, alpha=0.8)

    ax2.set_yticks(range(len(top20_util)))
    labels2 = [f"{row['organization_name'][:35]} ({row['state']})" for _, row in top20_util.iterrows()]
    ax2.set_yticklabels(labels2, fontsize=9)
    ax2.set_xlabel('Medicare Services (Millions)')
    ax2.set_title('Top 20 Organizations by Medicare Service Volume (2023)')
    ax2.grid(axis='x', alpha=0.3)

    # Add value labels
    for i in range(len(top20_util)):
        row = top20_util.iloc[i]
        if pd.notna(row['total_medicare_services']):
            ax2.text(row['total_medicare_services'] / 1_000_000 + 0.01, i,
                    f"{row['total_medicare_services'] / 1_000_000:.1f}M", va='center', fontsize=8)

    # Legend
    legend_elements2 = [
        Patch(facecolor='#d62728', label='Top 1% by Services'),
        Patch(facecolor='#ff7f0e', label='Top 5% by Services'),
        Patch(facecolor='#ffbb78', label='Top 10% by Services'),
        Patch(facecolor='#1f77b4', label='Other'),
    ]
    ax2.legend(handles=legend_elements2, loc='lower right', fontsize=9)

    plt.suptitle('Healthcare Provider Concentration: Medicare 2023\nTop Organizations by Provider Count & Service Volume', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "provider_concentration.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")

    plt.close()
    conn.close()
    print("\nChart generation complete.")


if __name__ == "__main__":
    import duckdb
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parent
    DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
    OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    main()