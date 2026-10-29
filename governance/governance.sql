-- Governance demos for CompliFlow AE. Run each statement one at a time in Snowflake.
-- Re-run `dbt run` after the erasure to rebuild Silver and Gold.

-- ===== 1. Right-to-erasure demo =====
create schema if not exists compliflow.governance;

create table if not exists compliflow.governance.erasure_log (
    customer_hash varchar,
    tickets_erased number,
    events_erased number,
    audit_rows_erased number,
    erased_at timestamp_ntz default current_timestamp()
);

-- Log the request first. A hash is stored, not the customer ID itself.
insert into compliflow.governance.erasure_log (customer_hash, tickets_erased, events_erased, audit_rows_erased)
select
    sha2('CUST-0152', 256),
    (select count(*) from compliflow.bronze.raw_tickets where customer_id = 'CUST-0152'),
    (select count(*) from compliflow.bronze.raw_ticket_events where ticket_id in (select ticket_id from compliflow.bronze.raw_tickets where customer_id = 'CUST-0152')),
    (select count(*) from compliflow.bronze.raw_pii_audit_log where ticket_id in (select ticket_id from compliflow.bronze.raw_tickets where customer_id = 'CUST-0152'));

-- Delete from Bronze (events and audit rows first, they look up tickets)
delete from compliflow.bronze.raw_ticket_events where ticket_id in (select ticket_id from compliflow.bronze.raw_tickets where customer_id = 'CUST-0152');
delete from compliflow.bronze.raw_pii_audit_log where ticket_id in (select ticket_id from compliflow.bronze.raw_tickets where customer_id = 'CUST-0152');
delete from compliflow.bronze.raw_tickets where customer_id = 'CUST-0152';

-- Then rebuild Silver and Gold with dbt run, and confirm the customer is gone from every layer.

-- ===== 2. Role-based masking with a secure view =====
-- (Masking policies need Enterprise edition; this trial is Standard edition.)
create or replace secure view compliflow.gold.v_tickets_masked as
select
    ticket_id, customer_id, category, priority, created_at, resolved_at,
    case when current_role() = 'ACCOUNTADMIN' then message_redacted else '*** masked ***' end as message_redacted
from compliflow.silver.stg_tickets;

create role if not exists analyst_demo;
grant usage on warehouse compliflow_wh to role analyst_demo;
grant usage on database compliflow to role analyst_demo;
grant usage on schema compliflow.gold to role analyst_demo;
grant select on view compliflow.gold.v_tickets_masked to role analyst_demo;
-- grant role analyst_demo to user <your_username>;
