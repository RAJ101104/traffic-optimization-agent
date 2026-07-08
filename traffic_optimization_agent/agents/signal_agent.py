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


def optimize_signal_timing(junction_name: str, road_a_density: int, road_b_density: int,
                            min_green: int = 15, max_green: int = 90) -> dict:
    """Dynamically allocates green-signal seconds per road based on live density,
    instead of using fixed timings."""
    llm = get_llm(temperature=0.2)
    prompt = f"""You are an AI smart traffic signal controller for junction "{junction_name}".

Live vehicle density (0-100 scale):
- Road A: {road_a_density}
- Road B: {road_b_density}

Allocate green signal duration to each road so total cycle time stays reasonable
(between {min_green * 2} and {max_green * 2} seconds combined), giving more green time
to the more congested road while never giving either road less than {min_green}
seconds or more than {max_green} seconds.

Return ONLY valid JSON in this exact format:
{{
  "road_a_green_seconds": <integer>,
  "road_b_green_seconds": <integer>,
  "reasoning": "1-2 sentence explanation of the allocation"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
