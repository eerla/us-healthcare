"""
Generate CT Provider Network Graph (simplified).
"""

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Generating CT Network Graph")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    # Get CT providers with group and facility info - simplified
    query = """
    SELECT
        p.provider_sk,
        p.npi,
        p.entity_type_code,
        p.practice_city,
        bpg.org_pac_id,
        o.legal_business_name AS org_name,
        bpf.facility_sk,
        f.facility_name,
        f.city AS facility_city,
        f.facility_type
    FROM core.dim_provider p
    LEFT JOIN core.bridge_provider_group bpg
        ON p.provider_sk = bpg.provider_sk
    LEFT JOIN core.dim_organization o
        ON bpg.org_pac_id = o.org_pac_id
    LEFT JOIN core.bridge_provider_facility bpf
        ON p.provider_sk = bpf.provider_sk
    LEFT JOIN core.dim_facility f
        ON bpf.facility_sk = f.facility_sk
    WHERE p.practice_state = 'CT'
      AND (p.deactivation_date IS NULL OR p.deactivation_date = '')
    LIMIT 2000
    """

    df = conn.execute(query).df()
    print(f"Retrieved {len(df)} CT provider records")

    if len(df) == 0:
        print("No CT data found!")
        return

    # Build network graph - simplified
    G = nx.Graph()

    # Sample to avoid too many nodes
    df = df.head(500)

    # Add nodes
    for _, row in df.iterrows():
        prov_id = f"P{row['provider_sk']}"
        G.add_node(prov_id, type='provider', npi=row['npi'], city=row['practice_city'])
        
        if pd.notna(row['org_pac_id']):
            org_id = f"O{row['org_pac_id']}"
            org_name = str(row['org_name'])[:30] if pd.notna(row['org_name']) else 'Unknown'
            G.add_node(org_id, type='organization', name=org_name)
            G.add_edge(prov_id, org_id, relation='group')
        
        if pd.notna(row['facility_sk']):
            fac_id = f"F{row['facility_sk']}"
            fac_name = str(row['facility_name'])[:30] if pd.notna(row['facility_name']) else 'Unknown'
            G.add_node(fac_id, type='facility', name=fac_name, city=row['practice_city'])
            G.add_edge(prov_id, fac_id, relation='affiliation')

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    if G.number_of_nodes() == 0:
        print("No graph data!")
        return

    # Layout - use simpler layout
    pos = nx.spring_layout(G, k=0.8, iterations=20, seed=42)

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    # Node colors by type
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'unknown')
        if node_type == 'provider':
            node_colors.append('#1f77b4')
            node_sizes.append(40)
        elif node_type == 'organization':
            node_colors.append('#ff7f0e')
            node_sizes.append(120)
        elif node_type == 'facility':
            node_colors.append('#2ca02c')
            node_sizes.append(120)
        else:
            node_colors.append('#d62728')
            node_sizes.append(30)

    edge_colors = []
    for u, v, data in G.edges(data=True):
        if data.get('relation') == 'group':
            edge_colors.append('#1f77b4')
        elif data.get('relation') == 'affiliation':
            edge_colors.append('#2ca02c')
        else:
            edge_colors.append('#999999')

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.7, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.3, width=0.5, ax=ax)

    # Labels for organizations and facilities
    labels = {}
    for node in G.nodes():
        node_type = G.nodes[node].get('type', '')
        if node_type == 'organization':
            labels[node] = G.nodes[node].get('name', '')[:25]
        elif node_type == 'facility':
            labels[node] = G.nodes[node].get('name', '')[:25]

    nx.draw_networkx_labels(G, pos, labels, font_size=7, font_weight='bold', ax=ax)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#1f77b4', label='Provider'),
        Patch(facecolor='#ff7f0e', label='Organization/Group'),
        Patch(facecolor='#2ca02c', label='Facility/Hospital'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

    ax.set_title('Connecticut Provider Network: Provider → Group → Facility\n(Hartford / New Haven Metro Areas - Sample)', fontsize=13, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()
    output_path = OUTPUT_DIR / "ct_provider_network.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")

    plt.close()
    conn.close()
    print("\nNetwork graph generation complete.")


if __name__ == "__main__":
    main()