"""
FeederIQ – Streamlit Frontend (PwC Hackathon R2)
Premium wizard-style UI with tile navigation, agent visualization,
grid maps, and multi-criteria portfolio ranking.
"""
import time
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FeederIQ – PwC Distribution Planning",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = "http://localhost:8000"

# ─── PwC Brand Colors ────────────────────────────────────────────────────────
PWC_ORANGE = "#D04A02"
PWC_ORANGE_LIGHT = "#EB8C00"
PWC_ORANGE_PALE = "#FFF3E8"
PWC_DARK = "#2D2D2D"
PWC_GREY = "#6B6B6B"
PWC_LIGHT_GREY = "#F7F7F7"
PWC_WHITE = "#FFFFFF"
PWC_GREEN = "#22992E"
PWC_RED = "#E0301E"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Global */
    .stApp {{
        background-color: {PWC_LIGHT_GREY};
    }}
    .main .block-container {{
        padding-top: 1rem;
        max-width: 1200px;
    }}

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {{
        background-color: {PWC_DARK};
    }}

    /* Top brand bar */
    .brand-bar {{
        background: {PWC_DARK};
        padding: 12px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 0 0 8px 8px;
        margin-bottom: 20px;
    }}
    .brand-bar h1 {{
        color: white;
        font-size: 1.6rem;
        margin: 0;
        font-weight: 700;
    }}
    .brand-bar .pwc-logo {{
        color: {PWC_ORANGE};
        font-size: 1.8rem;
        font-weight: 900;
        font-family: Georgia, serif;
        letter-spacing: -1px;
    }}

    /* Step tiles */
    .step-container {{
        display: flex;
        gap: 6px;
        margin-bottom: 24px;
        overflow-x: auto;
        padding: 4px 0;
    }}
    .step-tile {{
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        text-align: center;
        min-width: 120px;
        cursor: default;
        transition: all 0.2s;
        border: 2px solid transparent;
    }}
    .step-tile.active {{
        background: {PWC_ORANGE};
        color: white;
        border-color: {PWC_ORANGE};
        box-shadow: 0 3px 12px rgba(208, 74, 2, 0.3);
    }}
    .step-tile.done {{
        background: {PWC_ORANGE_PALE};
        color: {PWC_ORANGE};
        border-color: {PWC_ORANGE_LIGHT};
    }}
    .step-tile.pending {{
        background: {PWC_WHITE};
        color: {PWC_GREY};
        border-color: #E0E0E0;
    }}

    /* Cards */
    .metric-card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid {PWC_ORANGE};
        margin-bottom: 12px;
    }}
    .metric-card h4 {{
        margin: 0 0 4px 0;
        color: {PWC_GREY};
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .metric-card .value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {PWC_DARK};
    }}
    .metric-card .delta {{
        font-size: 0.85rem;
        color: {PWC_GREEN};
    }}
    .metric-card .delta.negative {{
        color: {PWC_RED};
    }}

    /* Agent cards */
    .agent-card {{
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        gap: 14px;
        border-left: 4px solid #E0E0E0;
    }}
    .agent-card.running {{
        border-left-color: {PWC_ORANGE};
        background: {PWC_ORANGE_PALE};
    }}
    .agent-card.complete {{
        border-left-color: {PWC_GREEN};
    }}
    .agent-card .agent-icon {{
        font-size: 1.4rem;
    }}
    .agent-card .agent-name {{
        font-weight: 700;
        color: {PWC_DARK};
        font-size: 0.95rem;
    }}
    .agent-card .agent-detail {{
        color: {PWC_GREY};
        font-size: 0.82rem;
        margin-top: 2px;
    }}

    /* Portfolio ranking card */
    .portfolio-card {{
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #EEE;
    }}
    .portfolio-card.top {{
        border: 2px solid {PWC_ORANGE};
        box-shadow: 0 4px 16px rgba(208, 74, 2, 0.12);
    }}
    .portfolio-card .rank {{
        color: {PWC_ORANGE};
        font-weight: 900;
        font-size: 1.3rem;
    }}
    .portfolio-card .name {{
        font-weight: 700;
        font-size: 1.1rem;
        color: {PWC_DARK};
    }}

    /* Section headers */
    .section-header {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {PWC_DARK};
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid {PWC_ORANGE};
    }}

    /* Score bars */
    .score-bar-bg {{
        background: #F0F0F0;
        border-radius: 6px;
        height: 8px;
        width: 100%;
    }}
    .score-bar-fill {{
        background: {PWC_ORANGE};
        border-radius: 6px;
        height: 8px;
    }}

    /* Override Streamlit elements */
    .stButton > button {{
        background: {PWC_ORANGE};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-weight: 700;
        font-size: 1rem;
    }}
    .stButton > button:hover {{
        background: {PWC_ORANGE_LIGHT};
        color: white;
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
    }}
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ─────────────────────────────────────────────────────────

