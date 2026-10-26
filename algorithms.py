"""
DSA Routing Algorithms Module for Smart Campus PathFinder.
Implements:
1. Dijkstra's Algorithm (using heapq for O((V + E) log V) shortest path).
2. Breadth-First Search (using collections.deque for minimum hop/edge count path).
3. Path reconstruction and algorithm comparison metrics.
"""

import heapq
import time
from collections import deque
from typing import Dict, List, Tuple, Optional, Any
from graph import CampusGraph


def reconstruct_path(predecessors: Dict[str, Optional[str]], start: str, destination: str) -> List[str]:
    """
    Reconstructs the path from destination to start using the predecessors dictionary,
    then reverses it to return [start, ..., destination].
    """
    if destination not in predecessors and start != destination:
        return []

    path = []
    current = destination
    while current is not None:
        path.append(current)
        if current == start:
            break
        current = predecessors.get(current)

    # If the backtrack did not reach start, destination is unreachable
    if not path or path[-1] != start:
        return []

    path.reverse()
    return path


def calculate_path_distance(graph: CampusGraph, path: List[str]) -> float:
    """Calculates total physical distance in meters along a given sequence of nodes."""
    if not path or len(path) < 2:
        return 0.0

    total_dist = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if not graph.has_edge(u, v):
            return float("inf")
        total_dist += graph.get_edge_distance(u, v)
    return round(total_dist, 2)


def dijkstra_shortest_path(
    graph: CampusGraph,
    start: str,
    destination: str,
    include_blocked: bool = False
) -> Dict[str, Any]:
    """
    Finds the shortest physical distance route between start and destination
    using Dijkstra's Algorithm with a binary min-heap (heapq).

    Parameters:
        graph: CampusGraph instance
        start: Name of starting campus location
        destination: Name of destination campus location
        include_blocked: If False (default), ignores pathways marked as blocked

    Returns:
        Dictionary containing path, total distance, node count, visited count, execution time, and stats.

    Complexity:
        Time: O((V + E) log V) where V = locations and E = pathways.
        Space: O(V) for distances, predecessors, and min-heap.
    """
    start_time = time.perf_counter()

    # Input validations
    if not graph.has_node(start):
        raise ValueError(f"Starting location '{start}' not found in campus database.")
    if not graph.has_node(destination):
        raise ValueError(f"Destination location '{destination}' not found in campus database.")

    # Base case: start and destination are the same location
    if start == destination:
        exec_time_us = round((time.perf_counter() - start_time) * 1_000_000, 2)
        return {
            "algorithm": "Dijkstra's Algorithm (Min-Heap)",
            "found": True,
            "start": start,
            "destination": destination,
            "path": [start],
            "total_distance": 0.0,
            "edges_count": 0,
            "visited_count": 1,
            "execution_time_us": exec_time_us,
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V + E)",
            "message": "Source and destination are identical. Distance is 0 meters.",
            "distances": {start: 0.0},
            "predecessors": {start: None}
        }

    # Initialize data structures
    distances: Dict[str, float] = {node: float("inf") for node in graph.nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.nodes}
    distances[start] = 0.0

    # Min-Heap Priority Queue: stores tuples of (current_shortest_distance, node_name)
    pq: List[Tuple[float, str]] = [(0.0, start)]
    visited_nodes = set()

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        # Lazy deletion: if popped distance is greater than the recorded shortest distance, skip
        if current_dist > distances[current_node]:
            continue

        visited_nodes.add(current_node)

        # Early exit if we reached the target destination
        if current_node == destination:
            break

        # Explore incident edges
        neighbors = graph.get_neighbors(current_node, include_blocked=include_blocked)
        for neighbor, weight in neighbors.items():
            if neighbor in visited_nodes:
                continue

            new_distance = current_dist + weight

            # Relaxation step: if a strictly shorter path to neighbor is discovered
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                heapq.heappush(pq, (new_distance, neighbor))

    exec_time_us = round((time.perf_counter() - start_time) * 1_000_000, 2)

    # Check reachability
    if distances[destination] == float("inf"):
        return {
            "algorithm": "Dijkstra's Algorithm (Min-Heap)",
            "found": False,
            "start": start,
            "destination": destination,
            "path": [],
            "total_distance": float("inf"),
            "edges_count": 0,
            "visited_count": len(visited_nodes),
            "execution_time_us": exec_time_us,
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V + E)",
            "message": f"Destination '{destination}' is unreachable from '{start}'. Pathways may be disconnected or blocked.",
            "distances": distances,
            "predecessors": predecessors
        }

    # Path reconstruction
    path = reconstruct_path(predecessors, start, destination)
    total_dist = round(distances[destination], 2)

    return {
        "algorithm": "Dijkstra's Algorithm (Min-Heap)",
        "found": True,
        "start": start,
        "destination": destination,
        "path": path,
        "total_distance": total_dist,
        "edges_count": max(0, len(path) - 1),
        "visited_count": len(visited_nodes),
        "execution_time_us": exec_time_us,
        "time_complexity": "O((V + E) log V)",
        "space_complexity": "O(V + E)",
        "message": f"Optimal shortest route found ({total_dist} m across {len(path) - 1} pathway segments).",
        "distances": distances,
        "predecessors": predecessors
    }


