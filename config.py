"""
Config configuration module for Smart Campus PathFinder.
Contains application constants, file paths, visual styling, and walking speed settings.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "campus.db"

# Human walking speed in meters per minute (approx. 4.8 km/h or 1.33 m/s)
DEFAULT_WALKING_SPEED_M_PER_MIN = 80.0

# Location Categories
LOCATION_CATEGORIES = [
    "Academic",
    "Administrative",
    "Library",
    "Laboratory",
    "Dining",
    "Residential",
    "Sports & Recreation",
    "Parking & Transport",
    "Auditorium & Events",
    "Utility & Support"
]

# Category Colors for Plotly Visualization
CATEGORY_COLORS = {
    "Academic": "#1E88E5",          # Vibrant Blue
    "Administrative": "#3949AB",    # Indigo
    "Library": "#8E24AA",           # Purple
    "Laboratory": "#00ACC1",        # Cyan
    "Dining": "#FB8C00",            # Orange
    "Residential": "#00897B",       # Teal
    "Sports & Recreation": "#43A047", # Green
    "Parking & Transport": "#5E35B1", # Deep Purple
    "Auditorium & Events": "#E53935", # Crimson Red
    "Utility & Support": "#6D4C41",  # Brown
}

# Edge Colors
COLOR_DEFAULT_EDGE = "#90A4AE"     # Neutral Grey-Blue
COLOR_BLOCKED_EDGE = "#E53935"     # Red
COLOR_HIGHLIGHT_PATH = "#00C853"   # Bright Emerald Green

# Sample Campus Layout Positions (X, Y) on a 100x100 grid for 2D Campus Map Visualization
DEFAULT_COORDINATES = {
    "Main Gate": (10, 10),
    "Admin Block": (30, 25),
    "Parking Area": (15, 45),
    "Central Library": (50, 40),
    "Computer Science Lab": (70, 30),
    "Engineering Block": (75, 55),
    "Campus Canteen": (45, 65),
    "Auditorium": (25, 75),
    "Student Hostel": (85, 80),
    "Sports Ground": (40, 90),
}