def render_brand_bar():
    st.markdown("""
    <div class="brand-bar">
        <div style="display:flex; align-items:center; gap:16px;">
            <span class="pwc-logo">pwc</span>
            <h1>FeederIQ – Agentic Distribution Planning</h1>
        </div>
        <div style="color: #AAA; font-size: 0.85rem;">Multi-Criteria Non-Wires Alternative Analysis</div>
    </div>
    """, unsafe_allow_html=True)


def render_step_tiles(current_step, completed_steps):
    steps = [
        ("1", "Planning Horizon"),
        ("2", "Load Growth"),
        ("3", "Data Center"),
        ("4", "Study Config"),
        ("5", "Agent Execution"),
        ("6", "Results & Ranking"),
    ]
    tiles_html = '<div class="step-container">'
    for step_id, label in steps:
        if int(step_id) == current_step:
            cls = "active"
        elif int(step_id) in completed_steps:
            cls = "done"
        else:
            cls = "pending"
        tiles_html += f'<div class="step-tile {cls}">{step_id}. {label}</div>'
    tiles_html += '</div>'
    st.markdown(tiles_html, unsafe_allow_html=True)


def metric_card(title, value, delta=None, negative=False):
    delta_html = ""
    if delta:
        cls = "negative" if negative else ""
        delta_html = f'<div class="delta {cls}">{delta}</div>'
    return f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <div class="value">{value}</div>
        {delta_html}
    </div>
    """


def agent_card(icon, name, detail, status="pending"):
    return f"""
    <div class="agent-card {status}">
        <div class="agent-icon">{icon}</div>
        <div>
            <div class="agent-name">{name}</div>
            <div class="agent-detail">{detail}</div>
        </div>
    </div>
    """


def score_bar(label, value, max_val=10):
    pct = min(100, (value / max_val) * 100)
    return f"""
    <div style="margin-bottom:8px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
            <span style="font-size:0.8rem; color:{PWC_GREY};">{label}</span>
            <span style="font-size:0.8rem; font-weight:700; color:{PWC_DARK};">{value:.1f}/10</span>
        </div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%;"></div></div>
    </div>
    """


def render_grid_map():
    """Render IEEE 123-bus feeder map using Buscoords.dss."""
    from pathlib import Path

    coords_path = Path(__file__).resolve().parent.parent.parent / "ai_synthetic_data" / "Buscoords.dss"
    if not coords_path.exists():
        return None

    buses = {}
    with open(coords_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                name = parts[0].lower()
                try:
                    x, y = float(parts[1]), float(parts[2])
                    buses[name] = (x, y)
                except ValueError:
                    continue

    # Filter out secondary buses (s prefix) and regulator buses (r suffix)
    primary_buses = {k: v for k, v in buses.items() if not k.startswith("s") and not k.endswith("r")}

    ev_buses = {"60", "83", "90", "92", "114"}
    solar_buses = {"66", "80", "92", "104", "110"}
    dc_bus = "67"

    xs, ys, colors, sizes, texts = [], [], [], [], []
    for bus, (x, y) in primary_buses.items():
        xs.append(x)
        ys.append(y)
        if bus == dc_bus:
            colors.append(PWC_RED)
            sizes.append(16)
            texts.append(f"Bus {bus}<br>🏢 Data Center")
        elif bus in ev_buses and bus in solar_buses:
            colors.append("#7B2D8B")
            sizes.append(13)
            texts.append(f"Bus {bus}<br>⚡ EV + ☀️ Solar")
        elif bus in ev_buses:
            colors.append(PWC_ORANGE)
            sizes.append(12)
            texts.append(f"Bus {bus}<br>⚡ EV Charging")
        elif bus in solar_buses:
            colors.append(PWC_GREEN)
            sizes.append(12)
            texts.append(f"Bus {bus}<br>☀️ Solar PV")
        else:
            colors.append("#B0B0B0")
            sizes.append(7)
            texts.append(f"Bus {bus}")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode='markers+text',
        marker=dict(size=sizes, color=colors, line=dict(width=1, color='white')),
        text=[b for b in primary_buses.keys()],
        textposition="top center",
        textfont=dict(size=7, color=PWC_GREY),
        hovertext=texts,
        hoverinfo='text',
        showlegend=False,
    ))

    # Legend items
    for label, color in [("Data Center", PWC_RED), ("EV Charging", PWC_ORANGE),
                          ("Solar PV", PWC_GREEN), ("EV + Solar", "#7B2D8B"), ("Bus Node", "#B0B0B0")]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=10, color=color),
            name=label,
        ))

    fig.update_layout(
        title=None,
        height=420,
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font=dict(size=11)),
    )
    return fig


# ─── Session State Init ───────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1
if "completed" not in st.session_state:
    st.session_state.completed = set()
if "study_data" not in st.session_state:
    st.session_state.study_data = None
if "scenario" not in st.session_state:
    st.session_state.scenario = {
        "horizon_label": "12m",
        "ev_level": "Base",
        "ev_custom": None,
        "solar_level": "Base",
        "solar_custom": None,
        "dc_level": "Moderate",
        "dc_timeline_label": "12m",
        "dc_custom": None,
        "max_active_measures": 3,
        "max_portfolios": 60,
    }


def go_to_step(n):
    st.session_state.step = n


# ─── Render ───────────────────────────────────────────────────────────────────
render_brand_bar()
render_step_tiles(st.session_state.step, st.session_state.completed)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Planning Horizon
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown(f'<div class="section-header">Planning Horizon</div>', unsafe_allow_html=True)
    st.markdown("Select how far into the future to model feeder stress. The simulation generates a representative peak day at that future date.")

    col1, col2 = st.columns([2, 1])
    with col1:
        horizons = {
            "6m": ("6 Months", "Near-term operational planning"),
            "12m": ("1 Year", "Standard annual planning cycle"),
            "18m": ("18 Months", "Extended near-term forecast"),
            "3yr": ("3 Years", "Medium-term capital planning"),
            "5yr": ("5 Years", "Long-term strategic planning"),
        }
        selected = st.radio(
            "Planning horizon",
            list(horizons.keys()),
            format_func=lambda x: f"{horizons[x][0]} — {horizons[x][1]}",
            index=list(horizons.keys()).index(st.session_state.scenario["horizon_label"]),
            label_visibility="collapsed",
        )
        st.session_state.scenario["horizon_label"] = selected

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Selected Horizon</h4>
            <div class="value">{horizons[selected][0]}</div>
            <div class="delta">{horizons[selected][1]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <h4>Simulation Approach</h4>
            <div style="font-size:0.9rem; color:{PWC_GREY}; margin-top:8px;">
                24-hour representative peak day<br>
                Load magnitudes scaled by horizon<br>
                Data center online if timeline ≤ horizon
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("Next → Load Growth", key="step1_next"):
        st.session_state.completed.add(1)
        go_to_step(2)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Load Growth (EV + Solar)
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown(f'<div class="section-header">Load Growth Scenarios</div>', unsafe_allow_html=True)
    st.markdown("Define EV charging growth and solar adoption levels. These drive the synthetic demand and generation profiles injected into the feeder model.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⚡ EV Charging Growth")
        ev_options = {"Low": "15% annual", "Base": "20% annual", "High": "25% annual"}
        ev_selected = st.selectbox(
            "EV growth rate",
            list(ev_options.keys()),
            format_func=lambda x: f"{x} ({ev_options[x]})",
            index=list(ev_options.keys()).index(st.session_state.scenario["ev_level"]),
        )
        st.session_state.scenario["ev_level"] = ev_selected

        ev_custom = st.number_input(
            "Or enter custom annual growth %",
            min_value=5, max_value=50, value=int(float(ev_options[ev_selected].split("%")[0])),
            step=1, key="ev_custom_input",
            help="Override the preset with your own growth rate"
        )
        st.session_state.scenario["ev_custom"] = ev_custom / 100.0

        st.info("📊 **Source**: EIA Annual Energy Outlook 2024 projects 15–25% annual EV adoption growth for US utilities through 2030.")

    with col2:
        st.markdown("#### ☀️ Solar Adoption")
        solar_options = {"Low": "100 MW regional", "Base": "200 MW regional", "High": "300 MW regional"}
        solar_selected = st.selectbox(
            "Solar adoption level",
            list(solar_options.keys()),
            format_func=lambda x: f"{x} ({solar_options[x]})",
            index=list(solar_options.keys()).index(st.session_state.scenario["solar_level"]),
        )
        st.session_state.scenario["solar_level"] = solar_selected

        solar_custom = st.number_input(
            "Or enter custom regional MW",
            min_value=50, max_value=1000, value=int(solar_options[solar_selected].split(" ")[0]),
            step=25, key="solar_custom_input",
            help="Override with your own MW estimate"
        )
        st.session_state.scenario["solar_custom"] = solar_custom

        st.info("📊 **Source**: SEIA/Wood Mackenzie Q1 2024 reports 100–400 MW regional adoption rates across US distribution systems.")

    st.markdown("")
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("← Back", key="step2_back"):
            go_to_step(1)
            st.rerun()
    with c2:
        if st.button("Next → Data Center", key="step2_next"):
            st.session_state.completed.add(2)
            go_to_step(3)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Data Center
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    st.markdown(f'<div class="section-header">Data Center Interconnection</div>', unsafe_allow_html=True)
    st.markdown("Model a new large-load interconnection request — a common planning challenge for US utilities seeing hyperscale demand from AI/cloud operators.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏢 Data Center Demand")
        dc_options = {"Low": "1.0 MW", "Moderate": "1.75 MW", "High": "3.0 MW"}
        dc_selected = st.selectbox(
            "Data center size",
            list(dc_options.keys()),
            format_func=lambda x: f"{x} ({dc_options[x]})",
            index=list(dc_options.keys()).index(st.session_state.scenario["dc_level"]),
        )
        st.session_state.scenario["dc_level"] = dc_selected

        dc_custom = st.number_input(
            "Or enter custom MW",
            min_value=0.5, max_value=10.0, value=float(dc_options[dc_selected].split(" ")[0]),
            step=0.25, key="dc_custom_input",
        )
        st.session_state.scenario["dc_custom"] = dc_custom

    with col2:
        st.markdown("#### 📅 Connection Timeline")
        dc_timeline_options = {"6m": "6 months", "12m": "12 months", "18m": "18 months"}
        dc_timeline = st.selectbox(
            "When does the data center come online?",
            list(dc_timeline_options.keys()),
            format_func=lambda x: dc_timeline_options[x],
            index=list(dc_timeline_options.keys()).index(st.session_state.scenario["dc_timeline_label"]),
        )
        st.session_state.scenario["dc_timeline_label"] = dc_timeline

        st.markdown(f"""
        <div class="metric-card">
            <h4>Planning Context</h4>
            <div style="font-size:0.85rem; color:{PWC_GREY}; margin-top:8px;">
                Data center load is modeled at Bus 67<br>
                3-phase balanced load, 0.97 power factor<br>
                Active only if planning horizon ≥ timeline<br><br>
                <em>US utilities received 35+ GW of data center interconnection requests in 2024 (DOE Grid Deployment Office)</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Grid map preview
    st.markdown(f'<div class="section-header">Feeder Topology — IEEE 123-Bus Network</div>', unsafe_allow_html=True)
    grid_fig = render_grid_map()
    if grid_fig:
        st.plotly_chart(grid_fig, use_container_width=True)
    else:
        st.warning("Bus coordinates file not found — grid map unavailable.")

    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("← Back", key="step3_back"):
            go_to_step(2)
            st.rerun()
    with c2:
        if st.button("Next → Study Config", key="step3_next"):
            st.session_state.completed.add(3)
            go_to_step(4)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Study Configuration
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    st.markdown(f'<div class="section-header">Study Configuration</div>', unsafe_allow_html=True)
    st.markdown("Configure portfolio generation parameters. The engine evaluates combinations of interventions at varying deployment levels.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎛️ Portfolio Parameters")
        max_portfolios = st.slider(
            "Maximum portfolios to evaluate",
            min_value=10, max_value=120, value=st.session_state.scenario["max_portfolios"], step=10,
            help="Higher = more thorough analysis, longer runtime"
        )
        st.session_state.scenario["max_portfolios"] = max_portfolios

        max_active = st.slider(
            "Maximum active measures per portfolio",
            min_value=1, max_value=5, value=st.session_state.scenario["max_active_measures"],
            help="Limits portfolio complexity"
        )
        st.session_state.scenario["max_active_measures"] = max_active

    with col2:
        st.markdown("#### 📋 Intervention Types")
        st.markdown(f"""
        <div class="metric-card">
            <h4>Available Interventions</h4>
            <div style="font-size:0.88rem; color:{PWC_DARK}; margin-top:8px; line-height:1.8;">
                🔧 <strong>Transformer Upgrade</strong> — Traditional capex<br>
                🔋 <strong>Battery Storage</strong> — Peak shaving & deferral<br>
                🔌 <strong>Managed EV Charging</strong> — Demand flexibility<br>
                📐 <strong>Phased Interconnection</strong> — Staged DC connection<br>
                💰 <strong>Demand Tariff</strong> — Price-based demand response
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <h4>Deployment Levels</h4>
            <div style="font-size:0.88rem; color:{PWC_DARK}; margin-top:8px; line-height:1.8;">
                <strong>0%</strong> — Not deployed<br>
                <strong>33%</strong> — Pilot / early adoption (EPRI Stage 1)<br>
                <strong>66%</strong> — Moderate-scale rollout (EPRI Stage 2)<br>
                <strong>100%</strong> — Full deployment (EPRI Stage 3)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    # Scenario summary
    st.markdown(f'<div class="section-header">Scenario Summary</div>', unsafe_allow_html=True)
    sc = st.session_state.scenario
    summary_cols = st.columns(5)
    labels = ["Horizon", "EV Growth", "Solar", "Data Center", "DC Timeline"]
    values = [sc["horizon_label"], f"{sc['ev_level']}", f"{sc['solar_level']}", f"{sc['dc_level']}", sc["dc_timeline_label"]]
    for col, label, val in zip(summary_cols, labels, values):
        col.markdown(metric_card(label, val), unsafe_allow_html=True)

    st.markdown("")
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("← Back", key="step4_back"):
            go_to_step(3)
            st.rerun()
    with c2:
        if st.button("🚀 Run FeederIQ Study", key="run_study"):
            st.session_state.completed.add(4)
            go_to_step(5)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Agent Execution
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 5:
    st.markdown(f'<div class="section-header">Agent Execution Pipeline</div>', unsafe_allow_html=True)
    st.markdown("FeederIQ agents are analyzing your scenario. Each agent handles a specialized planning task.")

    # Show agent cards with progress
    agents_info = [
        ("🔬", "Scenario Agent", "Converting selections into numeric growth assumptions and 24-hour synthetic profiles"),
        ("⚡", "Simulation Agent", "Running OpenDSS 24-hour power flow on IEEE 123-bus feeder model"),
        ("🔍", "Constraint Agent", "Detecting voltage violations, line overloads, and transformer overloads"),
        ("🌱", "NWA Agent", "Evaluating non-wires alternatives: batteries, managed charging, demand tariffs"),
        ("🔧", "Capex Agent", "Evaluating traditional infrastructure upgrades and hybrid portfolios"),
        ("📊", "Recommendation Agent", "Ranking all portfolios by multi-criteria weighted scoring"),
    ]

    agent_placeholder = st.empty()
    progress_bar = st.progress(0)

    # Build API payload
    sc = st.session_state.scenario
    payload = {
        "horizon_label": sc["horizon_label"],
        "ev_level": sc["ev_level"],
        "solar_level": sc["solar_level"],
        "dc_level": sc["dc_level"],
        "dc_timeline_label": sc["dc_timeline_label"],
        "max_active_measures": sc["max_active_measures"],
        "max_portfolios": sc["max_portfolios"],
    }

    # Animate agent progress while waiting for API
    for i, (icon, name, detail) in enumerate(agents_info):
        progress_bar.progress((i + 1) / len(agents_info))
        cards_html = ""
        for j, (ic, nm, dt) in enumerate(agents_info):
            if j < i:
                cards_html += agent_card(ic, nm, "✓ Complete", "complete")
            elif j == i:
                cards_html += agent_card(ic, nm, f"⏳ {dt}", "running")
            else:
                cards_html += agent_card(ic, nm, dt, "pending")
        agent_placeholder.markdown(cards_html, unsafe_allow_html=True)

        if i == 0:
            # Call the API on the first agent step (actual work happens here)
            try:
                resp = requests.post(f"{API_URL}/study", json=payload, timeout=300)
                resp.raise_for_status()
                st.session_state.study_data = resp.json()
            except requests.exceptions.HTTPError as e:
                st.error(f"Study failed: {e.response.text}")
                st.stop()
            except Exception as e:
                st.error(f"Connection failed: {e}. Is the backend running on {API_URL}?")
                st.stop()
        else:
            time.sleep(0.5)

    # Show all complete
    cards_html = ""
    for ic, nm, dt in agents_info:
        cards_html += agent_card(ic, nm, "✓ Complete", "complete")
    agent_placeholder.markdown(cards_html, unsafe_allow_html=True)
    progress_bar.progress(1.0)

    st.success("All agents completed successfully.")

    # Show grid map during execution results
    st.markdown(f'<div class="section-header">Feeder Under Analysis</div>', unsafe_allow_html=True)
    grid_fig = render_grid_map()
    if grid_fig:
        st.plotly_chart(grid_fig, use_container_width=True)

    st.markdown("")
    if st.button("View Results →", key="step5_next"):
        st.session_state.completed.add(5)
        go_to_step(6)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: Results & Ranking
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 6:
    data = st.session_state.study_data
    if not data:
        st.warning("No study results available. Please run a study first.")
        if st.button("← Go Back"):
            go_to_step(1)
            st.rerun()
    else:
        # ── Tabs for results sections ──
        tab_recommendation, tab_ranking, tab_baseline, tab_profiles, tab_memo = st.tabs([
            "✅ Recommendation", "🏆 Portfolio Ranking", "📊 Baseline Assessment",
            "📈 Load Profiles", "📝 Decision Memo"
        ])

        # ── TAB: Recommendation ──
        with tab_recommendation:
            st.markdown(f'<div class="section-header">Final Recommendation</div>', unsafe_allow_html=True)

            top = data.get("top_recommendation", {})
            second = data.get("second_best", {})
            nwa_resolved = data.get("nwa_resolved_all", False)

            if nwa_resolved:
                st.markdown(f"""
                <div style="background:{PWC_GREEN}22; border:2px solid {PWC_GREEN}; border-radius:10px; padding:16px 20px; margin-bottom:16px;">
                    <strong style="color:{PWC_GREEN}; font-size:1.1rem;">✅ Non-Wires Alternatives Fully Resolve All Violations</strong><br>
                    <span style="color:{PWC_GREY};">No traditional capex (transformer upgrades, reconductoring) is required.</span>
                </div>
                """, unsafe_allow_html=True)

            if top:
                st.markdown(f"""
                <div class="portfolio-card top">
                    <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
                        <span style="font-size:1.5rem;">🏆</span>
                        <div>
                            <div style="font-size:0.8rem; color:{PWC_GREY}; text-transform:uppercase; letter-spacing:0.5px;">Top Recommendation</div>
                            <div style="font-size:1.4rem; font-weight:800; color:{PWC_DARK};">{top.get('portfolio_name', 'N/A')}</div>
                        </div>
                        <span style="margin-left:auto; font-size:2rem; font-weight:900; color:{PWC_ORANGE};">{top.get('final_score', 0):.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Score breakdown
                st.markdown("#### Score Breakdown")
                sc1, sc2 = st.columns([1, 1])
                with sc1:
                    tech_val = min(10, top.get("technical_improvement_pct", 0) / 10)
                    st.markdown(
                        score_bar("Technical Effectiveness (40%)", tech_val) +
                        score_bar("Cost Attractiveness (25%)", top.get("cost_score", 0)) +
                        score_bar("Feasibility (20%)", top.get("feasibility_score", 0)) +
                        score_bar("Deployment Speed (15%)", top.get("deployment_score", 0)),
                        unsafe_allow_html=True
                    )
                with sc2:
                    # Radar chart
                    categories = ['Technical', 'Cost', 'Feasibility', 'Deployment']
                    values_top = [
                        min(10, top.get("technical_improvement_pct", 0) / 10),
                        top.get("cost_score", 0),
                        top.get("feasibility_score", 0),
                        top.get("deployment_score", 0),
                    ]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values_top + [values_top[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        fillcolor=f'rgba(208,74,2,0.15)',
                        line=dict(color=PWC_ORANGE, width=2),
                        name=top.get('portfolio_name', 'Top'),
                    ))
                    if second:
                        values_second = [
                            min(10, second.get("technical_improvement_pct", 0) / 10),
                            second.get("cost_score", 0),
                            second.get("feasibility_score", 0),
                            second.get("deployment_score", 0),
                        ]
                        fig.add_trace(go.Scatterpolar(
                            r=values_second + [values_second[0]],
                            theta=categories + [categories[0]],
                            fill='toself',
                            fillcolor='rgba(107,107,107,0.08)',
                            line=dict(color=PWC_GREY, width=1.5, dash='dot'),
                            name=second.get('portfolio_name', 'Runner-up'),
                        ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                        showlegend=True, height=300,
                        margin=dict(t=30, b=30),
                        paper_bgcolor="white",
                        font=dict(family="Arial", size=11),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Before / After
            if top:
                st.markdown("#### Before vs. After")
                ba1, ba2 = st.columns(2)
                bs = data.get("base_summary", {})
                impr = top.get("technical_improvement_pct", 0)
                after_stress = bs.get("grid_stress_score", 0) * (1 - impr / 100)

                with ba1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color:{PWC_RED};">
                        <h4>Before (No Intervention)</h4>
                        <div class="value">{bs.get('grid_stress_score', 0):.0f}</div>
                        <div style="color:{PWC_GREY}; font-size:0.85rem;">Grid Stress Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                with ba2:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color:{PWC_GREEN};">
                        <h4>After ({top.get('portfolio_name', '')})</h4>
                        <div class="value">{after_stress:.0f}</div>
                        <div class="delta">↓ {impr:.1f}% stress reduction</div>
                    </div>
                    """, unsafe_allow_html=True)

            if second:
                st.markdown("#### Runner-Up Option")
                st.markdown(f"""
                <div class="portfolio-card">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:1.2rem;">🥈</span>
                        <div>
                            <div style="font-weight:700; color:{PWC_DARK};">{second.get('portfolio_name', 'N/A')}</div>
                            <div style="color:{PWC_GREY}; font-size:0.85rem;">
                                Score: {second.get('final_score', 0):.2f} |
                                Technical: {second.get('technical_improvement_pct', 0):.1f}% |
                                Cost: {second.get('cost_score', 0):.1f}/10
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── TAB: Portfolio Ranking ──
        with tab_ranking:
            st.markdown(f'<div class="section-header">Portfolio Ranking</div>', unsafe_allow_html=True)
            st.markdown("All evaluated portfolios ranked by weighted multi-criteria score. Click column headers to sort by any dimension.")

            ranking = data.get("ranking", [])
            if ranking:
                rank_df = pd.DataFrame(ranking)

                # Top 3 as cards
                for idx, row in rank_df.head(3).iterrows():
                    is_top = idx == 0
                    card_class = "portfolio-card top" if is_top else "portfolio-card"
                    badge = "🥇" if idx == 0 else ("🥈" if idx == 1 else "🥉")

                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px;">
                            <span class="rank">{badge} #{idx+1}</span>
                            <span class="name">{row.get('portfolio_name', 'N/A')}</span>
                            <span style="margin-left:auto; font-size:1.3rem; font-weight:800; color:{PWC_ORANGE};">{row.get('final_score', 0):.2f}</span>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:12px;">
                            <div><span style="font-size:0.75rem; color:{PWC_GREY};">Technical</span><br><strong>{row.get('technical_improvement_pct', 0):.1f}%</strong></div>
                            <div><span style="font-size:0.75rem; color:{PWC_GREY};">Cost Score</span><br><strong>{row.get('cost_score', 0):.1f}/10</strong></div>
                            <div><span style="font-size:0.75rem; color:{PWC_GREY};">Feasibility</span><br><strong>{row.get('feasibility_score', 0):.1f}/10</strong></div>
                            <div><span style="font-size:0.75rem; color:{PWC_GREY};">Deployment</span><br><strong>{row.get('deployment_score', 0):.1f}/10</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Horizontal bar chart
                st.markdown("")
                top_n = min(10, len(rank_df))
                chart_df = rank_df.head(top_n).copy()
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=chart_df["portfolio_name"][::-1],
                    x=chart_df["final_score"][::-1],
                    orientation='h',
                    marker_color=[PWC_ORANGE if i == top_n - 1 else PWC_ORANGE_LIGHT for i in range(top_n)],
                    text=chart_df["final_score"][::-1].apply(lambda x: f"{x:.2f}"),
                    textposition='outside',
                ))
                fig.update_layout(
                    title=f"Top {top_n} Portfolios by Weighted Score",
                    height=max(300, top_n * 45),
                    xaxis_title="Final Score",
                    yaxis_title="",
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=40, l=220),
                    font=dict(family="Arial", size=11),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Full table
                st.markdown("#### Complete Ranking Table")
                display_cols = [c for c in ["portfolio_name", "final_score", "technical_improvement_pct",
                                            "cost_score", "feasibility_score", "deployment_score",
                                            "Battery", "ManagedCharging", "PhasedInterconnection",
                                            "DemandTariff", "TransformerUpgrade"] if c in rank_df.columns]
                st.dataframe(rank_df[display_cols], use_container_width=True, height=400)

        # ── TAB: Baseline Assessment ──
        with tab_baseline:
            st.markdown(f'<div class="section-header">Baseline Violation Assessment</div>', unsafe_allow_html=True)
            st.markdown("The feeder is simulated for 24 hours under future load conditions **without** any intervention.")

            bs = data.get("base_summary", {})
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(metric_card("Grid Stress Score", f"{bs.get('grid_stress_score', 0):.0f}", "Higher = more violations", True), unsafe_allow_html=True)
            col2.markdown(metric_card("Line Overloads", f"{bs.get('total_line_overloads', 0)}", "Across 24 hours"), unsafe_allow_html=True)
            col3.markdown(metric_card("Transformer Overloads", f"{bs.get('total_transformer_overloads', 0)}", "Across 24 hours"), unsafe_allow_html=True)
            col4.markdown(metric_card("Undervoltage Events", f"{bs.get('total_undervoltage_buses', 0)}", f"Threshold: < 0.95 pu"), unsafe_allow_html=True)

            # Additional metrics
            st.markdown("")
            vc1, vc2, vc3, vc4 = st.columns(4)
            vc1.markdown(metric_card("Worst Min Voltage", f"{bs.get('worst_vmin', 0):.4f} pu"), unsafe_allow_html=True)
            vc2.markdown(metric_card("Worst Max Voltage", f"{bs.get('worst_vmax', 0):.4f} pu"), unsafe_allow_html=True)
            vc3.markdown(metric_card("Overvoltage Events", f"{bs.get('total_overvoltage_buses', 0)}"), unsafe_allow_html=True)
            vc4.markdown(metric_card("Convergence Failures", f"{bs.get('convergence_failures', 0)}"), unsafe_allow_html=True)

            # Hourly violations chart
            base_results = data.get("base_results", [])
            if base_results:
                st.markdown("")
                br_df = pd.DataFrame(base_results)
                fig = go.Figure()
                fig.add_trace(go.Bar(x=br_df["time"], y=br_df["num_overloaded_lines"], name="Line Overloads", marker_color=PWC_ORANGE))
                fig.add_trace(go.Bar(x=br_df["time"], y=br_df["num_overloaded_transformers"], name="Transformer Overloads", marker_color=PWC_ORANGE_LIGHT))
                fig.add_trace(go.Bar(x=br_df["time"], y=br_df["undervoltage_buses"], name="Undervoltage Buses", marker_color=PWC_RED))
                fig.update_layout(
                    barmode="stack", height=320,
                    title="Hourly Violation Count (Baseline — No Intervention)",
                    xaxis_title="Hour of Day", yaxis_title="Violation Count",
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=40, b=40),
                    font=dict(family="Arial", size=11),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig, use_container_width=True)

            # Grid map
            st.markdown(f'<div class="section-header">Feeder Topology with Scenario Assets</div>', unsafe_allow_html=True)
            grid_fig = render_grid_map()
            if grid_fig:
                st.plotly_chart(grid_fig, use_container_width=True)

        # ── TAB: Load Profiles ──
        with tab_profiles:
            st.markdown(f'<div class="section-header">24-Hour Synthetic Load Profiles</div>', unsafe_allow_html=True)
            profiles = data.get("profiles", {})
            if profiles:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=profiles["time"], y=profiles["feeder_mult"],
                    name="Feeder Load Multiplier", line=dict(width=3, color=PWC_DARK),
                    fill='tozeroy', fillcolor='rgba(45,45,45,0.05)'
                ))
                fig.add_trace(go.Scatter(
                    x=profiles["time"], y=profiles["ev_mw"],
                    name="EV Demand (MW)", line=dict(width=3, color=PWC_ORANGE),
                    fill='tozeroy', fillcolor='rgba(208,74,2,0.08)'
                ))
                fig.add_trace(go.Scatter(
                    x=profiles["time"], y=profiles["solar_mw"],
                    name="Solar Generation (MW)", line=dict(width=3, color=PWC_GREEN, dash="dot"),
                ))
                fig.add_trace(go.Scatter(
                    x=profiles["time"], y=profiles["dc_mw"],
                    name="Data Center (MW)", line=dict(width=3, color=PWC_RED, dash="dash"),
                ))
                fig.update_layout(
                    height=380,
                    xaxis_title="Hour of Day",
                    yaxis_title="Value",
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=20, b=40),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    font=dict(family="Arial", size=11),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Profile interpretation
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Profile Interpretation</h4>
                    <div style="font-size:0.88rem; color:{PWC_GREY}; margin-top:8px; line-height:1.7;">
                        • <strong>Feeder multiplier</strong> — Scales all existing loads (morning + evening peaks, 3% annual growth)<br>
                        • <strong>EV demand</strong> — Peaks 19:00–22:00 reflecting residential charging patterns (EIA AEO 2024)<br>
                        • <strong>Solar generation</strong> — Bell curve sunrise–sunset, reduces net demand at midday<br>
                        • <strong>Data center</strong> — Near-flat baseload (97% utilization) representing continuous compute
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── TAB: Decision Memo ──
        with tab_memo:
            st.markdown(f'<div class="section-header">Decision Memo</div>', unsafe_allow_html=True)
            memo = data.get("memo", "")
            if memo:
                st.markdown(memo)
            else:
                st.info("Decision memo will appear here after the study completes.")

            # Agent workflow summary
            st.markdown(f'<div class="section-header">Agent Workflow Log</div>', unsafe_allow_html=True)
            for cp in data.get("checkpoints", []):
                icon = "✅" if not cp.get("requires_approval") else "⚠️"
                step_name = cp['step'].replace('_', ' ').title()
                st.markdown(f"""
                <div class="agent-card complete">
                    <div class="agent-icon">{icon}</div>
                    <div>
                        <div class="agent-name">{step_name}</div>
                        <div class="agent-detail">{cp['message']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Reset button
        st.markdown("---")
        if st.button("🔄 Start New Study", key="reset"):
            st.session_state.step = 1
            st.session_state.completed = set()
            st.session_state.study_data = None
            st.rerun()
