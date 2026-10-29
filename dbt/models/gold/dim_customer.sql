{{ config(materialized='table', schema='gold') }}

-- Pseudonymous ID and counts only. No names or emails.
select
    customer_id,
    count(*) as total_tickets,
    min(created_at) as first_ticket_at
from {{ ref('stg_tickets') }}
group by customer_id
