# Human coding guide (clarified after calibration round 1)

Code each record **without** opening `coder1.csv`, `coder2*.csv`, `final.csv`, `adjudication_log.csv`, `RESULTS.md`, or the paper's incident table.

Imagine a safety check that sees **one action at a time**: the command or tool call, its arguments, what the user asked for, and what is declared in scope. It has **no memory** of earlier steps.

## E: per_action_flaggable

- **Y**: at least one documented step is clearly unsafe on its own, given the task and scope. Judge the step as written, including its arguments. Examples:
  - a path such as `../../.bashrc` or an absolute path outside the workspace
  - writing to a config or hooks file
  - running code from an untrusted source
  - publishing internal data to a public location
- **N**: every step looks like normal, in-scope work when judged alone.
- **ID**: the source is too vague to tell which step was unsafe.

## F: min_state

- If E = Y, enter `none`.
- If E = N, choose one:
  - `trajectory`: needs memory of earlier steps.
  - `resource-metadata`: needs facts about what a file, URL or server really is.
  - `cross-trajectory`: needs several runs or agents.

## G: precursor_signal

Incidents only (`NA` for CVEs). Answer **Y** if the source documents **any** warning sign **before** the first unsafe step, **even if nobody noticed it at the time** and it was only found in a later investigation. Warning signs include:

- repeated failures or blocked attempts
- the user or operator refusing a request that the agent then pursues anyway
- probing or scanning
- searching for credentials or keys
- agents messaging each other
- researching a target

## H: monitor_present

- **Incidents:** Y only if a monitor, classifier or approval prompt was **running at the time** and could have stopped the action. Detection **afterwards** (logs reviewed later, an investigation, an outside party reporting it) does **not** count. If the source doesn't say, enter `ID`.
- **CVEs:** Y if the description shows a guard that **existed** and was bypassed or proved insufficient. Look for:
  - "requires approval" or "confirmation"
  - allowlist or denylist
  - "protected" files
  - sandbox, validation or a path check
  - "bypass"

  The guard can be partial; for example, edits require approval but creating a new file doesn't. Otherwise N.
