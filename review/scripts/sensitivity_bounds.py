"""Bounds each headline count by resolving every pre-adjudication coder disagreement
against it (low) and then in its favour (high). Uses coder1.csv and coder2.csv for all
263 records and final.csv for the reported values. Writes coding/sensitivity_bounds.csv.
Run from the SoK_v1 directory: python3 review/scripts/sensitivity_bounds.py
"""
import csv, os

R = lambda *p: os.path.join(os.path.dirname(__file__), "..", *p)
load = lambda f: {r["record_id"]: r for r in csv.DictReader(open(R("coding", f)))}
F, A, B = load("final.csv"), load("coder1.csv"), load("coder2.csv")
inc = [i for i in F if i.startswith("R")]
cve = [i for i in F if not i.startswith("R")]

def bound(ids, field, pred):
    final = sum(pred(F[i][field]) for i in ids)
    dis = [i for i in ids if A[i][field].strip() != B[i][field].strip()]
    low = final - sum(1 for i in dis if pred(F[i][field]) and not (pred(A[i][field]) and pred(B[i][field])))
    high = final + sum(1 for i in dis if not pred(F[i][field]) and (pred(A[i][field]) or pred(B[i][field])))
    return final, low, high, len(dis)

is_y = lambda v: v.strip() == "Y"
needs_state = lambda v: v.strip() in ("resource-metadata", "trajectory", "window", "cross-trajectory")
rows = [
    ("incidents with a flaggable step", inc, "per_action_flaggable", is_y),
    ("vulnerabilities with a flaggable step", cve, "per_action_flaggable", is_y),
    ("incidents with a precursor", inc, "precursor_signal", is_y),
    ("vulnerabilities with a bypassed guard", cve, "monitor_present", is_y),
    ("incidents with a monitor running", inc, "monitor_present", is_y),
    ("records needing information beyond the action", inc + cve, "min_state", needs_state),
]
with open(R("coding", "sensitivity_bounds.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["headline", "n", "reported", "low_bound", "high_bound", "coder_disagreements"])
    for name, ids, field, pred in rows:
        final, low, high, d = bound(ids, field, pred)
        w.writerow([name, len(ids), final, low, high, d])
        print(f"{name}: {final}/{len(ids)} (range {low}-{high}; {d} disagreements)")
