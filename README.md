# 🗺️ Smart Campus PathFinder — Intelligent Campus Navigation Using DSA

> **A Complete, Production-Quality Data Structures and Algorithms (DSA) College Mini-Project**  
> Built with **Python 3**, **Streamlit**, **NetworkX**, **Plotly**, and **SQLite**.

---

## 📌 1. Project Overview

**Smart Campus PathFinder** is an interactive, graph-theoretic campus navigation system designed to help students, visitors, and university personnel find the shortest walking routes between campus landmarks (academic blocks, lecture theaters, laboratories, libraries, canteens, hostels, parking facilities, and administrative offices).

The application models physical campus pathways as an **undirected, weighted graph** and computes the optimal walking route using a manual implementation of **Dijkstra’s Algorithm** with Python’s native binary min-heap (`heapq`). It also includes **Breadth-First Search (BFS)** for pedagogical comparison, dynamic pathway blocking with automatic detour recalculation, persistent SQLite data storage, and rich 2D interactive spatial visualization.

---

## 🚀 2. Key Features

* **Shortest Route Finder:** Calculates the minimum physical walking distance (in meters) and estimated walking time using **Dijkstra's Algorithm** with a binary min-heap ($O((V + E) \log V)$).
* **Pedagogical Algorithm Comparison:** Compares **Dijkstra** (minimum physical meters) with **Breadth-First Search (BFS)** (minimum edge hops / turns), demonstrating where and why the two algorithms diverge on weighted graphs.
* **Interactive 2D Campus Map:** Built using **NetworkX** and **Plotly** with color-coded categories, route highlighting in vibrant emerald green, and interactive hover tooltips.
* **Dynamic Pathway Closures & Detours:** Easily simulate construction or event closures. Blocked pathways are highlighted in red dashed lines and automatically bypassed in both directions.
* **Turn-by-Turn Walking Directions:** Generates human-friendly step-by-step guidance cards with segment distances and cumulative walking times based on configurable walking speed.
* **Complete Campus Management (CRUD):** Add, edit, or delete locations and pathways with instant database persistence and in-memory graph synchronization.
* **Persistent SQLite Storage:** Location coordinates, pathway weights, closure states, and search history persist across restarts using parameterized SQL queries and transactions.
* **100% Automated Test Suite:** 23 comprehensive tests written in `pytest` covering all edge cases, validations, graph mutations, and algorithmic invariants.

---

## 🏗️ 3. Project File Structure

```text
smart-campus-pathfinder/
├── app.py                     # Streamlit frontend with 9 distinct modules & custom styling
├── config.py                  # Global configurations, speeds, categories, and color schemes
├── graph.py                   # Pure DSA: CampusGraph class with Adjacency List representation
├── algorithms.py              # Pure DSA: Dijkstra (heapq), BFS (deque), and comparisons
├── database.py                # SQLite database management, schema, transactions, and seeding
├── campus_service.py          # Business logic orchestrator synchronizing DB and in-memory graph
├── visualization.py           # NetworkX & Plotly 2D interactive campus graph visualizer
├── requirements.txt           # Python library dependencies
├── README.md                  # Comprehensive setup, execution, and architectural guide
├── data/                      # Persistent storage directory
│   └── campus.db              # SQLite campus database
├── tests/                     # Automated pytest test suite (23 tests)
│   ├── test_algorithms.py     # Tests for Dijkstra, BFS, base cases, and divergences
│   ├── test_campus_service.py # End-to-end integration tests
│   ├── test_database.py       # SQLite CRUD, constraints, and persistence tests
│   └── test_graph.py          # Graph data structure and validation tests
└── docs/                      # Academic documentation for college submission
    ├── project_report.md      # Complete 28-section academic project report
    └── viva_questions.md      # 30+ Viva Voce questions with detailed answers
```

---

## ⚡ 4. Installation & Quick Start

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "c:\Users\sande\OneDrive\Desktop\DSA@"
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Launch the Streamlit Web Application
```bash
python -m streamlit run app.py
```
After running this command, open your web browser at:
👉 **`http://localhost:8501`**

---

## 🧪 5. Running the Automated Test Suite

The test suite validates graph integrity, algorithm correctness, edge cases, and SQLite persistence.

Run tests using `pytest`:
```bash
python -m pytest -v
```

### Test Results Summary:
* **Total Tests:** 23
* **Passed:** 23 (100% pass rate)
* **Execution Time:** ~0.9 seconds

---

## 🧠 6. DSA Concepts & Complexity Analysis

| Data Structure / Algorithm | Python Module | Role in Project | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Weighted Graph** | Adjacency List (`dict` of `dict`) | Stores locations and weighted pathways | $O(1)$ neighbor lookup | $O(V + E)$ |
| **Dijkstra's Algorithm** | `heapq` (Min-Heap Priority Queue) | Calculates minimum walking distance (meters) | $O((V + E) \log V)$ | $O(V + E)$ |
| **Breadth-First Search (BFS)**| `collections.deque` (FIFO Queue) | Calculates minimum hop/edge route | $O(V + E)$ | $O(V)$ |
| **Blocked Edge Handling** | Canonical Pair Hash Set (`set`) | Bypasses closed pathways in $O(1)$ time | $O(1)$ check | $O(E_{blocked})$ |
| **Path Reconstruction** | Backtracking via Predecessor Dict | Reconstructs ordered list of locations | $O(V)$ | $O(V)$ |

---

## 🎓 7. Faculty Demonstration & Viva Guide

When presenting this project to your college evaluator or external viva examiner, follow this recommended walkthrough:

1. **Dashboard (Module 1):** Point out the real-time summary cards (locations, pathways, closures) and the Plotly campus map.
2. **Shortest Route (Module 2):** Select **Main Gate** as Start and **Central Library** as Destination. Click **Calculate Shortest Route** to show the highlighted green path, distance (260m), time estimate (~3.2 mins), and turn-by-turn cards.
3. **Compare Algorithms (Module 4):** Select **Admin Block** to **Campus Canteen**. 
   * **Dijkstra:** Chooses Admin $\rightarrow$ Central Library $\rightarrow$ Campus Canteen (**2 hops, 250m**).
   * **BFS:** Chooses Admin $\rightarrow$ Campus Canteen direct (**1 hop, 260m**).
   * *Viva Explanation:* Explain that BFS minimizes edge count without considering weights, whereas Dijkstra accounts for edge weights in meters to find the true shortest physical distance.
4. **Blocked Paths & Detours (Module 7):** Block the pathway between `Admin Block` and `Central Library`. Show how the map turns the line into a red dotted pathway and reroutes paths via the Computer Science Lab automatically.
5. **Report & Viva Docs:** Direct faculty to [`docs/project_report.md`](docs/project_report.md) and [`docs/viva_questions.md`](docs/viva_questions.md).

---

## 📄 8. License & Academic Integrity

This project is created for academic coursework and demonstration. It is freely editable and suitable for undergraduate and diploma computer science curricula.
