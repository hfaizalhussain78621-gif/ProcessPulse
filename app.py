import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="ProcessPulse | Business Process Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-left: 4px solid #2563EB;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SYNTHETIC OPERATIONAL DATASET GENERATOR
# ---------------------------------------------------------
@st.cache_data
def load_process_data():
    np.random.seed(42)
    n_records = 360

    processes = [
        "Order-to-Cash",
        "Procure-to-Pay",
        "Customer Onboarding",
        "Invoice Approval",
        "IT Support Escalation",
        "Claims Processing"
    ]

    stages_map = {
        "Order-to-Cash": ["Order Entry", "Credit Check", "Fulfillment", "Billing"],
        "Procure-to-Pay": ["Requisition", "Vendor Quote", "PO Approval", "Goods Receipt"],
        "Customer Onboarding": ["KYC Submission", "Compliance Review", "Account Setup", "Welcome Call"],
        "Invoice Approval": ["OCR Scan", "3-Way Match", "Manager Sign-off", "Payment Release"],
        "IT Support Escalation": ["Ticket Triage", "L2 Diagnosis", "Engineering Fix", "QA Verification"],
        "Claims Processing": ["FNOL Intake", "Adjuster Review", "Fraud Check", "Settlement"]
    }

    sla_targets = {
        "Order-to-Cash": 24.0,
        "Procure-to-Pay": 48.0,
        "Customer Onboarding": 36.0,
        "Invoice Approval": 18.0,
        "IT Support Escalation": 12.0,
        "Claims Processing": 60.0
    }

    bottleneck_stages = {
        "Order-to-Cash": "Credit Check",
        "Procure-to-Pay": "PO Approval",
        "Customer Onboarding": "Compliance Review",
        "Invoice Approval": "Manager Sign-off",
        "IT Support Escalation": "L2 Diagnosis",
        "Claims Processing": "Adjuster Review"
    }

    root_causes = [
        "Manual Handoff Delay",
        "Incomplete Documentation",
        "Approver Bandwidth",
        "Legacy System Sync",
        "Policy Exception Review"
    ]

    regions = ["North America", "Europe", "APAC", "Middle East"]
    priorities = ["Standard", "High", "Critical"]

    records = []
    base_date = datetime(2026, 8, 1)

    for i in range(n_records):
        proc = np.random.choice(processes)
        stages = stages_map[proc]
        bn_stage = bottleneck_stages[proc]
        sla = sla_targets[proc]
        region = np.random.choice(regions, p=[0.35, 0.30, 0.20, 0.15])
        priority = np.random.choice(priorities, p=[0.60, 0.28, 0.12])
        case_id = f"PP-{1000 + i}"
        created_at = base_date + timedelta(hours=int(np.random.randint(0, 2160)))

        rework_flag = np.random.choice([0, 1], p=[0.78, 0.22])
        rework_count = int(np.random.randint(1, 4)) if rework_flag == 1 else 0

        total_cycle = 0.0
        stage_durations = {}

        for stg in stages:
            base_hrs = sla / len(stages)
            if stg == bn_stage:
                multiplier = np.random.uniform(1.4, 2.9)
            else:
                multiplier = np.random.uniform(0.5, 1.15)
            dur = round(base_hrs * multiplier + (rework_count * 2.5 if stg == bn_stage else 0), 2)
            stage_durations[stg] = dur
            total_cycle += dur

        total_cycle = round(total_cycle, 2)
        sla_breached = total_cycle > sla
        delay_hrs = round(max(0.0, total_cycle - sla), 2)
        cost_impact = round(total_cycle * np.random.uniform(18, 35) + (rework_count * 85), 2)
        cause = np.random.choice(root_causes) if sla_breached or rework_flag else "On-Track Execution"

        records.append({
            "Case_ID": case_id,
            "Process": proc,
            "Region": region,
            "Priority": priority,
            "Created_Date": created_at.date(),
            "Bottleneck_Stage": bn_stage,
            "Bottleneck_Hours": stage_durations[bn_stage],
            "Total_Cycle_Hours": total_cycle,
            "SLA_Target_Hours": sla,
            "SLA_Breached": sla_breached,
            "Delay_Hours": delay_hrs,
            "Rework_Count": rework_count,
            "Cost_Impact_USD": cost_impact,
            "Root_Cause": cause
        })

    return pd.DataFrame(records)

df = load_process_data()

# ---------------------------------------------------------
# SIDEBAR FILTERS & BRANDING
# ---------------------------------------------------------
st.sidebar.title("⚡ ProcessPulse")
st.sidebar.caption("Operational Bottleneck Intelligence")
st.sidebar.markdown("---")

selected_processes = st.sidebar.multiselect(
    "Filter by Business Process",
    options=sorted(df["Process"].unique()),
    default=sorted(df["Process"].unique())
)

