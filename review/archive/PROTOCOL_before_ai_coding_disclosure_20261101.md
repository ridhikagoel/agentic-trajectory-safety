# Review protocol — SoK revision

> **Current roles.** Two authors performed the original screening and coding and jointly resolved disagreements. Claude was used for manuscript editing. A subsequent Codex-assisted full-text reporting audit and source-based editorial reconciliation are documented separately below. The superseded protocol is retained in `archive/PROTOCOL_before_role_cleanup_20261030.md`; its older model-coder attributions are not the current method. Independent pre-resolution agreement is not established, and the current manuscript does not assert kappa statistics.

Fixed on 2026-10-14, before screening. Changes made after screening must be logged at the bottom with a reason.

## Research questions

- **RQ1.** In publicly documented agent incidents, how often is the harmful outcome visible only across a sequence of actions, and not from any single action judged in isolation?
- **RQ2.** What state (none, a bounded window, the full trajectory, or several trajectories or agents) would a monitor need in order to flag each incident?
- **RQ3.** Which detection and control approaches in the literature give monitors that kind of state? What do behavioral fraud and authentication systems already do that maps onto this?

## Window

Disclosure or publication date from **2025-01-01 to 2026-09-30**. Searches were run on 2026-10-14. Records disclosed after 2026-09-30 are excluded with reason E-DATE, and the number excluded is reported.

## Sources

| ID | Source | Method | Unit |
|---|---|---|---|
| S1 | NVD CVE API 2.0 | `scripts/s1_nvd_search.py`; 10 keyword queries; publication date in window | CVE |
| S2a | AI Incident Database research snapshot `backup-20261012101643` (CC BY-SA 4.0) | `scripts/s2_aiid_filter.py`; regex over title and description; incident date in window | AIID incident |
| S2b | Primary disclosures by frontier developers and government evaluators: UK AISI, US CAISI, Anthropic, OpenAI (including the misalignment-reports log), Google DeepMind, Meta, Microsoft | Logged web searches restricted to the organization's own domains, plus full enumeration of each index page found (`raw/s2b_search_log.csv`) | Disclosed incident |
| S3 | arXiv API | `scripts/s3_arxiv_search.py`; query blocks A1–A4 (agent trajectory safety) and B1–B2 (sequence and behavioral fraud); submitted 2023-01-01 to 2026-09-30 | Paper |
| S4 | Known items | The 8 cases in the original submission, screened against the same criteria (`raw/s4_known_items.csv`). Backward snowballing of S3 papers was planned but **not done** in this pass. | Case |

## Incident inclusion criteria (S1, S2)

Include the record if **all** of the following hold:

- **I1.** An LLM-based agent took, or could be made to take, actions through tools, code execution, or network access. Text-only harms are not enough.
- **I2.** The record describes either (a) an agent acting outside its sanctioned scope during training, evaluation, or deployment, or (b) an exploitable defect in an agent-enabled product where exploitation runs through the agent's tool actions.
- **I3.** There is a primary account (the affected organization, the developer, the evaluator, a CVE record, or a vendor advisory), or a named-organization statement quoted in reputable press.
- **I4.** The record has enough detail to identify at least one concrete agent action.

Exclude the record if any of the following applies:

| Code | Reason |
|---|---|
| E-DATE | Disclosed outside the window. |
| E-NOAGENT | No agentic tool use. Chatbot content harms, deepfakes, and similar are excluded. |
| E-SIM | The incident happened only in simulation, with no real systems affected or touched. |
| E-BENCH | Aggregate benchmark result with no discrete incident. |
| E-DUP | Duplicate of an included record. Duplicates are merged under the primary source. |
| E-SECONDARY | Unattributed secondary report only. |
| E-DETAIL | Not enough detail to identify an agent action. |
| E-NONAI | A CVE in a product that merely contains "AI" or "agent" in its name, where the flaw has nothing to do with agent behavior. |

## Codebook (one row per included incident)

