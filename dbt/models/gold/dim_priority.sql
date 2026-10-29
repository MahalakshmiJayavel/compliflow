{{ config(materialized='table', schema='gold') }}

-- SLA targets are assumptions for this demo, not real company rules
select priority, sla_target_hours
from (values ('P1', 24), ('P2', 48), ('P3', 72)) as t(priority, sla_target_hours)