selected_regions = st.sidebar.multiselect(
    "Filter by Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

selected_priorities = st.sidebar.multiselect(
    "Filter by Priority",
    options=["Standard", "High", "Critical"],
    default=["Standard", "High", "Critical"]
)

only_breached = st.sidebar.checkbox("Show Only SLA Breached Cases", value=False)

st.sidebar.markdown("---")
st.sidebar.info("**Developed by:** Faizal Hussain .H\n\nProcessPulse Analytics Suite v1.0")

# Apply Filters
filtered_df = df[
    (df["Process"].isin(selected_processes)) &
    (df["Region"].isin(selected_regions)) &
    (df["Priority"].isin(selected_priorities))
]
if only_breached:
    filtered_df = filtered_df[filtered_df["SLA_Breached"]]

# ---------------------------------------------------------
# HEADER & EXECUTIVE KPI CARDS
# ---------------------------------------------------------
st.markdown('<div class="main-header">📊 ProcessPulse — Business Bottleneck & Operational Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">End-to-end cycle time diagnostics, SLA compliance tracking, and root-cause bottleneck intelligence | Author: <b>Faizal Hussain .H</b></div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No operational records match your current filter selection. Please adjust the sidebar filters.")
    st.stop()

total_cases = len(filtered_df)
avg_cycle = filtered_df["Total_Cycle_Hours"].mean()
sla_compliance = (1 - filtered_df["SLA_Breached"].mean()) * 100
rework_rate = (filtered_df["Rework_Count"] > 0).mean() * 100
total_cost_leakage = filtered_df[filtered_df["SLA_Breached"]]["Cost_Impact_USD"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Workflow Cases", f"{total_cases:,}")
col2.metric("Avg Cycle Time", f"{avg_cycle:.1f} hrs")
col3.metric("SLA Compliance Rate", f"{sla_compliance:.1f}%", delta=f"{sla_compliance - 80:.1f}% vs 80% Goal")
col4.metric("Rework Loop Rate", f"{rework_rate:.1f}%", delta_color="inverse")
col5.metric("SLA Breach Cost Exposure", f"${total_cost_leakage:,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# TABS FOR MULTI-DIMENSIONAL ANALYSIS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Bottleneck & Cycle Diagnostics",
    "🎯 SLA & Root Cause Analysis",
    "📈 Trend & Regional Heatmap",
    "🗂️ Case Explorer & Export"
])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Average Cycle Time vs. SLA Target by Process")
        proc_summary = filtered_df.groupby("Process", as_index=False).agg(
            Avg_Cycle=("Total_Cycle_Hours", "mean"),
            SLA_Target=("SLA_Target_Hours", "mean"),
            Bottleneck_Share=("Bottleneck_Hours", "mean")
        )
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=proc_summary["Process"],
            y=proc_summary["Avg_Cycle"],
            name="Actual Avg Cycle (hrs)",
            marker_color="#2563EB"
        ))
        fig_bar.add_trace(go.Scatter(
            x=proc_summary["Process"],
            y=proc_summary["SLA_Target"],
            name="Target SLA (hrs)",
            mode="lines+markers",
            line=dict(color="#DC2626", width=3, dash="dash")
        ))
        fig_bar.update_layout(height=400, xaxis_title="", yaxis_title="Hours", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Primary Bottleneck Stage Dwell Time")
        bn_summary = filtered_df.groupby(["Process", "Bottleneck_Stage"], as_index=False).agg(
            Avg_Bottleneck_Hrs=("Bottleneck_Hours", "mean"),
            Case_Count=("Case_ID", "count")
        ).sort_values("Avg_Bottleneck_Hrs", ascending=True)
        fig_bn = px.bar(
            bn_summary,
            x="Avg_Bottleneck_Hrs",
            y="Bottleneck_Stage",
            color="Process",
            orientation="h",
            text_auto=".1f",
            labels={"Avg_Bottleneck_Hrs": "Avg Dwell Time (hrs)", "Bottleneck_Stage": "Bottleneck Stage"}
        )
        fig_bn.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_bn, use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Delay Root Cause Breakdown")
        delayed_df = filtered_df[filtered_df["Root_Cause"] != "On-Track Execution"]
        if not delayed_df.empty:
            rc_counts = delayed_df["Root_Cause"].value_counts().reset_index()
            rc_counts.columns = ["Root_Cause", "Cases"]
            fig_pie = px.pie(
                rc_counts,
                names="Root_Cause",
                values="Cases",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_layout(height=390)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.success("All filtered cases executed on track without delay root causes!")

    with c2:
        st.subheader("Rework Loops vs. Total Cycle Time")
        fig_scatter = px.box(
            filtered_df,
            x="Rework_Count",
            y="Total_Cycle_Hours",
            color="SLA_Breached",
            color_discrete_map={True: "#EF4444", False: "#10B981"},
            labels={"Rework_Count": "Number of Rework Loops", "Total_Cycle_Hours": "Total Cycle Time (hrs)"}
        )
        fig_scatter.update_layout(height=390)
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Weekly Cycle Time Trend")
        trend_df = filtered_df.copy()
        trend_df["Week"] = pd.to_datetime(trend_df["Created_Date"]).dt.to_period("W").apply(lambda r: r.start_time)
        weekly = trend_df.groupby("Week", as_index=False)["Total_Cycle_Hours"].mean()
        fig_line = px.line(
            weekly,
            x="Week",
            y="Total_Cycle_Hours",
            markers=True,
            labels={"Total_Cycle_Hours": "Avg Cycle Time (hrs)"}
        )
        fig_line.update_traces(line_color="#1D4ED8", line_width=3)
        fig_line.update_layout(height=380)
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.subheader("Regional SLA Breach Rate (%)")
        reg_df = filtered_df.groupby(["Region", "Process"], as_index=False)["SLA_Breached"].mean()
        reg_df["Breach_Pct"] = (reg_df["SLA_Breached"] * 100).round(1)
        pivot_reg = reg_df.pivot(index="Process", columns="Region", values="Breach_Pct").fillna(0)
        fig_heat = px.imshow(
            pivot_reg,
            text_auto=True,
            color_continuous_scale="YlOrRd",
            labels=dict(color="Breach %")
        )
        fig_heat.update_layout(height=380)
        st.plotly_chart(fig_heat, use_container_width=True)

with tab4:
    st.subheader("Operational Case Audit Log")
    st.dataframe(
        filtered_df.sort_values("Delay_Hours", ascending=False),
        use_container_width=True,
        height=380
    )
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Audit Report (CSV)",
        data=csv_data,
        file_name="ProcessPulse_Operational_Audit.csv",
        mime="text/csv"
    )