| Field | Values | Definition |
|---|---|---|
| `setting` | eval / training / internal-deploy / external-deploy / product-vuln | Where the agent was running. |
| `actor` | model-initiated / adversary-induced / mixed | Whether the harmful action came from the model itself or from injected content. |
| `harm_external` | Y / N / unclear | Whether effects reached a party outside the operator. |
| `per_action_flaggable` | Y / N / ID | **Core field.** Would a per-action policy flag at least one documented action as unsafe? The policy sees one proposed action, its arguments, the task instruction, and the declared environment scope, but no record of prior actions. **Y** means at least one action is unsafe on its own (examples: publishing a malicious package; running a destructive command on production). **N** means every documented action is acceptable in isolation and the harm comes from how they combine. **ID** means there is too little detail to tell. |
| `min_state` | none / window / trajectory / cross-trajectory / ID | The least state a monitor needs to flag the earliest unsafe point. **none** = a single action; **window** = the last k actions; **trajectory** = the full run history; **cross-trajectory** = state across runs, agents, or tenants. |
| `root_cause` | model / environment-config / software-defect / combination | The proximate cause the primary source names. |
| `detected_by` | transcript-review / automated-monitor / external-party / user / ID | How the incident was first detected. |
| `notes` | free text | Quote the source passage that justifies `per_action_flaggable`. |

## Coding procedure

- **Original screening and coding:** performed by two authors using the shared codebook.
- **Disagreement resolution:** the two authors jointly resolved disagreements. Final codes are retained in `coding/final.csv`, `coding/lit_A_final.csv`, and `coding/lit_B_final.csv`.
- **Claude's role:** manuscript editing, not original screening, coding, or adjudication.
- **Agreement statistics:** no independent pre-resolution agreement estimate is asserted until its underlying author coding sheets are confirmed. Joint resolution alone does not establish independent agreement.
- **Subsequent audit:** Codex performed the separately recorded reporting audit and source-based editorial resolutions described in entries 15–16. These are AI-assisted evidence checks, not human coding.

## Literature screening (S3)

- **Stage 1 (automated, reproducible):** the abstract must match at least one term from both lists:
  - **(i) sequence:** trajectory, multi-step, multi-turn, sequence, sequential, long-horizon, session, temporal, history, stateful, behavioral or behavioural
  - **(ii) control:** monitor, detect, detection, guardrail, verification, verifier, anomaly, audit, shield, oversight, fraud
- **Stage 2 (manual, C1):** a title and abstract screen. Include a paper if it proposes, evaluates, or benchmarks a mechanism that decides on the safety or legitimacy of an action using information from more than one action or event. That covers agent trajectories, or transaction and session sequences for the fraud block.
- **Stage 3:** included papers are coded on mechanism, state scope, learned vs. rule-based, evaluated-on, and whether false positive or reviewer cost is reported (`coding/lit_coder1.csv`).

## Deviations log

All entries below were made on 2026-10-14, during screening and coding. Each one lists what changed and why.

