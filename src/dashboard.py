import streamlit as st
import requests
import time
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="SalesGym", page_icon="🧬", layout="wide")


def get_status():
    try:
        return requests.get(f"{API_URL}/api/status", timeout=5).json()
    except Exception:
        return {"running": False, "generation": -1, "error": None}


def get_results():
    try:
        resp = requests.get(f"{API_URL}/api/results", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def get_rules():
    try:
        resp = requests.get(f"{API_URL}/api/rules", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def get_eval():
    try:
        resp = requests.get(f"{API_URL}/api/eval", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


# Header
st.title("🧬 SalesGym")
st.caption("Co-evolutionary sales agent that rewrites its own script to improve conversion rates")

# Sidebar
with st.sidebar:
    st.header("Controls")

    status = get_status()

    if status["running"]:
        st.warning(f"⏳ Evolution running — Generation {status['generation']}")
        if st.button("Refresh Progress", type="primary", use_container_width=True):
            st.rerun()
        st.info("Page auto-refreshes every 30s while running")
    else:
        if status.get("error"):
            st.error(f"Last run failed: {status['error']}")

        num_gens = st.slider("Generations", 1, 5, 3)
        if st.button("🚀 Run Evolution", type="primary", use_container_width=True):
            try:
                resp = requests.post(
                    f"{API_URL}/api/run",
                    json={"num_generations": num_gens},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "started":
                    st.success(f"Evolution started! Running {num_gens} generations...")
                    st.info("Results appear below as each generation completes. Page refreshes automatically.")
                    time.sleep(2)
                    st.rerun()
                elif data.get("status") == "already_running":
                    st.warning("Evolution already running!")
                else:
                    st.success("Done!")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to start: {e}")

    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    st.divider()
    st.markdown("**Architecture**")
    st.markdown("""
    - 8 strategies compete per gen
    - 3 customer personas (get harder)
    - Claude analyzes patterns
    - Top strategies survive + evolve
    - Rules injected into agent prompt
    """)

# Auto-refresh while running
if status["running"]:
    time.sleep(30)
    st.rerun()

def _show_strategies_and_workflow():
    """Show the 8 competing strategies and the evolution workflow."""
    st.subheader("🎯 Competing Strategies")
    try:
        strats = requests.get(f"{API_URL}/api/strategies", timeout=5).json()
    except Exception:
        strats = []

    if strats:
        cols = st.columns(4)
        for i, s in enumerate(strats):
            with cols[i % 4]:
                st.markdown(f"**{s['name']}**")
                st.caption(s.get("system_prompt", "")[:120] + "...")
    else:
        st.caption("Strategies load when the API is running.")

    st.subheader("🔄 Evolution Workflow")
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────┐
    │                   GENERATION N                       │
    ├─────────────────────────────────────────────────────┤
    │                                                     │
    │  8 Strategies  ──→  3 Customers  ──→  24 Calls     │
    │  (Dify Agent)      (Gemini Sim)     (scored 0-100)  │
    │                                                     │
    │       ┌──────────────────────────────┐              │
    │       │  Claude Sonnet Analysis      │              │
    │       │  - Pattern recognition       │              │
    │       │  - Rule generation           │              │
    │       │  - Strategy ranking          │              │
    │       └──────────────┬───────────────┘              │
    │                      │                              │
    │       ┌──────────────▼───────────────┐              │
    │       │  Evolution                   │              │
    │       │  - Top 3: KEEP              │              │
    │       │  - Mid 3: MUTATE + rules    │              │
    │       │  - Bot 2: CROSSOVER         │              │
    │       └──────────────┬───────────────┘              │
    │                      │                              │
    │              8 Evolved Strategies                   │
    │              + Harder Customers                     │
    │                      │                              │
    └──────────────────────┼──────────────────────────────┘
                           │
                    GENERATION N+1
    ```
    """)

    st.subheader("🏗️ Architecture")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        | Component | Tool | Role |
        |-----------|------|------|
        | Sales Agent | Dify + Gemini | Runs conversations |
        | Customer Sim | Gemini Flash | Simulates buyers |
        | Analysis | Claude Sonnet | Pattern recognition |
        | Voice | ElevenLabs | Agent speech |
        | Orchestration | n8n | Pipeline automation |
        | Dashboard | Streamlit | Visualization |
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

        **Scoring (0-100):**
        - Converted: +50
        - Rapport (0-1): ×30
        - Efficiency (<10 turns): ×2
        - Objection handled: +10
        """)


# Load data
results = get_results()
rules = get_rules()
eval_report = get_eval()

# Status banner
if status["running"]:
    st.info(f"🔄 Evolution in progress — Generation {status['generation']} running. "
            f"{len(results)} generation(s) completed so far.")
elif not results:
    st.info("👈 Click **Run Evolution** in the sidebar to start the co-evolutionary loop.")
    st.markdown("""
    ### How it works
    1. **8 sales strategies** compete against **3 simulated customers** (24 calls per generation)
    2. **Claude Sonnet** analyzes outcomes and generates improvement rules
    3. **Top strategies survive**, middle mutate, bottom get replaced by crossovers
    4. **Customers get harder** each generation with new objections
    5. **Repeat** — measurable conversion improvement
    """)

    # Show strategies and workflow even before running
    st.divider()
    _show_strategies_and_workflow()
    st.stop()

# Metrics
st.divider()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Generations", len(results))
with col2:
    initial = results[0]["conversion_rate"] if results else 0
    st.metric("Initial Conversion", f"{initial:.0%}")
with col3:
    final = results[-1]["conversion_rate"] if results else 0
    delta = final - initial if len(results) > 1 else 0
    st.metric("Final Conversion", f"{final:.0%}", delta=f"{delta:+.0%}" if delta else None)
with col4:
    st.metric("Rules Learned", len(rules))

# Conversion chart
st.divider()
st.subheader("📈 Conversion Rate Over Generations")
if len(results) >= 2:
    chart_data = pd.DataFrame({
        "Generation": [r["generation"] for r in results],
        "Conversion Rate": [r["conversion_rate"] for r in results],
    })
    st.line_chart(chart_data, x="Generation", y="Conversion Rate")
elif len(results) == 1:
    st.metric("Gen 0 Conversion", f"{results[0]['conversion_rate']:.0%}")
    st.caption("More data points will appear as generations complete")

# Strategy leaderboard
st.divider()
st.subheader("🏆 Strategy Leaderboard")

for gen_result in results:
    converted = sum(1 for t in gen_result["transcripts"] if t["outcome"]["converted"])
    total = gen_result["num_calls"]
    with st.expander(
        f"Generation {gen_result['generation']} — "
        f"{gen_result['conversion_rate']:.0%} conversion "
        f"({converted}/{total} calls converted)",
        expanded=(gen_result["generation"] == len(results) - 1),
    ):
        # Summary table
        strategies = {}
        for t in gen_result["transcripts"]:
            name = t["strategy_name"]
            if name not in strategies:
                strategies[name] = {"wins": 0, "total": 0, "rapport_sum": 0}
            strategies[name]["total"] += 1
            strategies[name]["rapport_sum"] += t["outcome"]["rapport"]
            if t["outcome"]["converted"]:
                strategies[name]["wins"] += 1

        cols = st.columns(min(4, len(strategies)))
        for i, (name, stats) in enumerate(sorted(strategies.items(), key=lambda x: -x[1]["wins"])):
            with cols[i % len(cols)]:
                rate = stats["wins"] / stats["total"] if stats["total"] else 0
                avg_rapport = stats["rapport_sum"] / stats["total"] if stats["total"] else 0
                st.markdown(f"**{name}**")
                st.caption(f"{stats['wins']}/{stats['total']} converted ({rate:.0%})")
                st.caption(f"Avg rapport: {avg_rapport:.1f}")

        st.markdown("---")
        st.markdown("**Call Details**")
        for t in gen_result["transcripts"]:
            icon = "✅" if t["outcome"]["converted"] else "❌"
            with st.expander(
                f"{icon} {t['strategy_name']} vs {t['customer_id']} "
                f"— rapport: {t['outcome']['rapport']:.1f}, "
                f"turns: {t['outcome']['turns']}, "
                f"score: {t['outcome'].get('fitness_score', 'N/A')}"
            ):
                for turn in t["turns"]:
                    if turn["role"] == "agent":
                        st.markdown(f"🤖 **Agent:** {turn['text']}")
                    else:
                        st.markdown(f"👤 **Customer:** {turn['text']}")
                if t["outcome"]["objections_faced"]:
                    st.caption(f"Objections: {', '.join(t['outcome']['objections_faced'])}")

# Improvement rules
st.divider()
st.subheader("🧠 Improvement Rules (Agent Memory)")
if rules:
    st.caption(f"{len(rules)} rules learned across all generations")
    for rule in rules:
        with st.container(border=True):
            st.markdown(f"**When:** {rule['trigger']}")
            st.markdown(f"~~{rule['old_response']}~~ → **{rule['new_response']}**")
            st.caption(f"Evidence: {rule['evidence']} | Gen {rule['generation_learned']}")
else:
    st.info("No rules learned yet — they appear after the first generation completes.")

# Eval report
st.divider()
st.subheader("📊 Evaluation Report")
if eval_report:
    col1, col2 = st.columns(2)
    with col1:
        improvement = eval_report.get("improvement", 0)
        st.metric("Total Improvement", f"{improvement:+.0%}")
        st.metric("Total Rules", eval_report.get("total_rules_learned", 0))
    with col2:
        trend = eval_report.get("conversion_trend", [])
        if trend:
            trend_df = pd.DataFrame({
                "Generation": list(range(len(trend))),
                "Conversion": trend,
            })
            st.bar_chart(trend_df, x="Generation", y="Conversion")
        if eval_report.get("improving"):
            st.success("✅ Agent consistently improved across all generations")
        else:
            st.warning("⚠️ Improvement was not monotonic (some generations dipped)")

    st.markdown("---")
    st.markdown("**Feedback Loop Demonstrated:**")
    st.markdown("```outcome → analysis → script adjustment → better outcome```")
    st.markdown(f"- Gen 0 baseline: **{eval_report.get('initial_conversion', 0):.0%}**")
    st.markdown(f"- Final conversion: **{eval_report.get('final_conversion', 0):.0%}**")
    st.markdown(f"- Rules driving improvement: **{eval_report.get('total_rules_learned', 0)}**")
else:
    st.info("Eval report appears after all generations complete.")

# Always show strategies and architecture at bottom
st.divider()
_show_strategies_and_workflow()
