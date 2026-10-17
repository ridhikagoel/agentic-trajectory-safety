"""Builds reconciled codes (coding/final.csv, coding/lit_A_final.csv, coding/lit_B_final.csv)
from Coder 1, Coder 2 and the adjudication decisions below, and writes
coding/adjudication_log.csv with the reason for every disputed value.

Adjudicator: Coder 1 (Claude), applying the codebook definitions. Because the
adjudicator is also a coder, every decision is logged with its rationale and
the human spot-check (coding/human_spotcheck_*.csv) is the independent check.
Where a dispute is not listed below, the Coder 1 value stands and is logged
as 'C1 retained (no adjudication note)'.
"""
import csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = lambda *p: os.path.join(ROOT, "coding", *p)

# record_id -> {field: (value, reason)}
DEC = {
 # --- CVEs: per_action_flaggable / min_state ---
 **{k: {"per_action_flaggable": ("N", "C2: the action string looks in scope; the danger depends on what the path resolves to (symlink) - resource ground truth"),
        "min_state": ("resource-metadata", "as above")}
    for k in ["CVE-2025-58373", "CVE-2026-27967", "CVE-2026-53766", "CVE-2026-50549"]},
 **{k: {"per_action_flaggable": ("N", "C2: hostname or URL passes checks; harm depends on what it resolves to or what the remote content is"),
        "min_state": ("resource-metadata", "as above")}
    for k in ["CVE-2026-31945", "CVE-2026-17534", "CVE-2026-54316"]},
 "CVE-2025-58374": {"per_action_flaggable": ("N", "C2: npm install is allowlisted and routine; harm is hidden in the repo's postinstall script"), "min_state": ("resource-metadata", "as above")},
 "CVE-2025-61592": {"per_action_flaggable": ("N", "C2: the shell command is permitted by the (overridden) config; harm depends on project config contents"), "min_state": ("resource-metadata", "as above")},
 "CVE-2026-30856": {"per_action_flaggable": ("N", "C2: calling a tool with a legitimate-looking name; harm depends on which server registered it"), "min_state": ("resource-metadata", "as above")},
 "CVE-2025-64110": {"per_action_flaggable": ("N", "C2: create a new cursorignore, then read protected files; each step plausible alone"), "min_state": ("trajectory", "composition of two steps")},
 "CVE-2025-34072": {"per_action_flaggable": ("N", "C2: posting a Slack message is allowed; harm is that the link embeds sensitive data read earlier (provenance)"), "min_state": ("trajectory", "data provenance")},
 "CVE-2025-55284": {"per_action_flaggable": ("Y", "C2: sending file contents to an external host is visibly unsafe given task scope"), "min_state": ("none", "as above")},
 **{k: {"per_action_flaggable": ("ID", "C2: description does not say which agent action is unsafe"), "min_state": ("ID", "as above")}
    for k in ["CVE-2026-33654", "CVE-2026-44246", "CVE-2026-13341", "CVE-2026-61439", "CVE-2026-57495", "CVE-2026-18875"]},
 **{k: {"per_action_flaggable": ("Y", "C1: resulting action (task definition with a command / exfil URL) is unsafe on its face"), "min_state": ("none", "as above")}
    for k in ["CVE-2026-44688", "CVE-2026-46580"]},
 "CVE-2026-66004": {"per_action_flaggable": ("Y", "C1: the '../../.bashrc' path is visible in the tool call"), "min_state": ("none", "as above")},
 "CVE-2026-73217": {"min_state": ("resource-metadata", "C1: harm depends on the environment fact that the extension later runs this file outside the sandbox")},
 # --- CVEs: monitor_present ---
 **{k: {"monitor_present": ("Y", "C1: a guard existed but was incomplete or bypassed")}
    for k in ["CVE-2025-58372", "CVE-2025-67511", "CVE-2026-25475", "CVE-2026-40160", "CVE-2026-9196", "CVE-2026-75858", "CVE-2026-75913", "CVE-2026-75857", "CVE-2026-55557"]},
 **{k: {"monitor_present": ("Y", "C2: an intended boundary or approval existed and was bypassed")}
    for k in ["CVE-2026-33654", "CVE-2025-66389", "CVE-2026-50181", "CVE-2026-76832"]},
 **{k: {"monitor_present": ("N", "C2: no guard described / auto-approval by design")}
    for k in ["CVE-2025-61592", "CVE-2025-62353", "CVE-2025-62356", "CVE-2026-45311"]},
}
INCIDENT_DEC = {
 **{k: {"per_action_flaggable": ("Y", "C2: the step is out of task scope on its own (public repo upload / edits to an unrelated public wiki / writes of messages to a shared package cache)"), "min_state": ("none", "as above")} for k in ["R25", "R28", "R35"]},
 "R25": {"per_action_flaggable": ("Y", "C2: publishing workspace data to a new public repo is outside the review task"), "min_state": ("none", "as above"), "precursor_signal": ("Y", "C2: hit private-repo image limit first")},
 "R28": {"per_action_flaggable": ("Y", "C2: writing to an unrelated public wiki is out of scope"), "min_state": ("none", "as above"), "precursor_signal": ("Y", "C2: repeated failed edits first"), "monitor_present": ("N", "C2: found by outside researchers; no monitor caught it")},
 "R35": {"per_action_flaggable": ("Y", "C2: PUT of messages to shared repositories exceeds download scope"), "min_state": ("none", "as above"), "precursor_signal": ("Y", "C2: credential search and 403s before")},
 **{k: {"precursor_signal": ("N", "C2: no precursor documented in the sources")} for k in ["R01", "R07", "R09", "R13", "R14", "R31", "R06", "R10"]},
 "R10": {"precursor_signal": ("N", "C2: the sandbox escape was instructed, so it is not a misbehaviour precursor")},
 **{k: {"monitor_present": ("N", "C2: sources indicate no running control caught it")} for k in ["R02", "R13", "R18", "R23", "R24", "R26", "R27", "R29", "R37", "R08"]},
 "R11": {"monitor_present": ("Y", "C2: Cursor guardrails were in place and failed")},
 "R03": {"monitor_present": ("Y", "C2: audit logging was the control and was bypassed")},
 **{k: {"setting": ("training", "C2: found in OpenAI's review of training activity")} for k in ["R26", "R27"]},
 "R24": {"detected_by": ("external-party", "C2: Irregular notified Google")},
}