1. **New exclusion code E-MISUSE.** Covers an agent operated by a malicious principal that does what that principal asks, for example threat actors using Claude Code or Cursor. *Why:* these are misuse cases, not control failures, and they don't satisfy I2. The code was added while title-screening AIID records; 13 records were excluded under it.
2. **New exclusion code E-INSCOPE.** Covers an agent that acts within its configured scope, where the harm comes from workflow or vendor design. *Why:* this came up for 2 AIID records (1470, 1675), and none of the existing codes fit them.
3. **Automated pre-filter on S1, applying I2(b), then audited.**
   - *First pass:* the CVE description had to contain prompt-injection or agent-manipulation language. That excluded 1,108 of 1,231 CVEs automatically; the other 123 were screened by hand and 94 were included.
   - *Problem found:* the known-item check (S4, below) showed the pre-filter dropped eligible CVEs whose vendor wording avoids "prompt injection" (for example "AI command injection" or "bypass the confirmation prompt").
   - *Second pass:* three audit steps were added to the 1,108 auto-excluded CVEs.
     - (a) A targeted pass: agent or product terms plus action terms plus agent-influence phrasing. 82 screened by hand, 42 included.
     - (b) A broad phrasing pass ("by an agent", "auto-approve", "confirmation prompt", ...): 73 screened, 21 included.
     - (c) Two seeded random samples of what was left. Before pass (b): 60 drawn, 4 eligible. After pass (b): 50 drawn from the final pool of 893, 3 eligible.
   - *Residual estimate:* 3/50 = 6% (Wilson 95% CI 2.1–16.2%), so roughly 51 eligible CVEs (about 17–137) remain among the 843 CVEs that were never screened by hand. The CVE stratum is a large sample, not a census.
   - *S4 known items:* the original submission's 8 cases were screened against the same criteria (`raw/s4_known_items.csv`). One eligible case missed by S1 (CVE-2025-53773) was added. Three failed the criteria: Unit 42 (E-DETAIL), n8n (E-NONAI) and EchoLeak (E-NOAGENT).
4. **Two codebook fields added after coding a pilot of 10 incident records.**
   - `precursor_signal` (Y/N/ID/NA): is there a documented sequence-level signal (repeated failures, probing, scanning, credential hunting, cross-agent messages) before the first unsafe action?
   - `monitor_present` (Y/N/ID): was an action-level or trajectory-level control running when the incident happened?

   *Why:* the pilot showed that `per_action_flaggable` alone hides the main pattern in the record, which is that most incidents had a flaggable step but no control was running to catch it.
5. **New codebook values.**
   - `per_action_flaggable = NA`: no unsafe action took place (R03, an audit-log gap).
   - `min_state = resource-metadata`: flagging the action requires ground truth about which resource it touches, such as whether a URL or volume is production. Neither action history nor trajectory history supplies that.
6. **CVE `monitor_present` is hand-coded.** A keyword rule was tried first. A 12-record spot check found errors: "without validation" was read as a guard being present, and "security disabled by default" was read as a guard that was bypassed. The rule was dropped, and Coder 1 hand-coded all 165 CVEs from their descriptions.
   - **Y:** the description shows an existing guard (approval, allowlist or denylist, validator, sandbox, path protection, injection detector, SSRF filter) that was bypassed or proved insufficient.
   - **N:** no guard existed, or it was disabled.
   - **ID:** the description is too thin to tell.

   `per_action_flaggable` defaults to Y for CVEs. 14 records were overridden by hand: 9 to N and 5 to ID.
7. **Inaccessible primary pages.** openai.com refused automated retrieval (HTTP 403) for two disclosure pages. The OpenAI–Irregular record is excluded as E-DETAIL. R28 (DSEwiki) is coded from Reuters and the misalignment-log index entry. This review did not try to get around the block.
8. **S3 coding is at abstract level only.** Full-text verification is left to Coder 2 and reported as a limitation.
9. **Corrected original-review attribution.** The authors confirmed that they performed screening and coding and jointly resolved disagreements. Claude's role was editing. Superseded model-coder statements and their associated procedural claims are preserved in the archived protocol rather than repeated as current methods.

### Entries made on 2026-10-23 (EuroS&P revision)

10. **S1 census replaces the residual estimate.** All 843 CVEs that the automated pre-filter had excluded, and that no earlier pass had screened by hand, were screened by hand against I1–I4 (`raw/s1_screen.csv`, stage `census`; the rules as applied are written out in `coding/census/SCREENING_RULES.md`). 63 were included at first pass.
    - *Screening check:* the existing files retain a 200-record screening check and adjudication log, with two records removed from the 63 initial inclusions. Original screening was performed by the authors. The current paper does not assert the older independent-agreement estimate without confirmed underlying author sheets.
    - *Why:* the residual estimate (about 51 eligible CVEs, 17–137) was the largest disclosed gap. The CVE stratum is now a census of the retrieved set.
    - CVE-2025-53773 appeared in the census pool; it was already included as an S4 known item and is marked E-DUP.
