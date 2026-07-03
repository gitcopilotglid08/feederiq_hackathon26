"""
FeederIQ – Streamlit Frontend (PwC Hackathon R2 v2)
White background, sidebar config, animated agents, HITL, filter, top-10 dropdown.
"""
import time
import requests
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="FeederIQ", page_icon="⚡", layout="wide")

API_URL = "http://localhost:8000"

# ─── Colors ───────────────────────────────────────────────────────────────────
C_ORANGE = "#D85604"
C_GOLD = "#E88D14"
C_DARK = "#2D2D2D"
C_GREY = "#7A7A7A"
C_LIGHT = "#F9F9F9"
C_GREEN = "#1B8C3A"
C_RED = "#C92A2A"

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp {{ background: white; }}
    .main .block-container {{ padding-top: 0.8rem; max-width: 1100px; }}
    section[data-testid="stSidebar"] {{ background: {C_LIGHT}; border-right: 1px solid #E8E8E8; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1rem; }}

    .brand {{ display:flex; align-items:center; gap:12px; padding:8px 0 16px 0; border-bottom:2px solid {C_ORANGE}; margin-bottom:16px; }}
    .brand .logo {{ color:{C_ORANGE}; font:900 1.6rem Georgia,serif; }}
    .brand .title {{ color:{C_DARK}; font:700 1.1rem Arial,sans-serif; }}

    .sec-head {{ font:700 1.2rem Arial,sans-serif; color:{C_DARK}; margin:24px 0 10px; padding-bottom:6px; border-bottom:2px solid {C_ORANGE}; }}
    .sub-head {{ font:600 0.95rem Arial,sans-serif; color:{C_DARK}; margin:16px 0 6px; }}

    .card {{ background:white; border-radius:10px; padding:16px 18px; margin-bottom:10px; box-shadow:0 1px 4px rgba(0,0,0,0.06); border:1px solid #EFEFEF; }}
    .card.highlight {{ border-left:4px solid {C_ORANGE}; }}
    .card .label {{ font:600 0.72rem Arial,sans-serif; color:{C_GREY}; text-transform:uppercase; letter-spacing:0.4px; margin-bottom:4px; }}
    .card .val {{ font:700 1.5rem Arial,sans-serif; color:{C_DARK}; }}
    .card .sub {{ font:400 0.82rem Arial,sans-serif; color:{C_GREY}; margin-top:2px; }}

    .agent-row {{ display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:8px; margin-bottom:8px; background:{C_LIGHT}; border:1px solid #E8E8E8; }}
    .agent-row.done {{ border-left:4px solid {C_GREEN}; background:#F0FFF4; }}
    .agent-row.running {{ border-left:4px solid {C_ORANGE}; background:#FFF8F0; }}
    .agent-row .icon {{ font-size:1.3rem; }}
    .agent-row .name {{ font:700 0.9rem Arial,sans-serif; color:{C_DARK}; }}
    .agent-row .detail {{ font:400 0.78rem Arial,sans-serif; color:{C_GREY}; }}

    .score-row {{ display:flex; align-items:center; gap:8px; margin-bottom:6px; }}
    .score-row .lbl {{ font:500 0.82rem Arial,sans-serif; color:{C_GREY}; width:160px; }}
    .score-row .bar {{ flex:1; height:7px; background:#EFEFEF; border-radius:4px; }}
    .score-row .fill {{ height:7px; background:{C_ORANGE}; border-radius:4px; }}
    .score-row .num {{ font:700 0.82rem Arial,sans-serif; color:{C_DARK}; width:50px; text-align:right; }}

    .rank-card {{ background:white; border-radius:10px; padding:14px 18px; margin-bottom:8px; border:1px solid #EFEFEF; box-shadow:0 1px 3px rgba(0,0,0,0.04); }}
    .rank-card.top {{ border:2px solid {C_ORANGE}; }}
    .rank-card .rc-name {{ font:700 1rem Arial,sans-serif; color:{C_DARK}; }}
    .rank-card .rc-score {{ font:800 1.2rem Arial,sans-serif; color:{C_ORANGE}; }}

    .stButton > button {{ background:{C_ORANGE}; color:white; border:none; border-radius:6px; padding:10px 24px; font:700 0.9rem Arial,sans-serif; }}
    .stButton > button:hover {{ background:{C_GOLD}; }}

    .info-box {{ background:#F8F9FA; border-radius:8px; padding:12px 16px; margin:8px 0; border:1px solid #E8E8E8; }}
    .info-box .txt {{ font:400 0.84rem Arial,sans-serif; color:{C_DARK}; line-height:1.6; }}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def card(label, value, sub="", highlight=True):
    cls = "card highlight" if highlight else "card"
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="{cls}"><div class="label">{label}</div><div class="val">{value}</div>{sub_html}</div>'


def score_bar(label, value, max_val=10):
    pct = min(100, (value / max_val) * 100)
    return f'''<div class="score-row">
        <div class="lbl">{label}</div>
        <div class="bar"><div class="fill" style="width:{pct}%"></div></div>
        <div class="num">{value:.1f}</div>
    </div>'''


def friendly_name(portfolio_name):
    """Already handled by backend now, but fallback."""
    return portfolio_name


def render_grid_map():
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

    primary = {k: v for k, v in buses.items() if not k.startswith("s") and not k.endswith("r")}
    ev_buses = {"60", "83", "90", "92", "114"}
    solar_buses = {"66", "80", "92", "104", "110"}
    dc_bus = "67"

    xs, ys, colors, sizes, hovers, texts = [], [], [], [], [], []
    for bus, (x, y) in primary.items():
        xs.append(x)
        ys.append(y)
        if bus == dc_bus:
            colors.append(C_RED)
            sizes.append(18)
            hovers.append(f"<b>Bus {bus}</b><br>🏢 Data Center")
            texts.append("")
        elif bus in ev_buses and bus in solar_buses:
            colors.append("#7B2D8B")
            sizes.append(14)
            hovers.append(f"<b>Bus {bus}</b><br>⚡ EV + ☀️ Solar")
            texts.append(bus)
        elif bus in ev_buses:
            colors.append(C_ORANGE)
            sizes.append(13)
            hovers.append(f"<b>Bus {bus}</b><br>⚡ EV Charging")
            texts.append(bus)
        elif bus in solar_buses:
            colors.append(C_GREEN)
            sizes.append(13)
            hovers.append(f"<b>Bus {bus}</b><br>☀️ Solar PV")
            texts.append(bus)
        else:
            colors.append("#CCCCCC")
            sizes.append(5)
            hovers.append(f"Bus {bus}")
            texts.append("")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode='markers',
        marker=dict(size=sizes, color=colors, line=dict(width=0.5, color='white')),
        text=hovers, hoverinfo='text', showlegend=False,
    ))
    # Only label key buses
    key_xs = [x for x, t in zip(xs, texts) if t]
    key_ys = [y for y, t in zip(ys, texts) if t]
    key_texts = [t for t in texts if t]
    fig.add_trace(go.Scatter(
        x=key_xs, y=key_ys, mode='text',
        text=key_texts, textposition="top center",
        textfont=dict(size=9, color=C_DARK), showlegend=False, hoverinfo='skip',
    ))
    # Legend
    for lbl, clr, sz in [("Data Center", C_RED, 14), ("EV Charging", C_ORANGE, 11),
                          ("Solar PV", C_GREEN, 11), ("EV + Solar", "#7B2D8B", 11)]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                  marker=dict(size=sz, color=clr), name=lbl))

    fig.update_layout(
        height=360, margin=dict(t=5, b=5, l=5, r=5),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center", font=dict(size=10)),
    )
    return fig


# ─── Session State ────────────────────────────────────────────────────────────
if "study_data" not in st.session_state:
    st.session_state.study_data = None
if "running" not in st.session_state:
    st.session_state.running = False

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand"><span class="logo">pwc</span><span class="title">FeederIQ</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sub-head">📅 Planning Horizon</div>', unsafe_allow_html=True)
    horizon = st.selectbox("Horizon", ["3m", "6m", "12m", "18m", "3yr", "5yr"],
                           index=2, format_func=lambda x: {"3m": "3 Months", "6m": "6 Months", "12m": "12 Months",
                                                            "18m": "18 Months", "3yr": "3 Years", "5yr": "5 Years"}[x],
                           label_visibility="collapsed")

    st.markdown('<div class="sub-head">⚡ EV Growth</div>', unsafe_allow_html=True)
    ev_level = st.selectbox("EV", ["Low", "Base", "High"], index=1,
                            format_func=lambda x: {"Low": "Low (15% annually)", "Base": "Base (20% annually)", "High": "High (25% annually)"}[x],
                            label_visibility="collapsed")
    ev_custom = st.number_input("Custom growth %", min_value=5, max_value=50,
                                value={"Low": 15, "Base": 20, "High": 25}[ev_level], step=1, key="ev_c")

    st.markdown('<div class="sub-head">☀️ Solar Adoption</div>', unsafe_allow_html=True)
    solar_level = st.selectbox("Solar", ["Low", "Base", "High"], index=1,
                               format_func=lambda x: {"Low": "Low (100 MW)", "Base": "Base (200 MW)", "High": "High (300 MW)"}[x],
                               label_visibility="collapsed")

    st.markdown('<div class="sub-head">🏢 Data Center</div>', unsafe_allow_html=True)
    dc_level = st.selectbox("DC Size", ["Low", "Moderate", "High"], index=1,
                            format_func=lambda x: {"Low": "Low (1.0 MW)", "Moderate": "Moderate (1.75 MW)", "High": "High (3.0 MW)"}[x],
                            label_visibility="collapsed")
    dc_timeline = st.selectbox("Connection timeline", ["6m", "12m", "18m"], index=1,
                               format_func=lambda x: {"6m": "6 Months", "12m": "12 Months", "18m": "18 Months"}[x],
                               label_visibility="collapsed")

    st.markdown('<div class="sub-head">🎯 Solution Preferences</div>', unsafe_allow_html=True)
    st.caption("Select interventions that **must** be included in recommended solutions:")
    filter_battery = st.checkbox("Battery Storage", key="f_bat")
    filter_mc = st.checkbox("Managed EV Charging", key="f_mc")
    filter_pi = st.checkbox("Phased Interconnection", key="f_pi")
    filter_dt = st.checkbox("Demand Tariff", key="f_dt")
    filter_tu = st.checkbox("Transformer Upgrade", key="f_tu")

    st.markdown('<div class="sub-head">⚙️ Study Parameters</div>', unsafe_allow_html=True)
    max_portfolios = st.slider("Portfolios to evaluate", 10, 120, 60, step=10)
    max_active = st.slider("Max measures per portfolio", 1, 5, 3)

    st.markdown("---")
    run_btn = st.button("▶  Run Study", use_container_width=True)

# ─── Main Area ────────────────────────────────────────────────────────────────
st.markdown('<div class="brand"><span class="logo">pwc</span><span class="title">FeederIQ — Agentic Distribution Planning</span></div>', unsafe_allow_html=True)

if run_btn:
    st.session_state.running = True
    st.session_state.study_data = None

# ── Agent Execution ───────────────────────────────────────────────────────────
if st.session_state.running and st.session_state.study_data is None:
    st.markdown('<div class="sec-head">Agent Execution</div>', unsafe_allow_html=True)
    st.markdown("Each agent performs a specialized step in the planning analysis pipeline.")

    agents = [
        ("🔬", "Scenario Agent", "Building 24-hour load and generation profiles from your selections"),
        ("⚡", "Simulation Agent", "Running OpenDSS power flow across 24 hourly timesteps"),
        ("🔍", "Constraint Agent", "Identifying voltage violations and equipment overloads"),
        ("🌱", "NWA Agent", "Evaluating non-wires alternatives (batteries, managed charging, tariffs)"),
        ("🔧", "Capex Agent", "Evaluating traditional infrastructure upgrade options"),
        ("📊", "Recommendation Agent", "Scoring and ranking all candidate solutions"),
    ]

    agent_container = st.empty()
    progress = st.progress(0)

    # Call API
    payload = {
        "horizon_label": horizon, "ev_level": ev_level, "solar_level": solar_level,
        "dc_level": dc_level, "dc_timeline_label": dc_timeline,
        "max_active_measures": max_active, "max_portfolios": max_portfolios,
    }

    api_done = False
    for i, (icon, name, detail) in enumerate(agents):
        # Animate fill
        for pct in range(0, 101, 5):
            progress.progress((i + pct / 100) / len(agents))
            html = ""
            for j, (ic, nm, dt) in enumerate(agents):
                if j < i:
                    html += f'<div class="agent-row done"><span class="icon">{ic}</span><div><div class="name">{nm}</div><div class="detail">✓ Complete</div></div></div>'
                elif j == i:
                    fill_w = pct
                    html += f'<div class="agent-row running"><span class="icon">{ic}</span><div><div class="name">{nm}</div><div class="detail">{dt}</div><div style="margin-top:6px;height:5px;background:#EFEFEF;border-radius:3px;"><div style="height:5px;background:{C_ORANGE};border-radius:3px;width:{fill_w}%;transition:width 0.1s;"></div></div></div></div>'
                else:
                    html += f'<div class="agent-row"><span class="icon">{ic}</span><div><div class="name">{nm}</div><div class="detail">{dt}</div></div></div>'
            agent_container.markdown(html, unsafe_allow_html=True)

            if i == 0 and pct == 0 and not api_done:
                try:
                    resp = requests.post(f"{API_URL}/study", json=payload, timeout=300)
                    resp.raise_for_status()
                    st.session_state.study_data = resp.json()
                    api_done = True
                except Exception as e:
                    st.error(f"Connection failed: {e}. Is the backend running?")
                    st.session_state.running = False
                    st.stop()
            else:
                time.sleep(0.04)

    # All done
    progress.progress(1.0)
    html = ""
    for ic, nm, dt in agents:
        html += f'<div class="agent-row done"><span class="icon">{ic}</span><div><div class="name">{nm}</div><div class="detail">✓ Complete</div></div></div>'
    agent_container.markdown(html, unsafe_allow_html=True)
    time.sleep(0.5)
    st.session_state.running = False
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.study_data:
    data = st.session_state.study_data

    # Apply user filters
    ranking = data.get("ranking", [])
    filters = {}
    if filter_battery:
        filters["Battery"] = True
    if filter_mc:
        filters["ManagedCharging"] = True
    if filter_pi:
        filters["PhasedInterconnection"] = True
    if filter_dt:
        filters["DemandTariff"] = True
    if filter_tu:
        filters["TransformerUpgrade"] = True

    if filters:
        ranking = [r for r in ranking if all(r.get(k, 0) > 0 for k in filters)]

    if not ranking:
        st.warning("No portfolios match your filter criteria. Try removing some filters.")
        st.stop()

    # Top 10 dropdown
    top10 = ranking[:10]
    top10_names = [r["portfolio_name"] for r in top10]

    # ── Tabs ──
    tab_rec, tab_rank, tab_baseline, tab_profiles, tab_memo = st.tabs([
        "✅ Recommendation", "📊 Rankings", "🔍 Baseline", "📈 Profiles", "📝 Memo"
    ])

    # ════════════════════════ RECOMMENDATION TAB ════════════════════════════════
    with tab_rec:
        st.markdown('<div class="sec-head">Recommended Solution</div>', unsafe_allow_html=True)

        # Human-in-the-loop: select from top 10
        st.markdown('<div class="sub-head">Select from Top 10 Solutions</div>', unsafe_allow_html=True)
        st.caption("Review the top-ranked options and select your preferred solution. The system recommends #1 but you can override.")
        selected_idx = st.selectbox("Solution", range(len(top10)),
                                    format_func=lambda i: f"#{i+1}  —  {top10_names[i]}  (Score: {top10[i]['final_score']:.2f})",
                                    label_visibility="collapsed")
        selected = top10[selected_idx]

        # NWA resolution badge
        if data.get("nwa_resolved_all"):
            st.success("Non-wires alternatives fully resolve all grid violations. No traditional capex required.")

        # Selected solution card
        st.markdown(f'''<div class="rank-card top" style="margin-top:12px;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div class="label" style="font:600 0.72rem Arial;color:{C_GREY};text-transform:uppercase;">Selected Solution</div>
                    <div class="rc-name" style="margin-top:4px;">{selected["portfolio_name"]}</div>
                </div>
                <div class="rc-score">{selected["final_score"]:.2f}</div>
            </div>
        </div>''', unsafe_allow_html=True)

        # Score breakdown
        st.markdown('<div class="sub-head">Score Breakdown</div>', unsafe_allow_html=True)

        col_bars, col_radar = st.columns([1, 1])
        with col_bars:
            grid_relief = selected.get("grid_relief_score", selected.get("technical_score", 0))
            cost_sc = selected.get("cost_score", 0)
            speed_sc = selected.get("speed_to_value_score",
                                    (selected.get("feasibility_score", 0) + selected.get("deployment_score", 0)) / 2)
            esg_sc = selected.get("esg_score", 8)

            st.markdown(
                score_bar("Grid Relief (40%)", grid_relief) +
                score_bar("Cost Efficiency (25%)", cost_sc) +
                score_bar("Speed to Value (20%)", speed_sc) +
                score_bar("ESG Alignment (15%)", esg_sc),
                unsafe_allow_html=True
            )
            st.markdown(f'''<div class="info-box"><div class="txt">
                <b>Grid Relief</b> → % reduction in overloads and voltage violations<br>
                <b>Cost Efficiency</b> → Lower implementation cost relative to full capex<br>
                <b>Speed to Value</b> → How quickly the solution can be deployed and deliver results<br>
                <b>ESG Alignment</b> → Sustainability benefit (lower carbon, less material intensity)
            </div></div>''', unsafe_allow_html=True)

        with col_radar:
            cats = ['Grid Relief', 'Cost', 'Speed', 'ESG']
            vals = [grid_relief, cost_sc, speed_sc, esg_sc]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill='toself', fillcolor=f'rgba(216,86,4,0.12)',
                line=dict(color=C_ORANGE, width=2.5), name="Selected",
            ))
            # Runner up
            if len(top10) > 1:
                runner = top10[1] if selected_idx == 0 else top10[0]
                r_vals = [
                    runner.get("grid_relief_score", runner.get("technical_score", 0)),
                    runner.get("cost_score", 0),
                    runner.get("speed_to_value_score", (runner.get("feasibility_score", 0) + runner.get("deployment_score", 0)) / 2),
                    runner.get("esg_score", 8),
                ]
                fig.add_trace(go.Scatterpolar(
                    r=r_vals + [r_vals[0]], theta=cats + [cats[0]],
                    fill='toself', fillcolor='rgba(122,122,122,0.05)',
                    line=dict(color=C_GREY, width=1.5, dash='dot'),
                    name="Comparison",
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=9))),
                showlegend=True, height=280, margin=dict(t=20, b=20, l=40, r=40),
                paper_bgcolor="white", font=dict(family="Arial", size=10),
                legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Before vs After
        st.markdown('<div class="sub-head">Impact Assessment</div>', unsafe_allow_html=True)
        st.caption("Comparison of grid stress before and after applying the selected solution.")
        bs = data.get("base_summary", {})
        impr = selected.get("technical_improvement_pct", 0)
        after_stress = bs.get("grid_stress_score", 0) * (1 - impr / 100)

        ba1, ba2, ba3 = st.columns(3)
        ba1.markdown(card("Before", f"{bs.get('grid_stress_score', 0):.0f}", "Grid stress score (no intervention)"), unsafe_allow_html=True)
        ba2.markdown(card("After", f"{after_stress:.0f}", f"↓ {impr:.1f}% reduction"), unsafe_allow_html=True)
        ba3.markdown(card("Improvement", f"{impr:.1f}%", "Violation and overload reduction"), unsafe_allow_html=True)

        # Hourly comparison: baseline vs selected
        base_results = data.get("base_results", [])
        if base_results:
            st.markdown('<div class="sub-head">Hourly Overload Comparison</div>', unsafe_allow_html=True)
            st.caption("Baseline violations (orange) vs estimated post-intervention (green). Reduction proportional to Grid Relief score.")
            br_df = pd.DataFrame(base_results)
            reduction_factor = 1 - (impr / 100)
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(x=br_df["time"], y=br_df["num_overloaded_lines"],
                                       name="Baseline Overloads", marker_color=C_ORANGE, opacity=0.7))
            fig_comp.add_trace(go.Bar(x=br_df["time"], y=(br_df["num_overloaded_lines"] * reduction_factor).astype(int),
                                       name="After Intervention", marker_color=C_GREEN, opacity=0.7))
            fig_comp.update_layout(barmode="group", height=260, margin=dict(t=10, b=30),
                                    xaxis_title="Hour", yaxis_title="Line Overloads",
                                    plot_bgcolor="white", paper_bgcolor="white",
                                    legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
                                    font=dict(family="Arial", size=10))
            st.plotly_chart(fig_comp, use_container_width=True)

    # ════════════════════════ RANKINGS TAB ═════════════════════════════════════
    with tab_rank:
        st.markdown('<div class="sec-head">Portfolio Rankings</div>', unsafe_allow_html=True)
        st.caption("All evaluated solutions ranked by weighted multi-criteria score. Click column headers to sort by any dimension.")

        # Top 3 cards
        for idx, row in enumerate(ranking[:3]):
            badges = ["🥇", "🥈", "🥉"]
            cls = "rank-card top" if idx == 0 else "rank-card"
            st.markdown(f'''<div class="{cls}">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:1.2rem;">{badges[idx]}</span>
                        <span class="rc-name">{row["portfolio_name"]}</span>
                    </div>
                    <span class="rc-score">{row["final_score"]:.2f}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-top:8px;">
                    <div><span style="font:500 0.7rem Arial;color:{C_GREY};">Grid Relief</span><br><b>{row.get("technical_improvement_pct",0):.1f}%</b></div>
                    <div><span style="font:500 0.7rem Arial;color:{C_GREY};">Cost</span><br><b>{row.get("cost_score",0):.1f}/10</b></div>
                    <div><span style="font:500 0.7rem Arial;color:{C_GREY};">Speed</span><br><b>{row.get("speed_to_value_score", (row.get("feasibility_score",0)+row.get("deployment_score",0))/2):.1f}/10</b></div>
                    <div><span style="font:500 0.7rem Arial;color:{C_GREY};">ESG</span><br><b>{row.get("esg_score",0):.1f}/10</b></div>
                </div>
            </div>''', unsafe_allow_html=True)

        # Bar chart
        if len(ranking) > 3:
            top_n = min(10, len(ranking))
            chart_data = ranking[:top_n]
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=[r["portfolio_name"] for r in chart_data][::-1],
                x=[r["final_score"] for r in chart_data][::-1],
                orientation='h',
                marker_color=[C_ORANGE if i == top_n-1 else C_GOLD for i in range(top_n)],
                text=[f'{r["final_score"]:.2f}' for r in chart_data][::-1],
                textposition='outside',
            ))
            fig_bar.update_layout(
                height=max(260, top_n * 36), margin=dict(t=10, l=250, b=20),
                xaxis_title="Score", plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Arial", size=10),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Data table
        st.markdown('<div class="sub-head">Full Results Table</div>', unsafe_allow_html=True)
        rank_df = pd.DataFrame(ranking)
        display_cols = [c for c in ["portfolio_name", "final_score", "technical_improvement_pct",
                                    "cost_score", "speed_to_value_score", "esg_score",
                                    "grid_relief_score"] if c in rank_df.columns]
        # Fallback for older field names
        if "speed_to_value_score" not in rank_df.columns and "feasibility_score" in rank_df.columns:
            rank_df["speed_to_value_score"] = (rank_df["feasibility_score"] + rank_df["deployment_score"]) / 2
            display_cols = [c for c in ["portfolio_name", "final_score", "technical_improvement_pct",
                                        "cost_score", "speed_to_value_score", "esg_score"] if c in rank_df.columns]
        st.dataframe(rank_df[display_cols] if display_cols else rank_df, use_container_width=True, height=350)

    # ════════════════════════ BASELINE TAB ═════════════════════════════════════
    with tab_baseline:
        st.markdown('<div class="sec-head">Baseline Grid Assessment</div>', unsafe_allow_html=True)
        st.caption("The feeder is simulated for 24 hours under projected future load conditions without any intervention applied.")

        bs = data.get("base_summary", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(card("Grid Stress Score", f"{bs.get('grid_stress_score',0):.0f}", "Higher → more violations"), unsafe_allow_html=True)
        c2.markdown(card("Line Overloads", str(bs.get('total_line_overloads', 0)), "Total across 24 hours"), unsafe_allow_html=True)
        c3.markdown(card("Transformer Overloads", str(bs.get('total_transformer_overloads', 0)), "Total across 24 hours"), unsafe_allow_html=True)
        c4.markdown(card("Undervoltage Events", str(bs.get('total_undervoltage_buses', 0)), "Below 0.95 per-unit"), unsafe_allow_html=True)

        c5, c6, c7, c8 = st.columns(4)
        c5.markdown(card("Min Voltage", f"{bs.get('worst_vmin',0):.4f} pu", "Worst hour"), unsafe_allow_html=True)
        c6.markdown(card("Max Voltage", f"{bs.get('worst_vmax',0):.4f} pu", "Worst hour"), unsafe_allow_html=True)
        c7.markdown(card("Overvoltage Events", str(bs.get('total_overvoltage_buses', 0)), "Above 1.05 per-unit"), unsafe_allow_html=True)
        c8.markdown(card("Convergence Failures", str(bs.get('convergence_failures', 0)), "Non-converged hours"), unsafe_allow_html=True)

        # Hourly chart
        base_results = data.get("base_results", [])
        if base_results:
            st.markdown('<div class="sub-head">Hourly Violation Breakdown</div>', unsafe_allow_html=True)
            st.caption("Stacked count of equipment overloads and voltage violations at each hour of the simulated day.")
            br_df = pd.DataFrame(base_results)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=br_df["time"], y=br_df["num_overloaded_lines"], name="Line Overloads", marker_color=C_ORANGE))
            fig2.add_trace(go.Bar(x=br_df["time"], y=br_df["num_overloaded_transformers"], name="Transformer Overloads", marker_color=C_GOLD))
            fig2.add_trace(go.Bar(x=br_df["time"], y=br_df["undervoltage_buses"], name="Undervoltage", marker_color=C_RED))
            fig2.update_layout(barmode="stack", height=280, margin=dict(t=10, b=30),
                                xaxis_title="Hour of Day", yaxis_title="Count",
                                plot_bgcolor="white", paper_bgcolor="white",
                                legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
                                font=dict(family="Arial", size=10))
            st.plotly_chart(fig2, use_container_width=True)

        # Grid map
        st.markdown('<div class="sub-head">Feeder Topology</div>', unsafe_allow_html=True)
        st.caption("IEEE 123-bus test feeder with scenario assets. Hover over nodes to see details.")
        grid_fig = render_grid_map()
        if grid_fig:
            st.plotly_chart(grid_fig, use_container_width=True)

    # ════════════════════════ PROFILES TAB ═════════════════════════════════════
    with tab_profiles:
        st.markdown('<div class="sec-head">24-Hour Load Profiles</div>', unsafe_allow_html=True)
        st.caption("Synthetic demand and generation curves used in the simulation. Profiles are shaped by scenario selections and scaled by planning horizon.")

        profiles = data.get("profiles", {})
        if profiles:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=profiles["time"], y=profiles["feeder_mult"],
                                       name="Feeder Load Multiplier", line=dict(width=2.5, color=C_DARK),
                                       fill='tozeroy', fillcolor='rgba(45,45,45,0.04)'))
            fig3.add_trace(go.Scatter(x=profiles["time"], y=profiles["ev_mw"],
                                       name="EV Demand (MW)", line=dict(width=2.5, color=C_ORANGE),
                                       fill='tozeroy', fillcolor='rgba(216,86,4,0.06)'))
            fig3.add_trace(go.Scatter(x=profiles["time"], y=profiles["solar_mw"],
                                       name="Solar Generation (MW)", line=dict(width=2.5, color=C_GREEN, dash="dot")))
            fig3.add_trace(go.Scatter(x=profiles["time"], y=profiles["dc_mw"],
                                       name="Data Center (MW)", line=dict(width=2.5, color=C_RED, dash="dash")))
            fig3.update_layout(height=320, margin=dict(t=10, b=30),
                                xaxis_title="Hour of Day", yaxis_title="Value",
                                plot_bgcolor="white", paper_bgcolor="white",
                                legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
                                font=dict(family="Arial", size=10))
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown(f'''<div class="info-box"><div class="txt">
                <b>Feeder Multiplier</b> scales all existing loads on the feeder (morning and evening peaks, 3% annual growth)<br><br>
                <b>EV Demand</b> peaks between 19:00 and 22:00, reflecting residential charging patterns. Source: EIA Annual Energy Outlook 2024<br><br>
                <b>Solar Generation</b> follows a bell curve from sunrise to sunset, reducing net demand at midday<br><br>
                <b>Data Center</b> operates at near-constant baseload (97% utilization) representing continuous compute operations
            </div></div>''', unsafe_allow_html=True)

    # ════════════════════════ MEMO TAB ═════════════════════════════════════════
    with tab_memo:
        st.markdown('<div class="sec-head">Planning Decision Memo</div>', unsafe_allow_html=True)
        memo = data.get("memo", "")
        if memo:
            st.markdown(memo)
        else:
            st.info("Decision memo content will appear here.")

        # Agent log
        st.markdown('<div class="sub-head">Agent Workflow Log</div>', unsafe_allow_html=True)
        for cp in data.get("checkpoints", []):
            icon = "✅" if not cp.get("requires_approval") else "⚠️"
            step_name = cp['step'].replace('_', ' ').title()
            st.markdown(f'''<div class="agent-row done">
                <span class="icon">{icon}</span>
                <div><div class="name">{step_name}</div><div class="detail">{cp["message"]}</div></div>
            </div>''', unsafe_allow_html=True)

    # Reset
    st.markdown("---")
    if st.button("🔄  Start New Study"):
        st.session_state.study_data = None
        st.session_state.running = False
        st.rerun()

elif not st.session_state.running:
    # Landing page
    st.markdown(f'''<div class="info-box"><div class="txt" style="font-size:0.95rem;">
        <b>FeederIQ</b> is an AI-powered planning copilot that stress-tests distribution feeders under future EV, solar, and data center growth scenarios.<br><br>
        Configure your scenario in the sidebar and click <b>Run Study</b> to start the agentic analysis pipeline.
    </div></div>''', unsafe_allow_html=True)

    st.markdown('<div class="sub-head">How It Works</div>', unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    h1.markdown(card("Step 1", "Configure", "Select growth scenarios and solution preferences", False), unsafe_allow_html=True)
    h2.markdown(card("Step 2", "Analyze", "6 AI agents run simulation and evaluate interventions", False), unsafe_allow_html=True)
    h3.markdown(card("Step 3", "Decide", "Review ranked solutions with multi-criteria scoring", False), unsafe_allow_html=True)

    # Show grid
    st.markdown('<div class="sub-head">IEEE 123-Bus Test Feeder</div>', unsafe_allow_html=True)
    st.caption("Hover over nodes to see asset details. Key buses are labeled.")
    grid_fig = render_grid_map()
    if grid_fig:
        st.plotly_chart(grid_fig, use_container_width=True)
