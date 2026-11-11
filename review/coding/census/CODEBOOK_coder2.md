# Codebook (Coder 2)

You are coding independently. Use only this folder and the primary sources listed in each record, which you may fetch from the web. Don't search for, open, or ask about any other coder's codes.

Use exactly the values listed below. Use **ID** when the sources don't give enough to decide, and **NA** only where a field defines it.

## Incident and vulnerability fields

- **setting**: where the agent was running.
  - `training`
  - `eval` (an authorized evaluation)
  - `internal-deploy` (used inside the developer's own organization)
  - `external-deploy` (used by customers or the public)
  - `product-vuln` (a vulnerability report rather than an incident)
  - `ID`
  - All CVE records are `product-vuln`.
- **actor**: who caused the harmful action.
  - `model-initiated`: the agent chose it.
  - `adversary-induced`: injected or attacker-controlled content steered it.
  - `mixed`
- **harm_external**: did effects reach a party outside the operator, meaning the person or organization running the agent?
  - `Y`, `N`, or `unclear`.
  - For CVEs with no reported exploitation, use `unclear`.
- **per_action_flaggable** (the core field): imagine a per-action policy that sees four things:
  - one proposed action
  - its arguments
  - the task instruction
  - the declared environment scope (which hosts, paths and resources are in scope)

  It has **no record of earlier actions**. Would it flag at least one documented action as unsafe?
  - `Y`: at least one action is unsafe on its own, for example publishing a malicious package, running a destructive command against production, or using a leaked credential.
  - `N`: every documented action is acceptable when judged alone; the harm comes from how actions combine, or from facts the policy cannot see.
  - `NA`: no unsafe action took place at all (for example, a missing audit-log entry).
  - `ID`: not enough detail.
- **min_state**: the least information a monitor needs to flag the **earliest** unsafe point.
  - `none`: the single action is enough.
  - `window`: the last few actions.
  - `trajectory`: the history of the whole run. This includes data provenance, meaning where a piece of data came from earlier in the run.
  - `cross-trajectory`: state across several runs, agents or samples.
  - `resource-metadata`: ground truth about what a resource is (for example, that a "test" URL, a volume or a folder actually points at production or live data). Neither action history nor run history supplies this.
  - `NA` when per_action_flaggable is `NA`; otherwise `ID` if you can't tell.
- **precursor_signal**: is a sequence-level signal documented **before** the first unsafe action? Examples are repeated failures or blocked attempts, probing, scanning or high request volume, credential hunting, and messages between agents.
  - `Y`, `N`, or `ID`.
  - Use `NA` for vulnerability reports, where no sequence of real actions is documented.
- **monitor_present**:
  - For incidents: was an action-level or trajectory-level control (a monitor, approval gate or classifier) running when it happened? `Y`, `N`, or `ID`.
  - For CVEs: does the description show an **existing guard** that was bypassed or proved insufficient? Examples are an approval or confirmation prompt, an allowlist or denylist, a validator, a sandbox, a path protection, an injection detector, or an SSRF filter. Then `Y`. If no guard existed or it was disabled, `N`.
- **root_cause**: the proximate cause the source names.
  - `model`, `environment-config`, `software-defect`, or `combination`.
  - CVEs are normally `software-defect`.
- **detected_by**: how the problem was first found.
  - `user` (the user or affected party)
  - `external-party`
  - `automated-monitor`
  - `transcript-review`
  - `ID`
  - CVEs are normally `external-party`.
- **notes**: one short line justifying `per_action_flaggable`, quoting the source where you can.

## Literature fields, block A (agent monitoring)

Code from the title and abstract.

- **mechanism**: `rule` (rules or automata), `formal` (temporal logic or model checking), `ifc-provenance` (information-flow or taint tracking), `learned` (a trained classifier), `llm-judge`, `graph-model`, `representation` (probes or internal model states), `probabilistic` (Markov, survival or statistical tests), `hybrid` (rules plus a model), `benchmark` (a benchmark or control setting, as the main contribution), or `position`.
- **state_scope**: `window`, `session`, `trajectory`, `cross-session` (persistent memory across sessions), `multi-agent`, or `cross-trajectory`.
- **timing**: `pre-execution`, `online`, `predictive` (forecasts a future violation), `post-hoc`, `mixed`, or `none`.
- **evaluated_on**: `benchmark`, `synthetic`, `simulation`, `real-traces`, `production-harness`, `case-study`, `preliminary`, `none`, or `ID`.
- **reports_fp_or_cost**: does it report false-positive, latency or compute figures? `Y`, `N`, or `ID`.
- **reports_timeliness**: does it report detection lead time or timing? `Y`, `N`, or `ID`.

## Literature fields, block B (fraud detection)

- **state_scope**: `sequence` (per-entity event sequences), `graph` (relations across entities), `both`, or `ID`.
- **production_data**: is it evaluated on production or industry data? `Y`, `N`, or `ID`.