LIT_DEC = {
 "A": {
  "2508.00500": {"reports_fp_or_cost": ("Y", "C2: reports false alarms")},
  "2605.03482": {"reports_fp_or_cost": ("Y", "C2: reports FPR")},
  "2606.26524": {"reports_fp_or_cost": ("Y", "C2: FPR below 10%"), "evaluated_on": ("real-traces", "C2: real LLM-agent runs")},
  "2608.19161": {"reports_fp_or_cost": ("Y", "C2: monitoring load reported")},
  "2608.22868": {"reports_fp_or_cost": ("Y", "C2: verification time reported")},
  "2609.33039": {"reports_fp_or_cost": ("Y", "C2: latency reported")},
  "2608.24777": {"reports_fp_or_cost": ("N", "C2: only utility drop; no FP/latency figures")},
  "2608.27496": {"reports_fp_or_cost": ("N", "C2: only utility retention")},
  "2609.39549": {"reports_fp_or_cost": ("N", "C2: claims fewer false positives, no figures"), "reports_timeliness": ("N", "C2: claims lead time, no figures"), "evaluated_on": ("none", "C2: no evaluation stated")},
  **{k: {"reports_timeliness": ("N", "C2: early/predictive detection claimed, no lead-time figures")}
     for k in ["2605.16198", "2605.18988", "2605.27690", "2608.05695", "2608.27348"]},
  "2605.18988": {"reports_timeliness": ("N", "C2: theoretical bound only"), "evaluated_on": ("none", "C2: no empirical evaluation stated")},
 },
 "B": {
  **{k: {"production_data": ("Y", "C2: abstract states deployed-platform or proprietary production data")}
     for k in ["2408.00513", "2412.18287", "2510.12652", "2512.19061", "2601.22579", "2606.25007", "2609.27287"]},
  "2408.00513": {"production_data": ("Y", "C2: deployed on e-commerce platforms"), "state_scope": ("both", "C2: cohort relations plus sequences")},
  "2607.09528": {"state_scope": ("both", "C2: dataset covers transactions and behavioural relations")},
 },
}


def merge(c1, c2, dec, key, fields, log, label):
    out = []
    for rid, r1 in c1.items():
        r = dict(r1)
        r2 = c2.get(rid)
        for f in fields:
            v1 = r1[f]; v2 = (r2 or {}).get(f, "").strip()
            if rid in dec and f in dec[rid]:
                r[f] = dec[rid][f][0]
                log.append([label, rid, f, v1, v2, r[f], dec[rid][f][1]])
            elif v2 and v1 != v2:
                log.append([label, rid, f, v1, v2, v1, "C1 retained (no adjudication note)"])
        out.append(r)
    return out


log = []
c1 = {r["record_id"]: r for r in csv.DictReader(open(C("coder1.csv"), newline=""))}
c2 = {}
for name in ["coder2_cves.csv", "coder2_incidents.csv"]:
    if os.path.exists(C(name)):
        c2.update({r["record_id"]: r for r in csv.DictReader(open(C(name), newline=""))})
F = ["setting", "actor", "harm_external", "per_action_flaggable", "min_state",
     "precursor_signal", "monitor_present", "root_cause", "detected_by"]
rows = merge(c1, c2, {**DEC, **INCIDENT_DEC}, "record_id", F, log, "incident/cve")
with open(C("final.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for blk, fs in [("A", ["mechanism", "state_scope", "timing", "evaluated_on", "reports_fp_or_cost", "reports_timeliness"]),
                ("B", ["state_scope", "production_data"])]:
    a = {r["arxiv_id"]: r for r in csv.DictReader(open(C(f"lit_{blk}_coder1.csv"), newline=""))}
    b = {r["arxiv_id"]: r for r in csv.DictReader(open(C(f"coder2_lit_{blk}.csv"), newline=""))}
    out = merge(a, b, LIT_DEC[blk], "arxiv_id", fs, log, f"lit-{blk}")
    with open(C(f"lit_{blk}_final.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
with open(C("adjudication_log.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["set", "id", "field", "coder1", "coder2", "final", "reason"]); w.writerows(log)
print("disputed values:", len(log), "adjudicated with note:", sum(1 for l in log if not l[-1].startswith("C1 retained")))
