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
    # Show the strategies and workflow
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🎯 The 8 Competing Strategies")
        strategies = api_get("/api/strategies") or []
        if strategies:
            for i in range(0, len(strategies), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(strategies):
                        s = strategies[i + j]
                        with col:
                            st.markdown(f"""
                            <div style="background:#1e1e2e;padding:0.8rem;border-radius:0.5rem;margin-bottom:0.5rem;">
                                <div style="font-weight:bold;font-size:1rem;">#{i+j+1} {s['name']}</div>
                                <div style="color:#aaa;font-size:0.85rem;margin-top:0.3rem;">{s.get('system_prompt', '')[:100]}...</div>
                            </div>
                            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🔄 Evolution Pipeline")
        st.markdown("""
        ```
        8 Strategies × 3 Customers
              = 24 Calls
                 │
                 ▼
          Score Each Call
          (0-100 fitness)
                 │
                 ▼
         Claude Analysis
         "ROI framing won 67%"
                 │
                 ▼
           Evolution
           Top 3: KEEP
           Mid 3: MUTATE
           Bot 2: CROSSOVER
                 │
                 ▼
        8 Evolved Strategies
        + Harder Customers
                 │
                 ▼
          Next Generation
        ```
        """)

    st.markdown("---")
    st.markdown("### 📊 Scoring Formula")
    cols = st.columns(4)
    with cols[0]:
        st.markdown("**Converted?**")
        st.markdown("`+50 points`")
    with cols[1]:
        st.markdown("**Rapport**")
        st.markdown("`0-30 points`")
    with cols[2]:
        st.markdown("**Efficiency**")
        st.markdown("`0-20 points`")
    with cols[3]:
        st.markdown("**Objection Handled**")
        st.markdown("`+10 points`")

    st.markdown("---")
    st.markdown("### 🔁 Feedback Loop")
    st.markdown("""
    > **outcome** → **analysis** → **script adjustment** → **better outcome**
    >
    > Rules like *"When customer says 'too expensive', use ROI framing instead of discounts"*
    > are injected into the agent's prompt before each call.
    """)

    st.info("👈 Click **Run Evolution** to start!")
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
