# Text Fitter

A Dify tool plugin that ensures text fits within LLM context window limits
via intelligent extractive summarization. Supports **Chinese**, **Japanese**,
and **English** text.

## Why

Locally deployed or resource-constrained LLM instances often have a smaller
effective context window than the model's official specification — due to
hardware limits (GPU VRAM), concurrency requirements, or serving parameters
like `--max-model-len`. When input text exceeds the window, the LLM fails
with a context-length error.

This plugin acts as a pre-processing guard: it measures the input, and if it
exceeds a user-configured threshold, trims it by extracting only the most
informative sentences — before the text ever reaches the LLM.

## Installation

### From Dify Marketplace

1. In your Dify workspace, go to **Plugins** → **Marketplace**.
2. Search for **Text Fitter** and click **Install**.
3. The plugin will appear in your workflow tools as **Smart Trim**.

### Manual Installation

1. Download the `.difypkg` file from the GitHub releases page.
2. In Dify, go to **Plugins** → **Install Plugin** → **Upload Package**.
3. Upload the `.difypkg` file.

## Usage

1. In a workflow, add the **Smart Trim** node from the tool palette.
2. Wire `text` to your upstream content source (document parser, HTTP input, etc.).
3. Set `max_chars` to a value below your LLM's actual context limit.
4. Connect the node's text output to your downstream LLM node.
5. Optionally use `was_trimmed` to branch logic (e.g., log a warning when trimming occurred).

### Choosing max_chars

Note that `max_chars` counts **characters**, while model context limits
(`--max-model-len`) are measured in **tokens** — they are different units.
The approximate tokens consumed per character varies by language:

| Language | Tokens per character |
|---|---|
| English | ~0.25 (1 token ≈ 4 characters) |
| Chinese | ~1.4 |
| Japanese | ~1.2 |

A conservative starting point: set `max_chars` to ~80% of your model's token
limit. For example, with `--max-model-len 25000`:

- English text: try `max_chars: 80000` (100K chars ≈ 25K tokens).
- Chinese text: try `max_chars: 14000` (14K chars ≈ 20K tokens).
- Japanese text: try `max_chars: 17000` (17K chars ≈ 20K tokens).

Adjust based on observed behavior with your specific workload.

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | Yes | — | Input text to process |
| `max_chars` | number | Yes | 30000 | Character threshold; exceeding triggers trimming |
| `method` | select | No | `mmr` | Sentence selection: `"mmr"` (diverse, O(n²)) or `"greedy"` (fast, O(n log n)) |
| `mmr_lambda` | select | No | `0.7` | MMR λ (relevance weight). 11 options from `0.0` (Pure Diversity) to `1.0` (Pure Relevance). Ignored when `method` is `"greedy"` |

## Outputs

| Output | Type | Description |
|---|---|---|
| `text` | string | The processed text (original or trimmed) |
| `original_char_count` | number | Character count of the original input text |
| `processed_char_count` | number | Character count of the output text |
| `was_trimmed` | boolean | Whether the text was trimmed (true if original exceeded max_chars) |

## Language Support

The tool automatically handles **Chinese**, **Japanese**, and **English** text
without any language selector parameter. The tokenizer recognizes:

- **CJK Unified Ideographs** (U+4E00–U+9FFF) — Chinese and Japanese kanji
- **CJK Extension A** (U+3400–U+4DBF) — rare and historical characters
- **Hiragana** (U+3040–U+309F) — Japanese syllabary
- **Katakana** (U+30A0–U+30FF) — Japanese syllabary
- **Latin words** — extracted via word-boundary regex (`[a-zA-Z0-9]+`)

The sentence splitter handles CJK fullwidth punctuation (`。！？`),
Japanese closing brackets (`」』`), English halfwidth punctuation (`. ! ?`),
ellipsis (`...` / `……`), and common abbreviations (`Mr.`, `Dr.`, etc.).

## Algorithm

This plugin uses **extractive summarization** — no external NLP dependencies,
pure Python standard library.

### 1. Sentence Segmentation

Regex-based sentence splitting aware of CJK, Japanese, and English
punctuation conventions, with abbreviation protection.

### 2. Sentence Scoring

```
score = 0.3 × position + 0.5 × keyword_density + 0.2 × length
```

- **Position Score (0.3):** Intro and conclusion sentences weighted higher.
- **Keyword Density (0.5):** Normalized TF-IDF analysis, penalizing
  function words (的/the/は) that appear across documents.
- **Length Score (0.2):** Penalizes very short (< 10 chars, likely filler)
  and very long (> 200 chars, likely verbose) sentences.

### 3. Sentence Selection

Two strategies via the `method` parameter:

- **Greedy** (`method = "greedy"`): Top-score selection, O(n log n). Fast.
- **MMR** (`method = "mmr"`): Maximal Marginal Relevance balancing
  relevance with diversity: `MMR = λ × relevance + (1 - λ) × diversity`.
  O(n²), but produces less redundant summaries.

### 4. Positional Reordering

Selected sentences are re-sorted by original order for coherent output.

### 5. Boundary-Aware Fallback

If no sentence fits within `max_chars`, falls back to sentence-boundary
truncation, then whitespace, then hard truncation with ellipsis.

### Complexity

| Metric | Value |
|---|---|
| Time | O(n²) for MMR, O(n log n) for greedy (n = number of sentences) |
| Space | O(n) |
| Dependencies | None (Python stdlib only) |

## Privacy

This plugin processes all text locally. No data is transmitted to external
servers, APIs, or third-party services. See [PRIVACY.md](PRIVACY.md) for details.

## License

[MIT](LICENSE)
