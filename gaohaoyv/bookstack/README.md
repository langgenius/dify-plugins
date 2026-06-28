# BookStack Plugin for Dify

BookStack Plugin for Dify connects Dify workflows and agents to self-hosted BookStack knowledge bases. Dify handles AI content generation, approval, and orchestration; BookStack stores the published documentation as a source of truth. This plugin bridges the two, enabling automated document publishing, reading, and synchronization from within Dify AI applications.

## Current implemented features

Implemented Dify Tool plugin features:

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`
- `list_shelves`
- `list_pages`

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

- [English usage guide](docs/user/en/usage.md)
- [Chinese usage guide](docs/user/zh/usage.md)

## Usage

Recommended first step:

1. Save provider credentials.
2. Run `validate_credentials`.
3. Confirm the provider can reach the target BookStack instance.
4. Use the implemented page and listing tools as needed, and refer to the linked user docs for details.

More information is covered in the usage guides above.

## Privacy

The plugin uses credentials provided by the user and connects only to the configured BookStack instance through the Dify runtime. Privacy and credential handling guidance is covered in the usage guides and [PRIVACY.md](PRIVACY.md).

## Repository and support

- Repository: <https://github.com/pandaria75/dify-plugin-bookstack>
- Issues / support: <https://github.com/pandaria75/dify-plugin-bookstack/issues>
- Architecture intent: [docs/target/architecture-intent.md](docs/target/architecture-intent.md)

## License

MIT. See [LICENSE](LICENSE).
