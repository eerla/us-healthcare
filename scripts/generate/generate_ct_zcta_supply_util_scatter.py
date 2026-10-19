"""
Generate CT ZCTA Supply vs Utilization Scatter Chart.

Shows providers per 100k vs. services per provider by CT ZCTA (ZIP Code Tabulation Area).
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
    print("Generating CT ZCTA Supply vs Utilization Scatter")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    query = """
    WITH zcta_supply AS (
        SELECT
            ms.geo_id AS zcta,
            ms.provider_count,
            pop.population
        FROM mart.mart_specialty_supply ms
        LEFT JOIN core.fact_population pop
            ON pop.geo_type = 'zcta'
            AND pop.geo_id = ms.geo_id
            AND pop.year = 2023
        WHERE ms.geo_type = 'zcta'
          AND ms.geo_id LIKE '06%'  -- CT ZIP codes start with 06
    ),
    zcta_util AS (
        SELECT
            l.zip5 AS zcta,
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
          AND l.zip5 LIKE '06%'
          AND l.zip5 IS NOT NULL
        GROUP BY l.zip5
    )
    SELECT
        cs.zcta,
        cs.provider_count,
        cs.population,
        ROUND(cs.provider_count * 100000.0 / NULLIF(cs.population, 0), 2) AS providers_per_100k,
        cu.providers_with_util,
        cu.total_services,
        cu.total_beneficiaries,
        cu.avg_services_per_provider,
        cu.services_per_beneficiary
    FROM zcta_supply cs
    LEFT JOIN zcta_util cu
        ON cs.zcta = cu.zcta
    WHERE cs.population > 0
    ORDER BY cs.provider_count DESC
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} CT ZCTAs")

    if len(df) == 0:
        print("No data found!")
        return

    # Filter to ZCTAs with utilization data
    df_util = df[df['avg_services_per_provider'].notna()].copy()
    print(f"ZCTAs with utilization data: {len(df_util)}")

    if len(df_util) == 0:
        print("No utilization data found!")
        return

    # Create scatter plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: Providers per 100k vs Avg Services per Provider
    scatter = ax1.scatter(
        df_util['providers_per_100k'],
        df_util['avg_services_per_provider'],
        c=df_util['population'],
        cmap='viridis',
        s=60,
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5
    )
    ax1.set_xlabel('Providers per 100k Population')
    ax1.set_ylabel('Avg Medicare Services per Provider')
    ax1.set_title('CT ZCTAs: Provider Supply vs. Service Intensity')
    ax1.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('ZCTA Population')

    # Right: Services per Beneficiary vs Providers per 100k
    scatter2 = ax2.scatter(
        df_util['providers_per_100k'],
        df_util['services_per_beneficiary'],
        c=df_util['population'],
        cmap='plasma',
        s=60,
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5
    )
    ax2.set_xlabel('Providers per 100k Population')
    ax2.set_ylabel('Services per Medicare Beneficiary')
    ax2.set_title('CT ZCTAs: Provider Supply vs. Utilization Efficiency')
    ax2.grid(alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label('ZCTA Population')

    plt.suptitle('Connecticut ZCTAs: Provider Supply vs. Medicare Utilization (2023)', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "ct_zcta_supply_util_scatter.png"
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