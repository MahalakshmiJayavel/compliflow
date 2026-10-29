{{ config(materialized='table') }}

select
    audit_id,
    ticket_id,
    entity_type,
    try_to_double(confidence_score) as confidence_score,
    try_to_number(start_pos) as start_pos,
    try_to_number(end_pos) as end_pos
from {{ source('bronze', 'raw_pii_audit_log') }}
