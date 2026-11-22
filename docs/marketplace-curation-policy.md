# Marketplace Curation Policy

This document states the quality bar for plugins published to the Dify Marketplace
from this repository, and how it is enforced. It complements
[plugin submission requirements](plugin-submission-requirements.md) and
[plugin review guidelines](plugin-review-guidelines.md).

Everything below is backed by a full audit of the marketplace supply: all 1,270
`.difypkg` files in this repository were unpacked and analysed (950 unique plugin
directories, 647 author directories). Where this policy and the submission
requirements overlap, this document is the more specific rule.

## Why this policy exists

The audit found that supply is growing fast (697 of the 1,270 packages were added
in 2026 alone) while metadata and de-duplication guardrails were missing:

| Signal | Measurement |
|---|---|
| Plugins without tags | 63.2% (803 of 1,270 packages) |
| Tag concentration | `utilities` (192) + `productivity` (186) = 80.9% of all tag assignments, co-occurring 83 times |
| Same-author near-duplicate families | 16 template-same-source families, e.g. acedatacloud (17 single-purpose wrappers, shared client module 98.6% identical), flashdata-dev (16 plugins from one template), investoday (11 data-category splits from one template) |
| Cross-author name collisions | 13 groups (volcengine_ai, zendesk, amap, qdrant, aippt, qiniu, ...) |
| Redundant old-version packages | 305 packages (24% of all packages, 186 authors) |
| Flattened layout (packages in the author root) | 153 packages in 121 directories |
| Directory name ≠ manifest author | 193 packages, 134 authors |
| Homogeneous OpenAI-compatible gateways | 107 unique plugins from 100 authors (11.3% of all unique plugins), only 14.1% of them tagged |
| `verified: true` | 7 packages from 6 authors |

The problem is structural, not incidental: authors write descriptions (688 of the
803 untagged plugins have a complete description) but were never given a tag
vocabulary to fill in, and nothing at pull-request time stopped one plugin from
being shipped seventeen times.

## 1. Tags are mandatory and come from a controlled vocabulary

Every `manifest.yaml` must declare a non-empty `tags` list, and every tag must be
one of the controlled values below. The check runs in CI on every changed
`.difypkg` / `manifest.yaml` and blocks the merge.

Existing tags (17): `agent`, `business`, `design`, `education`, `entertainment`,
`finance`, `image`, `news`, `other`, `productivity`, `rag`, `search`, `social`,
`travel`, `utilities`, `videos`, `weather`

New tags accepted from now on (8): `llm`, `model_provider`, `audio`, `document`,
`devtools`, `database`, `security`, `translation`

Guidance:

- Pick 1–3 tags that describe what the plugin *does*, not which vendor it calls.
  A model gateway is `llm` (or `model_provider` when it exposes one vendor's
  models), not `utilities`.
- `utilities` and `productivity` are the last resort. If a more specific tag
  applies, use it. In the audit, `utilities` matched the plugin's actual function
  in only 14.1% of high-confidence samples.
- Need a tag that is not in the list? Open a discussion issue first; the
  vocabulary is extended deliberately so that marketplace filtering stays useful.

## 2. One plugin per directory, one version per directory

- Every `.difypkg` lives in its own plugin directory: `<author>/<plugin-name>/<plugin>-<version>.difypkg`.
  Packages must not be flattened into the author root directory.
- A plugin directory must not contain packages of a different plugin.
- When a directory holds several versions of the same plugin, all versions must
  declare the same tags (contradictory tags made the same plugin appear in the
  marketplace both tagged and untagged in 14 audited directories).
- Keep only the current version in the repository; publish older versions as
  GitHub Releases. 305 redundant version packages (24% of all packages) are the
  reason this is enforced for new changes.

These rules are enforced in CI for the files a pull request changes; the existing
backlog is cleaned up separately (see section 7).

## 3. No same-author near-duplicate plugins

One author must not publish several plugins that do the same thing for different
endpoints or categories. Near-duplicates are detected in CI with three channels,
and the findings are attached to the pull request:

