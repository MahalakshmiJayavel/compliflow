{{ config(materialized='table', schema='gold') }}

-- Grain: one row per ticket. Message text is deliberately left out.
with tickets as (
    select * from {{ ref('stg_tickets') }}
),

targets as (
    select * from {{ ref('dim_priority') }}
),

reopens as (
    select ticket_id, count(*) as reopen_count
    from {{ ref('stg_ticket_events') }}
    where event_type = 'reopened'
    group by ticket_id
),

pii as (
    select ticket_id, count(*) as pii_detections
    from {{ ref('stg_pii_audit_log') }}
    group by ticket_id
)

select
    t.ticket_id,
    t.customer_id,
    t.category,
    t.priority,
    t.created_at,
    t.resolved_at,
    t.resolved_at is not null as is_resolved,
    round(datediff('minute', t.created_at, t.resolved_at) / 60.0, 2) as resolution_hours,
    g.sla_target_hours,
    case
        when t.resolved_at is null then null
        when datediff('minute', t.created_at, t.resolved_at) / 60.0 > g.sla_target_hours then true
        else false
    end as is_sla_breached,
    coalesce(r.reopen_count, 0) as reopen_count,
    coalesce(p.pii_detections, 0) as pii_detections
from tickets t
left join targets g on t.priority = g.priority
left join reopens r on t.ticket_id = r.ticket_id
left join pii p on t.ticket_id = p.ticket_id
