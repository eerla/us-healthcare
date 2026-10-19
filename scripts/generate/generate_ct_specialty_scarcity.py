"""
Generate CT Specialty Scarcity Map.

Shows primary care, cardiology, dermatology, psychiatry, orthopedics providers per 100k by CT county.
"""

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SPECIALTIES = [
    ('Primary Care', 'Primary Care'),
    ('Cardiology', 'Cardiovascular Disease'),
    ('Dermatology', 'Dermatology'),
    ('Psychiatry', 'Psychiatry'),
    ('Orthopedics', 'Orthopedic Surgery'),
]

def main():
    print("=" * 60)
    print("Generating CT Specialty Scarcity Map")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    # Get CT county boundaries (use Census TIGER/Line if available, or approximate)
    # For now, use county centroids from Census population data
    query = """
    WITH ct_providers AS (
        SELECT
            l.county_fips AS county,
            l.state,
            s.specialty_group,
            COUNT(DISTINCT p.provider_sk) AS provider_count
        FROM core.dim_provider p
        JOIN core.dim_specialty s
            ON p.primary_taxonomy_code = s.taxonomy_code
        JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        JOIN core.dim_location l
            ON bpl.location_sk = l.location_sk
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND l.state = 'CT'
          AND l.county_fips IS NOT NULL
        GROUP BY l.county_fips, l.state, s.specialty_group
    ),
    county_pop AS (
        SELECT
            county_fips AS county,
            state_name AS state,
            SUM(total_population) AS total_population
        FROM staging.stg_population_county
        WHERE state_name = 'CT'
        GROUP BY county_fips, state_name
    )
    SELECT
        cp.county,
        cp.state,
        cp.specialty_group,
        cp.provider_count,
        pop.total_population,
        ROUND(cp.provider_count * 100000.0 / pop.total_population, 2) AS providers_per_100k
    FROM ct_providers cp
    JOIN county_pop pop
        ON cp.county = pop.county AND cp.state = pop.state
    WHERE pop.total_population > 0
    ORDER BY cp.county, cp.specialty_group
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} county-specialty combinations")

    if len(df) == 0:
        print("No data found!")
        return

    # Create subplot for each specialty
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    ct_counties = df['county'].unique()
    print(f"CT counties with data: {len(ct_counties)}")

    for idx, (specialty_label, specialty_group) in enumerate(SPECIALTIES):
        ax = axes[idx]
        spec_data = df[df['specialty_group'] == specialty_group].copy()

        if len(spec_data) == 0:
            ax.text(0.5, 0.5, f'No data for {specialty_label}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'{specialty_label} (No Data)')
            continue

        # Sort by providers per 100k
        spec_data = spec_data.sort_values('providers_per_100k', ascending=True)

        bars = ax.barh(range(len(spec_data)), spec_data['providers_per_100k'], color='steelblue', alpha=0.7)
        ax.set_yticks(range(len(spec_data)))
        ax.set_yticklabels(spec_data['county'], fontsize=8)
        ax.set_xlabel('Providers per 100k Population')
        ax.set_title(f'{specialty_label} Providers per 100k (CT Counties)')
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (idx, row) in enumerate(spec_data.iterrows()):
            ax.text(row['providers_per_100k'] + 0.1, i, f"{row['providers_per_100k']:.1f}", va='center', fontsize=7)

    # Remove empty subplot
    axes[-1].axis('off')

    plt.suptitle('Connecticut Specialty Provider Scarcity Map\nProviders per 100,000 Population by County', fontsize=16, fontweight='bold')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "ct_specialty_scarcity.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")

    plt.close()
    conn.close()
    print("\nChart generation complete.")


if __name__ == "__main__":
    main()