"""Computes every count the paper reports from the screening and coding files.
Writes review/RESULTS.md. Re-run after Coder 2 reconciliation (point it at
coding/final.csv with --final) so the paper's numbers come from one place.
"""
import csv, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
codes = R("coding", "final.csv") if "--final" in sys.argv else R("coding", "coder1.csv")
rows = list(csv.DictReader(open(codes, newline="")))
inc = [r for r in rows if r["record_id"].startswith("R")]
cve = [r for r in rows if r["record_id"].startswith("CVE")]
out = [f"# Results ({os.path.basename(codes)})\n"]


def tab(title, grp, field):
    c = Counter(r[field] for r in grp)
    out.append(f"- {title} `{field}`: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())) + f" (n={len(grp)})")


out.append("## Screening flow")
s1 = Counter((r["stage"], r["decision"]) for r in csv.DictReader(open(R("raw", "s1_screen.csv"), newline="")))
out.append(f"- S1 NVD: retrieved {sum(s1.values())}; included {sum(v for (s, d), v in s1.items() if d == 'include')}; "
           f"stage breakdown {dict(s1)}")
s2a_t = Counter(r["reason"] or r["decision"] for r in csv.DictReader(open(R("raw", "s2a_screen_title.csv"), newline="")))
s2a_f = Counter(r["reason"] or r["decision"] for r in csv.DictReader(open(R("raw", "s2a_screen_fulltext.csv"), newline="")))
out.append(f"- S2a AIID: keyword hits {sum(s2a_t.values())}; title screen {dict(s2a_t)}; full text {dict(s2a_f)}")
s2b = Counter(r["reason"] or r["decision"] for r in csv.DictReader(open(R("raw", "s2b_screen.csv"), newline="")))
out.append(f"- S2b primary disclosures: candidates {sum(s2b.values())}; {dict(s2b)}")
for blk in "AB":
    st = Counter(r["stage2"] for r in csv.DictReader(open(R("raw", f"s3_stage2_{blk}.csv"), newline="")))
    out.append(f"- S3 block {blk} stage 2: {dict(st)}")

out.append("\n## Incidents")
for f in ["setting", "per_action_flaggable", "min_state", "precursor_signal", "monitor_present", "detected_by", "harm_external", "root_cause"]:
    tab("incidents", inc, f)
flag = [r for r in inc if r["per_action_flaggable"] == "Y"]
tab("incidents with a flaggable step", flag, "monitor_present")
tab("incidents with a flaggable step", flag, "precursor_signal")
mon = [r for r in inc if r["monitor_present"] == "Y"]
tab("incidents with a monitor running", mon, "detected_by")

out.append("\n## CVEs")
for f in ["per_action_flaggable", "min_state", "monitor_present"]:
    tab("cves", cve, f)

out.append("\n## Literature")
sfx = "final" if "--final" in sys.argv else "coder1"
la = list(csv.DictReader(open(R("coding", f"lit_A_{sfx}.csv"), newline="")))
lb = list(csv.DictReader(open(R("coding", f"lit_B_{sfx}.csv"), newline="")))
for f in ["mechanism", "state_scope", "timing", "evaluated_on", "reports_fp_or_cost", "reports_timeliness"]:
    tab("agent papers", la, f)
for f in ["state_scope", "production_data"]:
    tab("fraud papers", lb, f)
open(R("RESULTS.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
