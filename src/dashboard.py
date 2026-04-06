import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="SalesGym Dashboard", page_icon="", layout="wide")
st.title("SalesGym - Co-Evolutionary Sales Agent")
st.caption("Self-improving call center agent with evolutionary strategy selection")

# Sidebar: Controls
with st.sidebar:
    st.header("Controls")
    num_gens = st.slider("Generations to run", 2, 5, 3)
    if st.button("Run Evolution", type="primary"):
        with st.spinner(f"Running {num_gens} generations..."):
            try:
                resp = requests.post(
                    f"{API_URL}/api/run",
                    json={"num_generations": num_gens},
                    timeout=600,
                )
                resp.raise_for_status()
                st.session_state["run_results"] = resp.json()
                st.success("Evolution complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    if st.button("Refresh Data"):
        st.rerun()

# Main content
try:
    results_resp = requests.get(f"{API_URL}/api/results", timeout=10)
    results_resp.raise_for_status()
    results = results_resp.json()
except Exception:
    results = []

try:
    rules_resp = requests.get(f"{API_URL}/api/rules", timeout=10)
    rules_resp.raise_for_status()
    rules = rules_resp.json()
except Exception:
    rules = []

try:
    eval_resp = requests.get(f"{API_URL}/api/eval", timeout=10)
    eval_resp.raise_for_status()
    eval_report = eval_resp.json()
except Exception:
    eval_report = None

if not results:
    st.info("No results yet. Click 'Run Evolution' in the sidebar to start.")
    st.stop()

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Generations", len(results))
with col2:
    initial = results[0]["conversion_rate"] if results else 0
    st.metric("Initial Conversion", f"{initial:.0%}")
with col3:
    final = results[-1]["conversion_rate"] if results else 0
    delta = final - initial
    st.metric("Final Conversion", f"{final:.0%}", delta=f"{delta:+.0%}")
with col4:
    st.metric("Rules Learned", len(rules))

st.divider()

# Evolution Graph
st.subheader("Conversion Rate Over Generations")
import pandas as pd
chart_data = pd.DataFrame({
    "Generation": [r["generation"] for r in results],
    "Conversion Rate": [r["conversion_rate"] for r in results],
})
st.line_chart(chart_data, x="Generation", y="Conversion Rate")

# Strategy Leaderboard
st.subheader("Strategy Leaderboard")
for gen_result in results:
    with st.expander(
        f"Generation {gen_result['generation']} -- "
        f"{gen_result['conversion_rate']:.0%} conversion "
        f"({gen_result['num_calls']} calls)"
    ):
        for t in gen_result["transcripts"]:
            status = "PASS" if t["outcome"]["converted"] else "FAIL"
            with st.container():
                st.markdown(
                    f"**{status} {t['strategy_name']}** vs **{t['customer_id']}** "
                    f"-- Rapport: {t['outcome']['rapport']:.1f}"
                )
                with st.expander("View transcript"):
                    for turn in t["turns"]:
                        role_label = "Agent" if turn["role"] == "agent" else "Customer"
                        st.markdown(f"**{role_label}:** {turn['text']}")
                        if turn.get("audio_path") and os.path.exists(turn["audio_path"]):
                            st.audio(turn["audio_path"])

# Improvement Rules
st.subheader("Improvement Rules (Memory)")
if rules:
    for rule in rules:
        with st.container(border=True):
            st.markdown(f"**Trigger:** {rule['trigger']}")
            st.markdown(f"**Old approach:** {rule['old_response']}")
            st.markdown(f"**New approach:** {rule['new_response']}")
            st.caption(
                f"Evidence: {rule['evidence']} | Learned in Gen {rule['generation_learned']}"
            )
else:
    st.info("No rules yet.")

# Eval Report
st.subheader("Evaluation Report")
if eval_report:
    col1, col2 = st.columns(2)
    with col1:
        improvement = eval_report.get("improvement", 0)
        st.metric("Total Improvement", f"{improvement:.0%}")
        st.metric("Total Rules", eval_report.get("total_rules_learned", 0))
    with col2:
        trend = eval_report.get("conversion_trend", [])
        st.write("Conversion trend:", [f"{x:.0%}" for x in trend])
        if eval_report.get("improving"):
            st.success("Agent consistently improved across generations")
        else:
            st.warning("Improvement was not monotonic (some generations dipped)")
else:
    st.info("Run evolution to see eval results.")
