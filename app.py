"""
Streamlit Web Application: Smart Campus PathFinder
Intelligent Campus Navigation System Using Data Structures and Algorithms (DSA)
"""

import streamlit as st
import pandas as pd
from typing import List, Optional

from campus_service import CampusService
from visualization import create_campus_figure
from config import (
    LOCATION_CATEGORIES,
    DEFAULT_WALKING_SPEED_M_PER_MIN
)

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Campus PathFinder | DSA Navigation",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean blue-and-white college project theme
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, #0D47A1 0%, #1976D2 50%, #0288D1 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(13, 71, 161, 0.15);
    }
    .header-box h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .header-box p {
        color: #E3F2FD !important;
        margin: 6px 0 0 0;
        font-size: 15px;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 5px solid #1976D2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-card-title {
        color: #546E7A;
        font-size: 13px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-card-value {
        color: #0D47A1;
        font-size: 26px;
        font-weight: 700;
    }
    .metric-card-sub {
        color: #78909C;
        font-size: 12px;
    }

    /* Step-by-step card */
    .step-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 8px;
        border-left: 4px solid #00C853;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }

    /* Breadcrumbs ribbon */
    .route-ribbon {
        background: #E8F5E9;
        color: #1B5E20;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        border: 1px solid #C8E6C9;
        margin-bottom: 16px;
    }

    /* Subtle footer */
    .footer-text {
        text-align: center;
        color: #90A4AE;
        font-size: 13px;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid #ECEFF1;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Initialize Service & Session State
# -----------------------------------------------------------------------------
@st.cache_resource
def get_campus_service() -> CampusService:
    """Returns singleton CampusService instance connected to default SQLite DB."""
    return CampusService()

service = get_campus_service()

# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/marker.png", width=64)
st.sidebar.title("Navigation Menu")
st.sidebar.caption("Intelligent Campus Routing System")

menu = st.sidebar.radio(
    "Select System Module:",
    [
        "📊 Dashboard",
        "🧭 Find Shortest Route",
        "🗺️ Interactive Campus Map",
        "⚡ Compare Algorithms (Dijkstra vs BFS)",
        "🏢 Manage Locations",
        "🔗 Manage Connections",
        "🚧 Blocked Paths & Detours",
        "📜 Route Search History",
        "📚 About the Project & DSA"
    ],
    index=0
)

st.sidebar.divider()

# Quick summary in sidebar
stats = service.graph.get_summary_stats()
st.sidebar.markdown(f"""
**Campus Graph Summary:**
- 🏛️ Locations: **{stats['total_nodes']}**
- 🛤️ Total Pathways: **{stats['total_edges']}**
- ⛔ Blocked Pathways: **{stats['blocked_edges']}**
""")

if st.sidebar.button("🔄 Reload / Refresh Graph"):
    service.load_graph_from_db()
    st.sidebar.success("Graph refreshed from database!")

# -----------------------------------------------------------------------------
# Top Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <h1>Smart Campus PathFinder</h1>
    <p>Intelligent Walking Route Optimization Using Dijkstra's Algorithm, BFS, and Weighted Graphs</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MODULE 1: DASHBOARD
# =============================================================================
if menu == "📊 Dashboard":
    st.subheader("Campus Network Overview & Real-Time Telemetry")
    st.write("Welcome to the Smart Campus PathFinder control center. View active campus nodes, connection integrity, and navigation analytics.")

    dash_summary = service.get_dashboard_summary()

    # Metric Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Campus Locations</div>
            <div class="metric-card-value">{dash_summary['total_locations']}</div>
            <div class="metric-card-sub">Connected landmark nodes</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Total Pathways</div>
            <div class="metric-card-value">{dash_summary['total_connections']}</div>
            <div class="metric-card-sub">Bidirectional walking segments</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {'#E53935' if dash_summary['blocked_connections'] > 0 else '#43A047'};">
            <div class="metric-card-title">Blocked Pathways</div>
            <div class="metric-card-value" style="color: {'#E53935' if dash_summary['blocked_connections'] > 0 else '#43A047'};">{dash_summary['blocked_connections']}</div>
            <div class="metric-card-sub">Construction or event closures</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #00ACC1;">
            <div class="metric-card-title">Available Pathways</div>
            <div class="metric-card-value" style="color: #00ACC1;">{dash_summary['available_connections']}</div>
            <div class="metric-card-sub">Routable pathways in graph</div>
        </div>
        """, unsafe_allow_html=True)

    # Campus Map Visualization on Dashboard
    st.markdown("### 🗺️ Live Campus Layout")
    fig = create_campus_figure(service.graph, title="Active Campus Network Map")
    st.plotly_chart(fig, use_container_width=True)

    # Recent Searches & Categories Split
    col_hist, col_cats = st.columns([3, 2])
    with col_hist:
        st.markdown("### 📜 Recent Route Searches")
        recent = dash_summary["recent_searches"]
        if recent:
            df_recent = pd.DataFrame(recent)[[
                "start_location", "destination_location", "distance", "edges_count", "path_taken", "searched_at"
            ]]
            df_recent.columns = ["From", "To", "Distance (m)", "Segments", "Route Path", "Timestamp"]
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
        else:
            st.info("No route queries recorded yet. Search for a route in 'Find Shortest Route' to populate history.")

    with col_cats:
        st.markdown("### 🏷️ Location Categories")
        cat_df = pd.DataFrame(
            list(dash_summary["category_distribution"].items()),
            columns=["Category", "Count"]
        ).sort_values(by="Count", ascending=False)
        st.dataframe(cat_df, use_container_width=True, hide_index=True)

        if st.button("🔄 Reset to Default 10-Node Sample Campus"):
            service.reset_to_sample_campus()
            st.success("Successfully reset database to clean default campus dataset!")
            st.rerun()


# =============================================================================
# MODULE 2: FIND SHORTEST ROUTE
# =============================================================================
elif menu == "🧭 Find Shortest Route":
    st.subheader("Shortest-Path Navigation Using Dijkstra's Algorithm")
    st.write("Select starting location and destination to compute the optimal walking path, distance, and turn-by-turn guidance.")

    location_names = service.graph.get_node_names()
    if len(location_names) < 2:
        st.warning("At least two campus locations are required. Please add locations or reset to default campus data.")
    else:
        # Route Input Form
        with st.form("route_finder_form"):
            c1, c2, c3 = st.columns([3, 3, 2])
            with c1:
                start_loc = st.selectbox(
                    "📍 Select Starting Location (Source):",
                    location_names,
                    index=0,
                    help="Where your walk begins"
                )
            with c2:
                # Default destination to a different node if possible
                dest_default_idx = 1 if len(location_names) > 1 else 0
                dest_loc = st.selectbox(
                    "🎯 Select Destination Location:",
                    location_names,
                    index=dest_default_idx,
                    help="Where you want to reach"
                )
            with c3:
                walking_speed = st.slider(
                    "🚶 Walking Speed (m/min):",
                    min_value=50,
                    max_value=120,
                    value=int(DEFAULT_WALKING_SPEED_M_PER_MIN),
                    step=5,
                    help="Average walking speed (80 m/min ~ 4.8 km/h)"
                )

            submit_btn = st.form_submit_button("🚀 Calculate Shortest Route", type="primary", use_container_width=True)

        # Execution and Result Display
        if submit_btn:
            with st.spinner("Executing Dijkstra's Algorithm with Min-Heap..."):
                res = service.find_shortest_route(
                    start_loc,
                    dest_loc,
                    log_history=True,
                    walking_speed_m_per_min=float(walking_speed)
                )

            if not res["found"]:
                st.error(f"❌ **Unreachable Destination!** {res['message']}")
                st.info("💡 **Tip:** Some connecting pathways might be blocked or disconnected. Check the 'Blocked Paths' module to unblock paths.")
                fig = create_campus_figure(service.graph, start_node=start_loc, destination_node=dest_loc)
                st.plotly_chart(fig, use_container_width=True)
            elif start_loc == dest_loc:
                st.info(f"ℹ️ **Identical Locations:** {res['message']}")
                fig = create_campus_figure(service.graph, start_node=start_loc, destination_node=dest_loc)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Success results presentation
                st.success(f"✅ {res['message']}")

                # Route summary metrics
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Total Walking Distance", f"{res['total_distance']:.0f} m")
                with m2:
                    st.metric("Estimated Walk Time", f"~{res['estimated_time_mins']} mins")
                with m3:
                    st.metric("Path Segments", f"{res['edges_count']} hops")
                with m4:
                    st.metric("Compute Time", f"{res['execution_time_us']:.1f} µs")

                # Breadcrumbs ribbon
                path_str = " ➔ ".join(res["path"])
                st.markdown(f"""
                <div class="route-ribbon">
                    <b>Optimal Route:</b> {path_str}
                </div>
                """, unsafe_allow_html=True)

                # Visual Map with Highlighted Route
                fig = create_campus_figure(
                    service.graph,
                    highlight_path=res["path"],
                    start_node=start_loc,
                    destination_node=dest_loc,
                    title=f"Shortest Route: {start_loc} ➔ {dest_loc} ({res['total_distance']:.0f} m)"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Step-by-step turn-by-turn guidance
                st.markdown("### 📋 Step-by-Step Walking Directions")
                for step in res["instructions"]:
                    st.markdown(f"""
                    <div class="step-card">
                        <b>Step {step['step_number']}:</b> From <b>{step['from_node']}</b> ({step['from_category']}) 
                        walk <b>{step['segment_distance']:.0f} m</b> (~{step['segment_time_mins']} min) 
                        to <b>{step['to_node']}</b> ({step['to_category']}).<br>
                        <small style="color: #546E7A;">Cumulative: {step['cumulative_distance']:.0f} m (~{step['cumulative_time_mins']} mins)</small>
                    </div>
                    """, unsafe_allow_html=True)


# =============================================================================
# MODULE 3: INTERACTIVE CAMPUS MAP
# =============================================================================
elif menu == "🗺️ Interactive Campus Map":
    st.subheader("Interactive 2D Campus Spatial Layout")
    st.write("Explore all campus locations, pathways, and distance weights. Hover over nodes and edges to inspect detailed metadata.")

    fig = create_campus_figure(service.graph, title="Campus Infrastructure Map")
    st.plotly_chart(fig, use_container_width=True)

    # Filterable Directory
    st.markdown("### 🏛️ Campus Locations Directory")
    locs = service.db.get_all_locations()
    if locs:
        df_locs = pd.DataFrame(locs)[["name", "category", "x", "y", "description"]]
        df_locs.columns = ["Location Name", "Category", "Grid X", "Grid Y", "Description"]
        
        category_filter = st.multiselect(
            "Filter by Category:",
            options=LOCATION_CATEGORIES,
            default=[]
        )
        if category_filter:
            df_locs = df_locs[df_locs["Category"].isin(category_filter)]

        st.dataframe(df_locs, use_container_width=True, hide_index=True)


# =============================================================================
# MODULE 4: COMPARE ALGORITHMS (DIJKSTRA VS BFS)
# =============================================================================
elif menu == "⚡ Compare Algorithms (Dijkstra vs BFS)":
    st.subheader("Pedagogical DSA Comparison: Dijkstra's Algorithm vs Breadth-First Search (BFS)")
    st.markdown("""
    This module demonstrates the fundamental difference between **Dijkstra's Algorithm** (which accounts for weighted edge distances) 
    and **Breadth-First Search** (which finds the path with the minimum number of edges/hops without considering weights).
    """)

    location_names = service.graph.get_node_names()
    c1, c2 = st.columns(2)
    with c1:
        start_node = st.selectbox("Select Start Location:", location_names, index=1 if len(location_names) > 1 else 0)
    with c2:
        dest_node = st.selectbox(
            "Select Destination Location:",
            location_names,
            index=6 if len(location_names) > 6 else 0,
            help="For demonstration, 'Admin Block' to 'Campus Canteen' illustrates Dijkstra (2 hops, 250m) vs BFS (1 hop, 260m)"
        )

    if st.button("⚡ Run Comparative Analysis", type="primary", use_container_width=True):
        comp = service.compare_algorithms(start_node, dest_node)
        d_res = comp["dijkstra"]
        b_res = comp["bfs"]

        st.markdown(f"### 💡 DSA Insight")
        st.info(comp["pedagogical_insight"])

        # Side-by-side metric comparison
        col_dijkstra, col_bfs = st.columns(2)

        with col_dijkstra:
            st.markdown("#### 🌟 Dijkstra's Algorithm (Priority Queue)")
            if d_res["found"]:
                st.write(f"**Path:** {' ➔ '.join(d_res['path'])}")
                st.metric("Total Physical Distance", f"{d_res['total_distance']:.0f} meters")
                st.metric("Number of Pathway Edges", f"{d_res['edges_count']} hops")
                st.metric("Nodes Visited During Search", f"{d_res['visited_count']} nodes")
                st.metric("Execution Time", f"{d_res['execution_time_us']:.1f} µs")
                st.caption("Time Complexity: O((V + E) log V) | Space: O(V + E)")
            else:
                st.error("No path found.")

        with col_bfs:
            st.markdown("#### 🔄 Breadth-First Search (FIFO Queue)")
            if b_res["found"]:
                st.write(f"**Path:** {' ➔ '.join(b_res['path'])}")
                st.metric("Total Physical Distance", f"{b_res['total_distance']:.0f} meters")
                st.metric("Number of Pathway Edges", f"{b_res['edges_count']} hops")
                st.metric("Nodes Visited During Search", f"{b_res['visited_count']} nodes")
                st.metric("Execution Time", f"{b_res['execution_time_us']:.1f} µs")
                st.caption("Time Complexity: O(V + E) | Space: O(V)")
            else:
                st.error("No path found.")

        # Comparison summary table
        st.markdown("### 📊 Tabular Comparison")
        comp_table = [
            {
                "Metric": "Algorithm",
                "Dijkstra": "Dijkstra (heapq Min-Heap)",
                "BFS": "Breadth-First Search (deque)"
            },
            {
                "Metric": "Optimality Target",
                "Dijkstra": "Minimum Total Weight (Meters)",
                "BFS": "Minimum Hop / Edge Count"
            },
            {
                "Metric": "Total Distance",
                "Dijkstra": f"{d_res['total_distance']:.0f} m",
                "BFS": f"{b_res['total_distance']:.0f} m"
            },
            {
                "Metric": "Edge Segments (Hops)",
                "Dijkstra": f"{d_res['edges_count']} hops",
                "BFS": f"{b_res['edges_count']} hops"
            },
            {
                "Metric": "Time Complexity",
                "Dijkstra": "O((V + E) log V)",
                "BFS": "O(V + E)"
            },
            {
                "Metric": "Route Identical?",
                "Dijkstra": "Yes" if comp["same_path"] else "No (Dijkstra prioritized distance)",
                "BFS": "Yes" if comp["same_path"] else "No (BFS prioritized fewer hops)"
            }
        ]
        st.dataframe(pd.DataFrame(comp_table), use_container_width=True, hide_index=True)


# =============================================================================
# MODULE 5: MANAGE LOCATIONS
# =============================================================================
elif menu == "🏢 Manage Locations":
    st.subheader("Campus Locations Management")
    st.write("Add, edit, or safely remove campus locations. All changes persist in SQLite and update the in-memory graph.")

    tab1, tab2, tab3 = st.tabs(["➕ Add New Location", "✏️ Edit Existing Location", "🗑️ Delete Location"])

    with tab1:
        with st.form("add_location_form"):
            name = st.text_input("Location Name (Unique):", placeholder="e.g., Robotics Lab")
            category = st.selectbox("Category:", LOCATION_CATEGORIES)
            c1, c2 = st.columns(2)
            with c1:
                x = st.number_input("Grid X Coordinate (0 - 100):", value=50.0, step=5.0)
            with c2:
                y = st.number_input("Grid Y Coordinate (0 - 100):", value=50.0, step=5.0)
            desc = st.text_area("Description / Landmark Notes:", placeholder="e.g., Located near the north quadrangle.")
            
            submit_loc = st.form_submit_button("Add Location to Campus", type="primary")
            if submit_loc:
                try:
                    service.add_location(name, category, x, y, desc)
                    st.success(f"Location '{name}' successfully added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding location: {e}")

    with tab2:
        loc_names = service.graph.get_node_names()
        if not loc_names:
            st.info("No locations available to edit.")
        else:
            selected_loc = st.selectbox("Select Location to Edit:", loc_names)
            curr = service.db.get_location_by_name(selected_loc)
            if curr:
                with st.form("edit_location_form"):
                    new_name = st.text_input("Update Name:", value=curr["name"])
                    cat_idx = LOCATION_CATEGORIES.index(curr["category"]) if curr["category"] in LOCATION_CATEGORIES else 0
                    new_cat = st.selectbox("Category:", LOCATION_CATEGORIES, index=cat_idx)
                    c1, c2 = st.columns(2)
                    with c1:
                        new_x = st.number_input("Grid X:", value=float(curr["x"]), step=5.0)
                    with c2:
                        new_y = st.number_input("Grid Y:", value=float(curr["y"]), step=5.0)
                    new_desc = st.text_area("Description:", value=curr["description"])

                    update_btn = st.form_submit_button("Save Changes", type="primary")
                    if update_btn:
                        try:
                            service.update_location(
                                current_name=selected_loc,
                                new_name=new_name,
                                category=new_cat,
                                x=new_x,
                                y=new_y,
                                description=new_desc
                            )
                            st.success(f"Location '{new_name}' updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating location: {e}")

    with tab3:
        loc_names = service.graph.get_node_names()
        if not loc_names:
            st.info("No locations available to delete.")
        else:
            with st.form("delete_location_form"):
                del_loc = st.selectbox("Select Location to Delete:", loc_names)
                st.warning(f"⚠️ Deleting '{del_loc}' will also permanently remove all pathways connected to it.")
                confirm = st.checkbox("I confirm that I want to delete this campus location.")
                del_btn = st.form_submit_button("Delete Location", type="primary")
                if del_btn:
                    if not confirm:
                        st.error("Please tick the confirmation checkbox to proceed.")
                    else:
                        try:
                            service.delete_location(del_loc)
                            st.success(f"Location '{del_loc}' deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting location: {e}")


# =============================================================================
# MODULE 6: MANAGE CONNECTIONS
# =============================================================================
elif menu == "🔗 Manage Connections":
    st.subheader("Pathway Connections Management")
    st.write("Define physical walkways connecting campus locations with distance weights.")

    tab1, tab2, tab3 = st.tabs(["➕ Add Connection", "✏️ Edit Connection Distance", "🗑️ Remove Connection"])
    loc_names = service.graph.get_node_names()

    with tab1:
        if len(loc_names) < 2:
            st.warning("At least two locations are required to create a pathway.")
        else:
            with st.form("add_conn_form"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    u = st.selectbox("Location A:", loc_names, key="conn_u")
                with c2:
                    v = st.selectbox("Location B:", loc_names, index=1 if len(loc_names) > 1 else 0, key="conn_v")
                with c3:
                    dist = st.number_input("Walking Distance (meters):", min_value=1.0, value=100.0, step=10.0)
                is_blocked = st.checkbox("Mark as Blocked initially (construction/closure)")

                add_conn_btn = st.form_submit_button("Add Pathway Connection", type="primary")
                if add_conn_btn:
                    try:
                        service.add_connection(u, v, dist, is_blocked)
                        st.success(f"Pathway between '{u}' and '{v}' ({dist} m) added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        all_edges = service.graph.get_all_edges()
        if not all_edges:
            st.info("No connections currently exist.")
        else:
            edge_labels = [f"{e['u']} ↔ {e['v']} ({e['distance']:.0f}m)" for e in all_edges]
            selected_edge_label = st.selectbox("Select Pathway to Edit:", edge_labels)
            idx = edge_labels.index(selected_edge_label)
            target_edge = all_edges[idx]

            with st.form("edit_conn_form"):
                new_dist = st.number_input("New Distance (meters):", min_value=1.0, value=float(target_edge["distance"]), step=10.0)
                edit_conn_btn = st.form_submit_button("Update Distance", type="primary")
                if edit_conn_btn:
                    try:
                        service.update_connection(target_edge["u"], target_edge["v"], distance=new_dist)
                        st.success("Distance updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab3:
        all_edges = service.graph.get_all_edges()
        if not all_edges:
            st.info("No connections available to remove.")
        else:
            with st.form("del_conn_form"):
                edge_labels = [f"{e['u']} ↔ {e['v']}" for e in all_edges]
                del_label = st.selectbox("Select Pathway to Remove:", edge_labels)
                idx = edge_labels.index(del_label)
                target_del = all_edges[idx]

                del_conn_btn = st.form_submit_button("Remove Pathway", type="primary")
                if del_conn_btn:
                    try:
                        service.delete_connection(target_del["u"], target_del["v"])
                        st.success("Pathway removed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Display Current Connections Table
    st.markdown("### 📋 Active Campus Connections")
    connections = service.db.get_all_connections()
    if connections:
        df_conn = pd.DataFrame(connections)[["source_name", "destination_name", "distance", "is_blocked"]]
        df_conn.columns = ["Location A", "Location B", "Distance (m)", "Blocked?"]
        st.dataframe(df_conn, use_container_width=True, hide_index=True)


# =============================================================================
# MODULE 7: BLOCKED PATHS & DETOURS
# =============================================================================
elif menu == "🚧 Blocked Paths & Detours":
    st.subheader("Dynamic Pathway Blockage & Alternative Route Finder")
    st.markdown("""
    Campus administrators can temporarily block pathways due to maintenance, construction, or university events.
    The routing engine immediately recalculates detour routes bypassing blocked segments in both directions.
    """)

    all_edges = service.graph.get_all_edges()
    if not all_edges:
        st.info("No connections available in campus graph.")
    else:
        c1, c2 = st.columns([3, 2])

        with c1:
            st.markdown("### 🛠️ Block / Unblock Pathway")
            edge_options = [f"{e['u']} ↔ {e['v']} ({'BLOCKED' if e['is_blocked'] else 'OPEN'})" for e in all_edges]
            selected_edge_str = st.selectbox("Choose Pathway:", edge_options)
            sel_idx = edge_options.index(selected_edge_str)
            target = all_edges[sel_idx]

            status_btn = "🟢 Unblock Pathway" if target["is_blocked"] else "⛔ Block Pathway"
            if st.button(status_btn, type="primary"):
                new_state = not target["is_blocked"]
                service.toggle_connection_blocked(target["u"], target["v"], new_state)
                st.success(f"Pathway {target['u']} ↔ {target['v']} status updated to {'BLOCKED' if new_state else 'OPEN'}!")
                st.rerun()

        with c2:
            st.markdown("### 📌 Currently Blocked Pathways")
            blocked_list = [e for e in all_edges if e["is_blocked"]]
            if blocked_list:
                for b in blocked_list:
                    st.error(f"⛔ **{b['u']} ↔ {b['v']}** ({b['distance']:.0f} m)")
                if st.button("🟢 Unblock All Pathways"):
                    for b in blocked_list:
                        service.toggle_connection_blocked(b["u"], b["v"], False)
                    st.success("All pathways have been unblocked!")
                    st.rerun()
            else:
                st.success("✅ No pathways are currently blocked. All routes are open.")

    st.divider()

    # Alternative Route Finder Demo
    st.markdown("### 🔄 Alternative Route Recalculation Test")
    st.write("Test how the routing engine automatically redirects students around blocked pathways:")
    loc_names = service.graph.get_node_names()
    if len(loc_names) >= 2:
        ac1, ac2 = st.columns(2)
        with ac1:
            a_start = st.selectbox("Start Point:", loc_names, index=0, key="alt_start")
        with ac2:
            a_dest = st.selectbox("Destination Point:", loc_names, index=6 if len(loc_names) > 6 else 1, key="alt_dest")

        if st.button("🔍 Evaluate Route Detour", type="secondary"):
            alt_eval = service.find_alternative_route(a_start, a_dest)
            act = alt_eval["active_route"]
            unr = alt_eval["unrestricted_route"]

            if not act["found"]:
                st.error(f"Destination is completely blocked! {act['message']}")
            else:
                if alt_eval["has_blocked_detour"]:
                    st.warning(f"⚠️ **Detour Active!** Normal shortest route was blocked. Calculated alternative detour: {act['total_distance']:.0f} m (vs normal {unr['total_distance']:.0f} m).")
                else:
                    st.success(f"✅ Route is clear of closures. Total distance: {act['total_distance']:.0f} m.")

                st.write(f"**Calculated Route:** {' ➔ '.join(act['path'])}")
                fig_alt = create_campus_figure(service.graph, highlight_path=act["path"], start_node=a_start, destination_node=a_dest)
                st.plotly_chart(fig_alt, use_container_width=True)


# =============================================================================
# MODULE 8: ROUTE SEARCH HISTORY
# =============================================================================
elif menu == "📜 Route Search History":
    st.subheader("Navigation Audit Logs & Search Analytics")
    st.write("Persistent SQLite log of route queries executed by students and visitors.")

    searches = service.db.get_recent_searches(limit=50)
    if not searches:
        st.info("No route queries recorded yet.")
    else:
        df_hist = pd.DataFrame(searches)[[
            "id", "start_location", "destination_location", "algorithm",
            "distance", "edges_count", "path_taken", "execution_time_us", "searched_at"
        ]]
        df_hist.columns = [
            "Log ID", "Start", "Destination", "Algorithm",
            "Distance (m)", "Segments", "Route Path", "Exec Time (µs)", "Timestamp"
        ]
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        c1, c2 = st.columns([2, 2])
        with c1:
            csv = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export History as CSV",
                csv,
                "campus_route_history.csv",
                "text/csv",
                key='download-csv'
            )
        with c2:
            if st.button("🗑️ Clear Search History", type="secondary"):
                service.db.clear_search_history()
                st.success("Search history cleared!")
                st.rerun()


# =============================================================================
# MODULE 9: ABOUT THE PROJECT & DSA CONCEPTS
# =============================================================================
elif menu == "📚 About the Project & DSA":
    st.subheader("Smart Campus PathFinder — Architecture & DSA Specifications")
    st.markdown("""
    ### 🎯 Project Overview
    **Smart Campus PathFinder** is a comprehensive Data Structures and Algorithms college mini-project 
    engineered to solve the real-world problem of navigating complex academic, laboratory, residential, 
    and administrative campus environments.

    ---

    ### 🧠 Data Structures & Algorithms Employed

    | Concept / Algorithm | Implementation Method | Purpose / Role | Theoretical Complexity |
    | :--- | :--- | :--- | :--- |
    | **Weighted Graph** | Adjacency List (`dict` of `dict`) | Represents campus topology (locations as vertices, walkways as edges) | Space: $O(V + E)$ |
    | **Dijkstra's Algorithm** | Python `heapq` (Min-Heap Priority Queue) | Finds the absolute shortest physical walking distance (meters) | Time: $O((V + E) \log V)$ |
    | **Breadth-First Search (BFS)** | Python `collections.deque` (FIFO Queue) | Finds the path with the fewest number of edges / pathway turns | Time: $O(V + E)$ |
    | **Blocked Edge Handling** | Canonical Pair Lookup (`set`) | Bypasses construction or event closures in $O(1)$ time | Space: $O(E_{blocked})$ |
    | **Path Reconstruction** | Backtracking via Predecessor Dict | Reconstructs ordered list of locations from destination to source | Time: $O(V)$ |
    | **Persistent Storage** | SQLite Database with Foreign Keys | Ensures campus locations and pathways persist across application restarts | ACID Transactions |

    ---

    ### 🔬 Dijkstra vs. BFS: The Pedagogical Distinction
    - **Dijkstra's Algorithm:** Guarantees the **minimum physical walking distance in meters**. Because walking pathways have varying lengths (e.g. 80m vs 260m), Dijkstra prioritizes edge weights using a priority queue.
    - **Breadth-First Search (BFS):** Guarantees the **minimum number of edges (hops)**. On a weighted graph, BFS does not guarantee the shortest distance. For example, a single direct pathway of 260m will be chosen by BFS over a two-segment path of 140m + 110m = 250m.

    ---

    ### 💻 Technology Stack
    - **Language:** Python 3
    - **Frontend UI:** Streamlit (Responsive Blue-and-White Theme)
    - **Graph Analysis & Layout:** NetworkX
    - **Interactive Visualization:** Plotly Graph Objects
    - **Database:** SQLite3
    - **Testing Framework:** pytest (100% automated test coverage)

    ---

    ### 👨‍🎓 Project Credits & Submission Details
    - **Project Name:** Smart Campus PathFinder — Intelligent Campus Navigation Using DSA
    - **Course:** Data Structures and Algorithms (DSA) College Mini-Project
    - **Status:** Fully functional, verified with automated tests, and ready for viva demonstration.
    """)

# Footer
st.markdown("""
<div class="footer-text">
    Smart Campus PathFinder &bull; Developed for Academic Demonstration &bull; Powered by Python, Streamlit, NetworkX, and SQLite
</div>
""", unsafe_allow_html=True)
