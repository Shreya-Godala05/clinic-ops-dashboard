"""
Clinic Operations Analytics Dashboard
--------------------------------------
An interactive dashboard for tracking scheduling efficiency, billing
collection, and patient satisfaction for a small clinic -- the kind
of operational reporting a Project/Operations Coordinator would build
and present to stakeholders.

Run with: streamlit run app.py
"""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "clinic.db"

st.set_page_config(page_title="Clinic Ops Dashboard", layout="wide")


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    appointments = pd.read_sql("SELECT * FROM appointments", conn, parse_dates=["appointment_date"])
    billing = pd.read_sql("SELECT * FROM billing", conn)
    feedback = pd.read_sql("SELECT * FROM feedback", conn, parse_dates=["feedback_date"])
    patients = pd.read_sql("SELECT * FROM patients", conn, parse_dates=["registered_on"])
    conn.close()
    return appointments, billing, feedback, patients


appointments, billing, feedback, patients = load_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
departments = ["All"] + sorted(appointments["department"].unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)

min_date = appointments["appointment_date"].min().date()
max_date = appointments["appointment_date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

filtered = appointments.copy()
if selected_dept != "All":
    filtered = filtered[filtered["department"] == selected_dept]
if len(date_range) == 2:
    start, end = date_range
    filtered = filtered[(filtered["appointment_date"].dt.date >= start) &
                         (filtered["appointment_date"].dt.date <= end)]

# ---------------- Header ----------------
st.title("🏥 Clinic Operations Dashboard")
st.caption("Scheduling efficiency, billing collection, and patient satisfaction at a glance")

# ---------------- KPI row ----------------
total_appts = len(filtered)
no_show_rate = (filtered["status"] == "No-show").mean() * 100 if total_appts else 0
completed_ids = filtered.loc[filtered["status"] == "Completed", "appointment_id"]
appt_billing = billing[billing["appointment_id"].isin(completed_ids)]

total_billed = appt_billing["billed_amount"].sum()
total_collected = appt_billing["paid_amount"].sum()
collection_rate = (total_collected / total_billed * 100) if total_billed else 0

appt_feedback = feedback[feedback["appointment_id"].isin(completed_ids)]
avg_rating = appt_feedback["rating"].mean() if len(appt_feedback) else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Appointments", f"{total_appts:,}")
col2.metric("No-show Rate", f"{no_show_rate:.1f}%")
col3.metric("Billing Collection Rate", f"{collection_rate:.1f}%",
            help="Amount actually collected vs. amount billed for completed visits")
col4.metric("Avg. Patient Rating", f"{avg_rating:.1f} / 5" if avg_rating else "N/A")

st.divider()

# ---------------- Row 1: volume trend + status breakdown ----------------
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Appointment Volume Over Time")
    monthly = (filtered.set_index("appointment_date")
               .resample("ME").size()
               .reset_index(name="appointments"))
    fig = px.line(monthly, x="appointment_date", y="appointments", markers=True)
    fig.update_layout(xaxis_title="Month", yaxis_title="Appointments")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Appointment Status")
    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(status_counts, names="status", values="count", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 2: department load + payment methods ----------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Appointments by Department")
    dept_counts = filtered["department"].value_counts().reset_index()
    dept_counts.columns = ["department", "count"]
    fig = px.bar(dept_counts, x="department", y="count", color="department")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Billing Status Breakdown")
    pay_counts = appt_billing["payment_status"].value_counts().reset_index()
    pay_counts.columns = ["payment_status", "count"]
    fig = px.bar(pay_counts, x="payment_status", y="count", color="payment_status")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 3: feedback ----------------
st.subheader("Patient Feedback")
c5, c6 = st.columns([1, 2])

with c5:
    rating_counts = appt_feedback["rating"].value_counts().sort_index().reset_index()
    rating_counts.columns = ["rating", "count"]
    fig = px.bar(rating_counts, x="rating", y="count")
    st.plotly_chart(fig, use_container_width=True)

with c6:
    low_ratings = appt_feedback[appt_feedback["rating"] <= 2].sort_values("feedback_date", ascending=False)
    st.markdown("**Recent low-rating comments (flagged for follow-up)**")
    if len(low_ratings):
        for _, row in low_ratings.head(5).iterrows():
            st.warning(f"⭐ {row['rating']}/5 — {row['comment']}")
    else:
        st.success("No low ratings in the selected range.")

st.divider()
st.caption("Built with Python, SQLite, pandas, and Streamlit. Data is synthetic, modeled on "
           "real-world clinic scheduling, billing, and feedback workflows.")