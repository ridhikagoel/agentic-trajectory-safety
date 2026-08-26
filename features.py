"""
Step 3 - feature engineering for the logistic regression detector.

Deliberately NOT given the ground-truth credential-scope table - that would
let the model trivially reconstruct the exact rule used to generate the
label, which would be circular (re-deriving the answer through a differently
named feature isn't a result). Instead it only gets:

  - generic sequence-shape features (action n-grams, counts, length)
  - a structural "credential read near a connect" indicator (positional
    only - doesn't know if the pairing is dangerous)
  - sparse indicators for which (credential_id, host_id) pairs co-occurred
    within the window

That last group is the important one: it's raw identity co-occurrence, not a
scope lookup. The model has to LEARN from many labeled training examples
which specific pairs are associated with the unsafe label - the same way a
real model learns from incident history, not from being handed a policy
table. This is what makes it a genuine test of "can a model pick up
relational structure a stateless rule cannot," instead of a rigged one.
"""

import numpy as np

ACTION_TYPES = ["list_resources", "read_file", "write_file", "read_credential", "connect_host", "temporary_approval"]
ACTION_IDX = {a: i for i, a in enumerate(ACTION_TYPES)}
WINDOW = 6


def build_pair_vocab(cred_ids, host_ids):
    pairs = [(c, h) for c in cred_ids for h in host_ids]
    return {pair: i for i, pair in enumerate(pairs)}


def extract_features(steps, pair_vocab):
    n_actions = len(ACTION_TYPES)
    unigram = np.zeros(n_actions)
    bigram = np.zeros(n_actions * n_actions)
    pair_feats = np.zeros(len(pair_vocab))

    cred_positions = []  # (position, cred_id)
    host_positions = []  # (position, host_id)

    prev_type = None
    for i, step in enumerate(steps):
        a, r = step["action"], step["resource"]
        unigram[ACTION_IDX[a]] += 1
        if prev_type is not None:
            bigram[ACTION_IDX[prev_type] * n_actions + ACTION_IDX[a]] += 1
        prev_type = a

        if a == "read_credential":
            cred_positions.append((i, r))
        elif a == "connect_host":
            host_positions.append((i, r))

    near_pattern = 0
    for cp, cred in cred_positions:
        for hp, host in host_positions:
            if 0 < hp - cp <= WINDOW:
                near_pattern = 1
                key = (cred, host)
                if key in pair_vocab:
                    pair_feats[pair_vocab[key]] = 1

    extra = np.array([
        len(steps),
        len(cred_positions),
        len(host_positions),
        len(set(h for _, h in host_positions)),
        near_pattern,
    ])

    return np.concatenate([unigram, bigram, extra, pair_feats])


def feature_names(pair_vocab):
    n_actions = len(ACTION_TYPES)
    names = [f"unigram_{a}" for a in ACTION_TYPES]
    names += [f"bigram_{a1}_{a2}" for a1 in ACTION_TYPES for a2 in ACTION_TYPES]
    names += ["length", "n_cred_reads", "n_connects", "n_distinct_hosts", "near_pattern"]
    names += [f"pair_{c}_{h}" for (c, h) in pair_vocab]
    return names
