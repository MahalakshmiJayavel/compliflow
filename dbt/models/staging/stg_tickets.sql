{{ config(materialized='table') }}

select
    ticket_id,
    customer_id,
    category,
    priority,
    try_to_timestamp(created_at) as created_at,
    try_to_timestamp(nullif(trim(resolved_at), '')) as resolved_at,
    message_redacted
from {{ source('bronze', 'raw_tickets') }}
