"""
Generate State Provider Count Chart.

Shows total providers by state (no population normalization).
"""

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Generating State Provider Count Chart")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    query = """
    SELECT
        p.practice_state AS state,
        COUNT(DISTINCT p.provider_sk) AS provider_count
    FROM core.dim_provider p
    WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
      AND p.practice_state IS NOT NULL AND p.practice_state <> ''
    GROUP BY p.practice_state
    ORDER BY provider_count DESC
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} states/regions")

    if len(df) == 0:
        print("No data found!")
        return

    # Create horizontal bar chart - top 30
    df = df.head(30).sort_values('provider_count', ascending=True)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    bars = ax.barh(range(len(df)), df['provider_count'], color='steelblue', alpha=0.7)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['state'], fontsize=9)
    ax.set_xlabel('Number of Providers')
    ax.set_title('Top 30 States/Regions by Provider Count')
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (idx, row) in enumerate(df.iterrows()):
        ax.text(row['provider_count'] + 100, i, f"{row['provider_count']:,}", va='center', fontsize=8)

    plt.suptitle('Top 30 States/Regions by Provider Count', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "state_provider_count.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")

    plt.close()
    conn.close()
    print("\nChart generation complete.")


if __name__ == "__main__":
    import duckdb
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parent
    DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
    OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    main()