# CI scripts

Two directories, one rule each:

| Path | Owned by | Used by |
| ---- | -------- | ------- |
| `governance/` | this repository | `governance.yaml` (packaging rules, manifest tags, near-duplicates) |
| `toolkit/` | [dify-marketplace-toolkit](https://github.com/langgenius/dify-marketplace-toolkit) | `pre-check-plugin.yaml`, `upload-merged-plugin.yaml` |

`toolkit/` is **not committed**. CI clones it at run time into
`.github/scripts/toolkit` (the path is in `.gitignore`), so every run validates
against the toolkit's current `main`. To work on it locally:

```bash
gh repo clone langgenius/dify-marketplace-toolkit -- .github/scripts/toolkit
gh release download -R langgenius/dify-plugin-daemon \
  --pattern "dify-plugin-linux-amd64" --dir .github/scripts/toolkit
```

Keep in mind before renaming or moving anything under `toolkit/`: the plugin
repositories' workflows call these paths directly, and the toolkit's own CI
guards them.

Local commands:

```bash
# package-level checks for one .difypkg (what the PR pre-check runs)
python3 .github/scripts/toolkit/validator/validate-difypkg.py path/to/plugin.difypkg \
  --output-dir /tmp/validation

# governance checks for the files a PR changed
gh api --paginate "repos/OWNER/REPO/pulls/NUMBER/files" --slurp \
  | jq 'add | map({filename: .filename, status: .status})' > /tmp/changed_files.json
python3 .github/scripts/governance/check_packaging_rules.py --changed-files /tmp/changed_files.json
```
