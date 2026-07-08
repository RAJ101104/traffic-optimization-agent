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


VEHICLE_TYPES = ["Ambulance", "Fire Truck", "Police Vehicle"]


def activate_green_corridor(junction_name: str, vehicle_type: str, direction: str = "") -> dict:
    """Gives an approaching emergency vehicle priority through the junction by
    clearing a green corridor and holding conflicting signals red."""
    llm = get_llm(temperature=0.2)
    prompt = f"""You are an AI emergency-priority agent for junction "{junction_name}".

An emergency vehicle is approaching:
- Type: {vehicle_type}
- Direction: {direction or "not specified"}

Design an immediate green-corridor response: which signal(s) should turn green,
which should be held red, and what instructions should be sent to nearby junctions.

Return ONLY valid JSON in this exact format:
{{
  "status": "Green Corridor Activated",
  "signal_action": "1 short sentence on which lane/road gets green",
  "instructions": "1-2 sentence instruction for nearby junctions/traffic police",
  "estimated_clearance_seconds": <integer>
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
