# SalesGym — Co-Evolutionary Self-Improving Call Center Agent

## Overview

A sales agent that conducts calls, tracks outcomes, and iteratively rewrites its own script to improve conversion rates. Uses evolutionary strategy selection (8 competing approaches) and adversarial customer simulation (customers get harder each generation).

## Architecture

### Components

| Component | Tool | Role |
|-----------|------|------|
| Sales Agent | Dify (Chatflow + Gemini Flash) | Runs multi-turn sales conversations via API |
| Pipeline Orchestration | n8n (Cloud) | Coordinates: run calls → score → analyze → evolve → repeat |
| Backend Logic | Python (FastAPI) on Railway | Scoring, analysis (Claude), evolution, memory, voice |
| Voice | ElevenLabs TTS | Converts agent text to speech at every agent turn |
| Analysis | Claude Sonnet | Finds patterns in outcomes, generates improvement rules |
| Dashboard | Streamlit (Streamlit Cloud) | Leaderboard, evolution graph, call replays with audio |
| Storage | JSON files | Transparent, git-friendly, inspectable |

### Flow

```
n8n Workflow (one click to run):
  1. Get 8 strategies from Python API
  2. For each strategy × 3 customers = 24 calls:
     a. Set Dify agent's system prompt to this strategy
     b. Run multi-turn conversation (n8n relays between Dify agent and Python customer sim)
     c. ElevenLabs converts each agent turn to audio
     d. Save transcript + audio
  3. Send 24 transcripts to Python /api/score
  4. Send scores to Python /api/analyze (calls Claude Sonnet)
  5. Send analysis to Python /api/evolve (calls Claude Sonnet)
  6. If generation < 3 → loop back to step 2 with evolved strategies
  7. Run evals via Python /api/eval
```

### Memory System

- `data/conversations/gen_N/` — Full transcripts per generation
- `data/memory/outcomes.json` — Aggregated win rates, objection patterns
- `data/memory/rules.json` — Improvement rules (trigger → response + evidence)
- `data/strategies/gen_N.json` — Strategy snapshots per generation
- Agent reads rules before each call; rules accumulate across generations

### Evaluation

1. **Conversion metrics**: Did conversion rate improve gen-over-gen?
2. **Strategy quality**: Claude scores persuasion/naturalness of sample calls
3. **Adversarial robustness**: Gen 2 agent vs Gen 0 customers (should dominate)

### Generation Progression

- **Gen 0**: 8 raw strategies, no rules. Baseline ~37% conversion.
- **Gen 1**: First rules applied. Strategies mutated/crossed. Customers harder. ~54%.
- **Gen 2**: Refined rules. Converging strategies. Very hard customers. ~68%.
- **Gen 3+**: Diminishing returns. System supports unlimited generations.

### Cost Estimate

- Gemini Flash (72 calls): ~$0.07
- Claude Sonnet (15 calls): ~$0.50
- ElevenLabs TTS: Free tier (10K chars/month)
- Total per demo run: ~$0.60

### Hosting

- Python + Streamlit → Railway (free tier)
- n8n → n8n Cloud (user account)
- Dify → Dify Cloud (user account)
- Code → Public GitHub repo (shared with oscar@binox.com.hk)
