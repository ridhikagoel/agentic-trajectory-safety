"""S2a: AI Incident Database keyword filter.

Input: AIID public research snapshot backup-20261012101643 (CC BY-SA 4.0),
incidents.csv. Window: incident date 2025-01-01 .. 2026-09-30.
A record is retained if its title or description matches any pattern below
(case-insensitive). Output: review/raw/s2_aiid_records.csv.
"""
import csv, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "raw", "aiid_snapshot", "mongodump_full_snapshot", "incidents.csv")
PATTERNS = [
    r"\bagent(s|ic)?\b", r"\bautonomous(ly)?\b", r"prompt[- ]injection",
    r"\bsandbox", r"\bclaude code\b", r"\bcodex\b", r"\bcopilot\b",
    r"model context protocol", r"\bMCP\b", r"\btool[- ]use\b", r"\bcomputer[- ]use\b",
]
rx = re.compile("|".join(PATTERNS), re.I)
csv.field_size_limit(10**9)

rows = list(csv.DictReader(open(SRC, newline="")))
in_window = [r for r in rows if "2025-01-01" <= r["date"][:10] <= "2026-09-30"]
hits = [r for r in in_window if rx.search(r["title"] + " " + r["description"])]

with open(os.path.join(ROOT, "raw", "s2_aiid_records.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["incident_id", "date", "title", "description", "matched"])
    for r in sorted(hits, key=lambda r: r["date"]):
        m = sorted({x.group(0).lower() for x in rx.finditer(r["title"] + " " + r["description"])})
        w.writerow([r["incident_id"], r["date"][:10], r["title"], " ".join(r["description"].split()), "; ".join(m)])
print(f"snapshot incidents: {len(rows)}; in window: {len(in_window)}; keyword hits: {len(hits)}")
