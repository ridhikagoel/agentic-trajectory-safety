"""S3: arXiv literature search for trajectory-level agent safety and its
fraud/anomaly-detection precedent.

Window: submitted 2023-01-01 .. 2026-09-30. Raw Atom responses are saved
under review/raw/arxiv/; deduplicated records go to review/raw/s3_arxiv_records.csv.
"""
import csv, os, re, subprocess, time, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw", "arxiv")
os.makedirs(RAW, exist_ok=True)
NS = {"a": "http://www.w3.org/2005/Atom"}
DATE = "submittedDate:[202301010000 TO 202609302359]"

# Block A: agent-side trajectory safety. Block B: sequence/behavioral fraud precedent.
QUERIES = {
    "A1": 'abs:"agent" AND abs:"trajectory" AND (abs:"safety" OR abs:"security" OR abs:"guardrail")',
    "A2": 'abs:"agent" AND abs:"runtime" AND (abs:"monitor" OR abs:"monitoring" OR abs:"verification") AND (abs:"LLM" OR abs:"language model")',
    "A3": 'abs:"agent" AND (abs:"multi-step" OR abs:"multi-turn" OR abs:"sequence") AND abs:"unsafe" AND (abs:"LLM" OR abs:"language model")',
    "A4": 'abs:"agent" AND (abs:"anomaly detection" OR abs:"anomalous") AND (abs:"LLM" OR abs:"language model")',
    "B1": 'abs:"fraud detection" AND (abs:"sequential" OR abs:"sequence" OR abs:"behavioral" OR abs:"behavioural")',
    "B2": 'abs:"fraud" AND abs:"graph neural network"',
}


def fetch(q, start):
    params = {"search_query": f"({q}) AND {DATE}", "start": start,
              "max_results": 200, "sortBy": "submittedDate", "sortOrder": "ascending"}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            return subprocess.run(["curl", "-sf", "--max-time", "120", url],
                                  check=True, capture_output=True).stdout
        except Exception as ex:
            print("  retry", attempt, ex)
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(url)


records, log = {}, []
for key, q in QUERIES.items():
    start, total, got = 0, None, 0
    while total is None or start < total:
        body = fetch(q, start)
        with open(os.path.join(RAW, f"{key}_{start}.xml"), "wb") as f:
            f.write(body)
        root = ET.fromstring(body)
        total = int(root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults").text)
        entries = root.findall("a:entry", NS)
        if not entries:
            break
        for e in entries:
            aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.rsplit("/abs/", 1)[-1])
            r = records.setdefault(aid, {
                "id": aid,
                "published": e.find("a:published", NS).text[:10],
                "title": " ".join(e.find("a:title", NS).text.split()),
                "abstract": " ".join(e.find("a:summary", NS).text.split()),
                "queries": set()})
            r["queries"].add(key)
        got += len(entries)
        start += 200
        time.sleep(3.5)
    log.append((key, q, total, got))
    print(key, total, got, flush=True)

with open(os.path.join(ROOT, "raw", "s3_arxiv_records.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "published", "matched_queries", "title", "abstract"])
    for r in sorted(records.values(), key=lambda r: r["published"]):
        w.writerow([r["id"], r["published"], "; ".join(sorted(r["queries"])), r["title"], r["abstract"]])
with open(os.path.join(ROOT, "raw", "s3_arxiv_query_log.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["key", "query", "total_reported", "retrieved", "run_utc"])
    run = datetime.utcnow().isoformat(timespec="seconds")
    for row in log:
        w.writerow([*row, run])
print("unique papers:", len(records))
