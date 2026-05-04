"""
============================================================
INDODANA BI ANALYST PORTFOLIO — STREAMLIT DASHBOARD
Lending Analytics Dashboard | 2022–2024
============================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Indodana BI Dashboard",
    page_icon="indodana.avif",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── BRAND COLORS ─────────────────────────────────────────────
BRAND_ORANGE  = "#E84700"
ORANGE_LIGHT  = "#FF6B2C"
ORANGE_TINT   = "#FFF3EE"
BRAND_GREEN   = "#00B86B"
WHITE         = "#FFFFFF"
NEAR_BLACK    = "#1A1A1A"
GRAY          = "#5C6370"
LIGHT_BG      = "#FFFFFF"

# Legacy mappings for compatibility
TEAL          = BRAND_ORANGE
TEAL_DARK     = BRAND_ORANGE
TEAL_LITE     = ORANGE_TINT
ORANGE        = ORANGE_LIGHT
NAVY          = NEAR_BLACK

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Nunito Sans', sans-serif;
        background-color: {LIGHT_BG};
    }}
    .stApp {{ background-color: {LIGHT_BG}; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BRAND_ORANGE} 0%, #CC3D00 100%);
    }}
    section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {{ color: #FFE5D3 !important; font-size:12px; }}

    /* Metric cards */
    .metric-card {{
        background: {WHITE};
        border-radius: 16px;
        padding: 20px 24px;
        border-left: 4px solid {BRAND_ORANGE};
        box-shadow: 0 2px 12px rgba(232,71,0,0.10);
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {NEAR_BLACK};
        line-height: 1.1;
    }}
    .metric-label {{
        font-size: 0.78rem;
        color: {GRAY};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }}
    .metric-delta {{
        font-size: 0.82rem;
        color: {BRAND_ORANGE};
        font-weight: 600;
        margin-top: 6px;
    }}

    /* Section headers */
    .section-header {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {NEAR_BLACK};
        padding: 8px 0 2px 0;
        border-bottom: 2px solid {BRAND_ORANGE};
        margin-bottom: 16px;
    }}

    /* Header banner */
    .header-banner {{
        background: linear-gradient(135deg, {BRAND_ORANGE} 0%, #CC3D00 100%);
        border-radius: 18px;
        padding: 28px 36px;
        margin-bottom: 24px;
        color: white;
    }}
    .header-title {{
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }}
    .header-sub {{
        font-size: 0.9rem;
        color: #FFE5D3;
        margin-top: 4px;
    }}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        background: {WHITE};
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        color: {GRAY};
    }}
    .stTabs [aria-selected="true"] {{
        background: {BRAND_ORANGE} !important;
        color: white !important;
    }}

    /* Chart containers */
    .chart-container {{
        background: {WHITE};
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }}

    .badge {{
        display: inline-block;
        background: {ORANGE_TINT};
        color: {BRAND_GREEN};
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }}

    /* Date input styling for visibility */
    .stDateInput input,
    section[data-testid="stSidebar"] .stDateInput input {{
        background-color: {WHITE} !important;
        color: {NEAR_BLACK} !important;
        border: 1.5px solid {BRAND_ORANGE} !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }}
    
    .stDateInput input::placeholder {{
        color: {GRAY} !important;
    }}
    
    section[data-testid="stSidebar"] .stDateInput label {{
        color: {WHITE} !important;
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ─────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    data_dir = os.path.join(base, "data")
    if not os.path.exists(os.path.join(data_dir, "loan_applications.csv")):
        data_dir = base

    loans = pd.read_csv(os.path.join(data_dir, "loan_applications.csv"), parse_dates=["application_date","disbursement_date"])
    repay = pd.read_csv(os.path.join(data_dir, "repayments.csv"), parse_dates=["due_date","paid_date"])
    loans["app_month"]    = loans["application_date"].dt.to_period("M").astype(str)
    loans["app_quarter"]  = loans["application_date"].dt.to_period("Q").astype(str)
    loans["credit_tier"]  = pd.cut(loans["credit_score"],
                                   bins=[0,549,649,749,850],
                                   labels=["High Risk (<550)","Sub-Prime (550–649)",
                                           "Near-Prime (650–749)","Prime (750+)"])
    loans["income_seg"]   = pd.cut(loans["monthly_income_idr"],
                                   bins=[0,3e6,7e6,15e6,30e6,1e9],
                                   labels=["<3M","3M–7M","7M–15M","15M–30M",">30M"])
    return loans, repay

loans_df, repay_df = load_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────
with st.sidebar:
    col_logo_sb, col_text_sb = st.columns([0.8, 3])
    with col_logo_sb:
        st.image("indodana.avif", width=50)
    with col_text_sb:
        st.markdown("### Indodana BI")
    st.markdown("<span class='badge'>Lending Analytics</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📅 Date Range**")
    min_date = loans_df["application_date"].min().date()
    max_date = loans_df["application_date"].max().date()
    date_from = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    date_to   = st.date_input("To",   value=max_date, min_value=min_date, max_value=max_date)

    st.markdown("**📦 Product**")
    all_products = loans_df["product_type"].unique().tolist()
    sel_products = st.multiselect("Product Type", all_products, default=all_products)

    st.markdown("**🌍 Province**")
    all_prov = sorted(loans_df["province"].unique().tolist())
    sel_prov = st.multiselect("Province", all_prov, default=all_prov)

    st.markdown("---")
    st.caption("Data: Synthetic | Period: 2022–2024")
    st.caption("Built for BI Analyst Portfolio")

# ── FILTER DATA ───────────────────────────────────────────────
mask = (
    (loans_df["application_date"].dt.date >= date_from) &
    (loans_df["application_date"].dt.date <= date_to) &
    (loans_df["product_type"].isin(sel_products)) &
    (loans_df["province"].isin(sel_prov))
)
df = loans_df[mask].copy()
approved_df = df[df["status"] == "Approved"]
repay_filtered = repay_df[repay_df["loan_id"].isin(approved_df["loan_id"])]

# ── HEADER ────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-banner">
    <p class="header-title">📊 Lending Portfolio Analytics</p>
    <p class="header-sub">Indodana Fintech · Business Intelligence Dashboard · 2022–2024</p>
</div>
""", unsafe_allow_html=True)

