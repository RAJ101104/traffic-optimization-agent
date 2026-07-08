import streamlit as st
from database.db import (
    init_db, ensure_junction, log_traffic, save_signal_timing,
    save_emergency_alert, save_route, get_dashboard_data
)
from graph.workflow import run_agent
from agents.emergency_agent import VEHICLE_TYPES

st.set_page_config(page_title="Traffic Optimization Agent", page_icon="🚦", layout="wide")
init_db()

# --- Sidebar ---
st.sidebar.title("🚦 Traffic Optimization Agent")
st.sidebar.caption("AI-powered smart traffic management · SDG 11")
junction_name = st.sidebar.text_input("Junction name", "Junction A")

if not junction_name:
    st.title("Welcome to the Traffic Optimization Agent")
    st.write("Enter a junction name in the sidebar to get started.")
    st.stop()

ensure_junction(junction_name)
st.sidebar.success(f"Monitoring: {junction_name}")

(tab_monitor, tab_signal, tab_route, tab_emergency, tab_analytics) = st.tabs(
    ["📡 Live Monitoring", "🟢 Signal Control", "🗺️ Route Optimizer",
     "🚑 Emergency Priority", "📊 Analytics"]
)

# --- Tab 1: AI Traffic Monitoring + Congestion Prediction ---
with tab_monitor:
    st.header("Live traffic monitoring")
    st.caption("Enter current density readings (0-100 scale, where 100 = gridlock). "
               "In production these come from CCTV/IoT sensors.")

    col1, col2 = st.columns(2)
    road_a = col1.slider("Road A density", 0, 100, 40)
    road_b = col2.slider("Road B density", 0, 100, 30)
    time_of_day = st.selectbox(
        "Time of day", ["Morning peak", "Midday", "Evening peak", "Night"]
    )

    if st.button("Analyze Traffic", key="monitor_btn"):
        with st.spinner("AI agent analyzing junction..."):
            result = run_agent("monitor", {
                "junction_name": junction_name,
                "road_a_density": road_a,
                "road_b_density": road_b,
                "time_of_day": time_of_day,
            })
        congestion = result["congestion"]
        prediction = result["prediction"]

        level_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(
            congestion["congestion_level"], "⚪"
        )
        st.subheader(f"{level_icon} Current congestion: {congestion['congestion_level']}")
        st.write(congestion["analysis"])
        st.info(f"Recommended action: {congestion['recommended_action']}")

        st.subheader("🔮 Congestion prediction")
        st.write(
            f"Predicted level in ~{prediction['expected_peak_in_minutes']} min: "
            f"**{prediction['predicted_congestion']}**"
        )
        st.caption(prediction["reasoning"])
        st.info(f"Proactive step: {prediction['proactive_recommendation']}")

        log_traffic(
            junction_name, road_a, road_b,
            congestion["congestion_level"], congestion["analysis"]
        )

# --- Tab 2: Smart Traffic Signal Control ---
with tab_signal:
    st.header("Dynamic signal timing")
    st.caption("The AI reallocates green-light seconds based on which road is more congested.")

    col1, col2 = st.columns(2)
    sig_road_a = col1.slider("Road A density", 0, 100, 40, key="sig_a")
    sig_road_b = col2.slider("Road B density", 0, 100, 30, key="sig_b")

    if st.button("Optimize Signal Timing"):
        with st.spinner("Calculating optimal signal split..."):
            timing = run_agent("signal", {
                "junction_name": junction_name,
                "road_a_density": sig_road_a,
                "road_b_density": sig_road_b,
            })
        c1, c2 = st.columns(2)
        c1.metric("Road A green time", f"{timing['road_a_green_seconds']}s")
        c2.metric("Road B green time", f"{timing['road_b_green_seconds']}s")
        st.info(timing["reasoning"])
        save_signal_timing(
            junction_name, timing["road_a_green_seconds"],
            timing["road_b_green_seconds"], timing["reasoning"]
        )

# --- Tab 3: Route Optimization ---
with tab_route:
    st.header("Suggest the fastest route")
    col1, col2 = st.columns(2)
    source = col1.text_input("Source", placeholder="e.g. College")
    destination = col2.text_input("Destination", placeholder="e.g. Railway Station")
    traffic_context = st.text_area(
        "Known traffic context (optional)",
        placeholder="e.g. Junction A is heavily congested this morning"
    )

    if st.button("Suggest Route"):
        if source.strip() and destination.strip():
            with st.spinner("Finding the best route..."):
                route = run_agent("route", {
                    "source": source, "destination": destination,
                    "traffic_context": traffic_context,
                })
            st.subheader(f"🛣️ {route['recommended_route']}")
            st.metric("Estimated travel time", route["estimated_time"])
            st.caption(f"Alternate: {route['alternate_route']}")
            st.info(route["reason"])
            save_route(
                source, destination, route["recommended_route"],
                route["estimated_time"], route["reason"]
            )
        else:
            st.warning("Please enter both a source and a destination.")

# --- Tab 4: Emergency Vehicle Priority ---
with tab_emergency:
    st.header("Activate a green corridor")
    col1, col2 = st.columns(2)
    vehicle_type = col1.selectbox("Vehicle type", VEHICLE_TYPES)
    direction = col2.text_input("Approaching from (optional)", placeholder="e.g. North")

    if st.button("🚨 Activate Green Corridor"):
        with st.spinner("Clearing signals for emergency vehicle..."):
            alert = run_agent("emergency", {
                "junction_name": junction_name,
                "vehicle_type": vehicle_type,
                "direction": direction,
            })
        st.success(f"✅ {alert['status']} at {junction_name}")
        st.write(f"**Signal action:** {alert['signal_action']}")
        st.write(f"**Instructions to nearby junctions:** {alert['instructions']}")
        st.metric("Estimated clearance time", f"{alert['estimated_clearance_seconds']}s")
        save_emergency_alert(
            junction_name, vehicle_type, alert["status"], alert["instructions"]
        )

# --- Tab 5: Analytics ---
with tab_analytics:
    st.header("Traffic analytics")
    data = get_dashboard_data()

    col1, col2, col3 = st.columns(3)
    col1.metric("Readings logged", len(data["traffic_logs"]))
    col2.metric("Signal adjustments", len(data["signals"]))
    col3.metric("Emergency alerts handled", len(data["alerts"]))

    if st.button("Generate Report"):
        with st.spinner("Generating analytics report..."):
            report = run_agent("analytics", {"traffic_logs": data["traffic_logs"]})
        c1, c2 = st.columns(2)
        c1.metric("Avg. density", f"{report['avg_density']}/100")
        c1.metric("High-congestion events", report["high_congestion_events"])
        c2.metric("Est. fuel saved", f"{report['estimated_fuel_saved_liters']} L")
        c2.metric("Est. CO2 reduced", f"{report['estimated_co2_reduced_kg']} kg")
        st.info(report["summary"])

    if data["traffic_logs"]:
        st.subheader("Recent readings")
        for row in data["traffic_logs"][:10]:
            st.write(
                f"**{row['junction_name']}** — Road A: {row['road_a_density']}, "
                f"Road B: {row['road_b_density']} · {row['congestion_level']} "
                f"({row['timestamp']})"
            )
    else:
        st.write("No traffic data logged yet. Try Live Monitoring first.")
