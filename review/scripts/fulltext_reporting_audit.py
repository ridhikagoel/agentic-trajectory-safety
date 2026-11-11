"""Reproduce the reporting audit from inspected, page-located evidence decisions.
This does not perform independent human coding. Original coding files are read-only.
PDF page numbers are one-based, including title pages. U means unconfirmed, not absent.
"""
import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'fulltext_audit'
rows=list(csv.DictReader((ROOT/'coding/lit_A_final.csv').open()))
manifest={r['arxiv_id']:r for r in json.loads((OUT/'retrieval_manifest.json').read_text())}
# index | PDF page | evidence paraphrase. These decisions follow inspection of extracted full text.
COST='''0|7|Reports guardrail FPR and defines inference cost through GPT-4o query counts.
1|10|Reports average runtime per question and less than five seconds added on MATH.
3|11|Section 4.7 compares total token usage on AgentDojo without attacks.
4|20|Reports 24–30 hours wall-clock evaluation time per model; this is suite cost, not per-alert cost.
5|2|Reports runtime overhead below 50 ms for embodied agents and about 100 ms in the other evaluated setting.
6|11|Table 2 and Section 5.2 report USD cost per pentest trajectory.
8|5|Defines measured inference latency in milliseconds per example.
9|7|Cost and latency analysis gives sample generation cost below USD 0.02 and points to Appendix H.
10|23|Table 10 reports mean CTL-checking runtime near 1.07 seconds for 500 constraints.
11|7|Reports average detection latency of 66 ms.
12|7|Evaluates safety at 4 percent trajectory FPR and 0.08 percent step FPR.
13|14|Reports agentic FPR of 0.01–0.02.
14|9|Table 5 reports defense time cost in seconds.
15|4|Table 4 compares measured inference latency.
17|7|Reports measured FPR of 0.9 percent for o4-mini with recall 0.88 and a recall–cost comparison. PDF p.6 separately defines intervention timing and tokens saved.
19|2|Reports safety/benign-task performance and runtime-overhead analysis; verification of numeric runtime requires the efficiency section.
20|7|Table 2 compares measured latency, throughput and peak memory under a specified GPU protocol.
21|8|Tables 5 and 9 report FPR plus per-scenario runtime and token usage.
22|16|Table 4 reports preliminary benign false-positive rates; Table 5 on page 17 reports harness overhead.
23|2|Reports 2.0–2.8 times token inflation and separates token accounting by actor.
24|8|Reports FPR zero for ILION+SRM versus five percent for the stateless comparator.
25|2|Reports submicrosecond overhead versus 5–28 ms comparators.
27|15|Reports token cost and success across recovery configurations, including 154K tokens for Governor plus Reflexion.
28|26|Benign-only control and context-length sweep explicitly evaluate false-positive behavior.
31|2|Reports undetected sabotage under one-percent step-wise FPR.
33|13|Reports a concept-drift false-positive ablation; efficiency analysis distinguishes structural validation from other processing.
34|6|Table 3 reports per-prefix latency, including 4.6 ms for the proposed detector.
35|12|Reports token consumption and a turn-indexed detection-latency distribution.
36|2|Reports TPR one and FPR zero for the evaluated composite portfolios.
37|3|Reports low-millisecond median end-to-end latency on the internal benchmark.
39|9|Figure 3 reports average wall-clock runtime per sample.
41|7|Table 3 compares API calls, tokens and latency; full method uses six calls, 300 tokens and 75 seconds in the reported setting.
45|11|Figure 3 compares two calls per trajectory with eight and seventeen calls for ensemble approaches.
47|9|Table 6 reports 9.93 seconds and 47.4K tokens for the full system, versus 5.32 seconds and 11.2K tokens baseline.
48|7|Reports cost-aware routing and explicitly limits accounting to logged quantities rather than total pipeline cost.
50|2|Reports monitor catch rates at FPR no greater than two percent.
51|19|Appendix reports measured latency, throughput and peak memory under a fixed GPU protocol.
53|5|Reports sixteen flagged trajectories, fifteen failures among them, and group contingency counts; false alarms are observable as counts rather than a quoted FPR.
54|14|Appendix E Table 14 reports latency and inference overhead.
55|18|Appendix B.2 reports per-step probe and steering-search costs, including probe latency below one second.
56|10|Defines benign false positives and reports end-to-end and stage-level latency.
58|4|Honest baseline is used for monitor FPR calibration; inspection also finds measured coordination turn-budget costs on page 11.
59|33|Reports seventy/seventy-five-percent catch rates against seven-percent baseline FPR in one setting; other settings are reported separately.
61|6|Reports 48.1 ms per turn and 1.4 percent response-latency overhead, with false-alarm calibration.
64|4|Reports two invariants suppressed because measured benign FPR exceeded five percent.
65|5|Reports FPR and end-to-end wall-clock latency per guardrail call.
66|7|Reports ninety benign false positives for Cisco Skill Scanner and eight for AgentDoG.
67|9|Reports reduction in borderline-benign false positives from 37.3 percent to 0.7 percent in the pinned version.
70|22|Section 8.7 reports 6.4 microseconds average policy interception time, distinguishing wrapper and logging costs.
71|5|Reports measured mean model latency of 1.6 seconds for a replanning round trip, separately from simulated guard-check costs.
72|23|Reports approximately four percent false positives and six percent false negatives over the training analysis.
73|13|Reports 599.9 ms and 195.5 generated tokens per guard call, with 2.53 seconds per task.
74|21|Reports MELON clean-task FPR rising from 44 to 72 to 100 percent across delegation conditions.
75|20|Table 5 reports safety–utility–cost frontier, halt latency and censored time-to-detect.
77|5|Reports realized test FPR and calibration-target exceedance; page 16 reports recall and median lead.
79|6|Computational Cost section and Table 3 report added embedding, localization and verification costs.
80|7|Compares execution cost, runtime and tool usage against the coding-agent baseline.
81|6|Reports deterministic grounding latency measured on Apple M4 Pro.
87|8|Reports 53 ms and 215 ms comparator latencies and lower-latency internal-state readouts.
88|8|Reports guard-only runtime and long-context latency, with hardware and batch-size conditions.
93|9|Evaluates TPR at FPR of one percent or lower.
95|21|Table 7 reports runtime and VRAM; appendix reports token consumption.
98|16|Tables 10 and 11 report interaction/context overhead and seconds per sample.
99|5|Evaluates monitor curves down to one-percent FPR and discusses escalation burden.
101|15|Reports authorization latency decomposed into end-to-end client and server components.
102|10|Table 2 reports clean utility and FPR for three backbones.
103|11|Reports sixteen non-propagating false positives and a 400-scenario cascade evaluation.
104|2|Reports submillisecond hot-path operation overhead and a regenerated microbenchmark artifact.
105|7|Table 4 reports latency; page 8 Table 5 reports clean negative/borderline FPR.
106|5|Computes FPR on one thousand task-matched benign prompts and reports prototype operating points.
83|11|Table 3 reports measured per-trajectory latency of 0.09, 0.18 and 0.21 seconds for the three MATE sizes.
108|10|Reports protected median latency increment of 3930.8 ms and 2.35-times overhead with component attribution.'''
# Remove observations that do not yet establish a numerical operating result in the inspected locator.
EXCLUDE_COST={19,33,48,58,79,80,81,95,101,104,106}
# These exclusions remain U until a numeric result is directly located; prior Y is not enough.
TIMING='''5|8|advance_warning|Table 1 reports average advance warning in seconds before simulated safety violations.
11|7|temporal_localization|Table 1 reports step-level detector localization scores under the delay-penalized protocol defined on PDF p.5. The annotator MAE on p.16 measures label agreement and is not detector performance.
17|2|intervention_timing|Defines and evaluates intervention timeliness; EIR separates timing from coverage.
24|8|detection_turn|Reports average detection turn and Early Detection Gain on synthetic sessions.
25|6|advance_warning|Reports mean warning of 3.7 steps.
35|12|detection_delay|Reports mean delay of 0.05 turns in the long-horizon analysis and distinguishes early versus late alerts.
49|5|prefix_early_detection|Defines Early Detection Rate and early-alert metrics; full benchmark results must be interpreted with their prefix construction.
53|5|advance_warning|Reports median nine reasoning steps before termination for flagged failure trajectories, at 84 percent elapsed.
61|2|advance_warning|Reports 88.3 percent of violations forecast with average lead time; page 6 gives threshold-dependent mean lead.
65|10|advance_warning|Defines Mean Advance Steps before the first hazard and reports dedicated timing evaluation.
75|20|detection_delay|Table 5 reports halt latency and right-censored time-to-detect against the first invalid transition.
77|16|advance_warning|Reports recall and median lead, including median lead of 42 steps at one stated operating point.
85|5|intervention_timing|Table reports Perfect, Early, Late and On-Time interruption rates.
88|9|temporal_localization|Reports exact adjudicated intervention-boundary identification in 90.63 percent of unsafe root-language trajectories.
102|16|detection_delay|Aggregates alarm timing across suites and attack instances; appendix discusses short-horizon lead-time limitations.'''
PREFIX='''8|15|Reports prefix-length detection accuracy; no event-relative lead-time result confirmed.
41|8|Shows risk trajectories and corrections but no event-relative timing metric confirmed.
52|12|Reports predictive FNR and Precision across ethical-prefix windows; not equivalent to warning lead time.
55|8|Reports current-step and one-step-lookahead detection accuracy; a fixed prediction horizon is not measured intervention lead time.'''
def parse(s):return {int(x.split('|',1)[0]):x.split('|')[1:] for x in s.splitlines() if x.strip()}
cost=parse(COST);timing=parse(TIMING);prefix=parse(PREFIX)
# All seven legacy real-trace/production-harness positives were inspected for provenance.
PROVENANCE={27:(5,'production_observations','347 traces collected over eight days from a production ReAct system.'),53:(3,'recorded_task_runs','Recorded coding-agent trajectories; task-study evidence, not longitudinal production traffic.'),56:(2,'executed_skill_benchmarks','152 labeled runs and 216 real skill-bundle executions; benchmark execution must not be equated with deployed traffic.'),57:(2,'production_framework_test_harness','Tests four production agent frameworks; framework evaluation does not establish observation of production incidents.'),62:(18,'workspace_harness_runs','Stores run records and tool/environment artifacts from workspace-agent benchmark execution.'),80:(1,'repository_task_traces','642 documented anomalous traces from 382 real repository tasks; task-study corpus.'),83:(8,'mixed_synthetic_and_real_task_runs','Includes synthetic subsets and 162 manually collected real-device trajectories from 13 apps and three mobile-agent systems; retain the real-traces code, without equating this with production-traffic observation.')}
ledger=[];overlay=[]
for i,r in enumerate(rows):
 m=manifest[r['arxiv_id']];pdf=OUT/'pdf'/f"{r['arxiv_id']}.pdf"
 assert hashlib.sha256(pdf.read_bytes()).hexdigest()==m['sha256']
 cp=cost.get(i);tp=timing.get(i);pp=prefix.get(i)
 confirmed=cp is not None and i not in EXCLUDE_COST
 record=dict(arxiv_id=r['arxiv_id'],title=r['title'],version=m.get('downloaded_version','unresolved'),version_date=m.get('version_date',''),source_url=m['url'],sha256=m['sha256'],reviewer='OpenAI Codex (AI-assisted verification)',review_type='targeted full-text reporting audit',old_cost=r['reports_fp_or_cost'],cost_status='Y' if confirmed else 'U',cost_pdf_page=cp[0] if confirmed else '',cost_evidence=cp[1] if confirmed else 'No numerical operating result confirmed in the inspected evidence. U does not mean absent.',old_timing=r['reports_timeliness'],timing_status='Y' if tp else 'U',timing_kind=tp[1] if tp else 'fixed_prefix_or_lookahead_only' if pp else 'unconfirmed',timing_pdf_page=tp[0] if tp else pp[0] if pp else '',timing_evidence=tp[2] if tp else pp[1] if pp else 'No event-relative timing result confirmed; a proactive design claim alone is insufficient.',provenance_status=PROVENANCE[i][1] if i in PROVENANCE else 'not_reclassified',provenance_pdf_page=PROVENANCE[i][0] if i in PROVENANCE else '',provenance_evidence=PROVENANCE[i][2] if i in PROVENANCE else 'Legacy evaluation code retained without full provenance reclassification.',other_fields_status='mechanism/state scope remain inherited; not independently revalidated in this reporting audit')
 if m['version_status']!='within_cutoff':
  record['version']='unresolved';record['cost_status']='U';record['timing_status']='U';record['cost_evidence']='Version date unresolved; positive reporting evidence withheld from cutoff-respecting totals.'
 ledger.append(record);nr=dict(r);nr['reports_fp_or_cost']='Y' if record['cost_status']=='Y' else 'ID';nr['reports_timeliness']='Y' if record['timing_status']=='Y' else 'ID'
 # Evaluation codes are retained; MATE has both real and synthetic subsets.
 overlay.append(nr)
