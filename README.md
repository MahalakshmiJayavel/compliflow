\# CompliFlow AE



A privacy-aware data pipeline built on \*\*synthetic\*\* customer support tickets. Personal data is redacted

before it reaches the warehouse, then modelled with dbt on Snowflake (Bronze -> Silver -> Gold).



> Status: pipeline, tests, governance demos and a Streamlit dashboard are built.



\## Architecture



```

Synthetic tickets (Python, Faker)

&#x20;       |

&#x20;       v

Presidio redaction + PII audit log (no PII values stored)

&#x20;       |

&#x20;       v

Snowflake BRONZE  - raw tables, all columns as text, exactly as loaded

&#x20;       |

&#x20;       v

dbt SILVER        - typed, cleaned staging models + tests

&#x20;       |

&#x20;       v

dbt GOLD          - fct\_tickets, dimensions, and three analytics marts

```



\## What is in this repo



| Path | What it does |

|---|---|

| `generate\_tickets.py` | Creates 1,000 synthetic tickets with fake PII in the message text |

| `generate\_events.py` | Creates the status history (opened, assigned, resolved, reopened) |

| `redact\_pii.py` | Redacts PII with Presidio and writes an audit log of detections |

| `dbt/` | Silver and Gold models, schema tests, custom tests |

| `governance/governance.sql` | Right-to-erasure demo and role-based masking demo |

| `dashboard/` | Streamlit dashboard code and a screenshot |



\## Gold models



\- `fct\_tickets` - one row per ticket, with resolution hours, SLA breach flag, reopen count, PII detections

\- `dim\_category`, `dim\_priority`, `dim\_customer` - dimensions (customer holds a pseudonymous ID only)

\- `mart\_sla\_performance` - per category, priority and month

\- `mart\_backlog\_trends` - open tickets per day and category

\- `mart\_pii\_detection\_by\_category` - PII detections per category and entity type



\## Data quality



28 dbt tests: 27 pass and 1 deliberate warning (a check for phone numbers the redaction missed).



\## Dashboard



Streamlit app in Snowflake (code in `dashboard/streamlit\_app.py`) reading the Gold marts.

The data is synthetic, so the patterns reflect how it was generated, not real behaviour.



!\[Dashboard](dashboard/dashboard.png)



\## Privacy and governance



\- PII is redacted in Python before anything is loaded to Snowflake.

\- The audit log records entity type, confidence and position, never the value itself.

\- \*\*Right to erasure:\*\* one customer is deleted from Bronze, Silver and Gold are rebuilt, and the request is logged with a hashed ID.

\- \*\*Masking:\*\* a secure view shows message text only to ACCOUNTADMIN; other roles see `\*\*\* masked \*\*\*`.



\## Limitations (please read)



\- The data is synthetic and cleaner and more repetitive than real support tickets. Insights from it (for example the backlog trend) reflect how it was generated, not real behaviour.

\- Redaction is best-effort. Presidio's default phone recognizer missed numbers in several formats; a regex check found about 103 of 1,000 tickets with a phone-like number still visible. Names and other types were not separately validated.

\- SLA targets (24 / 48 / 72 hours) are assumptions for the demo.

\- The backlog model treats a ticket as open until its first resolution and ignores reopens.

\- Snowflake keeps deleted data for a period (Time Travel and Fail-safe), and the original CSV on the author's machine is not covered by the erasure demo. This is a demo, not legal compliance.

\- The trial account is Standard edition, so masking is done with a secure view, not masking policies or tags.

\- dbt rebuilds tables, which would remove column-level policies; a production setup would reapply them automatically.



\## Stack



Python (Faker, pandas, Presidio), Snowflake (trial), dbt 1.9 via dbt Projects on Snowflake, Streamlit in Snowflake.



\## What I would do next



\- Custom Presidio recognizers for the missed phone formats, then re-measure.

\- Build the backlog model from the status events table so reopens are handled.

\- Scheduled dbt runs and CI.

