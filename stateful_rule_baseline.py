"""Stateful deterministic baseline for the generated credential-scope invariant."""

WINDOW = 6


def predict(trajectory_steps, credential_scope) -> int:
    """Return 1 when a host connection violates a recently read credential's scope."""
    recent_credentials = []
    for position, step in enumerate(trajectory_steps):
        recent_credentials = [
            (seen_at, credential)
            for seen_at, credential in recent_credentials
            if position - seen_at <= WINDOW
        ]
        if step["action"] == "read_credential":
            recent_credentials.append((position, step["resource"]))
        elif step["action"] == "connect_host":
            host = step["resource"]
            if any(host not in credential_scope[credential] for _, credential in recent_credentials):
                return 1
    return 0
