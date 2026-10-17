"""S3 stage 1: automated abstract screen (PROTOCOL.md, Literature screening).

Keeps a paper only if its abstract matches at least one sequence term AND at
least one control term. Output: review/raw/s3_stage1.csv (all records, with
a stage1 decision column).
"""
import csv, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEQ = re.compile(r"\b(trajector(y|ies)|multi-step|multi-turn|sequen(ce|ces|tial)|long-horizon|"
                 r"sessions?|temporal|histor(y|ies|ical)|stateful|behaviou?ral)\b", re.I)
CTL = re.compile(r"\b(monitor\w*|detect\w*|guardrails?|verif(y|ication|ier)\w*|anomal\w*|"
                 r"audit\w*|shield\w*|oversight|fraud\w*)\b", re.I)

rows = list(csv.DictReader(open(os.path.join(ROOT, "raw", "s3_arxiv_records.csv"), newline="")))
kept = 0
with open(os.path.join(ROOT, "raw", "s3_stage1.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "published", "matched_queries", "title", "stage1"])
    for r in rows:
        ok = bool(SEQ.search(r["abstract"])) and bool(CTL.search(r["abstract"]))
        kept += ok
        w.writerow([r["id"], r["published"], r["matched_queries"], r["title"], "keep" if ok else "drop"])
print(f"records: {len(rows)}; stage-1 kept: {kept}; dropped: {len(rows) - kept}")
