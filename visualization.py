"""
Visualization Module for Smart Campus PathFinder.
Generates rich, interactive 2D Campus Graph visual maps using NetworkX and Plotly.
Features category color coding, route highlighting, blocked edge distinction, and hover tooltips.
"""

from typing import List, Dict, Optional, Tuple, Any
import networkx as nx
import plotly.graph_objects as go

from graph import CampusGraph
from config import (
    CATEGORY_COLORS,
    COLOR_DEFAULT_EDGE,
    COLOR_BLOCKED_EDGE,
    COLOR_HIGHLIGHT_PATH
)


def create_campus_figure(
    graph: CampusGraph,
    highlight_path: Optional[List[str]] = None,
    start_node: Optional[str] = None,
    destination_node: Optional[str] = None,
    title: str = "Smart Campus Interactive Navigation Map"
) -> go.Figure:
    """
    Constructs an interactive Plotly figure representing the campus network graph.

    Parameters:
        graph: CampusGraph instance with active nodes and edges.
        highlight_path: Ordered list of location names representing the chosen route.
        start_node: Source location name to emphasize.
        destination_node: Target location name to emphasize.
        title: Title of the chart.

    Returns:
        Plotly Figure object ready for `st.plotly_chart`.
    """
    # 1. Build NetworkX representation for layout
    G = nx.Graph()

    for node_name, meta in graph.nodes.items():
        G.add_node(
            node_name,
            category=meta.get("category", "Academic"),
            x=meta.get("x", 0.0),
            y=meta.get("y", 0.0),
            description=meta.get("description", "")
        )

    all_edges = graph.get_all_edges()
    for edge in all_edges:
        G.add_edge(
            edge["u"],
            edge["v"],
            distance=edge["distance"],
            is_blocked=edge["is_blocked"]
        )

    # 2. Extract or compute positions
    pos = {}
    for node_name, meta in graph.nodes.items():
        pos[node_name] = (meta.get("x", 0.0), meta.get("y", 0.0))

    # If coordinates are all 0, fall back to spring layout
    if all(x == 0.0 and y == 0.0 for x, y in pos.values()) and len(G.nodes) > 0:
        pos = nx.spring_layout(G, seed=42, k=1.5)

    # Convert highlight_path into set of canonical edge pairs
    path_edges = set()
    if highlight_path and len(highlight_path) > 1:
        for i in range(len(highlight_path) - 1):
            u, v = highlight_path[i], highlight_path[i + 1]
            path_edges.add((u, v) if u < v else (v, u))

    fig = go.Figure()

    # -------------------------------------------------------------------------
    # Draw Edges (Available vs Blocked vs Highlighted Route)
    # -------------------------------------------------------------------------

    # Group edges into:
    # a. Normal unblocked edges (not in path)
    # b. Blocked edges
    # c. Highlighted path edges
    normal_x, normal_y, normal_hover = [], [], []
    blocked_x, blocked_y, blocked_hover = [], [], []
    path_x, path_y, path_hover = [], [], []

    # Midpoint distance label coordinates
    mid_x, mid_y, mid_text = [], [], []

    for edge in all_edges:
        u, v = edge["u"], edge["v"]
        dist = edge["distance"]
        is_blocked = edge["is_blocked"]
        canon = (u, v) if u < v else (v, u)

        x0, y0 = pos[u]
        x1, y1 = pos[v]

        # Calculate midpoint for distance label
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        mid_x.append(mx)
        mid_y.append(my)
        mid_text.append(f"{dist:.0f}m")

        if canon in path_edges:
            path_x.extend([x0, x1, None])
            path_y.extend([y0, y1, None])
            path_hover.append(f"Route: {u} ↔ {v} ({dist:.0f}m)")
        elif is_blocked:
            blocked_x.extend([x0, x1, None])
            blocked_y.extend([y0, y1, None])
            blocked_hover.append(f"BLOCKED Pathway: {u} ↔ {v} ({dist:.0f}m)")
        else:
            normal_x.extend([x0, x1, None])
            normal_y.extend([y0, y1, None])
            normal_hover.append(f"Pathway: {u} ↔ {v} ({dist:.0f}m)")

    # 1. Normal Pathways trace
    if normal_x:
        fig.add_trace(go.Scatter(
            x=normal_x,
            y=normal_y,
            line=dict(width=2.5, color=COLOR_DEFAULT_EDGE),
            hoverinfo="none",
            mode="lines",
            name="Available Pathway"
        ))

    # 2. Blocked Pathways trace (Red dashed)
    if blocked_x:
        fig.add_trace(go.Scatter(
            x=blocked_x,
            y=blocked_y,
            line=dict(width=3, color=COLOR_BLOCKED_EDGE, dash="dot"),
            hoverinfo="none",
            mode="lines",
            name="Blocked Pathway"
        ))

    # 3. Highlighted Route trace (Vibrant Green solid)
    if path_x:
        fig.add_trace(go.Scatter(
            x=path_x,
            y=path_y,
            line=dict(width=6, color=COLOR_HIGHLIGHT_PATH),
            hoverinfo="none",
            mode="lines",
            name="Selected Shortest Route"
        ))

    # 4. Midpoint Distance Annotations
    if mid_x:
        fig.add_trace(go.Scatter(
            x=mid_x,
            y=mid_y,
            mode="text",
            text=mid_text,
            textposition="middle center",
            textfont=dict(size=10, color="#546E7A", family="Arial, sans-serif"),
            hoverinfo="text",
            hovertext=[f"Distance: {t}" for t in mid_text],
            showlegend=False
        ))

    # -------------------------------------------------------------------------
    # Draw Nodes (Locations)
    # -------------------------------------------------------------------------
    # Group nodes by category to enable nice legend toggles
    categories = sorted(list({meta.get("category", "Academic") for meta in graph.nodes.values()}))

    for cat in categories:
        cat_nodes = [name for name, meta in graph.nodes.items() if meta.get("category", "Academic") == cat]
        nx_coords = [pos[name][0] for name in cat_nodes]
        ny_coords = [pos[name][1] for name in cat_nodes]
        color = CATEGORY_COLORS.get(cat, "#1E88E5")

        hover_texts = []
        node_sizes = []
        border_widths = []
        border_colors = []

        for name in cat_nodes:
            meta = graph.nodes[name]
            neighbors_count = len(graph.adj.get(name, {}))
            desc = meta.get("description", "No description provided.")

            status_tag = ""
            if name == start_node and name == destination_node:
                status_tag = "<br><b>[START & DESTINATION]</b>"
                node_sizes.append(26)
                border_widths.append(4)
                border_colors.append("#FFD600")
            elif name == start_node:
                status_tag = "<br><b>[START LOCATION]</b>"
                node_sizes.append(24)
                border_widths.append(3.5)
                border_colors.append("#00E676")
            elif name == destination_node:
                status_tag = "<br><b>[DESTINATION LOCATION]</b>"
                node_sizes.append(24)
                border_widths.append(3.5)
                border_colors.append("#FF1744")
            elif highlight_path and name in highlight_path:
                status_tag = "<br><b>[ON ROUTE]</b>"
                node_sizes.append(20)
                border_widths.append(2.5)
                border_colors.append("#00C853")
            else:
                node_sizes.append(18)
                border_widths.append(1.5)
                border_colors.append("#37474F")

            hover_texts.append(
                f"<b>{name}</b>{status_tag}<br>"
                f"<i>Category:</i> {cat}<br>"
                f"<i>Connections:</i> {neighbors_count}<br>"
                f"<i>Details:</i> {desc}"
            )

        fig.add_trace(go.Scatter(
            x=nx_coords,
            y=ny_coords,
            mode="markers+text",
            text=cat_nodes,
            textposition="top center",
            textfont=dict(size=11, color="#263238", family="Arial, sans-serif"),
            hoverinfo="text",
            hovertext=hover_texts,
            marker=dict(
                size=node_sizes,
                color=color,
                line=dict(width=border_widths, color=border_colors),
                symbol="circle"
            ),
            name=f"{cat}"
        ))

    # -------------------------------------------------------------------------
    # Layout & Styling
    # -------------------------------------------------------------------------
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=18, color="#0D47A1")
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#CFD8DC",
            borderwidth=1
        ),
        hovermode="closest",
        margin=dict(b=60, l=40, r=40, t=60),
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            showgrid=True,
            zeroline=False,
            showticklabels=False,
            gridcolor="#ECEFF1"
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=False,
            showticklabels=False,
            gridcolor="#ECEFF1"
        ),
        height=620
    )

    return fig
