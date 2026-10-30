"""S5: backward snowballing (one round) from every paper included at S3 stage 2.

For each included paper, fetches its reference list from the Semantic Scholar
Graph API and saves the raw response to raw/snowball/<arxiv id>.json. Then pools
the references, drops ones already retrieved by S3 (matched on arXiv id or
normalized title), keeps those published 2023-01-01 to 2026-09-30, and applies
the same automated stage-1 abstract screen as S3. Output:
raw/s5_snowball_candidates.csv (all new references with a stage1 column) and
raw/s5_run.log.
"""
import csv, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SEQ = re.compile(r"\b(trajector(y|ies)|multi-step|multi-turn|sequen(ce|ces|tial)|long-horizon|"
                 r"sessions?|temporal|histor(y|ies|ical)|stateful|behaviou?ral)\b", re.I)
CTL = re.compile(r"\b(monitor\w*|detect\w*|guardrails?|verif(y|ication|ier)\w*|anomal\w*|"
                 r"audit\w*|shield\w*|oversight|fraud\w*)\b", re.I)
API = ("https://api.semanticscholar.org/graph/v1/paper/arXiv:{}/references"
       "?fields=title,abstract,externalIds,publicationDate,year&limit=1000")
OUT = R("raw", "snowball")
os.makedirs(OUT, exist_ok=True)
norm = lambda t: re.sub(r"[^a-z0-9]", "", (t or "").lower())

seeds = []
for blk in "AB":
    for r in csv.DictReader(open(R("raw", f"s3_stage2_{blk}.csv"), newline="")):
        if r["stage2"] == "include":
            seeds.append((blk, r["id"]))

log = []
for blk, aid in seeds:
    path = os.path.join(OUT, f"{aid}.json")
    if os.path.exists(path):
        continue
    for attempt in range(6):
        # curl rather than urllib: the local Python build lacks a CA bundle.
        res = subprocess.run(["curl", "-s", "-m", "60", "-w", "\\n%{http_code}", API.format(aid)],
                             capture_output=True, text=True)
        body, _, code = res.stdout.rpartition("\n")
        if code == "200":
            data = json.loads(body); json.dump(data, open(path, "w"))
            log.append(f"{aid}\tok\t{len(data.get('data') or [])}"); break
        if code == "404":
            json.dump({"error": 404}, open(path, "w")); log.append(f"{aid}\t404\t0"); break
        time.sleep(5 * (attempt + 1))
    else:
        log.append(f"{aid}\tfailed\t0")
    time.sleep(1.2)

known_ids, known_titles = set(), set()
for r in csv.DictReader(open(R("raw", "s3_arxiv_records.csv"), newline="")):
    known_ids.add(r["id"].split("v")[0]); known_titles.add(norm(r["title"]))

cands, seen = {}, set()
n_refs = 0
for blk, aid in seeds:
    if not os.path.exists(os.path.join(OUT, f"{aid}.json")):
        continue
    data = json.load(open(os.path.join(OUT, f"{aid}.json")))
    for item in data.get("data") or []:
        p = item.get("citedPaper") or {}
        n_refs += 1
        ax = (p.get("externalIds") or {}).get("ArXiv")
        key = ax or norm(p.get("title"))
        if not key or key in seen:
            if key in cands:
                cands[key]["cited_by"].add(aid)
            continue
        seen.add(key)
        if (ax and ax in known_ids) or norm(p.get("title")) in known_titles:
            continue
        date = p.get("publicationDate") or (f"{p['year']}-01-01" if p.get("year") else "")
        if not date or not ("2023-01-01" <= date <= "2026-09-30"):
            continue
        ab = p.get("abstract") or ""
        s1 = "keep" if SEQ.search(ab) and CTL.search(ab) else ("no-abstract" if not ab else "drop")
        cands[key] = {"key": key, "arxiv": ax or "", "date": date, "title": p.get("title") or "",
                      "abstract": ab, "stage1": s1, "cited_by": {aid}, "block": blk}

with open(R("raw", "s5_snowball_candidates.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["key", "arxiv", "date", "block_of_first_seed", "cited_by", "title", "stage1", "abstract"])
    for c in sorted(cands.values(), key=lambda c: c["key"]):
        w.writerow([c["key"], c["arxiv"], c["date"], c["block"], ";".join(sorted(c["cited_by"])),
                    c["title"], c["stage1"], c["abstract"]])
from collections import Counter
st = Counter(c["stage1"] for c in cands.values())
summary = (f"seeds {len(seeds)}; reference entries {n_refs}; new in-window candidates {len(cands)}; "
           f"stage1 {dict(st)}; run {time.strftime('%Y-%m-%dT%H:%M:%S')}")
open(R("raw", "s5_run.log"), "a").write("\n".join(log + [summary]) + "\n")
print(summary)
