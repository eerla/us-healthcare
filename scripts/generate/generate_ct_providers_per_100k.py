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
    print("Generating CT Provider Count by County Chart")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    query = """
    WITH ct_providers AS (
        SELECT
            l.county_fips AS county,
            'CT' AS state,
            COUNT(DISTINCT p.provider_sk) AS provider_count
        FROM core.dim_provider p
        JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        JOIN core.dim_location l
            ON bpl.location_sk = l.location_sk
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND l.state = 'CT'
          AND l.county_fips IS NOT NULL
        GROUP BY l.county_fips, l.state
    ),
    county_pop AS (
        SELECT
            county_fips AS county,
            'CT' AS state,
            SUM(total_population) AS total_population
        FROM staging.stg_population_county
        WHERE state_name = 'Connecticut'
        GROUP BY county_fips
    )
    SELECT
        cp.county,
        cp.state,
        cp.provider_count,
        pop.total_population,
        ROUND(cp.provider_count * 100000.0 / pop.total_population, 2) AS providers_per_100k
    FROM ct_providers cp
    JOIN county_pop pop
        ON cp.county = pop.county AND cp.state = pop.state
    WHERE pop.total_population > 0
    ORDER BY providers_per_100k DESC
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} CT counties")

    if len(df) == 0:
        print("No data found!")
        return

    # Create horizontal bar chart
    fig, ax = plt.subplots(1, 1, figsize=(10, 12))

    df = df.sort_values('providers_per_100k', ascending=True)

    bars = ax.barh(range(len(df)), df['providers_per_100k'], color='steelblue', alpha=0.7)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['county'], fontsize=8)
    ax.set_xlabel('Providers per 100k Population')
    ax.set_title('Connecticut Providers per 100,000 Population by County')
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (idx, row) in enumerate(df.iterrows()):
        ax.text(row['providers_per_100k'] + 0.1, i, f"{row['providers_per_100k']:.1f}", va='center', fontsize=7)

    plt.suptitle('Connecticut Providers per 100,000 Population by County', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "ct_providers_per_100k.png"
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