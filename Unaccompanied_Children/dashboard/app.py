from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# UAC SYSTEM CAPACITY & CARE LOAD ANALYTICS DASHBOARD
# ============================================================

st.set_page_config(
    page_title="UAC | System Capacity Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Project layout expected:
# project_root/
#   dashboard/app.py
#   data/processed/uac_analytics.csv 
#   data/processed/uac_cleaned.csv
#   outputs/*.csv
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# ----------------------------- Styling -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
          radial-gradient(circle at 5% 0%, rgba(36, 118, 185, .15), transparent 27%),
          radial-gradient(circle at 95% 5%, rgba(20, 184, 166, .12), transparent 24%),
          linear-gradient(135deg, #07111f 0%, #0b1728 52%, #101b2d 100%);
        color: #edf4ff;
    }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1525 0%, #101e32 100%);
        border-right: 1px solid rgba(148,163,184,.18);
    }
    [data-testid="stSidebar"] * { color: #e5eefb; }
    .block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; color: #f4f8ff; }
    .hero {
        padding: 1.45rem 1.65rem;
        border: 1px solid rgba(148,163,184,.22);
        border-radius: 22px;
        background: linear-gradient(115deg, rgba(19,43,70,.94), rgba(15,37,56,.80));
        box-shadow: 0 18px 45px rgba(0,0,0,.18);
        margin-bottom: 1.15rem;
    }
    .eyebrow {
        color: #62e6d0; font-size: .76rem; font-weight: 800;
        letter-spacing: .15em; text-transform: uppercase;
    }
    .hero-title { font-size: clamp(1.7rem, 3vw, 2.65rem); font-weight: 800; margin: .35rem 0; }
    .hero-sub { color: #b7c8dc; font-size: 1rem; max-width: 900px; }
    .metric-card {
        border: 1px solid rgba(148,163,184,.22);
        background: linear-gradient(145deg, rgba(22,42,65,.94), rgba(13,29,47,.96));
        padding: 1rem 1.1rem; border-radius: 17px; min-height: 120px;
        box-shadow: 0 12px 28px rgba(0,0,0,.12);
    }
    .metric-label { color: #a9bdd2; font-size: .82rem; font-weight: 600; }
    .metric-value { color: #f6fbff; font-size: 1.75rem; font-weight: 800; margin-top: .3rem; }
    .metric-note { color: #6ee7d3; font-size: .76rem; margin-top: .2rem; }
    .section-label {
        color: #63e6d1; text-transform: uppercase; letter-spacing: .13em;
        font-weight: 800; font-size: .72rem; margin-bottom: .15rem;
    }
    .insight {
        padding: 1rem 1.1rem; border-radius: 15px;
        background: rgba(19,42,64,.8); border: 1px solid rgba(148,163,184,.18);
        color: #d7e5f4; min-height: 92px;
    }
    .small-muted { color: #9eb2c9; font-size: .83rem; }
    div[data-testid="stPlotlyChart"] {
        border: 1px solid rgba(148,163,184,.16);
        border-radius: 16px; padding: .35rem;
        background: rgba(11,25,42,.52);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148,163,184,.16); border-radius: 12px; overflow: hidden;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(22,42,65,.72); border-radius: 10px 10px 0 0;
        padding: 10px 18px; color: #c7d7e8;
    }
    .stTabs [aria-selected="true"] { background: #164e63 !important; color: white !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Helpers -----------------------------
def find_dataset():
    candidates = [
        DATA_DIR / "uac_analytics.csv",
        DATA_DIR / "uac_cleaned.csv",
        PROJECT_ROOT / "uac_analytics.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def read_optional_csv(filename):
    path = OUTPUT_DIR / filename
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def fmt_num(value, decimals=0):
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def add_missing_derived_columns(frame):
    frame = frame.copy()
    required_components = [
        "Children in CBP custody",
        "Children in HHS Care",
        "Children transferred out of CBP custody",
        "Children discharged from HHS Care",
    ]
    for col in required_components:
        if col not in frame.columns:
            frame[col] = pd.NA

    if "Total System Load" not in frame.columns:
        frame["Total System Load"] = pd.to_numeric(
            frame["Children in CBP custody"], errors="coerce"
        ) + pd.to_numeric(frame["Children in HHS Care"], errors="coerce")

    if "Net Intake Pressure" not in frame.columns:
        frame["Net Intake Pressure"] = (
            pd.to_numeric(frame["Children transferred out of CBP custody"], errors="coerce")
            - pd.to_numeric(frame["Children discharged from HHS Care"], errors="coerce")
        )

    return frame


def style_plot(fig, height=360):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(7,17,31,.25)",
        font=dict(family="DM Sans, sans-serif", color="#dce9f7"),
        margin=dict(l=18, r=18, t=55, b=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#10243a", font_color="#f4f8ff"),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,.13)", zerolinecolor="rgba(148,163,184,.2)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.13)", zerolinecolor="rgba(148,163,184,.2)")
    return fig


# ----------------------------- Load data -----------------------------
data_path = find_dataset()
if data_path is None:
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Unified Mentor · Analytics workspace</div>
          <div class="hero-title">System Capacity & Care Load Analytics</div>
          <div class="hero-sub">Your dashboard shell is ready, but the processed dataset was not found.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.error(
        "Dataset not found. Expected `data/processed/uac_analytics.csv` "
        "or `data/processed/uac_cleaned.csv` relative to the project root."
    )
    st.code(
        "Unified_Mentor/\n"
        "├── data/\n"
        "│   └── processed/\n"
        "│       ├── uac_analytics.csv\n"
        "│       └── uac_cleaned.csv\n"
        "└── dashboard/\n"
        "    └── app.py",
        language="text",
    )
    st.info("Save this file as `dashboard/app.py`, confirm the CSV is in the expected folder, then run the launch command in the README.")
    st.stop()

try:
    raw_df = pd.read_csv(data_path)
except Exception as exc:
    st.error(f"Could not read dataset: {exc}")
    st.stop()

if "Date" not in raw_df.columns:
    st.error("The selected dataset does not contain a `Date` column.")
    st.write("Columns found:", list(raw_df.columns))
    st.stop()

df = raw_df.copy()
# Normalize common date-column variants while preserving the remaining source column names.
if "Date" not in df.columns:
    date_alias = next((c for c in df.columns if str(c).strip().lower() in {"date", "report_date", "reporting_date"}), None)
    if date_alias is not None:
        df = df.rename(columns={date_alias: "Date"})
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date").drop_duplicates(subset=["Date"])
df = add_missing_derived_columns(df)

numeric_candidates = [
    "Children in CBP custody",
    "Children in HHS Care",
    "Children transferred out of CBP custody",
    "Children discharged from HHS Care",
    "Total System Load",
    "Net Intake Pressure",
]
for col in numeric_candidates:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Total System Load"])
if df.empty:
    st.error("No valid system-load observations remain after parsing the dataset.")
    st.stop()

# ----------------------------- Sidebar filters -----------------------------
with st.sidebar:
    st.markdown("## 📊 UAC Analytics")
    st.caption("System capacity · care load · observed reporting")
    st.markdown("---")
    st.markdown("### Filters")
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    date_range = st.date_input(
        "Reporting date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filters the observed reporting dates. Missing calendar dates are not synthesized.",
    )
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    available_years = sorted(df["Date"].dt.year.unique().tolist())
    selected_years = st.multiselect(
        "Year comparison",
        options=available_years,
        default=available_years,
    )
    st.markdown("---")
    st.markdown("### Data status")
    st.success(f"{len(df):,} valid observed records")
    st.caption(f"Source: `{data_path.relative_to(PROJECT_ROOT) if data_path.is_relative_to(PROJECT_ROOT) else data_path.name}`")
    st.caption("Forecasts are preliminary and are not operational capacity thresholds.")

filtered = df[
    (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
].copy()

# The year selector is an active filter. An empty selection intentionally shows no rows.
if selected_years:
    filtered = filtered[filtered["Date"].dt.year.isin(selected_years)].copy()
else:
    filtered = filtered.iloc[0:0].copy()

if filtered.empty:
    st.warning("No observations match this date range. Choose a wider range in the sidebar.")
    st.stop()

# ----------------------------- Header -----------------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">Unified Mentor · Data analytics project</div>
      <div class="hero-title">System Capacity & Care Load Analytics</div>
      <div class="hero-sub">
        Explore observed CBP custody and HHS care loads, transfer/discharge flows,
        reporting-period changes, and preliminary next-observation forecasting.
        <br><span class="small-muted">Reporting window: {filtered['Date'].min().strftime('%d %b %Y')} — {filtered['Date'].max().strftime('%d %b %Y')}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- KPI cards -----------------------------
latest = filtered.sort_values("Date").iloc[-1]
mean_load = filtered["Total System Load"].mean()
peak_row = filtered.loc[filtered["Total System Load"].idxmax()]
cbp_mean = filtered["Children in CBP custody"].mean()
hhs_mean = filtered["Children in HHS Care"].mean()
transfer_mean = filtered["Children transferred out of CBP custody"].mean()
discharge_mean = filtered["Children discharged from HHS Care"].mean()
latest_date = latest["Date"].strftime("%d %b %Y")

kpis = [
    ("Latest observed system load", fmt_num(latest["Total System Load"]), f"Reported {latest_date}"),
    ("Average system load", fmt_num(mean_load), "Across selected observations"),
    ("Peak observed load", fmt_num(peak_row["Total System Load"]), peak_row["Date"].strftime("%d %b %Y")),
    ("Mean HHS care", fmt_num(hhs_mean), "Children in HHS care"),
    ("Mean CBP custody", fmt_num(cbp_mean), "Children in CBP custody"),
    ("Mean transfers / discharges", f"{fmt_num(transfer_mean)} / {fmt_num(discharge_mean)}", "Average per recorded observation"),
]
cols = st.columns(3)
for idx, (label, value, note) in enumerate(kpis):
    with cols[idx % 3]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True,
        )
    if idx == 2:
        cols = st.columns(3)

st.markdown("")
st.markdown('<div class="section-label">Explore the system</div>', unsafe_allow_html=True)

tab_overview, tab_flows, tab_pressure, tab_forecast, tab_data, tab_guide = st.tabs(
    ["Overview", "Transfers & Discharges", "Pressure Signals", "Forecasting", "Data Explorer", "Project Guide"]
)

# ----------------------------- Overview -----------------------------
with tab_overview:
    left, right = st.columns([1.6, 1])
    with left:
        fig = px.line(
            filtered, x="Date", y="Total System Load",
            title="Total system load across observed reporting dates",
            markers=True,
            hover_data={"Children in CBP custody": ":,.0f", "Children in HHS Care": ":,.0f"},
        )
        fig.update_traces(line=dict(color="#55d6be", width=2.5), marker=dict(size=4))
        fig.update_layout(yaxis_title="Children", xaxis_title="")
        st.plotly_chart(style_plot(fig, 385), use_container_width=True)
        color_map = {
            "CBP custody": "#f6bd60", 
            "HHS care": "#55d6be"
        }

        comp = pd.DataFrame({ 
            "Component": ["CBP custody", "HHS care"], 
            "Mean children": [cbp_mean, hhs_mean], 
        })
    with right:
        fig = px.pie(
            comp, names="Component", values="Mean children", hole=.5,
            title="Average load composition",
            color="Component",
            color_discrete_map={"CBP custody": "#f6bd60", "HHS care": "#55d6be"}, height=200
        )
        
        fig.update_traces(textposition="outside", textinfo="label+percent",domain=dict(x=[0.1, 0.9], y=[0.1, 0.9]))
        st.plotly_chart(style_plot(fig, 385), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered["Date"], y=filtered["Children in CBP custody"],
            mode="lines", name="CBP custody", line=dict(color="#f6bd60", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=filtered["Date"], y=filtered["Children in HHS Care"],
            mode="lines", name="HHS care", line=dict(color="#55d6be", width=2),
        ))
        fig.update_layout(title="CBP custody vs HHS care", yaxis_title="Children", xaxis_title="")
        st.plotly_chart(style_plot(fig, 340), use_container_width=True)
    with c2:
        monthly = filtered.assign(Month=filtered["Date"].dt.to_period("M").astype(str)).groupby("Month", as_index=False).agg(
            Mean_Load=("Total System Load", "mean"),
            Observations=("Total System Load", "size"),
        )
        fig = px.bar(monthly, x="Month", y="Mean_Load", title="Monthly mean system load",
                     hover_data=["Observations"], color="Mean_Load", color_continuous_scale="Teal")
        fig.update_layout(xaxis_title="", yaxis_title="Mean children", coloraxis_showscale=False)
        st.plotly_chart(style_plot(fig, 340), use_container_width=True)

    st.markdown("### Quick observations")
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(
            f'<div class="insight"><b>HHS care share of mean load</b><br>'
            f'<span style="font-size:1.4rem;color:#55d6be;font-weight:800;">{(hhs_mean / mean_load * 100):.1f}%</span><br>'
            f'<span class="small-muted">Descriptive composition, not a performance rating.</span></div>',
            unsafe_allow_html=True,
        )
    with i2:
        net = filtered["Net Intake Pressure"].mean()
        st.markdown(
            f'<div class="insight"><b>Mean flow-balance proxy</b><br>'
            f'<span style="font-size:1.4rem;color:#f6bd60;font-weight:800;">{fmt_num(net)}</span><br>'
            f'<span class="small-muted">Transfers minus discharges per observed report.</span></div>',
            unsafe_allow_html=True,
        )
    with i3:
        gap = filtered["Date"].diff().dt.days.dropna()
        avg_gap = gap.mean() if not gap.empty else float("nan")
        st.markdown(
            f'<div class="insight"><b>Average reporting gap</b><br>'
            f'<span style="font-size:1.4rem;color:#a5b4fc;font-weight:800;">{fmt_num(avg_gap, 1)} days</span><br>'
            f'<span class="small-muted">Reporting dates are irregular; no missing dates are invented.</span></div>',
            unsafe_allow_html=True,
        )

# ----------------------------- Transfers and discharges -----------------------------
with tab_flows:
    st.markdown("### Operational flows")
    flow1, flow2 = st.columns(2)
    with flow1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered["Date"], y=filtered["Children transferred out of CBP custody"],
            name="Transfers out of CBP", mode="lines+markers",
            line=dict(color="#60a5fa", width=2), marker=dict(size=4),
        ))
        fig.add_trace(go.Scatter(
            x=filtered["Date"], y=filtered["Children discharged from HHS Care"],
            name="Discharges from HHS care", mode="lines+markers",
            line=dict(color="#f6bd60", width=2), marker=dict(size=4),
        ))
        fig.update_layout(title="Transfers and discharges over time", yaxis_title="Children", xaxis_title="")
        st.plotly_chart(style_plot(fig, 390), use_container_width=True)
    with flow2:
        fig = px.scatter(
            filtered,
            x="Children transferred out of CBP custody",
            y="Children discharged from HHS Care",
            color=filtered["Date"].dt.year.astype(str),
            hover_data=["Date", "Net Intake Pressure"],
            title="Transfers vs discharges by observation",
            labels={"color": "Year"},
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
        st.plotly_chart(style_plot(fig, 390), use_container_width=True)

    flow_summary = filtered[[
        "Children transferred out of CBP custody",
        "Children discharged from HHS Care",
        "Net Intake Pressure",
    ]].agg(["mean", "median", "min", "max"]).T.reset_index()
    flow_summary.columns = ["Metric", "Mean", "Median", "Minimum", "Maximum"]
    st.markdown("#### Flow summary")
    st.dataframe(flow_summary.round(2), use_container_width=True, hide_index=True)
    st.caption("Net Intake Pressure is defined here as transfers out of CBP custody minus discharges from HHS care. It is a flow-balance proxy, not a validated capacity threshold.")

# ----------------------------- Pressure signals -----------------------------
with tab_pressure:
    st.markdown("### Pressure indicators")
    st.caption("These indicators describe recorded flows. They are not clinical assessments or validated system-capacity thresholds.")
    pressure = filtered.copy()
    pressure["Pressure category"] = pressure["Net Intake Pressure"].apply(
        lambda x: "Positive" if x > 0 else ("Negative" if x < 0 else "Zero")
    )
    p1, p2 = st.columns(2)
    with p1:
        counts = pressure["Pressure category"].value_counts().reindex(["Positive", "Negative", "Zero"], fill_value=0).reset_index()
        counts.columns = ["Category", "Observations"]
        fig = px.bar(counts, x="Category", y="Observations", color="Category",
                     title="Observed flow-balance direction",
                     color_discrete_map={"Positive": "#f6bd60", "Negative": "#55d6be", "Zero": "#94a3b8"})
        st.plotly_chart(style_plot(fig, 350), use_container_width=True)
    with p2:
        fig = px.scatter(
            pressure, x="Total System Load", y="Net Intake Pressure",
            color="Pressure category", hover_data=["Date"],
            title="System load vs transfers-minus-discharges",
            color_discrete_map={"Positive": "#f6bd60", "Negative": "#55d6be", "Zero": "#94a3b8"},
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#cbd5e1")
        st.plotly_chart(style_plot(fig, 350), use_container_width=True)

    positive_share = (pressure["Net Intake Pressure"] > 0).mean() * 100
    repeated_col = "Recent Repeated Pressure"
    if repeated_col in pressure.columns:
        flag = pressure[repeated_col].fillna(False).astype(bool)
        repeated_count = int(flag.sum())
        repeated_share = flag.mean() * 100
        st.info(f"Repeated-pressure indicator is flagged on {repeated_count:,} of {len(pressure):,} selected observations ({repeated_share:.1f}%). This is an analytical flag based on the notebook's rule, not an official threshold.")
    else:
        st.info("The selected dataset does not contain `Recent Repeated Pressure`; showing the basic flow-balance indicators instead.")
    st.markdown(
        f'<div class="insight"><b>Positive flow-balance observations</b><br>'
        f'<span style="font-size:1.35rem;color:#f6bd60;font-weight:800;">{positive_share:.1f}%</span><br>'
        f'<span class="small-muted">Share of selected reports where transfers exceeded discharges.</span></div>',
        unsafe_allow_html=True,
    )

# ----------------------------- Forecasting -----------------------------
with tab_forecast:
    st.markdown("### Preliminary forecasting evaluation")
    st.caption("The evaluation predicts the next recorded observation, which is not necessarily the next calendar day.")
    forecast = read_optional_csv("holt_forecast_statistical_model_comparison.csv")
    metadata_path = OUTPUT_DIR / "selected_forecasting_model.json"
    metadata = None
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            metadata = None

    if forecast is not None and {"Model", "MAE", "RMSE"}.issubset(forecast.columns):
        forecast["MAE"] = pd.to_numeric(forecast["MAE"], errors="coerce")
        forecast["RMSE"] = pd.to_numeric(forecast["RMSE"], errors="coerce")
        forecast = forecast.dropna(subset=["MAE", "RMSE"]).sort_values("MAE")
        f1, f2 = st.columns([1, 1.4])
        with f1:
            chosen = metadata.get("selected_candidate", "Not specified") if metadata else "Not specified"
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Selected candidate</div>'
                f'<div class="metric-value" style="font-size:1.45rem;">{chosen}</div>'
                f'<div class="metric-note">Preliminary model selection</div></div>',
                unsafe_allow_html=True,
            )
            if metadata:
                st.metric("MAE", fmt_num(metadata.get("mae"), 2))
                st.metric("RMSE", fmt_num(metadata.get("rmse"), 2))
                if metadata.get("mae_improvement_percent") is not None:
                    st.metric("MAE improvement vs baseline", f"{metadata['mae_improvement_percent']:.2f}%")
        with f2:
            melted = forecast.melt(id_vars="Model", value_vars=["MAE", "RMSE"], var_name="Metric", value_name="Error")
            fig = px.bar(melted, x="Model", y="Error", color="Metric", barmode="group",
                         title="Forecast model error comparison",
                         color_discrete_map={"MAE": "#55d6be", "RMSE": "#818cf8"})
            fig.update_layout(xaxis_title="", yaxis_title="Error (children)")
            st.plotly_chart(style_plot(fig, 390), use_container_width=True)
        st.dataframe(forecast.round(3), use_container_width=True, hide_index=True)
    else:
        st.warning("Forecast comparison file not found or does not contain the expected columns.")
        st.caption("Expected file: `outputs/holt_forecast_statistical_model_comparison.csv`")
    st.warning(
        "Interpret results cautiously: the source reports have irregular dates, the evaluation period is limited, "
        "and model performance does not by itself establish operational readiness."
    )
    st.markdown("#### Experimental model")
    st.write("The notebook's interpolation-based Random Forest experiment can be displayed separately, but should not be presented as the selected primary forecast because it performed worse than its baseline and includes synthetic daily values.")

# ----------------------------- Data explorer -----------------------------
with tab_data:
    st.markdown("### Filtered observation records")
    st.caption(f"Showing {len(filtered):,} observations after date filtering.")
    search_cols = [c for c in [
        "Date", "Children in CBP custody", "Children in HHS Care",
        "Children transferred out of CBP custody", "Children discharged from HHS Care",
        "Total System Load", "Net Intake Pressure", "Recent Repeated Pressure",
    ] if c in filtered.columns]
    display_df = filtered[search_cols].copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered records (CSV)",
        data=csv,
        file_name="uac_filtered_observations.csv",
        mime="text/csv",
    )

# ----------------------------- Project guide -----------------------------
with tab_guide:
    st.markdown("### About this project")
    st.markdown(
        """
        This dashboard is part of **System Capacity & Care Load Analytics for Unaccompanied Children**.
        It summarizes observed records associated with children in CBP custody and HHS care, alongside
        transfers, discharges, reporting-period changes, and exploratory forecasting results.

        The goal is to make the supplied historical data easier to explore—not to make individual-level
        decisions or to declare that a facility or program is officially at capacity.
        """
    )

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### How to use the dashboard")
        st.markdown(
            """
            1. Choose a reporting date range in the left sidebar.
            2. Select one or more years for comparison.
            3. Use **Overview** to inspect system-load levels and composition.
            4. Use **Transfers & Discharges** to compare recorded flows.
            5. Use **Pressure Signals** to examine the flow-balance indicator.
            6. Use **Forecasting** to compare the saved statistical-model results.
            7. Use **Data Explorer** to inspect and download the filtered records.
            """
        )
    with g2:
        st.markdown("#### Definitions")
        st.markdown(
            """
            - **Total System Load:** CBP custody plus HHS care, when both source fields are available.
            - **Net Intake Pressure:** transfers out of CBP custody minus discharges from HHS care, as defined in this project.
            - **MAE:** average absolute forecast error; lower is better.
            - **RMSE:** error metric that penalizes larger misses more heavily; lower is better.
            - **Repeated-pressure flag:** an analytical indicator based on the notebook's rule, when that field is present.
            """
        )

    st.markdown("#### Important interpretation notes")
    st.warning(
        "Reporting dates are irregular. The dashboard displays recorded observations and does not fill missing "
        "calendar dates with synthetic values. The forecast evaluation is for the next recorded observation, "
        "not necessarily the next day. Pressure indicators are descriptive and are not validated clinical, "
        "legal, or operational capacity thresholds."
    )
    st.markdown("#### Project workflow")
    st.code(
        "Raw CSV → Data validation & cleaning → Feature engineering → "
        "Exploratory analysis → Pressure indicators → Forecast comparison → Dashboard",
        language="text",
    )
    st.markdown("#### Expected project files")
    st.code(
        "data/processed/uac_analytics.csv  (preferred dashboard dataset)\n"
        "data/processed/uac_cleaned.csv    (fallback dataset)\n"
        "outputs/holt_forecast_statistical_model_comparison.csv\n"
        "outputs/selected_forecasting_model.json",
        language="text",
    )
    st.caption(
        "This dashboard is an exploratory analytics artifact. Verify source definitions, data freshness, "
        "and model assumptions before using any result in an operational setting."
    )

# ----------------------------- Footer -----------------------------
st.markdown("---")
st.markdown(
    '<div class="small-muted">UAC System Capacity & Care Load Analytics · Built for exploratory decision support. '
    'Interpret trends and flags as descriptive analytical signals, not official operational determinations.</div>',
    unsafe_allow_html=True,
)


