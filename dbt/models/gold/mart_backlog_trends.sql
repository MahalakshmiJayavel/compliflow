{{ config(materialized='table', schema='gold') }}

-- Grain: one row per day and category.
-- Simplification: a ticket counts as open until its first resolution (reopens are ignored).
with date_spine as (
    select dateadd('day', seq4(), (select min(created_at)::date from {{ ref('fct_tickets') }})) as date_day
    from table(generator(rowcount => 400))
)

select
    d.date_day,
    c.category,
    count(t.ticket_id) as open_tickets
from date_spine d
cross join {{ ref('dim_category') }} c
left join {{ ref('fct_tickets') }} t
    on t.category = c.category
   and t.created_at::date <= d.date_day
   and (t.resolved_at is null or t.resolved_at::date > d.date_day)
where d.date_day <= current_date()
group by 1, 2
