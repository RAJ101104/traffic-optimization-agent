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


def analyze_congestion(junction_name: str, road_a_density: int, road_b_density: int) -> dict:
    """Classifies current congestion level from live density readings (0-100 scale, vehicles/lane)."""
    llm = get_llm(temperature=0.2)
    prompt = f"""You are an AI traffic monitoring agent for junction "{junction_name}".

Live readings (vehicle density, 0-100 scale where 100 = gridlock):
- Road A: {road_a_density}
- Road B: {road_b_density}

Return ONLY valid JSON in this exact format:
{{
  "congestion_level": "Low" | "Medium" | "High",
  "analysis": "1-2 sentence explanation of what is happening at this junction",
  "recommended_action": "1 short sentence on what should happen next"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)


def predict_congestion(junction_name: str, time_of_day: str, context_note: str = "") -> dict:
    """Predicts near-future congestion so signals can be optimized proactively."""
    llm = get_llm(temperature=0.4)
    prompt = f"""You are an AI traffic prediction agent for junction "{junction_name}".

Time of day: {time_of_day}
Additional context: {context_note or "none provided"}

Based on typical urban traffic patterns for this time of day, predict what is about to happen.

Return ONLY valid JSON in this exact format:
{{
  "predicted_congestion": "Low" | "Medium" | "High",
  "expected_peak_in_minutes": <integer>,
  "reasoning": "1-2 sentence explanation",
  "proactive_recommendation": "1 short sentence on what to adjust in advance"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
