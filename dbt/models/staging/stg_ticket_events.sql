{{ config(materialized='table') }}

select
    event_id,
    ticket_id,
    event_type,
    try_to_timestamp(event_at) as event_at
from {{ source('bronze', 'raw_ticket_events') }}
