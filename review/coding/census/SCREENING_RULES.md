# Screening rules for NVD CVE records (S1)

These are the protocol's inclusion criteria (I1–I4) as they were applied to CVE descriptions in every S1 stage. Screen from the description text only.

**Include** a CVE when the description states that exploitation runs through an LLM agent's own tool actions (criterion I2b). Typical signs:
- the dangerous input is agent-supplied, LLM-controlled, or comes from a prompt, prompt injection, or untrusted content in the agent's context;
- a guard on the agent's actions (approval or confirmation prompt, command allowlist or denylist, read-only validation, sandbox, path or deny rules, SSRF filter on an agent tool) is bypassed or missing, and the agent is the one acting.

**Exclude** with one reason code:
- `E-NONAI`: the flaw is exploitable directly (an attacker calls an API, endpoint, or MCP tool themselves; a caller supplies a parameter) and the description states no agent-mediated path. This includes code that runs at startup or when a project or config file is loaded, before any agent action (for example, before a trust prompt).
- `E-NOAGENT`: the harm comes from client-side rendering of model or chat output (XSS, markdown or Mermaid rendering), not from an agent tool action.
- `E-DETAIL`: the description is too thin to identify any agent path (for example, a one-line vendor summary such as "command injection in Copilot allows information disclosure").
- `E-DUP`: duplicate of another included record.

A product being "AI", "agentic" or an "MCP server" is not enough by itself; the description must state the agent path.
