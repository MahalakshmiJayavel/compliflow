"""
Step 3: remove personal data from ticket messages using Presidio,
and record what was found in an audit log.

Needs raw_tickets.csv in the same folder.

Run:
    python redact_pii.py

Outputs:
    raw_tickets_redacted.csv  - tickets with PII replaced by labels like <EMAIL_ADDRESS>
    raw_pii_audit_log.csv     - what was found (type, confidence, position).
                                It NEVER contains the personal data itself.
"""

import re

import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

ENTITIES = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "IBAN_CODE"]

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

tickets = pd.read_csv("raw_tickets.csv")

redacted_messages = []
audit_rows = []

for _, t in tickets.iterrows():
    text = t["message"]

    # 1) find PII in the message
    findings = analyzer.analyze(text=text, entities=ENTITIES, language="en")

    # 2) replace each finding with a label, e.g. <PERSON>
    result = anonymizer.anonymize(text=text, analyzer_results=findings)
    redacted_messages.append(result.text)

    # 3) log what was found: type, score, position. NOT the value.
    for f in findings:
        audit_rows.append(
            {
                "ticket_id": t["ticket_id"],
                "entity_type": f.entity_type,
                "confidence_score": round(f.score, 2),
                "start_pos": f.start,
                "end_pos": f.end,
            }
        )

# Build the redacted tickets file. The original message column is dropped.
clean = tickets.drop(columns=["message"]).copy()
clean["message_redacted"] = redacted_messages
clean.to_csv("raw_tickets_redacted.csv", index=False)

audit = pd.DataFrame(audit_rows)
audit.insert(0, "audit_id", [f"AUD-{i:06d}" for i in range(1, len(audit) + 1)])
audit.to_csv("raw_pii_audit_log.csv", index=False)

print(f"Redacted {len(clean)} tickets -> raw_tickets_redacted.csv")
print(f"Logged {len(audit)} detections -> raw_pii_audit_log.csv")
print()
print("Detections by type:")
print(audit["entity_type"].value_counts().to_string())

# Simple safety check: look for any email-looking text that survived
email_pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
leaks = sum(bool(email_pattern.search(m)) for m in redacted_messages)
print()
print(f"Check: tickets with an email still visible after redaction = {leaks}")
