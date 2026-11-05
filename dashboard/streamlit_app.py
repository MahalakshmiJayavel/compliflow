import os
import streamlit as st

conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

st.title("CompliFlow AE: support ticket analytics")
st.caption("Synthetic data. Personal data is redacted before it reaches the warehouse.")

# 1. SLA performance
sla = session.sql("""
    select category,
           round(100.0 * sum(sla_breaches) / nullif(sum(resolved_tickets), 0), 1) as breach_pct
    from compliflow.gold.mart_sla_performance
    group by category
    order by category
""").to_pandas()
st.subheader("SLA breach rate by category (%)")
st.bar_chart(sla, x="CATEGORY", y="BREACH_PCT")

# 2. Backlog trend
backlog = session.sql("""
    select date_day, category, open_tickets
    from compliflow.gold.mart_backlog_trends
    order by date_day
""").to_pandas()
st.subheader("Open tickets over time")
st.line_chart(backlog.pivot(index="DATE_DAY", columns="CATEGORY", values="OPEN_TICKETS"))

# 3. PII detections
pii = session.sql("""
    select category, entity_type, detections
    from compliflow.gold.mart_pii_detection_by_category
""").to_pandas()
st.subheader("PII detections by category and type")
st.bar_chart(pii, x="CATEGORY", y="DETECTIONS", color="ENTITY_TYPE")

st.info("Limitations: the data is synthetic, SLA targets are assumed, and redaction is best-effort.")