1. **Name collision** — normalized plugin names (lowercase, alphanumeric,
   generic suffixes such as `plugin`/`tool`/`dify`/`integration` stripped) that
   collide within the same author fail the check; collisions across authors are
   reported as warnings.
2. **Text similarity** — normalized name, tags or description similarity ≥ 0.65
   (tags count when tag Jaccard ≥ 0.65 and the names are also similar) is
   reported as a warning.
3. **Source skeleton similarity** — after removing comments, string literals and
   identifiers from every source file, the plugins' normalized line sets are
   compared; Jaccard ≥ 0.85 is reported as a warning.

Warnings do not block a merge by themselves, but the author is expected to
explain the difference in the pull request. If the plugin is a reskin or a
category split of an existing plugin, it will not be merged:

- **Consolidate** several near-identical single-purpose plugins into one plugin
  with multiple tools (one multi-model gateway instead of 17 per-model wrappers;
  one data suite instead of 11 per-category splits).
- **Deadline mechanism**: when reviewers flag a same-author near-duplicate
  family, the author gets **14 days** to consolidate. After the deadline the
  older packages are deprecated in the marketplace and only the consolidated
  plugin stays listed. Refusing to consolidate leads to removal of the newer
  duplicates.

## 4. OpenAI-compatible gateways must be differentiated

107 unique plugins from 100 authors are "one OpenAI-compatible endpoint plus one
API key" wrappers, the second-largest supply category in the marketplace and the
least differentiated (14.1% tagged). A new gateway plugin is only accepted when
it adds real capability beyond proxying, for example:

- **Routing** — model selection, fallback chains, cost/latency-aware routing.
- **Metering** — per-key or per-model usage accounting and limits.
- **Resilience** — retries, circuit breaking, multi-provider failover, health checks.
- **Evaluation** — built-in evals, A/B comparison, quality scoring.
- **Caching** — semantic or exact response caching, prompt caching.
- **Governance** — PII redaction, content filtering, audit logging, budget caps.

A gateway that only forwards chat completions to a single endpoint will be
guided to merge into the existing gateway for that provider (or into a
community-maintained generic gateway). Existing homogeneous gateways are being
graded in a follow-up pass.

## 5. Packaging and repository hygiene

The CI packaging check enforces, for every package a pull request changes:

- one plugin per directory (different plugins in one directory fail);
- no `.difypkg` flattened into the author root directory (fails);
- consistent tags across the versions of one plugin (fails);
- a warning when a directory keeps several versions, pointing to GitHub Releases.

The author directory name should match the `author` field in `manifest.yaml`
(193 packages, 134 authors, currently do not; 4 authors ship under two
capitalization variants). New submissions must be consistent; existing
mismatches are fixed in the cleanup pass.

## 6. Verified plugins

`verified: true` is a trust signal and currently applies to only 7 packages from
6 authors, so it carries no weight in search and recommendations. Expectation:

- Verified is granted to plugins with a maintained source repository, complete
  metadata (labels in at least `en_US` and `zh_Hans`, a `PRIVACY.md`, a README
  with setup and credential requirements), a clean security review, and a
  responsive maintainer.
- Large-volume authors are not automatically verified; volume without
  differentiation (see section 4) works against verification.
- Maintainers can request verification in a pull request once the criteria above
  are met; the marketplace team confirms and flips the flag.

## 7. Existing backlog

The rules above apply to new and updated packages from the day the corresponding
CI checks are merged. The backlog (803 untagged packages, 305 redundant version
packages, 153 flattened packages, 193 author/directory mismatches, 16
near-duplicate families, 107 homogeneous gateways) is handled as a separate
cleanup programme with author-facing issues, not by retro-active CI failures.

## Enforcement summary

| Rule | CI check | Effect |
|---|---|---|
| Tags required, controlled vocabulary | Governance - Manifest Tags | blocks merge |
| Same-author name collision | Governance - Near-Duplicate Detection | blocks merge |
| Text / source-skeleton similarity | Governance - Near-Duplicate Detection | warning in the check summary |
| One plugin per directory, no flat packages, consistent version tags | Governance - Packaging Rules | blocks merge (warns on multi-version directories) |
