{{ config(materialized='table', schema='gold') }}

-- Grain: one row per category, priority and month
select
    category,
    priority,
    date_trunc('month', created_at)::date as created_month,
    count(*) as total_tickets,
    count(case when is_resolved then 1 end) as resolved_tickets,
    round(avg(resolution_hours), 2) as avg_resolution_hours,
    count(case when is_sla_breached then 1 end) as sla_breaches,
    round(100.0 * count(case when is_sla_breached then 1 end)
          / nullif(count(case when is_resolved then 1 end), 0), 1) as sla_breach_pct
from {{ ref('fct_tickets') }}
group by 1, 2, 3
