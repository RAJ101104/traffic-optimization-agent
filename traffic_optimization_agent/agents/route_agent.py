import json
import re
from utils.llm import get_llm


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Could not parse JSON from model response.")


def suggest_route(source: str, destination: str, traffic_context: str = "") -> dict:
    """Recommends the fastest, least congested route between two points.

    `traffic_context` is a free-text summary of known congestion (e.g. from the
    monitoring agent) that should influence the recommendation. In Phase 2 this
    function can be swapped to call a real routing API (Google Maps / OSRM) and
    use the LLM only to explain the choice.
    """
    llm = get_llm(temperature=0.4)
    prompt = f"""You are an AI route optimization agent for a smart city traffic system.

Source: {source}
Destination: {destination}
Known current traffic context: {traffic_context or "no live data available, use general reasoning"}

Suggest the best route, considering congestion avoidance and travel time.

Return ONLY valid JSON in this exact format:
{{
  "recommended_route": "short description of the route (e.g. via named roads/landmarks)",
  "estimated_time": "e.g. '18 minutes'",
  "alternate_route": "short description of a backup route",
  "reason": "1-2 sentence explanation for why this route is best right now"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
