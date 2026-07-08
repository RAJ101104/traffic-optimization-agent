# Traffic Optimization Agent (Phase 1 MVP)

AI-powered smart traffic management system built with Python, LangChain, LangGraph, GROQ,
Streamlit, and SQLite. Contributes to **SDG 11 – Sustainable Cities and Communities** by
reducing congestion, improving emergency response, and cutting fuel use and emissions.

## Features included (Phase 1)
1. **AI Traffic Monitoring** — classifies live congestion level per junction
2. **Congestion Prediction** — forecasts near-future congestion before it gets severe
3. **Smart Signal Control** — dynamically allocates green-light time instead of fixed timings
4. **Route Optimization** — recommends the fastest, least congested route between two points
5. **Emergency Vehicle Priority** — activates a green corridor for ambulances/fire trucks/police
6. **Traffic Analytics** — average density, high-congestion events, estimated fuel/CO2 savings

## Project structure
```
traffic_optimization_agent/
├── app.py                     # Streamlit dashboard (entry point)
├── requirements.txt
├── .env.example
├── database/
│   └── db.py                   # SQLite: traffic logs, signals, alerts, routes
├── agents/
│   ├── monitor_agent.py         # Congestion analysis + prediction
│   ├── signal_agent.py          # Dynamic signal timing
│   ├── route_agent.py           # Route suggestions
│   ├── emergency_agent.py       # Green-corridor activation
│   └── analytics_agent.py       # Reports: fuel/CO2 savings, summaries
└── graph/
    └── workflow.py              # LangGraph router connecting the agents
```

## Setup in VS Code

### 1. Get a free GROQ API key
Sign up at https://console.groq.com and create an API key under "API Keys".

### 2. Open the project folder
In VS Code: File → Open Folder → select `traffic_optimization_agent`.

### 3. Create a virtual environment
Open the VS Code terminal (`` Ctrl+` ``) and run:

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

VS Code may prompt "Select Interpreter" — choose the one inside `venv`.

### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Add your API key
Copy `.env.example` to a new file named `.env`, then paste your key:
```
GROQ_API_KEY=gsk_your_actual_key_here
```
`.env` should never be committed to GitHub — it's already in `.gitignore`.

### 6. Run the app
```
streamlit run app.py
```
This opens the dashboard in your browser at `http://localhost:8501`.

## How it works
- Enter a **junction name** in the sidebar — this is the junction currently being managed.
- **Live Monitoring** tab → enter density readings, get an AI congestion analysis + a
  prediction of what happens next; logs get saved for analytics.
- **Signal Control** tab → the AI reallocates green-light seconds between Road A and
  Road B based on which is more congested (instead of a fixed 30/30 split).
- **Route Optimizer** tab → suggests the fastest route between a source and destination,
  optionally factoring in known congestion.
- **Emergency Priority** tab → simulates an approaching ambulance/fire truck/police vehicle
  and activates a green corridor with clear instructions.
- **Analytics** tab → aggregates logged data into average density, high-congestion event
  counts, and estimated fuel/CO2 savings from dynamic (vs. fixed) signal timing, plus an
  AI-written summary for city planners.

## Data source note (Phase 1 vs. real deployment)
This MVP uses **manually entered density values** (0-100 scale) as a stand-in for live
sensor feeds, and the AI reasons over that data to make decisions. This keeps the system
fully runnable with no hardware. The fuel/CO2 figures in Analytics are simplified
heuristics, not calibrated emissions models — see Phase 2 below for the upgrade path.

## Next steps (Phase 2 ideas from the concept note)
- **Smart City Integration**: replace manual density sliders with real feeds — CCTV +
  computer vision vehicle counts, or IoT loop/radar sensors — by writing a new function
  that fills the same `road_a_density` / `road_b_density` inputs the agents already expect.
- **Real routing**: swap `agents/route_agent.py` to call OpenStreetMap/Google Maps
  Directions API for the actual route/ETA, and keep the LLM only for the natural-language
  explanation.
- **Mobile Notifications**: add a lightweight notification table + a simple API endpoint
  (FastAPI) that a companion mobile app can poll for congestion/route alerts.
- **Free-text/voice routing**: the `graph/workflow.py` router node already has a comment
  marking where to add an LLM-based intent classifier for non-tab-based input (e.g. a
  traffic police radio transcript triggering the emergency agent automatically).
- **Multi-junction coordination**: extend the signal agent to consider neighboring
  junctions together (a "green wave") rather than one junction in isolation.

## Troubleshooting
- **`GROQ_API_KEY not found`** → check your `.env` file exists in the project root and
  has no quotes around the key.
- **`ModuleNotFoundError`** → make sure your venv is activated (you should see `(venv)`
  in the terminal prompt) and you ran `pip install -r requirements.txt` inside it.
- **JSON parsing errors from an agent** → the model occasionally wraps JSON in extra
  text; the parsing helpers already strip common cases, but if it persists, lower
  `temperature` in the relevant agent file or retry.
