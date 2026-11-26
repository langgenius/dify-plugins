# Marketplace Overview pre-review prototype

This standalone Python 3.10+ example shows how a reviewer could flag listings with a clearly insufficient Overview. It reads UTF-8 JSON Lines (one submission per line) and emits a decision per line. It does not send requests, post comments, or update any Marketplace review state.

## Run the example

    python overview_guard.py examples.jsonl --min-visible 12 --review-below 20
    python overview_guard.py examples.jsonl --min-visible 12 --review-below 20 --enforce
    python -m unittest -v

The sample input is fictional. The 12/20 thresholds are demonstration values, not Marketplace policy. For production, measure historical outcomes by language, publish approved thresholds, and start in dry-run mode.

## Input and decisions

Each record has an id and an overview. Explicit null denotes an empty Overview; a missing or invalid field is routed to review rather than treated as empty. Optional plugin_name detects a title pasted as the entire Overview. The engine counts Unicode letters and numbers, including CJK characters. Images, URL destinations, comments, and punctuation do not count. It is not a Markdown renderer: complex or ambiguous markup goes to manual review.

By default, deterministic failures produce decision=review and proposed_decision=reject. With --enforce, they produce decision=reject. Passing only means this check did not flag the Overview, not that the plugin passed review. Each result records the policy version, active thresholds, reason, and character count where available.

Use an approved Marketplace integration to consume the decision, if one is available. Keep an audit record and reviewer override, and never treat file parsing or input transport failures as a basis for returning a submission.