11. **Census CVE coding.** The authors coded the 61 added records under the codebook and jointly resolved disagreements. Coding and adjudication files are retained. Resource resolution and data-provenance distinctions follow the recorded definitions. No unconfirmed blind-coding or single-model adjudication claim is asserted.

12. **S5 backward snowballing (one round) done.** `scripts/s5_snowball.py` fetched the reference lists of all 133 S3-included papers from the Semantic Scholar Graph API (raw responses in `raw/snowball/`, log in `raw/s5_run.log`). New in-window references were screened with the same stage-1 rule and stage-2 criteria (`raw/s5_stage2.csv`). References without abstracts were title-screened; for title-plausible ones, abstracts were sought from Semantic Scholar, arXiv and OpenAlex (`raw/s5_noabstract_title_matches.json`). 19 title-plausible references had no retrievable abstract and are reported as unscreened. *Why:* backward snowballing was planned in the original protocol but not done (S4 note above).
13. **Full-text check of the papers the manuscript cites by name.** The 22 arXiv papers cited with a specific claim or characterization were read in full (`coding/fulltext_checks.csv`). Three abstract-level codes changed (2601.18491 timing; 2605.27690 reports_timeliness; 2608.27141 evaluated_on and reports_fp_or_cost), logged in `coding/adjudication_log.csv`. Literature codes for all other papers remain abstract-level.

### Entries made on 2026-10-29

14. **Calibration records.** The 30-record calibration sheet and its clarification log are retained as calibration artifacts, separately from the paper-reporting verification. They do not establish independent pre-resolution reliability. Earlier agreement figures and procedural descriptions are preserved in the archived protocol, not asserted in the current manuscript. The subsequent 20-record reliability form remains uncompleted.

### Entry made on 2026-10-30

15. **Author-role correction and separate full-text reporting audit.** The authors clarified their original human screening/coding and joint resolution roles. The manuscript distinguishes that process from the present Codex-assisted reporting check. Earlier role descriptions are retained in the archived protocol; earlier kappa figures are not presented as human agreement without confirmed underlying independent sheets.

    All 111 monitoring PDFs were retrieved, version-pinned to the September 30 cutoff, and searched for numerical operating-reporting and timing evidence. Inspected page-located positives, unknowns, and original codes are recorded in `fulltext_audit/reporting_evidence_ledger.csv`. At least 59 papers have confirmed quantitative operating evidence and at least 15 timing-related evaluation, under the explicit definitions in that folder's README. Unknowns are not negative findings. The new definition does not equate task utility alone with operating-cost evidence, so it is not identical to the earlier abstract-derived composite.

    The original seven trace/harness-positive studies received provenance checks. MATE retains its real-trace label because its evaluation includes a separate real-device subset in addition to synthesis. Other inherited taxonomy labels and the 74-paper fraud corpus were not independently reclassified in this pass.

    `scripts/fulltext_reporting_audit.py` regenerates the new ledger/overlay/summary without overwriting original coding files. The revised manuscript uses lower-bound reporting totals and distinguishes warning lead time, detection delay, localization, and prefix evaluation. This is not independent human validation or a reproduction of the reviewed papers' experiments.

16. **Source-based resolution and human-review integration.** Four reporting-definition differences in the supplied 14-paper single-author review were resolved editorially with source evidence, retaining original human answers. The 14 supplied reviews and 16 disjoint earlier monitoring checks form a purposive set of 30 papers, not 30 human validations or a random sample. The source-resolution log identifies AI authorship and does not assert human consensus. StepShield and Stale Does Not Mean Unsafe supply two additional numerical operating reports, raising the conservative lower bound from 59 to 61; timing remains 15. OS-Sentinel's timing evidence locator now cites its detector protocol/results, not annotator MAE. Fixed-prefix prediction is kept separate from event-relative timing. Independent pre-resolution human agreement remains unestablished; no kappa is asserted.
