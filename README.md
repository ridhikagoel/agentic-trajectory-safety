# Agentic trajectory safety synthetic experiment

This directory retains the implementation and saved artifacts used for Section 8 of *From Rules to Sequences*. It uses synthetic data only; no proprietary data is included.

## Environment

- Python 3.14.3
- macOS 26.0.1 on arm64 for the verified rerun
- Exact Python dependencies are in `requirements.txt`.
- CPU execution is supported and was used for the verified rerun.

## Reproduce the saved datasets and five-seed study

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generate_dataset.py
python generate_generalization_splits.py
python evaluate.py
python run_five_seed.py
python generate_manifest.py
python -m unittest discover -s tests -v
```

On the verified machine, the five-seed study used approximately 51 seconds of measured detector runtime and completed in roughly one minute after dependencies were installed. The commands regenerate the JSONL datasets, credential scope, pair metadata, single-seed compatibility output, five-seed CSV artifacts, and file manifest.

Important: regeneration overwrites the saved generated datasets. Preserve an immutable copy before rerunning if exact file-level comparison is required.

## Recorded design

- Main generator seed: 42
- Main train/test split seed: 7
- Generalization split seed: 99
- Main dataset: 10,000 trajectories, balanced 5,000 unsafe / 5,000 benign
- Main split: 8,000 train / 2,000 test
- Generalization data: 8,000 train, 2,000 in-distribution test, 2,000 held-out-pair test
- Unsafe-pair split: 126 training pairs / 30 held-out pairs
- Trajectory length: 8–20 actions
- Credential-to-connect window: 6 actions
- Resources: 6 credentials, 29 hosts, 39 file identifiers
- Benign subtype probabilities: in-scope decoy 0.35; two credential reads 0.20; two connects 0.20; out-of-window connection 0.25
- Logistic regression: scikit-learn `LogisticRegression`, `C=1.0`, `max_iter=2000`; action unigrams, action bigrams, trajectory counts, near-pattern indicator, and sparse credential/host co-occurrence indicators
- LSTM: action embedding 8, resource embedding 16, hidden size 48, one layer, Adam, learning rate 0.01, batch size 64, 8 epochs, threshold 0.5; no early stopping or model selection
- Confidence intervals: Wilson 95% intervals implemented in `evaluate.py`
- Fixed-data training seeds: 7, 19, 42, 73, and 101
- Exact McNemar analysis: separate two-sided exact paired test for each training seed; the results are not pooled as if repeated predictions were independent examples

The credential-to-host policy is saved in `data/cred_scope.json`. Exact generated train/test examples and pair assignments are saved under `data/`.

## Detectors

1. Stateless per-action allowlist (`baseline.py`)
2. Stateful deterministic credential-scope rule (`stateful_rule_baseline.py`)
3. Logistic regression (`features.py` and `evaluate.py`)
4. LSTM (`lstm_model.py` and `evaluate.py`)

The stateful rule was added and measured on August 25, 2026. Across five training seeds, random-split recall was 0.000 for the stateless baseline and 1.000 for the stateful rule, logistic regression, and LSTM. On held-out credential/host pairs, recall was 1.000 for the stateful rule and logistic regression; LSTM recall was 0.877 ± 0.062 (sample SD; range 0.789–0.954). Detailed outputs are in `results/five_seed_fixed_data/`.

## Limitations and release status

The robustness study varies training initialization and shuffle seed while holding the saved generated data, split, and held-out pairs fixed. It does not measure sensitivity to independently regenerated datasets. The dataset is deliberately synthetic, balanced, small, and generated from an explicit invariant. These results do not estimate production behavior.

The versioned public release is hosted on GitHub. This project does not use a separate DOI archive; cite the exact GitHub release and version recorded in `CITATION.cff`.

Code is licensed under MIT (`LICENSE`). Synthetic data is licensed under CC BY 4.0 (`DATA_LICENSE.md`).
