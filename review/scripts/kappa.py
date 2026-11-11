"""Cohen's kappa per field between coding/coder1.csv and a completed Coder 2 sheet.

Usage: python3 -I scripts/kappa.py coding/coder2.csv
Rows with an empty Coder 2 value for a field are skipped for that field.
Writes coding/agreement.csv and coding/disagreements.csv.
"""
import csv, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["setting", "actor", "harm_external", "per_action_flaggable", "min_state",
          "precursor_signal", "monitor_present", "root_cause", "detected_by"]


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan"), 0, float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    k = float("nan") if pe == 1 else (po - pe) / (1 - pe)
    return k, n, po


c1 = {r["record_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "coding", "coder1.csv"), newline=""))}
c2 = {r["record_id"]: r for r in csv.DictReader(open(sys.argv[1], newline=""))}
ids = sorted(set(c1) & set(c2))

with open(os.path.join(ROOT, "coding", "agreement.csv"), "w", newline="") as fa, \
     open(os.path.join(ROOT, "coding", "disagreements.csv"), "w", newline="") as fd:
    wa, wd = csv.writer(fa), csv.writer(fd)
    wa.writerow(["stratum", "field", "n", "percent_agreement", "cohen_kappa"])
    wd.writerow(["record_id", "field", "coder1", "coder2"])
    for stratum, pick in [("incidents", lambda i: i.startswith("R")),
                          ("cves", lambda i: i.startswith("CVE")), ("all", lambda i: True)]:
        for f in FIELDS:
            pairs = [(c1[i][f], c2[i][f].strip()) for i in ids if pick(i) and c2[i][f].strip()]
            k, n, po = kappa(pairs)
            wa.writerow([stratum, f, n, f"{po:.3f}", f"{k:.3f}"])
            print(f"{stratum:9s} {f:22s} n={n:3d} agree={po:.3f} kappa={k:.3f}")
            if stratum == "all":
                for i in ids:
                    if c2[i][f].strip() and c1[i][f] != c2[i][f].strip():
                        wd.writerow([i, f, c1[i][f], c2[i][f].strip()])
