"""
Graph Data Structure Module for Smart Campus PathFinder.
Implements a weighted, undirected campus network graph using an Adjacency List.
Supports dynamic node/edge addition, deletion, validation, and blocked path state.
"""

from typing import Dict, List, Set, Tuple, Optional, Any


class CampusGraph:
    """
    Weighted, undirected graph representation of campus locations and pathways.
    
    Data Structures:
    - Adjacency List: Dictionary mapping each location name to a dictionary of {neighbor: distance}.
    - Blocked Edges Set: Set of canonical tuples (min(u, v), max(u, v)) for O(1) blocked state checks.
    - Nodes Dictionary: Stores location metadata (category, coordinates, description).
    """

    def __init__(self):
        # Maps node_name -> {neighbor_name: distance}
        self.adj: Dict[str, Dict[str, float]] = {}
        # Maps node_name -> metadata dict {'category': str, 'x': float, 'y': float, 'description': str}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # Stores canonical undirected pairs (u, v) where u < v that are blocked
        self.blocked_edges: Set[Tuple[str, str]] = set()

    @staticmethod
    def _canonical_edge(u: str, v: str) -> Tuple[str, str]:
        """Returns ordered tuple (min, max) so undirected edge (u, v) is identical to (v, u)."""
        return (u, v) if u < v else (v, u)

    # -------------------------------------------------------------------------
    # Node Management
    # -------------------------------------------------------------------------

    def add_node(
        self,
        name: str,
        category: str = "Academic",
        x: float = 0.0,
        y: float = 0.0,
        description: str = ""
    ) -> None:
        """
        Adds a new campus location node.
        
        Raises:
            ValueError: If location name is empty or already exists.
        """
        name = name.strip()
        if not name:
            raise ValueError("Location name cannot be empty.")
        if name in self.nodes:
            raise ValueError(f"Location '{name}' already exists in the graph.")

        self.nodes[name] = {
            "name": name,
            "category": category.strip() if category else "Academic",
            "x": float(x),
            "y": float(y),
            "description": description.strip()
        }
        if name not in self.adj:
            self.adj[name] = {}

    def update_node(
        self,
        name: str,
        category: Optional[str] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        description: Optional[str] = None
    ) -> None:
        """Updates attributes of an existing location node."""
        if name not in self.nodes:
            raise ValueError(f"Location '{name}' does not exist.")

        if category is not None:
            self.nodes[name]["category"] = category.strip()
        if x is not None:
            self.nodes[name]["x"] = float(x)
        if y is not None:
            self.nodes[name]["y"] = float(y)
        if description is not None:
            self.nodes[name]["description"] = description.strip()

    def remove_node(self, name: str) -> None:
        """
        Safely removes a location and all incident pathways.
        
        Raises:
            ValueError: If location does not exist.
        """
        if name not in self.nodes:
            raise ValueError(f"Location '{name}' does not exist.")

        # Remove all incident edges from neighbors' adjacency lists
        for neighbor in list(self.adj[name].keys()):
            del self.adj[neighbor][name]
            edge_key = self._canonical_edge(name, neighbor)
            self.blocked_edges.discard(edge_key)

        # Remove from self.adj and self.nodes
        del self.adj[name]
        del self.nodes[name]

    def has_node(self, name: str) -> bool:
        """Checks if a location exists in the graph."""
        return name in self.nodes

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Returns a list of all nodes with their metadata."""
        return list(self.nodes.values())

    def get_node_names(self) -> List[str]:
        """Returns sorted list of all location names."""
        return sorted(list(self.nodes.keys()))

    # -------------------------------------------------------------------------
    # Edge Management
    # -------------------------------------------------------------------------

    def add_edge(
        self,
        u: str,
        v: str,
        distance: float,
        is_blocked: bool = False
    ) -> None:
        """
        Adds a bidirectional weighted edge between two locations.
        
        Raises:
            ValueError: If locations do not exist, u == v, distance <= 0, or edge already exists.
        """
        u = u.strip()
        v = v.strip()

        if u not in self.nodes:
            raise ValueError(f"Starting location '{u}' does not exist.")
        if v not in self.nodes:
            raise ValueError(f"Destination location '{v}' does not exist.")
        if u == v:
            raise ValueError("Self-loops are not allowed: starting and destination location cannot be identical.")
        if distance <= 0:
            raise ValueError(f"Distance must be strictly positive (got {distance} m).")
        if v in self.adj[u]:
            raise ValueError(f"Connection between '{u}' and '{v}' already exists.")

        self.adj[u][v] = float(distance)
        self.adj[v][u] = float(distance)

        edge_key = self._canonical_edge(u, v)
        if is_blocked:
            self.blocked_edges.add(edge_key)
        else:
            self.blocked_edges.discard(edge_key)

    def update_edge(self, u: str, v: str, distance: float) -> None:
        """Updates the walking distance between two existing connected locations."""
        if not self.has_edge(u, v):
            raise ValueError(f"Connection between '{u}' and '{v}' does not exist.")
        if distance <= 0:
            raise ValueError(f"Distance must be strictly positive (got {distance} m).")

        self.adj[u][v] = float(distance)
        self.adj[v][u] = float(distance)

    def remove_edge(self, u: str, v: str) -> None:
        """Removes a bidirectional connection between two locations."""
        if not self.has_edge(u, v):
            raise ValueError(f"Connection between '{u}' and '{v}' does not exist.")

        del self.adj[u][v]
        del self.adj[v][u]
        self.blocked_edges.discard(self._canonical_edge(u, v))

    def has_edge(self, u: str, v: str) -> bool:
        """Checks if a connection exists between u and v."""
        return u in self.adj and v in self.adj[u]

    def get_edge_distance(self, u: str, v: str) -> float:
        """Returns the walking distance between u and v."""
        if not self.has_edge(u, v):
            raise ValueError(f"No connection between '{u}' and '{v}'.")
        return self.adj[u][v]

    def set_edge_blocked(self, u: str, v: str, is_blocked: bool = True) -> None:
        """Blocks or unblocks a pathway between two locations."""
        if not self.has_edge(u, v):
            raise ValueError(f"Connection between '{u}' and '{v}' does not exist.")

        edge_key = self._canonical_edge(u, v)
        if is_blocked:
            self.blocked_edges.add(edge_key)
        else:
            self.blocked_edges.discard(edge_key)

    def is_edge_blocked(self, u: str, v: str) -> bool:
        """Checks whether the connection between u and v is currently blocked."""
        return self._canonical_edge(u, v) in self.blocked_edges

    def get_neighbors(self, node: str, include_blocked: bool = False) -> Dict[str, float]:
        """
        Returns adjacent nodes and their edge weights.
        If include_blocked is False (default for routing), blocked edges are excluded.
        """
        if node not in self.adj:
            return {}

        neighbors = {}
        for neighbor, weight in self.adj[node].items():
            if not include_blocked and self.is_edge_blocked(node, neighbor):
                continue
            neighbors[neighbor] = weight
        return neighbors

    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Returns a list of all unique undirected edges with distance and blocked status."""
        visited = set()
        edges = []
        for u in self.adj:
            for v, dist in self.adj[u].items():
                canon = self._canonical_edge(u, v)
                if canon not in visited:
                    visited.add(canon)
                    edges.append({
                        "u": canon[0],
                        "v": canon[1],
                        "distance": dist,
                        "is_blocked": canon in self.blocked_edges
                    })
        return sorted(edges, key=lambda e: (e["u"], e["v"]))

    def get_blocked_edges(self) -> List[Tuple[str, str]]:
        """Returns list of currently blocked canonical edge tuples (u, v)."""
        return sorted(list(self.blocked_edges))

    def clear(self) -> None:
        """Clears all nodes and edges."""
        self.adj.clear()
        self.nodes.clear()
        self.blocked_edges.clear()

    def get_summary_stats(self) -> Dict[str, int]:
        """Returns summary counts of nodes, total edges, and blocked edges."""
        total_nodes = len(self.nodes)
        total_edges = sum(len(neighbors) for neighbors in self.adj.values()) // 2
        total_blocked = len(self.blocked_edges)
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "blocked_edges": total_blocked,
            "available_edges": total_edges - total_blocked
        }
