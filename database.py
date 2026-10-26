"""
Database Module for Smart Campus PathFinder.
Manages persistent SQLite storage for campus locations, pathway connections,
blocked pathways, and route search logs using parameterized SQL queries and transactions.
"""

import sqlite3
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from config import DEFAULT_DB_PATH, DEFAULT_COORDINATES


class CampusDatabase:
    """Encapsulates SQLite database operations with atomic transactions and validation."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Creates the required tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Locations Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Academic',
                    x REAL NOT NULL DEFAULT 0.0,
                    y REAL NOT NULL DEFAULT 0.0,
                    description TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Connections Table (Undirected edges stored in canonical alphabetical order)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    destination_name TEXT NOT NULL,
                    distance REAL NOT NULL CHECK(distance > 0),
                    is_blocked INTEGER NOT NULL DEFAULT 0 CHECK(is_blocked IN (0, 1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_name, destination_name),
                    FOREIGN KEY(source_name) REFERENCES locations(name) ON UPDATE CASCADE ON DELETE CASCADE,
                    FOREIGN KEY(destination_name) REFERENCES locations(name) ON UPDATE CASCADE ON DELETE CASCADE
                );
            """)

            # Search History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_location TEXT NOT NULL,
                    destination_location TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    distance REAL NOT NULL,
                    edges_count INTEGER NOT NULL,
                    path_taken TEXT NOT NULL,
                    execution_time_us REAL DEFAULT 0.0,
                    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    @staticmethod
    def _canonical_pair(u: str, v: str) -> Tuple[str, str]:
        """Ensures source < destination alphabetically for undirected consistency."""
        return (u, v) if u < v else (v, u)

    # -------------------------------------------------------------------------
    # Location Operations
    # -------------------------------------------------------------------------

    def add_location(
        self,
        name: str,
        category: str = "Academic",
        x: float = 0.0,
        y: float = 0.0,
        description: str = ""
    ) -> int:
        """Inserts a new campus location."""
        name = name.strip()
        if not name:
            raise ValueError("Location name cannot be empty.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO locations (name, category, x, y, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, category.strip(), float(x), float(y), description.strip())
            )
            conn.commit()
            return cursor.lastrowid

    def update_location(
        self,
        current_name: str,
        new_name: Optional[str] = None,
        category: Optional[str] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        description: Optional[str] = None
    ) -> None:
        """Updates attributes of an existing campus location."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM locations WHERE name = ?", (current_name,))
            existing = cursor.fetchone()
            if not existing:
                raise ValueError(f"Location '{current_name}' not found.")

            target_name = (new_name.strip() if new_name and new_name.strip() else current_name)
            target_category = (category.strip() if category is not None else existing["category"])
            target_x = float(x) if x is not None else existing["x"]
            target_y = float(y) if y is not None else existing["y"]
            target_desc = description.strip() if description is not None else existing["description"]

            cursor.execute(
                """
                UPDATE locations
                SET name = ?, category = ?, x = ?, y = ?, description = ?
                WHERE name = ?
                """,
                (target_name, target_category, target_x, target_y, target_desc, current_name)
            )
            conn.commit()

    def delete_location(self, name: str) -> None:
        """Deletes a location and cascades deletion to associated connections."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM locations WHERE name = ?", (name,))
            if cursor.rowcount == 0:
                raise ValueError(f"Location '{name}' does not exist.")
            conn.commit()

    def get_all_locations(self) -> List[Dict[str, Any]]:
        """Returns all locations ordered alphabetically by name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, category, x, y, description, created_at FROM locations ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def get_location_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Finds a single location by its exact name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, category, x, y, description FROM locations WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # -------------------------------------------------------------------------
    # Connection Operations
    # -------------------------------------------------------------------------

    def add_connection(
        self,
        u: str,
        v: str,
        distance: float,
        is_blocked: bool = False
    ) -> int:
        """Inserts a new pathway between two campus locations."""
        u, v = u.strip(), v.strip()
        if u == v:
            raise ValueError("A connection cannot start and end at the same location.")
        if distance <= 0:
            raise ValueError(f"Distance must be positive. Received {distance} m.")

        canon_u, canon_v = self._canonical_pair(u, v)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Ensure both locations exist
            cursor.execute("SELECT name FROM locations WHERE name IN (?, ?)", (canon_u, canon_v))
            existing_locs = {r[0] for r in cursor.fetchall()}
            if canon_u not in existing_locs:
                raise ValueError(f"Location '{canon_u}' does not exist.")
            if canon_v not in existing_locs:
                raise ValueError(f"Location '{canon_v}' does not exist.")

            cursor.execute(
                """
                INSERT INTO connections (source_name, destination_name, distance, is_blocked)
                VALUES (?, ?, ?, ?)
                """,
                (canon_u, canon_v, float(distance), 1 if is_blocked else 0)
            )
            conn.commit()
            return cursor.lastrowid

    def update_connection(
        self,
        u: str,
        v: str,
        distance: Optional[float] = None,
        is_blocked: Optional[bool] = None
    ) -> None:
        """Updates distance or blocked status of an existing pathway."""
        canon_u, canon_v = self._canonical_pair(u.strip(), v.strip())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT distance, is_blocked FROM connections WHERE source_name = ? AND destination_name = ?",
                (canon_u, canon_v)
            )
            existing = cursor.fetchone()
            if not existing:
                raise ValueError(f"Connection between '{u}' and '{v}' does not exist.")

            target_dist = float(distance) if distance is not None else existing["distance"]
            if target_dist <= 0:
                raise ValueError(f"Distance must be positive. Received {target_dist} m.")

            target_blocked = (1 if is_blocked else 0) if is_blocked is not None else existing["is_blocked"]

            cursor.execute(
                """
                UPDATE connections
                SET distance = ?, is_blocked = ?
                WHERE source_name = ? AND destination_name = ?
                """,
                (target_dist, target_blocked, canon_u, canon_v)
            )
            conn.commit()

    def delete_connection(self, u: str, v: str) -> None:
        """Removes a pathway between two locations."""
        canon_u, canon_v = self._canonical_pair(u.strip(), v.strip())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM connections WHERE source_name = ? AND destination_name = ?",
                (canon_u, canon_v)
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Connection between '{u}' and '{v}' does not exist.")
            conn.commit()

    def set_connection_blocked(self, u: str, v: str, is_blocked: bool = True) -> None:
        """Toggles blocked status of a pathway."""
        self.update_connection(u, v, is_blocked=is_blocked)

    def get_all_connections(self) -> List[Dict[str, Any]]:
        """Returns all connections ordered by source and destination."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, source_name, destination_name, distance, is_blocked, created_at
                FROM connections
                ORDER BY source_name ASC, destination_name ASC
                """
            )
            return [
                {
                    "id": row["id"],
                    "source_name": row["source_name"],
                    "destination_name": row["destination_name"],
                    "distance": row["distance"],
                    "is_blocked": bool(row["is_blocked"]),
                    "created_at": row["created_at"]
                }
                for row in cursor.fetchall()
            ]

    # -------------------------------------------------------------------------
    # Route Search History
    # -------------------------------------------------------------------------

    def log_search(
        self,
        start_location: str,
        destination_location: str,
        algorithm: str,
        distance: float,
        edges_count: int,
        path_taken: List[str],
        execution_time_us: float = 0.0
    ) -> None:
        """Logs a path calculation query into SQLite for audit and dashboard analytics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO search_history
                (start_location, destination_location, algorithm, distance, edges_count, path_taken, execution_time_us)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    start_location,
                    destination_location,
                    algorithm,
                    float(distance),
                    int(edges_count),
                    " -> ".join(path_taken) if path_taken else "None",
                    float(execution_time_us)
                )
            )
            conn.commit()

    def get_recent_searches(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves most recent route calculation records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, start_location, destination_location, algorithm, distance,
                       edges_count, path_taken, execution_time_us, searched_at
                FROM search_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear_search_history(self) -> None:
        """Clears all logged route searches."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_history")
            conn.commit()

    # -------------------------------------------------------------------------
    # Seed Data Initialization
    # -------------------------------------------------------------------------

    def seed_sample_campus(self) -> None:
        """
        Populates a clean campus network with 10 realistic interconnected locations.
        Includes pathways with varied distances to demonstrate Dijkstra vs BFS differences.
        """
        # 10 Campus Locations
        locations_data = [
            ("Main Gate", "Parking & Transport", 10.0, 10.0, "Primary campus entrance with security checkpoint"),
            ("Admin Block", "Administrative", 30.0, 25.0, "Dean's office, registrar, and administrative services"),
            ("Parking Area", "Parking & Transport", 15.0, 45.0, "Designated visitor and student two-wheeler / car parking"),
            ("Central Library", "Library", 50.0, 40.0, "Three-story central library with study zones and digital repository"),
            ("Computer Science Lab", "Laboratory", 70.0, 30.0, "Specialized programming, networking, and AI computing labs"),
            ("Engineering Block", "Academic", 75.0, 55.0, "Lecture theaters, faculty chambers, and tutorial rooms"),
            ("Campus Canteen", "Dining", 45.0, 65.0, "Central dining facility, cafeteria, and student refreshments"),
            ("Auditorium", "Auditorium & Events", 25.0, 75.0, "800-seater main stage hall for convocations and cultural fests"),
            ("Student Hostel", "Residential", 85.0, 80.0, "Undergraduate and postgraduate on-campus residential towers"),
            ("Sports Ground", "Sports & Recreation", 40.0, 90.0, "Athletics track, football arena, basketball and tennis courts"),
        ]

        # 16 Connected Pathways with illustrative distances in meters
        connections_data = [
            ("Main Gate", "Admin Block", 120.0, False),
            ("Main Gate", "Parking Area", 80.0, False),
            ("Parking Area", "Admin Block", 100.0, False),
            ("Parking Area", "Auditorium", 220.0, False),
            ("Admin Block", "Central Library", 140.0, False),
            ("Admin Block", "Computer Science Lab", 210.0, False),
            # Key comparison segment:
            # Direct Admin Block -> Campus Canteen: 260m (1 hop)
            # Via Central Library: Admin -> Central Library (140) + Library -> Canteen (110) = 250m (2 hops)
            # Demonstrates Dijkstra selects shorter distance (250m) while BFS selects fewer hops (1 hop, 260m)
            ("Admin Block", "Campus Canteen", 260.0, False),
            ("Central Library", "Computer Science Lab", 95.0, False),
            ("Central Library", "Campus Canteen", 110.0, False),
            ("Computer Science Lab", "Engineering Block", 130.0, False),
            ("Engineering Block", "Campus Canteen", 150.0, False),
            ("Engineering Block", "Student Hostel", 160.0, False),
            ("Campus Canteen", "Auditorium", 130.0, False),
            ("Campus Canteen", "Sports Ground", 175.0, False),
            ("Auditorium", "Sports Ground", 140.0, False),
            ("Student Hostel", "Sports Ground", 240.0, False),
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Clear existing data safely
            cursor.execute("DELETE FROM connections")
            cursor.execute("DELETE FROM locations")

            for name, cat, x, y, desc in locations_data:
                cursor.execute(
                    "INSERT INTO locations (name, category, x, y, description) VALUES (?, ?, ?, ?, ?)",
                    (name, cat, x, y, desc)
                )

            for u, v, dist, blocked in connections_data:
                canon_u, canon_v = self._canonical_pair(u, v)
                cursor.execute(
                    "INSERT INTO connections (source_name, destination_name, distance, is_blocked) VALUES (?, ?, ?, ?)",
                    (canon_u, canon_v, dist, 1 if blocked else 0)
                )

            conn.commit()
