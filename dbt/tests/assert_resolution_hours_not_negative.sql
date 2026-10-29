select ticket_id
from {{ ref('fct_tickets') }}
where resolution_hours < 0