def save(path,rs):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
# Preserve human review columns and any later reviewer annotations on regeneration.
existing_path = OUT/'reporting_evidence_ledger.csv'
if existing_path.exists():
    existing_rows=list(csv.DictReader(existing_path.open(newline='')))
    existing_by_id={row['arxiv_id']:row for row in existing_rows}
    extra_headers=[key for key in existing_rows[0] if key not in ledger[0]] if existing_rows else []
    for row in ledger:
        previous=existing_by_id.get(row['arxiv_id'],{})
        for key in extra_headers:row[key]=previous.get(key,'')
save(OUT/'reporting_evidence_ledger.csv',ledger);save(OUT/'lit_A_reporting_audited.csv',overlay)
summary={'papers':len(rows),'fulltexts_retrieved':len(manifest),'confirmed_quantitative_operating_reports':sum(r['cost_status']=='Y' for r in ledger),'confirmed_event_relative_timing_reports':sum(r['timing_status']=='Y' for r in ledger),'unresolved_versions':[r['arxiv_id'] for r in ledger if r['version']=='unresolved'],'scope':'All 111 received targeted full-text reporting checks. Not a full independent recoding of every taxonomy field. U means unconfirmed, never verified absence.','original_files_modified':False,'timing_kinds':dict(Counter(r['timing_kind'] for r in ledger if r['timing_status']=='Y'))}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
