"""
Step 1: generate fake customer support tickets.

Run:
    pip install faker pandas
    python generate_tickets.py

Output: raw_tickets.csv  (1,000 fake tickets)
All data is synthetic. Nobody real is in it.
"""

import random
from datetime import timedelta

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)       # same seed = same data every run
random.seed(42)

N_TICKETS = 1000
N_CUSTOMERS = 200

CATEGORIES = ["Billing", "Delivery", "Returns", "Account Access", "Product Issue"]
PRIORITIES = ["P1", "P2", "P3"]

# Message templates. {name}, {email}, {phone}, {iban} will be replaced
# with fake personal data, so Presidio has something to find later.
TEMPLATES = {
    "Billing": [
        "Hi, I'm {name}. I was charged twice this month. My email is {email}. Please refund to {iban}.",
        "Hello, my invoice is wrong. You can reach me at {phone} or {email}.",
    ],
    "Delivery": [
        "My order has not arrived. This is {name}, call me on {phone}.",
        "Package is late again. Contact me at {email}. Regards, {name}",
    ],
    "Returns": [
        "I want to return my item. Name: {name}, email: {email}.",
        "Return label not working. Please call {phone}. Thanks, {name}",
    ],
    "Account Access": [
        "I can't log in. My account email is {email}, phone {phone}.",
        "Locked out of my account. I'm {name}. Please email me at {email}.",
    ],
    "Product Issue": [
        "The product stopped working after a week. {name} here, reach me at {phone}.",
        "Item arrived damaged. Email {email} for photos. {name}",
    ],
}

# Customers: only a pseudonymous ID plus non-identifying details.
customers = [f"CUST-{i:04d}" for i in range(1, N_CUSTOMERS + 1)]

rows = []
for i in range(1, N_TICKETS + 1):
    category = random.choice(CATEGORIES)
    priority = random.choices(PRIORITIES, weights=[0.15, 0.35, 0.50])[0]
    created = fake.date_time_between(start_date="-180d", end_date="now")

    # ~85% of tickets get resolved; the rest are still open
    if random.random() < 0.85:
        hours = max(1, int(random.gauss(30, 20)))
        resolved = created + timedelta(hours=hours)
    else:
        resolved = None

    message = random.choice(TEMPLATES[category]).format(
        name=fake.name(),
        email=fake.email(),
        phone=fake.phone_number(),
        iban=fake.iban(),
    )

    rows.append(
        {
            "ticket_id": f"TCK-{i:05d}",
            "customer_id": random.choice(customers),
            "category": category,
            "priority": priority,
            "created_at": created,
            "resolved_at": resolved,
            "message": message,
        }
    )

df = pd.DataFrame(rows)
df.to_csv("raw_tickets.csv", index=False)
print(f"Wrote {len(df)} tickets to raw_tickets.csv")
print(df.head(3).to_string())
