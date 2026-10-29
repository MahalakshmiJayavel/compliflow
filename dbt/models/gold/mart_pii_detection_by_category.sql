{{ config(materialized='table', schema='gold') }}

-- Grain: one row per category and PII entity type
select
    t.category,
    a.entity_type,
    count(*) as detections,
    count(distinct a.ticket_id) as tickets_affected
from {{ ref('stg_pii_audit_log') }} a
join {{ ref('fct_tickets') }} t on a.ticket_id = t.ticket_id
group by 1, 2
