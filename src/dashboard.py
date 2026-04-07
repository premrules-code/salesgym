import streamlit as st
import requests
import time
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="SalesGym", page_icon="🧬", layout="wide")

# Custom CSS for better look
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stMetric { background: #1e1e2e; padding: 1rem; border-radius: 0.5rem; }
    div[data-testid="stExpander"] { background: #0e1117; border-radius: 0.5rem; margin-bottom: 0.5rem; }
    .status-running { color: #f0ad4e; font-weight: bold; }
    .status-done { color: #5cb85c; font-weight: bold; }
    .call-win { border-left: 3px solid #5cb85c; padding-left: 0.5rem; margin: 0.3rem 0; }
    .call-loss { border-left: 3px solid #d9534f; padding-left: 0.5rem; margin: 0.3rem 0; }
</style>
""", unsafe_allow_html=True)


def api_get(path, timeout=5):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def api_post(path, data, timeout=10):
    try:
        r = requests.post(f"{API_URL}{path}", json=data, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ─── HEADER ───
st.markdown("# 🧬 SalesGym")
st.markdown("**Self-improving AI sales agent** — evolves its own script through simulated calls")
st.markdown("---")

# ─── STATUS CHECK ───
status = api_get("/api/status") or {"running": False, "generation": -1, "error": None}
results = api_get("/api/results") or []
rules = api_get("/api/rules") or []
eval_report = api_get("/api/eval")

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown("## Controls")

    if status["running"]:
        gen = status["generation"]
        st.markdown(f"""
        <div style="background:#2d2d3d;padding:1rem;border-radius:0.5rem;text-align:center;">
            <div style="font-size:2rem;">⏳</div>
            <div style="font-size:1.1rem;font-weight:bold;color:#f0ad4e;">Running</div>
            <div style="color:#aaa;">Generation {gen} in progress</div>
            <div style="color:#aaa;">{len(results)} gen(s) completed</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("🔄 Refresh", use_container_width=True, type="primary"):
            st.rerun()
    else:
        if results:
            st.markdown(f"""
            <div style="background:#1a3a1a;padding:1rem;border-radius:0.5rem;text-align:center;">
                <div style="font-size:2rem;">✅</div>
                <div style="font-size:1.1rem;font-weight:bold;color:#5cb85c;">Complete</div>
                <div style="color:#aaa;">{len(results)} generations done</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

        num_gens = st.selectbox("Generations", [1, 2, 3, 4, 5], index=2)
        if st.button("🚀 Run Evolution", use_container_width=True, type="primary"):
            resp = api_post("/api/run", {"num_generations": num_gens})
            if resp and resp.get("status") == "started":
                st.success(f"Started! Running {num_gens} generations...")
                time.sleep(2)
                st.rerun()
            elif resp and resp.get("status") == "already_running":
                st.warning("Already running!")
            elif resp and resp.get("error"):
                st.error(resp["error"])

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    st.markdown("---")
    st.markdown("#### How It Works")
    st.markdown("""
    1. **8 strategies** compete
    2. **24 calls** per generation
    3. **Claude** analyzes patterns
    4. **Top survive**, rest evolve
    5. **Customers get harder**
    6. **Rules** injected into prompts
    """)

    st.markdown("---")
    st.markdown("#### Tech Stack")
    st.markdown("""
    | | |
    |---|---|
    | Agent | Dify + Gemini |
    | Customers | Gemini Flash |
    | Analysis | Claude Sonnet |
    | Voice | ElevenLabs |
    | Backend | FastAPI |
    """)

# ─── AUTO REFRESH ───
if status["running"]:
    placeholder = st.empty()
    placeholder.info(f"⏳ Evolution running — Generation {status['generation']}. Auto-refreshing in 30s...")
    time.sleep(30)
    st.rerun()

# ─── NO RESULTS YET ───
if not results:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a3a5c,#1e1e2e);padding:1.5rem;border-radius:0.8rem;margin-bottom:1.5rem;border:1px solid #2a4a6c;">
        <div style="font-size:1.3rem;font-weight:bold;margin-bottom:0.5rem;">🚀 How to Run</div>
        <div style="font-size:1rem;line-height:1.8;">
            <strong>1.</strong> In the sidebar (left), select number of <strong>Generations</strong> (3 recommended)<br>
            <strong>2.</strong> Click <strong>"🚀 Run Evolution"</strong><br>
            <strong>3.</strong> Wait ~20-30 min — the page auto-refreshes every 30s<br>
            <strong>4.</strong> Watch strategies compete, evolve, and improve their conversion rates
        </div>
        <div style="color:#aaa;font-size:0.85rem;margin-top:0.8rem;">
            Each generation runs 24 simulated sales calls (8 strategies × 3 customers),
            then Claude analyzes patterns and evolves the strategies.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── WORKFLOW: HOW IT WORKS ───
    st.markdown("### 🔄 How the Self-Improvement Works")
    st.markdown("")

    # Step-by-step flow using colored HTML cards
    steps = [
        ("1", "#2563eb", "📞 Simulate Calls", "8 sales strategies each call 3 customer personas = <strong>24 calls</strong> per generation. Agent uses Dify + Gemini, customers simulated by Gemini Flash."),
        ("2", "#7c3aed", "📊 Score Each Call", "Every call scored on: <strong>Conversion</strong> (+50), <strong>Rapport</strong> (0-30), <strong>Efficiency</strong> (0-20), <strong>Objection handling</strong> (+10). Max score = 110."),
        ("3", "#db2777", "🧠 Analyze Patterns", "<strong>Claude Sonnet</strong> reads all 24 transcripts. Finds patterns like <em>\"ROI framing converted 67% vs discounts at 12%\"</em>. Generates improvement rules."),
        ("4", "#ea580c", "📝 Learn Rules", "Rules like: <em>\"When customer says 'too expensive' → use ROI framing, not discounts\"</em> are saved to memory and <strong>injected into future prompts</strong>."),
        ("5", "#16a34a", "🧬 Evolve Strategies", "<strong>Top 3</strong>: keep unchanged. <strong>Mid 3</strong>: mutate with new rules. <strong>Bottom 2</strong>: replaced by crossovers of the best. 8 new strategies emerge."),
        ("6", "#0891b2", "🔁 Repeat with Harder Customers", "Next generation: evolved strategies face <strong>tougher customers</strong> with new objections. Rules accumulate. Agent gets smarter each round."),
    ]

    for i in range(0, len(steps), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(steps):
                num, color, title, desc = steps[i + j]
                with col:
                    st.markdown(f"""
                    <div style="background:#1e1e2e;padding:1rem;border-radius:0.5rem;margin-bottom:0.8rem;border-left:4px solid {color};min-height:160px;">
                        <div style="color:{color};font-weight:bold;font-size:0.8rem;margin-bottom:0.3rem;">STEP {num}</div>
                        <div style="font-weight:bold;font-size:1.05rem;margin-bottom:0.4rem;">{title}</div>
                        <div style="color:#bbb;font-size:0.85rem;line-height:1.5;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Core feedback loop — one clear sentence
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a2a1a,#1e1e2e);padding:1rem 1.5rem;border-radius:0.5rem;border:1px solid #2a4a2a;text-align:center;margin:0.5rem 0 1rem 0;">
        <div style="font-size:1.1rem;font-weight:bold;margin-bottom:0.3rem;">The Feedback Loop</div>
        <div style="font-size:1rem;color:#bbb;">
            Call outcomes → Claude analyzes what worked → Generates rules → Rules injected into next generation's prompts → Better outcomes
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📅 What Happens Each Generation")

    gen_tabs = st.tabs(["Gen 0 — Baseline", "Gen 1 — First Evolution", "Gen 2 — Final Push"])

    with gen_tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Inputs")
            st.markdown("""
            - **8 original strategies** (Storyteller, Closer, Consultant, Friend, Expert, Challenger, Value First, Direct)
            - **3 easy customers** (Budget Bob, Skeptical Sarah, Busy Ben)
            - **No improvement rules** — cold start
            - **24 calls** total (8 strategies × 3 customers)
            """)
        with col2:
            st.markdown("#### What Happens")
            st.markdown("""
            1. Each strategy talks to each customer via Dify
            2. Gemini simulates realistic customer responses
            3. ElevenLabs voices the agent's responses
            4. Each call scored (conversion, rapport, efficiency)
            5. **Claude Sonnet** analyzes all 24 outcomes
            6. Generates first improvement rules
            7. Ranks strategies: KEEP / MUTATE / REPLACE
            """)
        st.markdown("#### Expected Output")
        st.markdown("""
        - **~25-35% conversion** (no rules yet, some strategies work naturally)
        - **~4 improvement rules** (e.g., "When price objection → use ROI framing not discounts")
        - **Strategy rankings** (e.g., Storyteller wins, Closer loses)
        """)

    with gen_tabs[1]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Inputs")
            st.markdown("""
            - **8 evolved strategies** (top 3 kept, mid 3 mutated with rules, bottom 2 replaced by crossovers)
            - **3 harder customers** — new objections added:
              - Bob: *"My nephew said he can set up a free backup"*
              - Sarah: *"Dropbox already has versioning. What do you do different?"*
              - Ben: *"Every call starts with 'this will be quick.' Prove it."*
            - **4+ improvement rules** injected into every agent prompt
            """)
        with col2:
            st.markdown("#### What Happens")
            st.markdown("""
            1. Evolved strategies face harder customers
            2. Rules guide agent: *"Use ROI framing"* instead of old approach
            3. Mutated strategies have refined pitches
            4. Crossover strategies combine best traits
            5. **Claude** generates more rules from new patterns
            6. Strategies re-ranked with new data
            """)
        st.markdown("#### Expected Output")
        st.markdown("""
        - **~35-50% conversion** (rules help, but customers are harder)
        - **~8 total rules** (accumulated from Gen 0 + Gen 1)
        - **Strategies converge** on what works (e.g., ROI framing, story-driven approaches)
        """)

    with gen_tabs[2]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Inputs")
            st.markdown("""
            - **Twice-evolved strategies** (battle-tested through 2 rounds)
            - **Hardest customers** — even more objections:
              - Bob: *"Show me a money-back guarantee in writing"*
              - Sarah: *"Can you prove your encryption is better than Dropbox's?"*
              - Ben: *"You have exactly one sentence. Go."*
            - **8+ improvement rules** accumulated over 2 generations
            """)
        with col2:
            st.markdown("#### What Happens")
            st.markdown("""
            1. Best-evolved strategies vs toughest customers
            2. Full rule library guides every agent response
            3. Agent adapts to new objections using learned patterns
            4. Final analysis shows overall improvement trend
            5. **Eval report** generated comparing Gen 0 → Gen 2
            """)
        st.markdown("#### Expected Output")
        st.markdown("""
        - **~40-60% conversion** (agent is now battle-hardened)
        - **~12 total rules** (deep library of sales wisdom)
        - **Clear improvement trend**: Gen 0 < Gen 1 < Gen 2
        - **Eval report**: proves the feedback loop works
        """)

    st.markdown("---")
    st.markdown("### 👥 Customer Personas")
    cust_cols = st.columns(3)
    with cust_cols[0]:
        st.markdown("""
        <div style="background:#1e1e2e;padding:1rem;border-radius:0.5rem;">
            <div style="font-size:1.5rem;">💰</div>
            <div style="font-weight:bold;font-size:1.1rem;">Budget Bob</div>
            <div style="color:#aaa;font-size:0.85rem;">Small bakery owner. Tight budget. Skeptical of new expenses. Responds to clear ROI.</div>
            <div style="color:#f0ad4e;font-size:0.8rem;margin-top:0.5rem;">Main objection: Price</div>
        </div>
        """, unsafe_allow_html=True)
    with cust_cols[1]:
        st.markdown("""
        <div style="background:#1e1e2e;padding:1rem;border-radius:0.5rem;">
            <div style="font-size:1.5rem;">🔍</div>
            <div style="font-weight:bold;font-size:1.1rem;">Skeptical Sarah</div>
            <div style="color:#aaa;font-size:0.85rem;">Freelance designer. Already uses Dropbox. Needs proof and data to switch.</div>
            <div style="color:#f0ad4e;font-size:0.8rem;margin-top:0.5rem;">Main objection: Already has solution</div>
        </div>
        """, unsafe_allow_html=True)
    with cust_cols[2]:
        st.markdown("""
        <div style="background:#1e1e2e;padding:1rem;border-radius:0.5rem;">
            <div style="font-size:1.5rem;">⏱️</div>
            <div style="font-weight:bold;font-size:1.1rem;">Busy Ben</div>
            <div style="color:#aaa;font-size:0.85rem;">Restaurant owner. Gets 10 sales calls/day. 15 seconds to hook him or he hangs up.</div>
            <div style="color:#f0ad4e;font-size:0.8rem;margin-top:0.5rem;">Main objection: No time</div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ─── RESULTS ───

# Top metrics
st.markdown("### 📊 Results")
col1, col2, col3, col4 = st.columns(4)
initial = results[0]["conversion_rate"] if results else 0
final = results[-1]["conversion_rate"] if results else 0
delta = final - initial if len(results) > 1 else 0

with col1:
    st.metric("Generations", len(results))
with col2:
    st.metric("Gen 0 Conversion", f"{initial:.0%}")
with col3:
    st.metric("Latest Conversion", f"{final:.0%}",
              delta=f"{delta:+.0%}" if len(results) > 1 else None)
with col4:
    st.metric("Rules Learned", len(rules))

# Conversion chart
if len(results) >= 2:
    st.markdown("### 📈 Conversion Improvement")
    chart_data = pd.DataFrame({
        "Generation": [f"Gen {r['generation']}" for r in results],
        "Conversion Rate": [r["conversion_rate"] for r in results],
    })
    st.bar_chart(chart_data, x="Generation", y="Conversion Rate", color="#5cb85c")

st.markdown("---")

# ─── GENERATION DETAILS ───
st.markdown("### 🏆 Generation Details")

tabs = st.tabs([f"Gen {r['generation']} ({r['conversion_rate']:.0%})" for r in results])

for tab, gen_result in zip(tabs, results):
    with tab:
        # Strategy performance summary
        strategies = {}
        for t in gen_result["transcripts"]:
            name = t["strategy_name"]
            if name not in strategies:
                strategies[name] = {"wins": 0, "total": 0, "rapport": 0, "scores": []}
            strategies[name]["total"] += 1
            strategies[name]["rapport"] += t["outcome"]["rapport"]
            if t["outcome"]["converted"]:
                strategies[name]["wins"] += 1

        sorted_strats = sorted(strategies.items(), key=lambda x: -x[1]["wins"])

        st.markdown("#### Strategy Performance")
        cols = st.columns(min(4, len(sorted_strats)))
        for i, (name, stats) in enumerate(sorted_strats):
            with cols[i % len(cols)]:
                rate = stats["wins"] / stats["total"] if stats["total"] else 0
                avg_rapport = stats["rapport"] / stats["total"] if stats["total"] else 0
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
                st.markdown(f"""
                <div style="background:#1e1e2e;padding:0.8rem;border-radius:0.5rem;text-align:center;">
                    <div style="font-size:1.3rem;">{medal}</div>
                    <div style="font-weight:bold;">{name}</div>
                    <div style="font-size:1.5rem;color:{'#5cb85c' if rate > 0 else '#d9534f'};">{rate:.0%}</div>
                    <div style="color:#aaa;font-size:0.8rem;">{stats['wins']}/{stats['total']} converted</div>
                    <div style="color:#aaa;font-size:0.8rem;">rapport: {avg_rapport:.1f}</div>
                </div>
                """, unsafe_allow_html=True)

        # Individual calls
        st.markdown("")
        st.markdown("#### Call Transcripts")
        for t in gen_result["transcripts"]:
            icon = "✅" if t["outcome"]["converted"] else "❌"
            score = t["outcome"].get("fitness_score", "—")
            label = (
                f"{icon} **{t['strategy_name']}** vs **{t['customer_id']}** "
                f"| rapport: {t['outcome']['rapport']:.1f} "
                f"| turns: {t['outcome']['turns']} "
                f"| score: {score}"
            )
            with st.expander(label):
                for turn in t["turns"]:
                    if turn["role"] == "agent":
                        st.markdown(f"🤖 **Agent:** {turn['text']}")
                        # Play voice audio if available
                        audio_path = turn.get("audio_path", "")
                        if audio_path:
                            filename = os.path.basename(audio_path)
                            audio_url = f"{API_URL}/api/audio/{t['generation']}/{filename}"
                            try:
                                audio_resp = requests.get(audio_url, timeout=5)
                                if audio_resp.status_code == 200:
                                    st.audio(audio_resp.content, format="audio/mpeg")
                            except Exception:
                                pass
                    else:
                        st.markdown(f"👤 **Customer:** {turn['text']}")
                if t["outcome"]["objections_faced"]:
                    st.caption(f"Objections faced: {', '.join(t['outcome']['objections_faced'])}")

st.markdown("---")

# ─── IMPROVEMENT RULES ───
st.markdown("### 🧠 Improvement Rules")
st.caption("These rules are injected into the agent's prompt — the feedback loop in action")

if rules:
    for rule in rules:
        st.markdown(f"""
        <div style="background:#1e1e2e;padding:0.8rem;border-radius:0.5rem;margin-bottom:0.5rem;">
            <div><strong>When:</strong> {rule['trigger']}</div>
            <div style="color:#d9534f;text-decoration:line-through;margin:0.2rem 0;">Old: {rule['old_response']}</div>
            <div style="color:#5cb85c;margin:0.2rem 0;">New: {rule['new_response']}</div>
            <div style="color:#666;font-size:0.8rem;">Evidence: {rule['evidence']} | Gen {rule['generation_learned']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Rules appear after the first generation completes.")

st.markdown("---")

# ─── EVAL REPORT ───
st.markdown("### 📋 Evaluation Report")
if eval_report:
    col1, col2 = st.columns(2)
    with col1:
        improvement = eval_report.get("improvement", 0)
        st.metric("Total Improvement", f"{improvement:+.0%}")
        st.metric("Rules Generated", eval_report.get("total_rules_learned", 0))

        if eval_report.get("improving"):
            st.success("✅ Agent improved consistently across all generations")
        else:
            st.warning("⚠️ Non-monotonic — some generations dipped (normal with harder customers)")

    with col2:
        trend = eval_report.get("conversion_trend", [])
        if trend:
            st.markdown("**Conversion by Generation:**")
            for i, conv in enumerate(trend):
                bar_len = int(conv * 30)
                color = "#5cb85c" if i == len(trend) - 1 else "#4a9eff"
                st.markdown(
                    f"Gen {i}: `{'█' * bar_len}{'░' * (30 - bar_len)}` **{conv:.0%}**"
                )

    st.markdown("---")
    st.markdown("#### Success Criteria")
    st.markdown(f"""
    | Criteria | Status |
    |----------|--------|
    | Agent simulates sales conversations (voice) | ✅ Dify + Gemini + ElevenLabs TTS |
    | Feedback loop: outcome → analysis → script | ✅ {eval_report.get('total_rules_learned', 0)} rules generated |
    | Documents improvement logic | ✅ Rules with evidence stored in memory |
    | 2+ iteration cycles | ✅ {len(results)} generations completed |
    | Baseline: {eval_report.get('initial_conversion', 0):.0%} → Final: {eval_report.get('final_conversion', 0):.0%} | {'✅' if improvement > 0 else '⚠️'} {improvement:+.0%} change |
    """)
else:
    st.info("Eval report appears after all generations complete.")

st.markdown("---")

# ─── N8N WORKFLOW ───
st.markdown("### 🔗 n8n Workflow — Pipeline Orchestration")
st.caption("Import `docs/n8n-workflow.json` into n8n to orchestrate the evolution pipeline visually")

# n8n pipeline as clear step cards
n8n_steps = [
    ("🟦", "#2563eb", "1. Trigger", "Manual button or scheduled (e.g., daily)"),
    ("🟦", "#3b82f6", "2. Configure", "Set API URL, number of generations (default: 3)"),
    ("🟩", "#16a34a", "3. Start Evolution", "POST /api/run — kicks off background task"),
    ("🟨", "#eab308", "4. Poll Status", "GET /api/status every 30s until running = false"),
    ("🟪", "#7c3aed", "5. Collect Results", "GET /api/results + /api/rules + /api/eval"),
    ("🟧", "#ea580c", "6. Check Improvement", "Did conversion improve? → Pass or Needs Tuning"),
]
n8n_cols = st.columns(6)
for i, (icon, color, title, desc) in enumerate(n8n_steps):
    with n8n_cols[i]:
        st.markdown(f"""
        <div style="background:#1e1e2e;padding:0.7rem;border-radius:0.5rem;text-align:center;border-top:3px solid {color};min-height:130px;">
            <div style="font-size:0.75rem;font-weight:bold;color:{color};margin-bottom:0.3rem;">{title}</div>
            <div style="color:#bbb;font-size:0.75rem;line-height:1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")
n8n_detail_col1, n8n_detail_col2 = st.columns(2)
with n8n_detail_col1:
    st.markdown("#### How to Use")
    st.markdown("""
    1. **Import** `docs/n8n-workflow.json` into n8n
    2. **Set** `SALESGYM_API_URL` environment variable in n8n settings
    3. **Click Run** — it triggers evolution, polls until done, then collects all results
    4. **Webhook mode** (alternative): pass `webhook_url` in the POST body to get notified after each generation
    """)
with n8n_detail_col2:
    st.markdown("#### API Endpoints Used")
    st.markdown("""
    | Endpoint | Purpose |
    |----------|---------|
    | `POST /api/run` | Start evolution |
    | `GET /api/status` | Poll progress |
    | `GET /api/results` | All generation results |
    | `GET /api/results/{gen}` | Single generation data |
    | `GET /api/rules` | Learned improvement rules |
    | `GET /api/eval` | Final evaluation report |
    """)

st.markdown("---")

# ─── ARCHITECTURE ───
st.markdown("### 🏗️ Architecture")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    | Component | Tool | Purpose |
    |-----------|------|---------|
    | Sales Agent | Dify Chatflow | Dynamic prompt injection |
    | Customer Sim | Gemini Flash | Role-play as buyers |
    | Analysis | Claude Sonnet | Pattern recognition |
    | Evolution | Claude Sonnet | Strategy mutation |
    | Voice | ElevenLabs | Agent speech synthesis |
    | Backend | Python FastAPI | Scoring + orchestration |
    | Dashboard | Streamlit | Visualization |
    | Orchestration | n8n | Pipeline automation |
    """)

with col2:
    st.markdown("""
    **Feedback Loop:**
    ```
    outcome → analysis → script adjustment
       ↑                        │
       │   Calls run with       │
       │   improved script      │
       └────────────────────────┘
    ```

    **Why this architecture?**
    - Gemini Flash for calls ($0.07/gen) — cheap
    - Claude Sonnet for analysis — smart
    - 8 strategies explore solution space
    - Evolutionary approach avoids local optima
    - Total cost: ~$1 for full 3-gen run
    """)
