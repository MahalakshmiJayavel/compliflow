{{ config(materialized='table', schema='gold') }}

select distinct category
from {{ ref('stg_tickets') }}