# ── KPI METRICS ───────────────────────────────────────────────
total_apps    = len(df)
total_approved= len(approved_df)
approval_rate = total_approved / total_apps * 100 if total_apps else 0
total_disburse= approved_df["loan_amount_idr"].sum() / 1e9
avg_ticket    = approved_df["loan_amount_idr"].mean() / 1e6 if len(approved_df) else 0
npl_rate      = (repay_filtered[repay_filtered["repayment_status"]=="Overdue"].shape[0] /
                 max(len(repay_filtered), 1)) * 100

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, f"{total_apps:,.0f}", "Total Applications", "📋"),
    (c2, f"{approval_rate:.1f}%", "Approval Rate", "✅"),
    (c3, f"Rp {total_disburse:.1f}B", "Total Disbursed", "💰"),
    (c4, f"Rp {avg_ticket:.1f}M", "Avg Ticket Size", "🎫"),
    (c5, f"{npl_rate:.1f}%", "NPL Rate (Overdue)", "⚠️"),
]
for col, val, label, icon in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.4rem">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Portfolio Trend", "🗺️ Geographic", "⚡ Credit Risk", "🔄 Repayment Health", "🧩 Segmentation"
])

PLOTLY_LAYOUT = dict(
    font=dict(family="Nunito Sans", color=NEAR_BLACK, size=12),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=[BRAND_ORANGE, ORANGE_LIGHT, NEAR_BLACK, "#F59E0B", "#6366F1", "#EC4899"],
    title=dict(
        font=dict(color=NEAR_BLACK, size=14, family="Nunito Sans"),
        x=0.0,
        xanchor="left",
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#E8E8E8",
        gridwidth=1,
        tickcolor=NEAR_BLACK,
        tickfont=dict(color=NEAR_BLACK, size=11),
        title=dict(font=dict(color=NEAR_BLACK, size=12)),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#E8E8E8",
        gridwidth=1,
        tickcolor=NEAR_BLACK,
        tickfont=dict(color=NEAR_BLACK, size=11),
        title=dict(font=dict(color=NEAR_BLACK, size=12)),
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_color=NEAR_BLACK,
        font_size=12,
        font_family="Nunito Sans",
    ),
)

