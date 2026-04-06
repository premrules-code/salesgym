# SalesGym - Self-Improving Call Center Agent

A co-evolutionary AI sales agent that conducts calls, analyzes outcomes, and iteratively rewrites its own script to improve conversion rates.

## How It Works

1. **8 sales strategies compete** against 3 simulated customer personas (24 calls per generation)
2. **Claude Sonnet analyzes outcomes** and generates improvement rules ("When price objection -> use ROI framing")
3. **Top strategies survive**, middle strategies mutate, bottom strategies are replaced by crossovers
4. **Customers get harder** each generation with new objections
5. **ElevenLabs voices** the agent so you can hear the improvement
6. **Repeat for 3 generations** - measurable conversion improvement

## Architecture

```
n8n (orchestration) --> Dify (sales agent) <--> Python/Gemini (customer sim)
                    --> Python/FastAPI (scoring, analysis, evolution, memory)
                    --> Streamlit (dashboard)
```

| Component | Tool | Role |
|-----------|------|------|
| Sales Agent | Dify + Gemini Flash | Runs conversations |
| Orchestration | n8n | Coordinates the evolution pipeline |
| Backend | Python FastAPI (Railway) | Scoring, analysis, evolution, memory |
| Voice | ElevenLabs TTS | Agent speech synthesis |
| Analysis | Claude Sonnet | Pattern recognition + rule generation |
| Dashboard | Streamlit | Visual results |

## Feedback Loop

```
outcome -> analysis -> script adjustment
   |                         |
   |    Calls run with       |
   |    improved script      |
   +<------------------------+
```

1. **Outcome:** 24 calls scored (converted? rapport? objections?)
2. **Analysis:** Claude finds patterns ("ROI framing won 67%, discounts won 0%")
3. **Script Adjustment:** Rules injected into agent's prompt ("When price -> use ROI")
4. **Repeat:** Next generation uses improved script against harder customers

## Quick Start

### Prerequisites

- Python 3.11+
- API keys: Anthropic, Google (Gemini), ElevenLabs
- Dify account (app.dify.ai)
- n8n account (app.n8n.cloud)

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/salesgym.git
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

# In another terminal - start the dashboard
streamlit run src/dashboard.py
```

### Run Evolution

Option A: Via dashboard - click "Run Evolution" button

Option B: Via API:
```bash
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"num_generations": 3}'
```

Option C: Via n8n - execute the workflow (see n8n setup below)

### Run Tests

```bash
python -m pytest tests/ -v
```

### Run Evaluation

```bash
python -m src.eval
```

### n8n Setup

1. Import the workflow from `docs/n8n-workflow.json` into your n8n instance
2. Set the API URL credential to your Railway deployment URL
3. Click "Execute Workflow"

### Dify Setup

1. Create a new Chatflow app in Dify
2. Set model to Gemini Flash
3. Add `system_prompt` as an input variable
4. Publish and copy API key to `.env`

## Evaluation

See [evaluation.md](./evaluation.md) for:
- Architecture trade-offs and justifications
- Scoring formula explanation
- Cost analysis
- Memory architecture
- Limitations and production roadmap

## Project Structure

```
salesgym/
├── src/
│   ├── api.py              # FastAPI backend
│   ├── arena.py            # Orchestrates one generation
│   ├── analyzer.py         # Claude analysis engine
│   ├── config.py           # Configuration
│   ├── customer_simulator.py # Gemini customer sim
│   ├── dashboard.py        # Streamlit dashboard
│   ├── dify_agent.py       # Dify API integration
│   ├── eval.py             # Evaluation suite
│   ├── evolution.py        # Mutation + crossover
│   ├── memory.py           # Persistence layer
│   ├── models.py           # Data models
│   └── seed_data.py        # Initial strategies + personas
├── tests/                  # Test suite
├── data/                   # Runtime data (JSON)
├── evaluation.md           # Architecture trade-offs
├── docs/                   # Design documents
│   └── n8n-workflow.json   # n8n workflow template
└── README.md
```

## Success Criteria Mapping

| Requirement | Implementation |
|---|---|
| Agent simulates sales conversations (voice) | Dify + Gemini conversations, ElevenLabs TTS |
| Feedback loop: outcome -> analysis -> script | Scoring -> Claude analysis -> rule injection |
| Documents improvement logic | `data/memory/rules.json` + dashboard display |
| 2+ iteration cycles | 3 generations (Gen 0, 1, 2) |
