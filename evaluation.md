# evaluation.md - SalesGym Architecture Trade-offs

## Architecture Decisions

### Why Evolutionary (8 strategies) vs Single Agent?

**Chosen:** Population of 8 competing strategies with selection/mutation/crossover.

**Alternative:** Single agent improving linearly after each call.

**Trade-off:**
- Evolutionary approach explores more of the strategy space simultaneously
- 8x more API calls per generation (cost: ~$0.07 vs ~$0.01 per gen with Gemini)
- Better at avoiding local optima - if one approach plateaus, others may find better paths
- Produces a strategy diversity metric (how different are the surviving strategies?)
- Risk: premature convergence if all strategies converge to the same approach

**Verdict:** The 7x cost increase is negligible ($0.07 vs $0.01) and the exploration benefit is significant.

### Why Gemini Flash for Calls + Claude for Analysis?

**Chosen:** Gemini Flash (cheap) for role-playing conversations, Claude Sonnet (smart) for analysis/evolution.

**Alternative 1:** Claude for everything - better quality but ~30x more expensive for calls.
**Alternative 2:** Gemini for everything - cheaper but weaker at nuanced analysis.

**Trade-off:**
- Gemini Flash: $0.10/M input, $0.40/M output - good enough for role-play
- Claude Sonnet: $3/$15 per M - needed for pattern recognition and rule generation
- Hybrid saves ~95% on call costs while keeping analysis quality high
- Risk: Gemini's role-play may be lower quality, affecting simulation realism

**Verdict:** Hybrid is optimal. Calls don't need Claude-level reasoning; analysis does.

### Why Dify + n8n (not pure Python)?

**Chosen:** Dify hosts the agent, n8n orchestrates the pipeline.

**Alternative:** Pure Python script doing everything.

**Trade-off:**
- Dify provides: conversation state management, built-in UI, model provider integration
- n8n provides: visual workflow, error retry, scheduling, loop handling
- More setup time vs faster development
- The brief explicitly recommends n8n/Dify
- Visual workflow is easier for reviewers to understand

**Verdict:** Using both demonstrates architectural thinking and addresses the brief's requirements.

### Why JSON Files (not Database)?

**Chosen:** JSON files in /data directory.

**Alternative:** SQLite or PostgreSQL.

**Trade-off:**
- JSON is human-readable - reviewer can inspect data directly
- Git-friendly - data changes are visible in commits
- No database setup needed
- Won't scale past ~1000 calls, but demo only needs ~72
- No query optimization, but data is small enough that brute-force is fine

**Verdict:** JSON is correct for a demo. Production would use a database.

## Evaluation Metrics

### 1. Conversion Rate (Primary)

- **What:** Percentage of simulated calls where customer agreed to trial
- **Baseline (Gen 0):** Expected ~30-40%
- **Target (Gen 2):** Expected ~60-70%
- **Pass condition:** Gen 2 conversion > Gen 0 conversion
- **How calculated:** `converted_calls / total_calls` per generation

### 2. Rule Quality

- **What:** Are improvement rules backed by evidence from actual call data?
- **Measurement:** % of rules with specific evidence citations (>10 chars)
- **Pass condition:** >=50% of rules have evidence

### 3. Adversarial Robustness

- **What:** Can the final generation's agent outperform the first generation's baseline?
- **Measurement:** Final gen conversion rate vs Gen 0 conversion rate
- **Pass condition:** Final > Gen 0

## Scoring Formula

Each call produces a fitness score (0-100):

```
score = 0
if converted:     score += 50   # Did the sale happen?
score += rapport * 30            # How well did the agent connect? (0-30)
score += max(0, (10 - turns)) * 2  # How efficiently? (0-20)
if objection_handled: score += 10  # Did agent address concerns?
```

- **High score example:** converted=True, rapport=0.8, turns=4, handled=True -> 96/100
- **Low score example:** converted=False, rapport=0.1, turns=2, handled=False -> 19/100

## Memory Architecture

The feedback loop works through three layers:

1. **Conversation History** (`data/conversations/gen_N/`) - Raw transcripts
2. **Outcome Aggregation** (`data/memory/outcomes.json`) - Win rates, objection patterns
3. **Improvement Rules** (`data/memory/rules.json`) - "When X, try Y" rules with evidence

Rules are injected into the agent's system prompt before each call, creating the feedback loop:
`outcome -> analysis -> script adjustment -> better outcome`

## Cost Analysis

| Component | Per Generation | Per Full Run (3 gen) |
|-----------|---------------|---------------------|
| Gemini Flash (24 calls) | ~$0.02 | ~$0.07 |
| Claude Sonnet (analysis) | ~$0.15 | ~$0.45 |
| Claude Sonnet (evolution) | ~$0.15 | ~$0.45 |
| ElevenLabs TTS | Free tier | Free tier |
| **Total** | **~$0.32** | **~$0.97** |

## Limitations

1. **Simulated customers, not real humans** - Gemini may not perfectly mimic real customer behavior
2. **Text-based evaluation of voice calls** - rapport scoring is approximate
3. **Small sample size** - 24 calls per generation is enough for a demo but not statistically significant
4. **No A/B significance testing** - improvement could be noise with such small N
5. **Strategy convergence** - after 3+ generations, strategies may all look similar

## Production Roadmap

If this were a production system:
- Replace JSON with PostgreSQL for scale
- Add A/B testing with statistical significance
- Use real customer interactions (not simulated)
- Add more customer personas for diversity
- Implement rollback if a generation performs worse
- Add cost monitoring and budget limits
- Deploy granular n8n workflow with per-step nodes
