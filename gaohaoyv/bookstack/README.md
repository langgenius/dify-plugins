# BookStack Plugin for Dify

BookStack Plugin for Dify connects Dify workflows and agents to self-hosted BookStack knowledge bases. The plugin provides BookStack foundation capabilities inside Dify; higher-level business composition, approval, and orchestration belong to your workflow or adapter layer. Today this plugin covers content lookup, search, export, non-destructive CRUD support, publishing, and related support flows.

## Current implemented features

Implemented Dify Tool plugin features:

- `validate_credentials`
- `search_pages`
- `search_content`
- `get_page`
- `export_page_markdown`
- `export_chapter_markdown`
- `export_book_markdown`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `find_books`
- `get_book`
- `create_book`
- `update_book`
- `list_chapters`
- `find_chapters`
- `get_chapter`
- `create_chapter`
- `update_chapter`
- `list_shelves`
- `find_shelves`
- `get_shelf`
- `create_shelf`
- `update_shelf`
- `list_pages`
- `find_pages`
- `list_tag_names`
- `list_tag_values`

Current tool-surface notes:

- No delete or archive tools are implemented.
- Tag support in this slice is discovery-only via `list_tag_names` and `list_tag_values`.
- `search_pages` is page-only search.
- `search_content` is broader global search with optional supported type filtering.
- `export_page_markdown` exports one page; `export_chapter_markdown` and `export_book_markdown` return both aggregate Markdown and a structured `pages` list for the exported hierarchy.
- `find_*` tools are structured name lookups; `list_*` tools support destination and content discovery.
- `list_books`, `list_chapters`, `list_pages`, and `list_shelves` support optional bounded `sort` and JSON `filters`; `list_pages` also keeps optional `book_id` and `chapter_id` filtering.
- `publish_page` is the writing/publishing path after you choose or confirm the destination with search, find, or list tools.
- Tool plugin remains the primary path; Datasource work is separate and still broader follow-up scope.

Current repository direction:

- Tool plugin first
- A separate Datasource package track exists in this repository, but it is not the primary Marketplace-facing path
- Broader Datasource work remains planned

## Setup

1. Build or obtain the plugin package from this repository.
2. Import it into a Dify environment that supports plugin installation.
3. Open the BookStack provider settings in Dify.
4. Enter your BookStack `base_url`, `token_id`, and `token_secret` in the Dify UI.

See the consolidated guides:

- [English usage guide](https://github.com/pandaria75/dify-plugin-bookstack/blob/main/docs/user/en/usage.md)
- [Chinese usage guide](https://github.com/pandaria75/dify-plugin-bookstack/blob/main/docs/user/zh/usage.md)

## Usage

Recommended first step:

1. Save provider credentials.
2. Run `validate_credentials`.
3. Confirm the provider can reach the target BookStack instance.
4. Use search, find, and list tools to inspect or choose destinations, then use export or non-delete create/update/publish tools as needed.

More information is covered in the usage guides above.

## Privacy

The plugin uses credentials provided by the user and connects only to the configured BookStack instance through the Dify runtime. Privacy and credential handling guidance is covered in the usage guides and [PRIVACY.md](PRIVACY.md).

## Repository and support

- Repository: <https://github.com/pandaria75/dify-plugin-bookstack>
- Issues / support: <https://github.com/pandaria75/dify-plugin-bookstack/issues>
- Architecture intent: [docs/target/architecture-intent.md](https://github.com/pandaria75/dify-plugin-bookstack/blob/main/docs/target/architecture-intent.md)

## License

MIT. See [LICENSE](LICENSE).
