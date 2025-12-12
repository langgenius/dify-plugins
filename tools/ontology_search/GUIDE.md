# Ontology Search Plugin Guide

This guide is tailored for your Ontology Search tool plugin.

## Overview
- Type: Tool plugin
- Manifest: `ontology_search/manifest.yaml`
- Provider: `ontology_search/provider/ontology_provider.yaml`
- Tools: `ontology_search/tools/*.yaml`
- Python source: `ontology_search/provider/ontology_provider.py` (entry class `OntologyProvider`)

## Quick Setup
- Python 3.11+
- Install deps:
```bash
pip install -r ontology_search/requirements.txt
```

## Manifest (Simplified)
`ontology_search/manifest.yaml` should include:
```yaml
name: ontology_search
author: 编程小萌新
version: "0.0.1"
type: tool
description:
  zh_Hans: 本体查询插件
  en_US: Ontology Search Plugin
providers:
  - provider/ontology_provider.yaml
```

## Provider YAML
`ontology_search/provider/ontology_provider.yaml`:
```yaml
identity:
  name: ontology_provider
  author: ontology_team
  label:
    zh_Hans: 本体查询 Provider
  description:
    zh_Hans: 提供本体基础查询能力

tools:
  - ../tools/query_by_keyword.yaml
  - ../tools/query_by_id.yaml
  - ../tools/query_advanced.yaml

extra:
  python:
    source: provider/ontology_provider.py
    entry: OntologyProvider
```

## Python Entry (Provider)
`ontology_search/provider/ontology_provider.py` must define class `OntologyProvider` with methods matching tool names:
- `query_by_keyword(params: dict)`
- `query_by_id(params: dict)`
- `query_advanced(params: dict)`

Each method should read fields according to the tool `input_schema` and return `ToolInvokeMessage` JSON via `create_json_message`.

Example imports using your implementation in `src/ontology.py`:
```python
from src.ontology import (
  get_ontology_list,
  get_object_types,
  get_ontology_object_details,
)
```

## Tools Definition
Place files under `ontology_search/tools/` and ensure names match the provider methods:
- `query_by_keyword.yaml` → calls `OntologyProvider.query_by_keyword`
- `query_by_id.yaml` → calls `OntologyProvider.query_by_id`
- `query_advanced.yaml` → calls `OntologyProvider.query_advanced`

Key tips:
- Use correct relative paths in provider YAML (`../tools/...` from provider dir)
- Ensure required fields in `input_schema` match what your provider code reads from `params`

## Package & Upload
Zip on macOS:
```bash
cd ontology_search
zip -r ontology_search.difypkg . --exclude="*.DS_Store"
```
Upload the `.difypkg` to Dify Marketplace or your instance.

## Troubleshooting
- Error: `read tools: is a directory`
  - Cause: provider YAML tools path points to a directory instead of specific YAML files
  - Fix: use `../tools/query_by_keyword.yaml` etc.
- Error: cannot load python source
  - Ensure `extra.python.source` exists and `entry` class name matches implementation
  - Verify imports (e.g., `from src.ontology import ...`) exist under `ontology_search/src/ontology.py`

## Local Testing (Optional)
Add a minimal test harness under `ontology_search/src/test.py` to call your Python functions directly for quick validation before packaging.