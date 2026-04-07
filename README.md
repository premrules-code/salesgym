# SalesGym — Self-Improving Call Center Agent

> **Binox 2026 Take-Home — G1**

A co-evolutionary AI sales agent that conducts simulated sales calls, analyzes outcomes, and iteratively rewrites its own script to improve conversion rates.

**Live demo:** https://salesgym-production.up.railway.app

---

## Success Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| Agent simulates sales conversations **(voice)** | ✅ | Dify + Gemini run multi-turn calls. ElevenLabs voices every agent turn. Audio playable in dashboard. |
| Feedback loop: outcome → analysis → script adjustment | ✅ | Claude Sonnet reads all 24 transcripts, extracts patterns, generates rules injected into next generation's prompts. |
| Documents improvement logic ("When objection X, try response Y") | ✅ | Rules stored in `data/memory/rules.json` with trigger, old response, new response, and evidence. Visible in dashboard. |
| Handles at least 2 iteration cycles | ✅ | 3 generations: Gen 0 (17%) → Gen 1 (21%) → Gen 2 (17%). Strategies evolved across all 3. |

---

## How It Works

1. **8 sales strategies compete** against 3 simulated customer personas (24 calls per generation)
2. **Each agent turn is voiced** via ElevenLabs TTS
3. **Claude Sonnet analyzes outcomes** — finds patterns like "ROI framing converted 67% vs discounts at 12%"
4. **Generates improvement rules** — "When customer says 'too expensive', use ROI framing instead of discounts"
5. **Rules injected into agent prompts** for next generation
6. **Strategies evolve** — top 3 keep, middle 3 mutate, bottom 2 replaced by crossovers
7. **Customers get harder** each generation with new objections
8. **Repeat for 3 generations** — measurable improvement

## Architecture

```
Dify (sales agent) <──> Gemini Flash (customer simulator)
        │                         │
        ▼                         ▼
   ElevenLabs TTS           Call Transcripts
                                  │
                                  ▼
                        FastAPI (scoring + memory)
                                  │
                                  ▼
                        Claude Sonnet (analysis)
                                  │
                          ┌───────┴───────┐
                          ▼               ▼
                   Improvement      Evolution Engine
                   Rules            (keep/mutate/crossover)
                          │               │
                          └───────┬───────┘
                                  ▼
                          Next Generation
```

| Component | Tool | Role |
|-----------|------|------|
| Sales Agent | Dify Chatflow + Gemini | Runs multi-turn conversations with dynamic prompt injection |
| Customer Simulator | Gemini Flash | Role-plays as 3 customer personas with increasing difficulty |
| Voice | ElevenLabs TTS | Voices every agent turn — playable in dashboard |
| Scoring | Python FastAPI | Scores each call: conversion, rapport, efficiency, objection handling |
| Analysis | Claude Sonnet | Reads transcripts, finds patterns, generates improvement rules |
| Evolution | Claude Sonnet | Mutates mid-tier strategies, creates crossovers of top strategies |
| Orchestration | n8n | Pipeline automation (workflow JSON included) |
| Dashboard | Streamlit | Visual results, voice playback, strategy cards, flowcharts |
| Hosting | Railway | API + dashboard with persistent volume for data |

## Feedback Loop

The core of the project — how the agent improves itself:

```
outcome → analysis → script adjustment → better outcome
   ↑                                          │
   └──────────────────────────────────────────┘
```

1. **Outcome:** 24 calls scored (converted? rapport? objections handled?)
2. **Analysis:** Claude reads all transcripts, finds what worked and what didn't
3. **Rules Generated:** e.g., "When price objection → use ROI framing, not discounts"
4. **Script Adjustment:** Rules injected into agent's system prompt via Dify input variables
5. **Better Outcome:** Next generation's agent uses improved script against harder customers

Example rule from an actual run:
> **When:** Customer mentions budget concerns
> **Old approach:** Offer discounts
> **New approach:** Frame the cost as an investment with specific ROI numbers
> **Evidence:** ROI framing converted 3/4 budget-conscious customers vs 0/4 for discounting

## Quick Start

### Prerequisites

- Python 3.11+
- API keys: Anthropic, Google (Gemini), ElevenLabs, Dify

### Setup

```bash
git clone https://github.com/premrules-code/salesgym.git
cd salesgym
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Run Locally

```bash
# Start the API
uvicorn src.api:app --reload --port 8000

# In another terminal — start the dashboard
API_URL=http://localhost:8000 streamlit run src/dashboard.py
```

### Run Evolution

**Option A:** Dashboard — click "Run Evolution" button (recommended)

**Option B:** API:
```bash
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"num_generations": 3}'
```

**Option C:** n8n — import `docs/n8n-workflow.json` and execute

### Run Tests

```bash
python -m pytest tests/ -v
```

## n8n Integration

The evolution pipeline can be orchestrated via n8n:

1. Import `docs/n8n-workflow.json` into your n8n instance
2. Set `SALESGYM_API_URL` environment variable to the Railway URL
3. Click "Execute Workflow"

The workflow triggers evolution, polls for completion, collects results, and checks if the agent improved.

The API also supports webhooks — pass `webhook_url` in the POST body to get notified after each generation.

## Dify Setup

1. Create a new **Chatflow** app in Dify
2. Set model to Gemini 2.5 Flash (or Flash Lite)
3. Add `system_prompt` and `improvement_rules` as input variables
4. Use `{{system_prompt}}` in the system prompt field and `{{improvement_rules}}` in the prompt
5. Publish and copy the API key to `.env`

## Project Structure

```
salesgym/
├── src/
│   ├── api.py              # FastAPI backend + evolution runner
│   ├── arena.py            # Orchestrates one generation (24 calls)
│   ├── analyzer.py         # Claude analysis engine
│   ├── config.py           # Configuration + env vars
│   ├── customer_simulator.py # Gemini customer simulator
│   ├── dashboard.py        # Streamlit dashboard
│   ├── dify_agent.py       # Dify API integration
│   ├── eval.py             # Evaluation suite
│   ├── evolution.py        # Mutation + crossover engine
│   ├── memory.py           # Persistence layer (JSON)
│   ├── models.py           # Pydantic data models
│   ├── scoring.py          # Fitness scoring
│   ├── seed_data.py        # Initial strategies + personas
│   └── voice.py            # ElevenLabs TTS
├── tests/                  # 36 tests
├── docs/
│   └── n8n-workflow.json   # n8n workflow (importable)
├── data/                   # Runtime data (persisted on Railway volume)
├── evaluation.md           # Architecture trade-offs + cost analysis
├── start.sh                # Runs API + Streamlit on Railway
├── Procfile                # Railway entrypoint
└── README.md
```

## Cost

| Component | Per Generation | Full Run (3 gen) |
|-----------|---------------|-----------------|
| Gemini Flash (24 calls) | ~$0.02 | ~$0.07 |
| Claude Sonnet (analysis) | ~$0.15 | ~$0.45 |
| Claude Sonnet (evolution) | ~$0.15 | ~$0.45 |
| ElevenLabs TTS | Free tier | Free tier |
| **Total** | **~$0.32** | **~$0.97** |

## Evaluation

See [evaluation.md](./evaluation.md) for architecture trade-offs, scoring formula, memory architecture, limitations, and production roadmap.
