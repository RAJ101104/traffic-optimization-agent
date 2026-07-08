import sqlite3
from contextlib import contextmanager

DB_PATH = "traffic_agent.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS junctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                junction_name TEXT,
                road_a_density INTEGER,
                road_b_density INTEGER,
                congestion_level TEXT,
                analysis TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                junction_name TEXT,
                road_a_green_seconds INTEGER,
                road_b_green_seconds INTEGER,
                reasoning TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emergency_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                junction_name TEXT,
                vehicle_type TEXT,
                status TEXT,
                instructions TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS route_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                destination TEXT,
                recommended_route TEXT,
                estimated_time TEXT,
                reason TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)


def ensure_junction(name: str):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO junctions (name) VALUES (?)", (name,))


def log_traffic(junction_name, road_a_density, road_b_density, congestion_level, analysis):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO traffic_logs (junction_name, road_a_density, road_b_density, "
            "congestion_level, analysis) VALUES (?, ?, ?, ?, ?)",
            (junction_name, road_a_density, road_b_density, congestion_level, analysis),
        )


def save_signal_timing(junction_name, road_a_green_seconds, road_b_green_seconds, reasoning):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO signal_status (junction_name, road_a_green_seconds, "
            "road_b_green_seconds, reasoning) VALUES (?, ?, ?, ?)",
            (junction_name, road_a_green_seconds, road_b_green_seconds, reasoning),
        )


def save_emergency_alert(junction_name, vehicle_type, status, instructions):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO emergency_alerts (junction_name, vehicle_type, status, instructions) "
            "VALUES (?, ?, ?, ?)",
            (junction_name, vehicle_type, status, instructions),
        )


def save_route(source, destination, recommended_route, estimated_time, reason):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO route_history (source, destination, recommended_route, "
            "estimated_time, reason) VALUES (?, ?, ?, ?, ?)",
            (source, destination, recommended_route, estimated_time, reason),
        )


def get_dashboard_data():
    with get_conn() as conn:
        traffic_logs = conn.execute(
            "SELECT * FROM traffic_logs ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        signals = conn.execute(
            "SELECT * FROM signal_status ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        alerts = conn.execute(
            "SELECT * FROM emergency_alerts ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        routes = conn.execute(
            "SELECT * FROM route_history ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        return {
            "traffic_logs": [dict(r) for r in traffic_logs],
            "signals": [dict(r) for r in signals],
            "alerts": [dict(r) for r in alerts],
            "routes": [dict(r) for r in routes],
        }
