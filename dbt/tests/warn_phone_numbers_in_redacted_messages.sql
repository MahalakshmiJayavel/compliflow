{{ config(severity='warn') }}

-- Deliberate warning: flags phone-like numbers that Presidio missed
select ticket_id
from {{ ref('stg_tickets') }}
where regexp_count(message_redacted, '[0-9]{3}[-. )(]{0,2}[0-9]{3}[-. ]?[0-9]{4}') > 0
