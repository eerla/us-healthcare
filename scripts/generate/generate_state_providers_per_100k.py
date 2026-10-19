"""
Generate State Providers per 100k Chart.

Shows total providers per 100k population by state.
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
    print("Generating State Providers per 100k Chart")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))
    conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw")
    conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw")
    conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw")
    conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw")
    conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw")

    query = """
    WITH state_providers AS (
        SELECT 
            CASE p.practice_state
                WHEN 'AL' THEN 'Alabama' WHEN 'AK' THEN 'Alaska' WHEN 'AZ' THEN 'Arizona'
                WHEN 'AR' THEN 'Arkansas' WHEN 'CA' THEN 'California' WHEN 'CO' THEN 'Colorado'
                WHEN 'CT' THEN 'Connecticut' WHEN 'DE' THEN 'Delaware' WHEN 'DC' THEN 'District of Columbia'
                WHEN 'FL' THEN 'Florida' WHEN 'GA' THEN 'Georgia' WHEN 'HI' THEN 'Hawaii'
                WHEN 'ID' THEN 'Idaho' WHEN 'IL' THEN 'Illinois' WHEN 'IN' THEN 'Indiana'
                WHEN 'IA' THEN 'Iowa' WHEN 'KS' THEN 'Kansas' WHEN 'KY' THEN 'Kentucky'
                WHEN 'LA' THEN 'Louisiana' WHEN 'ME' THEN 'Maine' WHEN 'MD' THEN 'Maryland'
                WHEN 'MA' THEN 'Massachusetts' WHEN 'MI' THEN 'Michigan' WHEN 'MN' THEN 'Minnesota'
                WHEN 'MS' THEN 'Mississippi' WHEN 'MO' THEN 'Missouri' WHEN 'MT' THEN 'Montana'
                WHEN 'NE' THEN 'Nebraska' WHEN 'NV' THEN 'Nevada' WHEN 'NH' THEN 'New Hampshire'
                WHEN 'NJ' THEN 'New Jersey' WHEN 'NM' THEN 'New Mexico' WHEN 'NY' THEN 'New York'
                WHEN 'NC' THEN 'North Carolina' WHEN 'ND' THEN 'North Dakota' WHEN 'OH' THEN 'Ohio'
                WHEN 'OK' THEN 'Oklahoma' WHEN 'OR' THEN 'Oregon' WHEN 'PA' THEN 'Pennsylvania'
                WHEN 'RI' THEN 'Rhode Island' WHEN 'SC' THEN 'South Carolina' WHEN 'SD' THEN 'South Dakota'
                WHEN 'TN' THEN 'Tennessee' WHEN 'TX' THEN 'Texas' WHEN 'UT' THEN 'Utah'
                WHEN 'VT' THEN 'Vermont' WHEN 'VA' THEN 'Virginia' WHEN 'WA' THEN 'Washington'
                WHEN 'WV' THEN 'West Virginia' WHEN 'WI' THEN 'Wisconsin' WHEN 'WY' THEN 'Wyoming'
                ELSE p.practice_state
            END AS state_name,
            COUNT(DISTINCT p.provider_sk) AS provider_count
        FROM core.dim_provider p
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND p.practice_state IS NOT NULL AND p.practice_state <> ''
        GROUP BY p.practice_state
    ),
    state_pop AS (
        SELECT state_name AS state, SUM(total_population) AS total_population
        FROM staging.stg_population_county
        GROUP BY state_name
    )
    SELECT sp.state_name AS state, sp.provider_count, pop.total_population,
           ROUND(sp.provider_count * 100000.0 / pop.total_population, 2) AS providers_per_100k
    FROM state_providers sp
    JOIN state_pop pop ON sp.state_name = pop.state
    WHERE pop.total_population > 0
    ORDER BY providers_per_100k DESC
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} states")

    if len(df) == 0:
        print("No data found!")
        return

    # Create horizontal bar chart - top 30
    df = df.head(30).sort_values('providers_per_100k', ascending=True)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    bars = ax.barh(range(len(df)), df['providers_per_100k'], color='steelblue', alpha=0.7)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['state'], fontsize=9)
    ax.set_xlabel('Providers per 100k Population')
    ax.set_title('Top 30 States: Providers per 100,000 Population')
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (idx, row) in enumerate(df.iterrows()):
        ax.text(row['providers_per_100k'] + 0.1, i, f"{row['providers_per_100k']:.1f}", va='center', fontsize=8)

    plt.suptitle('Providers per 100,000 Population by State', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "state_providers_per_100k.png"
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