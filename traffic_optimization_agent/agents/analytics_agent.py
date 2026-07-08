from utils.llm import get_llm


def _estimate_impact(traffic_logs: list) -> dict:
    """Deterministic back-of-envelope estimates from logged traffic data.
    These are simplified placeholders — swap in real fuel/emission models
    once IoT sensor data is available (see README Phase 2 notes)."""
    if not traffic_logs:
        return {
            "avg_density": 0,
            "high_congestion_events": 0,
            "estimated_fuel_saved_liters": 0,
            "estimated_co2_reduced_kg": 0,
        }

    densities = [
        (row["road_a_density"] + row["road_b_density"]) / 2 for row in traffic_logs
    ]
    avg_density = sum(densities) / len(densities)
    high_events = sum(1 for row in traffic_logs if row["congestion_level"] == "High")

    # Rough heuristic: each high-congestion event resolved faster by dynamic
    # signaling saves ~0.8L fuel and ~1.9kg CO2 across the junction, vs fixed timing.
    estimated_fuel_saved = round(high_events * 0.8, 2)
    estimated_co2_reduced = round(high_events * 1.9, 2)

    return {
        "avg_density": round(avg_density, 1),
        "high_congestion_events": high_events,
        "estimated_fuel_saved_liters": estimated_fuel_saved,
        "estimated_co2_reduced_kg": estimated_co2_reduced,
    }


def generate_report(traffic_logs: list) -> dict:
    """Combines deterministic metrics with an LLM-written narrative summary
    for the city authority dashboard."""
    metrics = _estimate_impact(traffic_logs)

    if not traffic_logs:
        return {
            **metrics,
            "summary": "No traffic data logged yet. Run some Live Monitoring checks "
                       "to start building analytics.",
        }

    llm = get_llm(temperature=0.4)
    recent = traffic_logs[:10]
    log_summary = "\n".join(
        f"- {row['junction_name']}: Road A={row['road_a_density']}, "
        f"Road B={row['road_b_density']}, level={row['congestion_level']}"
        for row in recent
    )
    prompt = f"""You are an AI traffic analytics agent writing a short report for a
city traffic authority.

Recent logged readings:
{log_summary}

Summary metrics:
- Average density: {metrics['avg_density']}/100
- High-congestion events: {metrics['high_congestion_events']}
- Estimated fuel saved vs fixed-timing signals: {metrics['estimated_fuel_saved_liters']} L
- Estimated CO2 reduction: {metrics['estimated_co2_reduced_kg']} kg

Write a concise 3-4 sentence summary covering: overall traffic health, any junction(s)
needing attention, and one concrete recommendation for city planners. Keep it under 100 words."""
    response = llm.invoke(prompt)

    return {**metrics, "summary": response.content}
