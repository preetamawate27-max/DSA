"""
Campus Service Module for Smart Campus PathFinder.
Acts as the central business logic controller coordinating SQLite database persistence,
in-memory CampusGraph synchronization, and DSA algorithm execution.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from graph import CampusGraph
from database import CampusDatabase
from algorithms import (
    dijkstra_shortest_path,
    bfs_shortest_hops,
    compare_algorithms,
    get_step_by_step_instructions
)
from config import DEFAULT_WALKING_SPEED_M_PER_MIN


class CampusService:
    """Coordinates database persistence with active in-memory graph state."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db = CampusDatabase(db_path)
        self.graph = CampusGraph()
        self.load_graph_from_db()

    def load_graph_from_db(self) -> None:
        """Hydrates the in-memory CampusGraph from SQLite tables."""
        self.graph.clear()

        # Load Locations
        locations = self.db.get_all_locations()
        if not locations:
            # First-time initialization: automatically seed sample campus data
            self.db.seed_sample_campus()
            locations = self.db.get_all_locations()

        for loc in locations:
            self.graph.add_node(
                name=loc["name"],
                category=loc["category"],
                x=loc["x"],
                y=loc["y"],
                description=loc.get("description", "")
            )

        # Load Connections
        connections = self.db.get_all_connections()
        for conn in connections:
            self.graph.add_edge(
                u=conn["source_name"],
                v=conn["destination_name"],
                distance=conn["distance"],
                is_blocked=conn["is_blocked"]
            )

    # -------------------------------------------------------------------------
    # Route Finding Operations
    # -------------------------------------------------------------------------

    def find_shortest_route(
        self,
        start: str,
        destination: str,
        log_history: bool = True,
        walking_speed_m_per_min: float = DEFAULT_WALKING_SPEED_M_PER_MIN
    ) -> Dict[str, Any]:
        """
        Calculates shortest path using Dijkstra's algorithm.
        Generates step-by-step turn directions and walking time estimates.
        Optionally logs query to SQLite search_history.
        """
        result = dijkstra_shortest_path(self.graph, start, destination, include_blocked=False)

        # Generate human-friendly walking instructions if a route was found
        if result["found"] and len(result["path"]) > 1:
            result["instructions"] = get_step_by_step_instructions(
                self.graph,
                result["path"],
                walking_speed_m_per_min=walking_speed_m_per_min
            )
            result["estimated_time_mins"] = round(result["total_distance"] / walking_speed_m_per_min, 1)
        elif result["found"] and len(result["path"]) == 1:
            result["instructions"] = []
            result["estimated_time_mins"] = 0.0
        else:
            result["instructions"] = []
            result["estimated_time_mins"] = None

        if log_history and result["found"]:
            self.db.log_search(
                start_location=start,
                destination_location=destination,
                algorithm="Dijkstra",
                distance=result["total_distance"],
                edges_count=result["edges_count"],
                path_taken=result["path"],
                execution_time_us=result["execution_time_us"]
            )

        return result

    def find_alternative_route(
        self,
        start: str,
        destination: str,
        walking_speed_m_per_min: float = DEFAULT_WALKING_SPEED_M_PER_MIN
    ) -> Dict[str, Any]:
        """
        Evaluates routing resilience:
        Compares route without any blocked pathways against route with blocked pathways bypassed.
        """
        # Baseline route (ignoring blocked status as if all paths are open)
        unrestricted_result = dijkstra_shortest_path(self.graph, start, destination, include_blocked=True)

        # Active route (respecting active pathway closures)
        active_result = self.find_shortest_route(
            start, destination, log_history=False, walking_speed_m_per_min=walking_speed_m_per_min
        )

        has_blocked_detour = False
        if unrestricted_result["found"] and active_result["found"]:
            if unrestricted_result["path"] != active_result["path"]:
                has_blocked_detour = True

        return {
            "active_route": active_result,
            "unrestricted_route": unrestricted_result,
            "has_blocked_detour": has_blocked_detour,
            "blocked_pathways_in_graph": len(self.graph.blocked_edges)
        }

    def compare_algorithms(self, start: str, destination: str) -> Dict[str, Any]:
        """Runs side-by-side comparison of Dijkstra's Algorithm vs Breadth-First Search (BFS)."""
        return compare_algorithms(self.graph, start, destination)

    # -------------------------------------------------------------------------
    # Campus Location Management
    # -------------------------------------------------------------------------

    def add_location(
        self,
        name: str,
        category: str = "Academic",
        x: float = 0.0,
        y: float = 0.0,
        description: str = ""
    ) -> None:
        """Adds location to both database and in-memory graph."""
        name = name.strip()
        if self.graph.has_node(name):
            raise ValueError(f"Location '{name}' already exists in the graph.")

        self.db.add_location(name, category, x, y, description)
        self.graph.add_node(name, category, x, y, description)

    def update_location(
        self,
        current_name: str,
        new_name: Optional[str] = None,
        category: Optional[str] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        description: Optional[str] = None
    ) -> None:
        """Updates location in database and refreshes graph."""
        self.db.update_location(current_name, new_name, category, x, y, description)
        self.load_graph_from_db()

    def delete_location(self, name: str) -> None:
        """Deletes location and all associated edges from database and graph."""
        self.db.delete_location(name)
        self.graph.remove_node(name)

    # -------------------------------------------------------------------------
    # Pathway Connection Management
    # -------------------------------------------------------------------------

    def add_connection(
        self,
        u: str,
        v: str,
        distance: float,
        is_blocked: bool = False
    ) -> None:
        """Adds a new pathway to both database and graph."""
        self.db.add_connection(u, v, distance, is_blocked)
        self.graph.add_edge(u, v, distance, is_blocked)

    def update_connection(
        self,
        u: str,
        v: str,
        distance: Optional[float] = None,
        is_blocked: Optional[bool] = None
    ) -> None:
        """Updates distance or status of a pathway in database and graph."""
        self.db.update_connection(u, v, distance, is_blocked)
        if distance is not None:
            self.graph.update_edge(u, v, distance)
        if is_blocked is not None:
            self.graph.set_edge_blocked(u, v, is_blocked)

    def delete_connection(self, u: str, v: str) -> None:
        """Deletes pathway from database and graph."""
        self.db.delete_connection(u, v)
        self.graph.remove_edge(u, v)

    def toggle_connection_blocked(self, u: str, v: str, is_blocked: bool) -> None:
        """Blocks or unblocks a pathway."""
        self.db.set_connection_blocked(u, v, is_blocked)
        self.graph.set_edge_blocked(u, v, is_blocked)

    def reset_to_sample_campus(self) -> None:
        """Resets the entire campus map to the curated 10-node demonstration dataset."""
        self.db.seed_sample_campus()
        self.load_graph_from_db()

    # -------------------------------------------------------------------------
    # Dashboard & Query Helpers
    # -------------------------------------------------------------------------

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Provides statistics for the overview dashboard."""
        stats = self.graph.get_summary_stats()
        recent_searches = self.db.get_recent_searches(limit=5)

        # Compute category distribution
        category_counts = {}
        for node in self.graph.nodes.values():
            cat = node.get("category", "Other")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_locations": stats["total_nodes"],
            "total_connections": stats["total_edges"],
            "blocked_connections": stats["blocked_edges"],
            "available_connections": stats["available_edges"],
            "recent_searches": recent_searches,
            "category_distribution": category_counts,
            "location_names": self.graph.get_node_names()
        }
