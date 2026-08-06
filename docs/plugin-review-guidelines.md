# Plugin Review Guidelines

Use this checklist when reviewing a plugin package before merge. It is intentionally lightweight and focused on issues that are hard to fix after publication.

## Quick package inspection

Unpack the submitted `.difypkg` and check the file list before reading the code. Reject or request changes if the package includes secrets, `.env`, `.git`, virtual environments, caches, logs, local settings, IDE files, OS-generated files, or unexplained executables.

Confirm that the package has the expected runtime files, including `manifest.yaml`, README, privacy policy, provider or model definitions, tool/model/endpoint files, assets, and dependency files.

## Documentation review

Check that the README tells users how to configure and use the plugin, lists required credentials or APIs, explains connection requirements, and links to the source repository.

Check that the privacy policy matches the plugin behavior and the third-party services it calls. If the plugin handles sensitive data, the policy should name the data types and explain where the data goes.

## Security review

Confirm that the PR risk level matches the plugin behavior. When a plugin fits multiple levels, review it at the higher level.

Look for high-risk capabilities first: command execution, code execution, SQL, SSH/SFTP, file operations, browser automation, arbitrary URL fetching, proxying, and webhook forwarding.

For high-risk plugins, verify that user inputs are constrained, network requests have timeouts, credentials are not returned in errors, and dangerous behavior is documented in the PR.

## Dependency review

Check `requirements.txt` or equivalent dependency files for unnecessary packages, direct URL installs, git-based installs, and very broad dependency ranges. Ask for justification when the dependency footprint is larger than the plugin behavior requires.

## Merge expectation

Only approve when the package content, documentation, privacy declaration, dependencies, and sensitive-capability disclosure are consistent with the plugin behavior.
