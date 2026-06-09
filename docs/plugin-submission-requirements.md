# Plugin Submission Requirements

These requirements keep Marketplace submissions reviewable and safe. They apply to every new plugin and version update submitted to this repository.

## Package contents

A `.difypkg` must contain only files required for the plugin to run in Dify.

Do not include:

- Secrets or local credentials, including `.env` files, access tokens, API keys, private keys, certificates with private material, or cloud credentials.
- Development state, including `.git/`, virtual environments, dependency caches, build caches, test caches, `__pycache__/`, `.ruff_cache/`, logs, local settings, or IDE files.
- OS-generated files, including `.DS_Store` and thumbnail databases.
- Executables or bundled binaries, unless they are essential to the plugin and clearly explained in the PR.

## Metadata and documentation

Every submission must include:

- A valid `manifest.yaml` with accurate author, name, version, plugin type, runner, icon, and privacy fields.
- A README with setup steps, usage instructions, required APIs or credentials, connection requirements, and a link to the source repository.
- A `PRIVACY.md` file or hosted privacy policy that explains what user data is collected, stored, logged, or sent to third parties. If no user data is collected, say so explicitly.
- Primary user-facing text in English. Additional translations are welcome.

## Dependencies

Keep dependencies minimal and explain unusual runtime requirements. Python plugins should avoid unbounded or unnecessary dependencies, direct URL installs, and git-based package installs unless the PR explains why they are required.

## Risk classification

Select one risk level in the PR template:

- Low risk: The plugin only calls fixed, documented third-party HTTPS APIs and does not execute user-controlled code, commands, SQL, file operations, browser automation, or arbitrary network requests.
- Medium risk: The plugin processes uploaded files or user-provided URLs, performs write actions in a third-party service, sends user content to external services, or handles personal data that is not highly sensitive.
- High risk: The plugin can execute commands or code, run SQL, access databases, use SSH/SFTP, operate on filesystems, automate browsers, proxy or crawl arbitrary URLs, bundle executables, or handle health, financial, biometric, children, authentication, location, or other sensitive personal data.

When more than one level seems possible, choose the higher risk level.

## Version updates

Version update PRs should normally add only the new `.difypkg` file. The plugin version in `manifest.yaml` must be incremented and must not already exist on the Dify Marketplace.

If the update has breaking changes, document them in the plugin README and summarize them in the PR.

## Sensitive capabilities

Plugins with sensitive capabilities receive extra review. Disclose these capabilities in the PR template:

- Command execution, code execution, shell access, or sandbox control.
- SQL execution, database write access, SSH, SFTP, filesystem operations, or browser automation.
- Arbitrary URL fetching, proxying, crawling, webhook forwarding, or user-controlled network destinations.
- Processing health, financial, biometric, children, location, authentication, or other sensitive personal data.

Sensitive plugins should constrain user input, set request timeouts, avoid leaking credentials in errors or logs, and document the security boundary clearly.