# ── TAB 1: Portfolio Trend ────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Monthly Disbursement Trend</div>', unsafe_allow_html=True)

    monthly = (approved_df.groupby(["app_month","product_type"])
               .agg(count=("loan_id","count"), value=("loan_amount_idr","sum"))
               .reset_index())
    monthly["value_bio"] = monthly["value"] / 1e9

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(monthly, x="app_month", y="count", color="product_type",
                     title="Loans Disbursed per Month", barmode="stack",
                     color_discrete_sequence=[TEAL, ORANGE, NAVY, "#F59E0B"])
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Month", yaxis_title="# Loans")
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.area(monthly.groupby("app_month")["value_bio"].sum().reset_index(),
                       x="app_month", y="value_bio", title="Portfolio Value (Bio IDR)",
                       color_discrete_sequence=[TEAL])
        fig2.update_traces(fill="tozeroy", line_color=TEAL, fillcolor=TEAL_LITE)
        fig2.update_layout(**PLOTLY_LAYOUT, xaxis_title="Month", yaxis_title="Bio IDR")
        fig2.update_xaxes(tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Approval Rate by Product & Channel</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        funnel = (df.groupby("product_type")["status"]
                  .value_counts(normalize=True).rename("pct").reset_index())
        funnel_approved = funnel[funnel["status"]=="Approved"]
        fig3 = px.bar(funnel_approved, x="product_type", y="pct", title="Approval Rate by Product",
                      color_discrete_sequence=[TEAL])
        fig3.update_traces(texttemplate='%{y:.1%}', textposition='outside')
        fig3.update_layout(**PLOTLY_LAYOUT, yaxis_tickformat=".0%", yaxis_title="Approval Rate")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        channel_stats = (df.groupby("channel")
                          .apply(lambda x: pd.Series({
                              "Approval Rate": (x["status"]=="Approved").mean()*100,
                              "Avg Credit Score": x["credit_score"].mean(),
                              "Applications": len(x),
                          })).reset_index())
        fig4 = px.scatter(channel_stats, x="Avg Credit Score", y="Approval Rate",
                          size="Applications", color="channel", title="Channel Quality Matrix",
                          color_discrete_sequence=[TEAL, ORANGE, NAVY, "#F59E0B"])
        fig4.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

# ── TAB 2: Geographic ────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Province-Level Portfolio Performance</div>', unsafe_allow_html=True)

    geo = df.groupby("province").agg(
        total_apps=("loan_id","count"),
        approved=("status", lambda x: (x=="Approved").sum()),
        portfolio_bio=("loan_amount_idr", lambda x: x[df.loc[x.index,"status"]=="Approved"].sum()/1e9),
        avg_credit=("credit_score","mean"),
    ).reset_index()
    geo["approval_rate"] = geo["approved"] / geo["total_apps"] * 100

    geo_repay = repay_filtered.merge(approved_df[["loan_id","province"]], on="loan_id")
    geo_npl = (geo_repay.groupby("province")
               .apply(lambda x: (x["repayment_status"]=="Overdue").mean()*100)
               .rename("npl_rate").reset_index())
    geo = geo.merge(geo_npl, on="province", how="left")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(geo.sort_values("portfolio_bio", ascending=True),
                     x="portfolio_bio", y="province", orientation="h",
                     title="Portfolio Value by Province (Bio IDR)",
                     color="portfolio_bio", color_continuous_scale=[[0,TEAL_LITE],[1,TEAL_DARK]])
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.scatter(geo, x="approval_rate", y="npl_rate",
                          size="total_apps", color="province",
                          title="Approval Rate vs NPL Rate by Province",
                          labels={"approval_rate":"Approval Rate (%)", "npl_rate":"NPL Rate (%)"},
                          color_discrete_sequence=[TEAL,ORANGE,NAVY,"#F59E0B","#6366F1",
                                                   "#EC4899","#10B981","#F97316","#8B5CF6","#06B6D4"])
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Province Summary Table</div>', unsafe_allow_html=True)
    display_geo = geo.rename(columns={
        "province":"Province", "total_apps":"Applications", "approved":"Approved",
        "approval_rate":"Approval Rate %", "portfolio_bio":"Portfolio (Bio IDR)",
        "avg_credit":"Avg Credit Score", "npl_rate":"NPL Rate %"
    }).sort_values("Portfolio (Bio IDR)", ascending=False)
    for col in ["Approval Rate %","NPL Rate %","Avg Credit Score","Portfolio (Bio IDR)"]:
        display_geo[col] = display_geo[col].round(2)
    st.dataframe(display_geo, use_container_width=True, hide_index=True)

# ── TAB 3: Credit Risk ───────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Credit Risk Distribution & NPL by Tier</div>', unsafe_allow_html=True)

    tier_stats = df[df["status"]=="Approved"].groupby("credit_tier").agg(
        count=("loan_id","count"),
        avg_loan=("loan_amount_idr", lambda x: x.mean()/1e6),
        avg_dti=("dti_ratio","mean"),
    ).reset_index()

    tier_repay = repay_filtered.merge(approved_df[["loan_id","credit_tier"]], on="loan_id")
    tier_npl = (tier_repay.groupby("credit_tier")
                .apply(lambda x: (x["repayment_status"]=="Overdue").mean()*100)
                .rename("npl_rate").reset_index())
    tier_stats = tier_stats.merge(tier_npl, on="credit_tier", how="left")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(tier_stats, x="credit_tier", y="npl_rate",
                     title="NPL Rate by Credit Tier",
                     color="npl_rate",
                     color_continuous_scale=[[0,TEAL_LITE],[0.5,"#FCD34D"],[1,ORANGE]])
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                          yaxis_title="NPL Rate (%)", xaxis_title="Credit Tier")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(df[df["status"]=="Approved"], x="credit_score", nbins=40,
                            title="Credit Score Distribution (Approved Loans)",
                            color_discrete_sequence=[TEAL])
        fig2.update_layout(**PLOTLY_LAYOUT, xaxis_title="Credit Score", yaxis_title="Count")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.scatter(df[df["status"]=="Approved"].sample(min(500,len(approved_df))),
                          x="credit_score", y="dti_ratio",
                          color="credit_tier", title="Credit Score vs DTI Ratio",
                          opacity=0.6,
                          color_discrete_sequence=[TEAL, ORANGE, NAVY, "#F59E0B"])
        fig3.update_layout(**PLOTLY_LAYOUT, xaxis_title="Credit Score", yaxis_title="DTI Ratio (%)")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        status_counts = df["status"].value_counts().reset_index()
        fig4 = px.pie(status_counts, values="count", names="status",
                      title="Application Status Distribution",
                      color_discrete_map={"Approved":TEAL,"Rejected":ORANGE,"Pending":NAVY})
        fig4.update_traces(textinfo='label+percent', hole=0.45)
        fig4.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

