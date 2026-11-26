# Marketplace Overview pre-review prototype

This standalone Python 3.10+ example shows how a reviewer could flag listings with a clearly insufficient Overview. It reads UTF-8 JSON Lines (one submission per line) and emits a decision per line. It does not send requests, post comments, or update any Marketplace review state.

## Run the example

    python overview_guard.py examples.jsonl
    python overview_guard.py examples.jsonl --enforce
    python overview_guard.py examples.jsonl --review-below 20 --enforce
    python -m unittest -v

The sample input is fictional. By default, a short description such as “按城市查天气” (look up the weather by city) passes this check. An empty Overview, a recognized placeholder such as `TBD`, or an Overview containing only the plugin name is flagged.

Use `--review-below 20` to send other descriptions with fewer than 20 letters or numbers to manual review, including in enforce mode. To test a separate rejection cutoff, add an explicit `--min-visible`, for example `--min-visible 12 --review-below 20`. Both numbers are illustrative. Evaluate outcomes by language before choosing a Marketplace policy.

## Input and decisions

Each record has an id and an overview. Explicit null denotes an empty Overview; a missing or invalid field is routed to review rather than treated as empty. Optional plugin_name detects a title pasted as the entire Overview. The engine counts Unicode letters and numbers, including CJK characters. Images, URL destinations, comments, and punctuation do not count. It is not a Markdown renderer: complex or ambiguous markup goes to manual review.

A bare URL can run into the next sentence in languages that omit spaces. For example, `https://example.test。按城市查天气` goes to manual review. With an explicit boundary such as `<https://example.test>按城市查天气`, the checker counts the six characters after the URL.

By default, deterministic failures produce decision=review and proposed_decision=reject. With --enforce, they produce decision=reject. Passing only means this check did not flag the Overview, not that the plugin passed review. Each result records the policy version, active thresholds, reason, and character count where available.

Use an approved Marketplace integration to consume the decision, if one is available. Keep an audit record and reviewer override, and never treat file parsing or input transport failures as a basis for returning a submission.
