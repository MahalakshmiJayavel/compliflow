"""
Step 2: generate status events for each ticket.

Needs raw_tickets.csv (made by generate_tickets.py) in the same folder.

Run:
    python generate_events.py

Output: raw_ticket_events.csv
One row per status change: opened, assigned, resolved, reopened.
"""

import random
from datetime import timedelta

import pandas as pd

random.seed(42)

tickets = pd.read_csv(
    "raw_tickets.csv", parse_dates=["created_at", "resolved_at"]
)

events = []


def add_event(ticket_id, event_type, event_at):
    events.append(
        {"ticket_id": ticket_id, "event_type": event_type, "event_at": event_at}
    )


for _, t in tickets.iterrows():
    tid = t["ticket_id"]
    created = t["created_at"]
    resolved = t["resolved_at"]

    # 1) every ticket is opened
    add_event(tid, "opened", created)

    if pd.notna(resolved):
        total_minutes = int((resolved - created).total_seconds() // 60)

        # 2) assigned a little after opening, always before resolution
        assigned_after = random.randint(5, min(240, total_minutes - 1))
        add_event(tid, "assigned", created + timedelta(minutes=assigned_after))

        # 3) resolved
        add_event(tid, "resolved", resolved)

        # 4) about 10% of resolved tickets get reopened, then resolved again
        if random.random() < 0.10:
            reopened = resolved + timedelta(hours=random.randint(1, 48))
            add_event(tid, "reopened", reopened)
            add_event(
                tid, "resolved", reopened + timedelta(hours=random.randint(2, 48))
            )
    else:
        # still-open tickets: assigned shortly after opening
        add_event(tid, "assigned", created + timedelta(minutes=random.randint(5, 240)))

df = pd.DataFrame(events).sort_values(["ticket_id", "event_at"]).reset_index(drop=True)
df.insert(0, "event_id", [f"EVT-{i:06d}" for i in range(1, len(df) + 1)])
df.to_csv("raw_ticket_events.csv", index=False)

print(f"Wrote {len(df)} events to raw_ticket_events.csv")
print(df["event_type"].value_counts().to_string())
