"""
Generate CT Supply vs Utilization Scatter Chart.

Shows providers per 100k vs. services per provider by CT county.
"""

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Generating CT Supply vs Utilization Scatter")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    query = """
    WITH county_supply AS (
        SELECT
            fips.county_fips AS county_fips,
            'Connecticut' AS state,
            fips.county_name_clean AS county,
            fips.county_name AS county_name,
            SUM(ms.provider_count) AS total_providers,
            SUM(fips.total_population) AS total_population,
            ROUND(SUM(ms.provider_count) * 100000.0 / SUM(fips.total_population), 2) AS providers_per_100k
        FROM mart.mart_specialty_supply ms
        JOIN staging.stg_population_county fips
            ON ms.geo_id = fips.county_fips
        WHERE ms.geo_type = 'county' AND fips.state_name = 'Connecticut'
        GROUP BY fips.county_fips, fips.county_name_clean, fips.county_name
    ),
    county_util AS (
        SELECT
            l.state || l.county_fips AS county_fips,
            COUNT(DISTINCT fu.provider_sk) AS providers_with_util,
            SUM(CAST(fu.total_services AS BIGINT)) AS total_services,
            SUM(CAST(fu.total_beneficiaries AS BIGINT)) AS total_beneficiaries,
            AVG(CAST(fu.total_services AS DOUBLE)) AS avg_services_per_provider,
            SUM(CAST(fu.total_services AS DOUBLE)) * 1.0 / NULLIF(SUM(CAST(fu.total_beneficiaries AS DOUBLE)), 0) AS services_per_beneficiary
        FROM core.fact_provider_utilization fu
        JOIN core.dim_provider p ON fu.provider_sk = p.provider_sk
        JOIN core.bridge_provider_location bpl ON p.provider_sk = bpl.provider_sk
        JOIN core.dim_location l ON bpl.location_sk = l.location_sk
        WHERE fu.year = 2023
          AND l.state = 'CT'
          AND l.county_fips IS NOT NULL
        GROUP BY l.state || l.county_fips
    )
    SELECT
        cs.county_fips,
        'Connecticut' AS state,
        cs.county,
        cs.county_name,
        cs.total_providers,
        cs.total_population,
        cs.providers_per_100k,
        cu.providers_with_util,
        cu.total_services,
        cu.total_beneficiaries,
        cu.avg_services_per_provider,
        cu.services_per_beneficiary
    FROM county_supply cs
    LEFT JOIN county_util cu
        ON cs.county_fips = cu.county_fips
    WHERE cs.total_population > 0
    ORDER BY cs.providers_per_100k DESC
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} CT counties")

    if len(df) == 0:
        print("No data found!")
        return

    # Filter to counties with utilization data
    df_util = df[df['avg_services_per_provider'].notna()].copy()
    print(f"Counties with utilization data: {len(df_util)}")

    if len(df_util) == 0:
        print("No utilization data found!")
        return

    # Create scatter plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: Providers per 100k vs Avg Services per Provider
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df_util)))
    scatter = ax1.scatter(
        df_util['providers_per_100k'],
        df_util['avg_services_per_provider'],
        c=df_util['total_population'],
        cmap='viridis',
        s=80,
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5
    )
    ax1.set_xlabel('Providers per 100k Population')
    ax1.set_ylabel('Avg Medicare Services per Provider')
    ax1.set_title('CT Counties: Provider Supply vs. Service Intensity')
    ax1.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('County Population')

    # Add county labels for outliers
    for _, row in df_util.iterrows():
        ax1.annotate(row['county_name'][:8], (row['providers_per_100k'], row['avg_services_per_provider']),
                    fontsize=7, ha='center', va='bottom')

    # Right: Services per Beneficiary vs Providers per 100k
    scatter2 = ax2.scatter(
        df_util['providers_per_100k'],
        df_util['services_per_beneficiary'],
        c=df_util['total_population'],
        cmap='plasma',
        s=80,
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5
    )
    ax2.set_xlabel('Providers per 100k Population')
    ax2.set_ylabel('Services per Medicare Beneficiary')
    ax2.set_title('CT Counties: Provider Supply vs. Utilization Efficiency')
    ax2.grid(alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label('County Population')

    for _, row in df_util.iterrows():
        ax2.annotate(row['county_name'][:8], (row['providers_per_100k'], row['services_per_beneficiary']),
                    fontsize=7, ha='center', va='bottom')

    plt.suptitle('Connecticut: Provider Supply vs. Medicare Utilization (2023)', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "ct_supply_util_scatter.png"
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
    import numpy as np
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parent
    DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
    OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    main()