def bfs_shortest_hops(
    graph: CampusGraph,
    start: str,
    destination: str,
    include_blocked: bool = False
) -> Dict[str, Any]:
    """
    Finds the route with the fewest number of edges (hops) using Breadth-First Search (BFS)
    with a FIFO queue (collections.deque).

    Note: In a weighted graph, BFS guarantees the minimum number of transitions/edges,
    NOT the minimum physical walking distance.

    Complexity:
        Time: O(V + E)
        Space: O(V)
    """
    start_time = time.perf_counter()

    if not graph.has_node(start):
        raise ValueError(f"Starting location '{start}' not found in campus database.")
    if not graph.has_node(destination):
        raise ValueError(f"Destination location '{destination}' not found in campus database.")

    if start == destination:
        exec_time_us = round((time.perf_counter() - start_time) * 1_000_000, 2)
        return {
            "algorithm": "Breadth-First Search (BFS)",
            "found": True,
            "start": start,
            "destination": destination,
            "path": [start],
            "total_distance": 0.0,
            "edges_count": 0,
            "visited_count": 1,
            "execution_time_us": exec_time_us,
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "message": "Source and destination are identical.",
            "note": "BFS minimizes edge/hop count, not weighted physical distance."
        }

    queue = deque([start])
    visited = {start}
    predecessors: Dict[str, Optional[str]] = {start: None}

    found = False
    while queue:
        current = queue.popleft()

        if current == destination:
            found = True
            break

        neighbors = graph.get_neighbors(current, include_blocked=include_blocked)
        for neighbor in sorted(neighbors.keys()):  # Deterministic iteration
            if neighbor not in visited:
                visited.add(neighbor)
                predecessors[neighbor] = current
                queue.append(neighbor)

    exec_time_us = round((time.perf_counter() - start_time) * 1_000_000, 2)

    if not found or destination not in predecessors:
        return {
            "algorithm": "Breadth-First Search (BFS)",
            "found": False,
            "start": start,
            "destination": destination,
            "path": [],
            "total_distance": float("inf"),
            "edges_count": 0,
            "visited_count": len(visited),
            "execution_time_us": exec_time_us,
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "message": f"Destination '{destination}' is unreachable from '{start}'.",
            "note": "BFS explores unweighted graphs level by level."
        }

    path = reconstruct_path(predecessors, start, destination)
    total_dist = calculate_path_distance(graph, path)

    return {
        "algorithm": "Breadth-First Search (BFS)",
        "found": True,
        "start": start,
        "destination": destination,
        "path": path,
        "total_distance": total_dist,
        "edges_count": len(path) - 1,
        "visited_count": len(visited),
        "execution_time_us": exec_time_us,
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
        "message": f"Fewest-hops route found ({len(path) - 1} hops, total distance {total_dist} m).",
        "note": "BFS finds minimum edge count, which may not be the shortest physical distance."
    }


def compare_algorithms(graph: CampusGraph, start: str, destination: str) -> Dict[str, Any]:
    """
    Runs both Dijkstra's algorithm and BFS on the same query to provide
    a side-by-side pedagogical DSA comparison.
    """
    dijkstra_res = dijkstra_shortest_path(graph, start, destination, include_blocked=False)
    bfs_res = bfs_shortest_hops(graph, start, destination, include_blocked=False)

    distance_diff = None
    hop_diff = None
    same_path = False

    if dijkstra_res["found"] and bfs_res["found"]:
        distance_diff = round(bfs_res["total_distance"] - dijkstra_res["total_distance"], 2)
        hop_diff = bfs_res["edges_count"] - dijkstra_res["edges_count"]
        same_path = (dijkstra_res["path"] == bfs_res["path"])

    return {
        "dijkstra": dijkstra_res,
        "bfs": bfs_res,
        "same_path": same_path,
        "distance_difference_meters": distance_diff,
        "hops_difference": hop_diff,
        "pedagogical_insight": (
            "Dijkstra's Algorithm accounts for pathway weights (meters), finding the minimal physical walking distance. "
            "BFS treats every edge as equal weight (1 hop), minimizing the number of turns/intersections. "
            f"{'In this scenario, BFS selected a path that was longer in distance by ' + str(distance_diff) + ' meters to save hops.' if (distance_diff and distance_diff > 0) else 'In this scenario, the fewest-hop path also happened to be the shortest physical distance.'}"
        )
    }


def get_step_by_step_instructions(
    graph: CampusGraph,
    path: List[str],
    walking_speed_m_per_min: float = 80.0
) -> List[Dict[str, Any]]:
    """
    Generates human-friendly walking instructions and time estimates for each leg of a path.
    """
    if not path or len(path) < 2:
        return []

    instructions = []
    cumulative_distance = 0.0
    cumulative_time = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        dist = graph.get_edge_distance(u, v)
        time_mins = round(dist / walking_speed_m_per_min, 1)

        cumulative_distance += dist
        cumulative_time += time_mins

        u_meta = graph.nodes.get(u, {})
        v_meta = graph.nodes.get(v, {})

        instructions.append({
            "step_number": i + 1,
            "from_node": u,
            "to_node": v,
            "segment_distance": dist,
            "segment_time_mins": time_mins,
            "cumulative_distance": round(cumulative_distance, 2),
            "cumulative_time_mins": round(cumulative_time, 1),
            "from_category": u_meta.get("category", "General"),
            "to_category": v_meta.get("category", "General"),
            "instruction_text": f"Walk from **{u}** to **{v}** along the designated pathway ({dist:.0f} m, ~{time_mins:.1f} min)."
        })

    return instructions
