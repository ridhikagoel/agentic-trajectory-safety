"""
Step 4 - small LSTM sequence detector.

Unlike the logistic regression detector, this one is NOT given the
(credential, host) pair-co-occurrence features directly. It only sees the
raw (action_type, resource_id) sequence, embedded, and has to learn from
label alone whether tracking specific resource identities across time
matters - the same class of approach as Trajectory Guard (arXiv:2601.00516,
Section 2.1), just far smaller.
"""

import random
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

ACTION_TYPES = ["list_resources", "read_file", "write_file", "read_credential", "connect_host"]
ACTION_IDX = {a: i for i, a in enumerate(ACTION_TYPES)}


def build_resource_vocab(rows):
    resources = set()
    for r in rows:
        for step in r["steps"]:
            resources.add(step["resource"])
    resources = sorted(resources)
    vocab = {r: i + 1 for i, r in enumerate(resources)}  # 0 reserved for padding/unknown
    return vocab


def encode_trajectory(steps, resource_vocab):
    action_ids = torch.tensor([ACTION_IDX[s["action"]] for s in steps], dtype=torch.long)
    resource_ids = torch.tensor(
        [resource_vocab.get(s["resource"], 0) for s in steps], dtype=torch.long
    )
    return action_ids, resource_ids


def collate(batch, resource_vocab):
    action_seqs, resource_seqs, labels, lengths = [], [], [], []
    for row in batch:
        a, r = encode_trajectory(row["steps"], resource_vocab)
        action_seqs.append(a)
        resource_seqs.append(r)
        labels.append(row["label"])
        lengths.append(len(a))
    action_pad = pad_sequence(action_seqs, batch_first=True, padding_value=0)
    resource_pad = pad_sequence(resource_seqs, batch_first=True, padding_value=0)
    labels = torch.tensor(labels, dtype=torch.float)
    lengths = torch.tensor(lengths, dtype=torch.long)
    return action_pad, resource_pad, labels, lengths


class TrajectoryLSTM(nn.Module):
    def __init__(self, n_resources, action_dim=8, resource_dim=16, hidden=48):
        super().__init__()
        self.action_emb = nn.Embedding(len(ACTION_TYPES), action_dim)
        self.resource_emb = nn.Embedding(n_resources + 1, resource_dim, padding_idx=0)
        self.lstm = nn.LSTM(action_dim + resource_dim, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, action_ids, resource_ids, lengths):
        x = torch.cat([self.action_emb(action_ids), self.resource_emb(resource_ids)], dim=-1)
        packed = nn.utils.rnn.pack_padded_sequence(
            x, lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        _, (h_n, _) = self.lstm(packed)
        logits = self.head(h_n[-1]).squeeze(-1)
        return logits


def train_model(train_rows, resource_vocab, epochs=8, batch_size=64, lr=1e-2, seed=0):
    torch.manual_seed(seed)
    model = TrajectoryLSTM(n_resources=len(resource_vocab))
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCEWithLogitsLoss()

    rng = random.Random(seed)
    for epoch in range(epochs):
        rows = train_rows[:]
        rng.shuffle(rows)
        total_loss = 0.0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            action_pad, resource_pad, labels, lengths = collate(batch, resource_vocab)
            opt.zero_grad()
            logits = model(action_pad, resource_pad, lengths)
            loss = loss_fn(logits, labels)
            loss.backward()
            opt.step()
            total_loss += loss.item() * len(batch)
        print(f"  epoch {epoch + 1}/{epochs}  loss={total_loss / len(rows):.4f}")
    return model


@torch.no_grad()
def predict(model, rows, resource_vocab, batch_size=256):
    model.eval()
    all_probs = []
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        action_pad, resource_pad, labels, lengths = collate(batch, resource_vocab)
        logits = model(action_pad, resource_pad, lengths)
        probs = torch.sigmoid(logits)
        all_probs.append(probs)
    return torch.cat(all_probs).numpy()
