from typing import TypedDict, Optional, Any, Dict
from langgraph.graph import StateGraph, END

from agents.monitor_agent import analyze_congestion, predict_congestion
from agents.signal_agent import optimize_signal_timing
from agents.route_agent import suggest_route
from agents.emergency_agent import activate_green_corridor
from agents.analytics_agent import generate_report


class TrafficState(TypedDict):
    intent: str
    payload: Dict[str, Any]
    result: Optional[Any]


def route_intent(state: TrafficState) -> TrafficState:
    # The Streamlit UI already decides intent via tabs (monitor / signal /
    # route / emergency / analytics). This node exists so you can later swap
    # in an LLM-based intent classifier here for free-text/voice routing
    # without changing the rest of the graph.
    return state


def monitor_node(state: TrafficState) -> TrafficState:
    p = state["payload"]
    congestion = analyze_congestion(p["junction_name"], p["road_a_density"], p["road_b_density"])
    prediction = predict_congestion(p["junction_name"], p.get("time_of_day", "now"))
    state["result"] = {"congestion": congestion, "prediction": prediction}
    return state


def signal_node(state: TrafficState) -> TrafficState:
    p = state["payload"]
    state["result"] = optimize_signal_timing(
        p["junction_name"], p["road_a_density"], p["road_b_density"]
    )
    return state


def route_node(state: TrafficState) -> TrafficState:
    p = state["payload"]
    state["result"] = suggest_route(
        p["source"], p["destination"], p.get("traffic_context", "")
    )
    return state


def emergency_node(state: TrafficState) -> TrafficState:
    p = state["payload"]
    state["result"] = activate_green_corridor(
        p["junction_name"], p["vehicle_type"], p.get("direction", "")
    )
    return state


def analytics_node(state: TrafficState) -> TrafficState:
    p = state["payload"]
    state["result"] = generate_report(p["traffic_logs"])
    return state


def build_graph():
    graph = StateGraph(TrafficState)
    graph.add_node("router", route_intent)
    graph.add_node("monitor", monitor_node)
    graph.add_node("signal", signal_node)
    graph.add_node("route", route_node)
    graph.add_node("emergency", emergency_node)
    graph.add_node("analytics", analytics_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "monitor": "monitor",
            "signal": "signal",
            "route": "route",
            "emergency": "emergency",
            "analytics": "analytics",
        },
    )
    graph.add_edge("monitor", END)
    graph.add_edge("signal", END)
    graph.add_edge("route", END)
    graph.add_edge("emergency", END)
    graph.add_edge("analytics", END)

    return graph.compile()


traffic_graph = build_graph()


def run_agent(intent: str, payload: Dict[str, Any]):
    result_state = traffic_graph.invoke({"intent": intent, "payload": payload, "result": None})
    return result_state["result"]