# ── TAB 4: Repayment Health ──────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Repayment Performance & DPD Buckets</div>', unsafe_allow_html=True)

    repay_filtered["dpd_bucket"] = pd.cut(
        repay_filtered["delay_days"],
        bins=[-1,0,30,60,90,9999],
        labels=["Current (0 DPD)","1–30 DPD","31–60 DPD","61–90 DPD","90+ DPD (NPL)"]
    )
    dpd_counts = (repay_filtered.groupby("dpd_bucket", observed=True)
                  .agg(count=("repayment_id","count"),
                       exposure=("monthly_payment_idr","sum")).reset_index())
    dpd_counts["exposure_bio"] = dpd_counts["exposure"] / 1e9
    dpd_counts["pct"] = dpd_counts["count"] / dpd_counts["count"].sum() * 100

    col1, col2 = st.columns(2)
    with col1:
        dpd_colors = [TEAL, "#F59E0B", ORANGE, "#EF4444", "#7C3AED"]
        fig = px.bar(dpd_counts, x="dpd_bucket", y="pct",
                     title="Installments by DPD Bucket (%)",
                     color="dpd_bucket",
                     color_discrete_sequence=dpd_colors)
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                          yaxis_title="% of Installments", xaxis_title="DPD Bucket")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(dpd_counts, x="dpd_bucket", y="exposure_bio",
                      title="Exposure by DPD Bucket (Bio IDR)",
                      color="dpd_bucket",
                      color_discrete_sequence=dpd_colors)
        fig2.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                           yaxis_title="Exposure (Bio IDR)", xaxis_title="DPD Bucket")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Repayment Status Over Time</div>', unsafe_allow_html=True)
    repay_time = repay_filtered.copy()
    repay_time["due_month"] = repay_time["due_date"].dt.to_period("M").astype(str)
    monthly_repay = (repay_time.groupby(["due_month","repayment_status"])
                    .size().reset_index(name="count"))
    fig3 = px.bar(monthly_repay, x="due_month", y="count", color="repayment_status",
                  title="Monthly Repayments by Status",
                  barmode="stack",
                  color_discrete_map={"On Time":TEAL,"Late":"#F59E0B","Overdue":ORANGE})
    fig3.update_layout(**PLOTLY_LAYOUT, xaxis_title="Month", yaxis_title="# Installments")
    fig3.update_xaxes(tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 5: Segmentation ──────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Customer & Income Segmentation</div>', unsafe_allow_html=True)

    seg = df.groupby("income_seg", observed=True).agg(
        applications=("loan_id","count"),
        approval_rate=("status", lambda x: (x=="Approved").mean()*100),
        avg_loan=("loan_amount_idr", lambda x: x.mean()/1e6),
        avg_credit=("credit_score","mean"),
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(seg, x="income_seg", y="approval_rate",
                     title="Approval Rate by Income Segment",
                     color="income_seg",
                     color_discrete_sequence=[ORANGE_TINT, "#FFB399", BRAND_ORANGE, ORANGE_LIGHT, NEAR_BLACK])
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                          yaxis_title="Approval Rate (%)", xaxis_title="Income Segment")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(seg, x="income_seg", y="avg_loan",
                      title="Average Loan Size by Income Segment (Mio IDR)",
                      color="income_seg",
                      color_discrete_sequence=[ORANGE_TINT, "#FFB399", BRAND_ORANGE, ORANGE_LIGHT, NEAR_BLACK])
        fig2.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                           yaxis_title="Avg Loan (Mio IDR)", xaxis_title="Income Segment")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Employment Type & Loan Product Heatmap</div>', unsafe_allow_html=True)

    heatmap_data = (df[df["status"]=="Approved"]
                    .groupby(["employment_type","product_type"])
                    .size().unstack(fill_value=0))
    fig3 = px.imshow(heatmap_data,
                     title="Approved Loans: Employment Type × Product",
                     color_continuous_scale=[[0,WHITE],[0.5,TEAL_LITE],[1,TEAL_DARK]],
                     aspect="auto", text_auto=True)
    fig3.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; color:{GRAY}; font-size:0.78rem; padding:12px 0;">
    Indodana BI Portfolio Project · Synthetic Data · Built with Streamlit + Plotly ·
    <span style="color:{TEAL}; font-weight:600;">Business Intelligence Analyst</span>
</div>
""", unsafe_allow_html=True)
