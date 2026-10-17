"""S1: NVD CVE search for agent-enabled product vulnerabilities.

Window: 2025-01-01 .. 2026-09-30 (CVE publication date). NVD limits a
pubStartDate/pubEndDate range to 120 days, so the window is chunked.
Every raw API response is saved under review/raw/nvd/ and a deduplicated
record list is written to review/raw/s1_nvd_records.csv.
"""
import csv, json, os, subprocess, sys, time, urllib.parse
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw", "nvd")
os.makedirs(RAW, exist_ok=True)

QUERIES = [
    "prompt injection",
    "AI agent",
    "agentic",
    "LLM agent",
    "Model Context Protocol",
    "MCP server",
    "coding agent",
    "AI assistant",
    "Copilot",
    "large language model",
]
START, END = datetime(2025, 1, 1), datetime(2026, 9, 30, 23, 59, 59)
API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def chunks():
    s = START
    while s <= END:
        e = min(s + timedelta(days=119, hours=23, minutes=59, seconds=59), END)
        yield s, e
        s = e + timedelta(seconds=1)


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            out = subprocess.run(["curl", "-sf", "--max-time", "90", url],
                                 check=True, capture_output=True).stdout
            return json.loads(out)
        except Exception as ex:
            print("  retry", attempt, ex, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(url)


records, log = {}, []
for q in QUERIES:
    total_q = 0
    for s, e in chunks():
        idx = 0
        while True:
            params = {
                "keywordSearch": q,
                "pubStartDate": s.strftime("%Y-%m-%dT%H:%M:%S.000"),
                "pubEndDate": e.strftime("%Y-%m-%dT%H:%M:%S.000"),
                "resultsPerPage": 2000,
                "startIndex": idx,
            }
            data = fetch(params)
            tag = f"{q.replace(' ', '_')}_{s:%Y%m%d}_{idx}"
            with open(os.path.join(RAW, tag + ".json"), "w") as f:
                json.dump(data, f)
            for v in data.get("vulnerabilities", []):
                c = v["cve"]
                desc = next((d["value"] for d in c["descriptions"] if d["lang"] == "en"), "")
                rec = records.setdefault(c["id"], {
                    "id": c["id"], "published": c["published"][:10],
                    "description": desc.replace("\n", " "), "queries": set()})
                rec["queries"].add(q)
            n = data.get("totalResults", 0)
            total_q += len(data.get("vulnerabilities", []))
            idx += 2000
            time.sleep(6.5)  # unauthenticated limit: 5 requests / 30 s
            if idx >= n:
                break
    log.append((q, total_q))
    print(f"{q!r}: {total_q}", flush=True)

with open(os.path.join(ROOT, "raw", "s1_nvd_records.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "published", "matched_queries", "description"])
    for r in sorted(records.values(), key=lambda r: r["published"]):
        w.writerow([r["id"], r["published"], "; ".join(sorted(r["queries"])), r["description"]])

with open(os.path.join(ROOT, "raw", "s1_nvd_query_log.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["query", "hits", "run_utc"])
    run = datetime.utcnow().isoformat(timespec="seconds")
    for q, n in log:
        w.writerow([q, n, run])
print("unique CVEs:", len(records))
