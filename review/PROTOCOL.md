# Review protocol — SoK revision

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

- **Coder 1 (C1):** Claude (Anthropic), working from primary sources fetched directly. C1's codes go in `coding/coder1.csv`.
- **Coder 2 (C2):** an author who codes independently from `coding/coder2_blank.csv` and has not seen `coder1.csv`.
- **Agreement:** Cohen's κ is computed per field by `scripts/kappa.py`. Disagreements are settled by discussion, and the final codes go in `coding/final.csv`. Both the pre-discussion κ and the number of changed codes are reported.

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
9. **Coder 2 is an LLM.** The protocol planned for an author to be Coder 2. On 2026-10-16, at the authors' direction, Coder 2 was instead a separate model instance (Claude Sonnet).
   - It started with a fresh context and had access only to the codebook (`coding/CODEBOOK_coder2.md`), the record lists and the sources. It never saw Coder 1's codes.
   - Coder 1 adjudicated every disagreement and logged a reason for each in `coding/adjudication_log.csv`.
   - Because Coder 1 is also the adjudicator, a human author codes a seeded random sample of 30 records (`coding/human_spotcheck_blank.csv`) as the independent check.
   - Reconciled codes are in `coding/final.csv`, `coding/lit_A_final.csv` and `coding/lit_B_final.csv`.

### Entries made on 2026-10-23 (EuroS&P revision)

10. **S1 census replaces the residual estimate.** All 843 CVEs that the automated pre-filter had excluded, and that no earlier pass had screened by hand, were screened by hand against I1–I4 (`raw/s1_screen.csv`, stage `census`; the rules as applied are written out in `coding/census/SCREENING_RULES.md`). 63 were included at first pass.
    - *Second screener:* a separate model instance (Claude Sonnet), blind to the first decisions, screened all 63 includes plus 137 randomly drawn excludes (seed 20261023), shuffled. Agreement 195/200, Cohen's κ = 0.94. The 5 disagreements were adjudicated with logged reasons (`coding/census/screen_adjudication.csv`); 2 were excluded, leaving 61 census includes.
    - *Why:* the residual estimate (about 51 eligible CVEs, 17–137) was the largest disclosed gap. The CVE stratum is now a census of the retrieved set.
    - CVE-2025-53773 appeared in the census pool; it was already included as an S4 known item and is marked E-DUP.
11. **Census CVEs coded by both coders.** The 61 new CVE records were coded by Coder 1 under the existing CVE rules and independently by Coder 2 (blind). Coder 1 adjudicated with logged reasons, following the precedents already in `coding/adjudication_log.csv` (symlink escapes and SSRF that depends on DNS resolution or redirects are `resource-metadata`; tool calls whose harm depends on their origin are `trajectory`, data provenance).
12. **S5 backward snowballing (one round) done.** `scripts/s5_snowball.py` fetched the reference lists of all 133 S3-included papers from the Semantic Scholar Graph API (raw responses in `raw/snowball/`, log in `raw/s5_run.log`). New in-window references were screened with the same stage-1 rule and stage-2 criteria (`raw/s5_stage2.csv`). References without abstracts were title-screened; for title-plausible ones, abstracts were sought from Semantic Scholar, arXiv and OpenAlex (`raw/s5_noabstract_title_matches.json`). 19 title-plausible references had no retrievable abstract and are reported as unscreened. *Why:* backward snowballing was planned in the original protocol but not done (S4 note above).
13. **Full-text check of the papers the manuscript cites by name.** The 22 arXiv papers cited with a specific claim or characterization were read in full (`coding/fulltext_checks.csv`). Three abstract-level codes changed (2601.18491 timing; 2605.27690 reports_timeliness; 2608.27141 evaluated_on and reports_fp_or_cost), logged in `coding/adjudication_log.csv`. Literature codes for all other papers remain abstract-level.

### Entries made on 2026-10-29

14. **Human calibration round, then a fresh reliability sample.** A human author independently coded the 30-record seeded sample (`coding/human_spotcheck.csv`, 12 incidents and 18 CVEs). Agreement with the reconciled codes was low:

    | Field | Agreement | κ |
    |---|---|---|
    | per_action_flaggable | 63% | −0.01 |
    | min_state | 60% | −0.06 |
    | monitor_present | 57% | 0.15 |
    | precursor_signal (incidents only) | 33% | −0.09 |

    The disagreements fell into three patterns:
    - precursor coded only when noticed at the time;
    - monitor counted when detection came afterwards;
    - CVE guards that the description states only partially.

    After review, the human coder adopted the reconciled codes for all 21 disagreeing rows (`coding/calibration_round1_log.csv`), so no final codes changed. The round is reported as **calibration**, not as reliability.

    The definitions of precursor and monitor were then clarified (`coding/HUMAN_CODING_GUIDE.md`). A fresh seeded sample (seed 20261029) of 8 incidents and 12 CVEs, not seen in round 1, is drawn for the reported human reliability check (`coding/human_reliability_blank.csv`).
