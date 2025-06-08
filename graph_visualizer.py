from pyvis.network import Network
import webbrowser

# --- Colors for different entity types
type_colors = {
    "Person": "#FF6961",              # red
    "Scientific Theory": "#779ECB",   # blue
    "Concept": "#77DD77",             # green
    "Location": "#FFD700",            # yellow
    "Organization": "#FFB347",        # orange
    "Unknown": "#D3D3D3"              # grey fallback
}

def build_and_open_graph(triplets):
    # net = Network(height="750px", width="100%", directed=True, notebook=False)
    
    # for i in range(0, len(triplets), 3):
    #     print(triplets[i])
    #     try:
    #         node1 = triplets[i][0]
    #         edge = triplets[i][1]
    #         node2 = triplets[i][2]

    #         # Get node info
    #         source = node1.name
    #         source_type = node1.label
    #         source_desc = node1.properties.get("entity_description", "")

    #         target = node2.name or node2.properties.get("id") or "Unknown"
    #         target_type = node2.label or "Unknown"
    #         target_desc = node2.properties.get("entity_description", "")

    #         relation = edge.label or "related_to"
    #         relation_desc = edge.properties.get("relation_description", "")

    #         # Add source node
    #         net.add_node(
    #             source,
    #             label=source,
    #             title=f"{source_type}: {source_desc}",
    #             color=type_colors.get(source_type, type_colors["Unknown"])
    #         )

    #         # Add target node
    #         net.add_node(
    #             target,
    #             label=target,
    #             title=f"{target_type}: {target_desc}",
    #             color=type_colors.get(target_type, type_colors["Unknown"])
    #         )

    #         # Add edge with tooltip
    #         net.add_edge(
    #             source,
    #             target,
    #             label=relation,
    #             title=relation_desc
    #         )
    #     except Exception as e:
    #         print(f"Skipping triplet group {i}-{i+2}: {e}")
    #         continue

    # net.repulsion()
    output_path = "graph.html"
    # net.save_graph(output_path)
    with open(output_path, "r", encoding="utf-8") as f:
        return f.read()