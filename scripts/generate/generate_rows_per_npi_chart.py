"""
Generate the "CMS Clinician Rows vs. Unique NPIs" chart.

Shows why COUNT(*) from CMS clinician file ≠ number of doctors.
"""

import duckdb
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Generating CMS Clinician Rows per NPI Chart")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    # Get the data directly from staging
    df = conn.execute("""
        SELECT
            npi_normalized AS npi,
            COUNT(*) AS clinician_rows
        FROM staging.stg_clinician
        GROUP BY npi_normalized
        ORDER BY clinician_rows DESC
    """).df()

    print(f"Total unique NPIs in CMS clinician file: {len(df):,}")
    print(f"Total clinician rows: {df['clinician_rows'].sum():,}")
    print(f"Mean rows per NPI: {df['clinician_rows'].mean():.2f}")
    print(f"Max rows per NPI: {df['clinician_rows'].max():,}")

    # Distribution
    dist = df['clinician_rows'].value_counts().sort_index()
    print("\nDistribution of clinician rows per NPI:")
    for rows, count in dist.items():
        pct = count / len(df) * 100
        print(f"  {rows} row(s): {count:,} NPIs ({pct:.1f}%)")

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Bar chart of distribution (top 10)
    top_dist = dist.head(10)
    ax1.bar(range(len(top_dist)), top_dist.values, color='steelblue', alpha=0.8)
    ax1.set_xticks(range(len(top_dist)))
    ax1.set_xticklabels([f'{int(k)}' for k in top_dist.index])
    ax1.set_xlabel('Clinician Rows per NPI')
    ax1.set_ylabel('Number of NPIs (log scale)')
    ax1.set_yscale('log')
    ax1.set_title('Distribution of Clinician Rows per NPI (Top 10)')
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for i, v in enumerate(top_dist.values):
        ax1.text(i, v * 1.1, f'{v:,}', ha='center', va='bottom', fontsize=9)

    # Right: Cumulative percentage
    df_sorted = df.sort_values('clinician_rows', ascending=False)
    df_sorted['cum_pct'] = df_sorted['clinician_rows'].cumsum() / df_sorted['clinician_rows'].sum() * 100
    df_sorted['npi_cum_pct'] = np.arange(1, len(df_sorted) + 1) / len(df_sorted) * 100

    ax2.plot(df_sorted['npi_cum_pct'], df_sorted['cum_pct'], 'b-', linewidth=2)
    ax2.set_xlabel('Cumulative % of NPIs')
    ax2.set_ylabel('Cumulative % of Clinician Rows')
    ax2.set_title('Lorenz Curve: Concentration of Clinician Rows')
    ax2.grid(alpha=0.3)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)

    # Add reference line (perfect equality)
    ax2.plot([0, 100], [0, 100], 'k--', alpha=0.5, label='Perfect equality')
    ax2.legend()

    plt.suptitle('CMS Clinician Rows vs. Unique NPIs\n"COUNT(*) ≠ Number of Doctors"', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "cms_rows_per_npi.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nChart saved to: {output_path}")

    # Key stats for annotation
    npi_with_1 = (df['clinician_rows'] == 1).sum()
    npi_with_multiple = (df['clinician_rows'] > 1).sum()
    max_rows = df['clinician_rows'].max()
    npi_at_max = (df['clinician_rows'] == max_rows).sum()

    print(f"\nKey stats:")
    print(f"  NPIs with 1 row: {npi_with_1:,} ({npi_with_1/len(df)*100:.1f}%)")
    print(f"  NPIs with multiple rows: {npi_with_multiple:,} ({npi_with_multiple/len(df)*100:.1f}%)")
    print(f"  Max rows per NPI: {max_rows} ({npi_at_max} NPIs)")

    plt.close()
    conn.close()
    print("\nChart generation complete.")


if __name__ == "__main__":
    main()