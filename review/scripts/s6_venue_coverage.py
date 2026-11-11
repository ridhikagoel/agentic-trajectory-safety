"""S6: venue coverage check of IEEE, ACM and USENIX publications.

DBLP's API blocks scripted access, so IEEE and ACM are searched through Crossref,
where both publishers register every DOI (prefixes 10.1109 and 10.1145), and
USENIX through OpenAlex (all 22 OpenAlex sources named USENIX; OpenAlex's USENIX coverage is incomplete). Queries mirror the agent-monitoring blocks A1-A4; window
2023-01-01 to 2026-09-30. A stage-1 title rule (as in S3) keeps records naming an
LLM/agent and a monitoring or safety term; each kept record is checked against the
S3/S5 corpus by normalized title. Raw responses: review/raw/venue/.
Output: review/raw/s6_venue_hits.csv (screened by hand afterwards).
"""
import csv, json, os, re, subprocess, time, urllib.parse
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw", "venue")
os.makedirs(RAW, exist_ok=True)

QUERIES = {
    "V1": "agent trajectory safety",
    "V2": "agent trajectory guardrail",
    "V3": "LLM agent runtime monitoring",
    "V4": "LLM agent runtime verification",
    "V5": "LLM agent guardrail",
    "V6": "multi-turn agent unsafe actions",
    "V7": "LLM agent anomaly detection",
    "V8": "tool-using agent safety monitor",
}
AGENT = re.compile(r"\b(agent\w*|LLM\w*|language models?)\b", re.I)
CTL = re.compile(r"\b(monitor\w*|guardrails?|safe\w*|secur\w*|verif\w*|anomal\w*|trajector\w*|audit\w*|shield\w*)\b", re.I)
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

def get(url, path):
    for attempt in range(4):
        body = subprocess.run(["curl", "-sf", "--max-time", "90", "-A", "SoK-review-script (mailto:anonymous@example.org)", url],
                              capture_output=True).stdout
        if body[:1] == b"{":
            open(path, "wb").write(body)
            return json.loads(body)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(url)

corpus = {}
for f, key in (("s3_arxiv_records.csv", "id"), ("s5_stage2.csv", "key")):
    for r in csv.DictReader(open(os.path.join(ROOT, "raw", f), newline="")):
        corpus[norm(r["title"])] = r[key]

hits, log = {}, []
def add(title, year, venue, pub, doi, key):
    title = " ".join(title.split())
    if not (AGENT.search(title) and CTL.search(title)):
        return False
    r = hits.setdefault(norm(title), {"title": title, "year": year, "venue": venue, "publisher": pub,
                                      "doi": doi, "queries": set()})
    r["queries"].add(key)
    return True

for key, q in QUERIES.items():
    for prefix, pub in (("10.1109", "IEEE"), ("10.1145", "ACM")):
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode({
            "query.bibliographic": q, "rows": 200,
            "filter": f"prefix:{prefix},from-pub-date:2023-01-01,until-pub-date:2026-09-30",
            "select": "DOI,title,container-title,issued,type"})
        items = get(url, os.path.join(RAW, f"{key}_{pub}.json"))["message"]["items"]
        kept = sum(add((it.get("title") or [""])[0], (it.get("issued", {}).get("date-parts") or [[0]])[0][0],
                       (it.get("container-title") or [""])[0], pub, it["DOI"], key)
                   for it in items if it.get("type") in ("proceedings-article", "journal-article"))
        log.append((key, pub, q, len(items), kept)); time.sleep(1)
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "search": q, "per-page": 200,
        "filter": "from_publication_date:2023-01-01,to_publication_date:2026-09-30,primary_location.source.id:S4306421123|S4306421113|S4306518845|S4306421122|S4306533996|S4306418106|S4306533995|S4306417563|S4306421125|S4306421118|S4306421114|S4306421124|S4306421116|S4306421119|S4306421120|S4306421128|S4306421117|S4306421127|S4306421121|S4306421129|S4306482094|S4306421115"})
    items = get(url, os.path.join(RAW, f"{key}_USENIX.json"))["results"]
    kept = sum(add(it.get("title") or "", it.get("publication_year"),
                   ((it.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
                   "USENIX", it.get("doi") or it["id"], key) for it in items)
    log.append((key, "USENIX", q, len(items), kept)); time.sleep(1)

with open(os.path.join(ROOT, "raw", "s6_venue_hits.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["title", "year", "venue", "publisher", "doi", "queries", "in_corpus_as", "in_scope", "reason"])
    for k, r in sorted(hits.items(), key=lambda kv: (kv[1]["year"] or 0)):
        w.writerow([r["title"], r["year"], r["venue"], r["publisher"], r["doi"],
                    "; ".join(sorted(r["queries"])), corpus.get(k, ""), "", ""])
with open(os.path.join(ROOT, "raw", "s6_venue_query_log.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["key", "source", "query", "returned", "kept_after_title_rule", "run_utc"])
    run = datetime.utcnow().isoformat(timespec="seconds")
    for row in log:
        w.writerow([*row, run])
print("title-rule records:", len(hits), "| already in corpus:", sum(1 for k in hits if k in corpus))
