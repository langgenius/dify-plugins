## Ontology Search Plugin

- Author: asiainfo
- Version: 0.0.1
- Type: tool

### Overview
Ontology Search is a Dify tool plugin providing basic ontology queries:
- Query ontology by keyword and status
- Query object types by ontology ID
- Advanced object query with fields, filters, sorting, pagination

### Structure
- Manifest: `ontology_search/manifest.yaml`
- Provider: `ontology_search/provider/ontology_provider.yaml`
- Tools: `ontology_search/tools/*.yaml`
- Python entry: `ontology_search/provider/ontology_provider.py` (class `OntologyProvider`)

### Setup
```bash
pip install -r ontology_search/requirements.txt
```

### Usage (Dify)
1. Import manifest `ontology_search/manifest.yaml` into Dify.
2. Ensure provider YAML points to tools and Python entry:
	- `tools: ../tools/query_by_keyword.yaml`, `../tools/query_by_id.yaml`, `../tools/query_advanced.yaml`
	- `extra.python.source: provider/ontology_provider.py`
	- `extra.python.entry: OntologyProvider`
3. Configure tool parameters (e.g., `api_key`, `keyword`, `ontology_id`).

### Packaging
```bash
cd ontology_search
zip -r ontology_search.difypkg . --exclude="*.DS_Store"
```

### Troubleshooting
- "read tools: is a directory": fix provider tool paths to specific YAML files (use `../tools/...`).
- Python source load error: ensure `provider/ontology_provider.py` exists and defines `OntologyProvider` with methods `query_by_keyword`, `query_by_id`, `query_advanced`.




