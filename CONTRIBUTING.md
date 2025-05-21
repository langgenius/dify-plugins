# Contributing to Dify Plugins

First off, thank you for considering contributing to Dify Plugins! Your help is essential for making this a vibrant and useful collection for the Dify community.

This document provides guidelines for contributing to this repository. Please read it carefully to ensure a smooth contribution process.

## Code of Conduct

All contributors are expected to adhere to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please make sure you are familiar with its terms. Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at [security@dify.ai](mailto:security@dify.ai).

## Getting Started

Before you begin:
- Ensure you have a GitHub account.
- Familiarize yourself with the Dify plugin development process. Refer to the [Plugin Docs](https://docs.dify.ai/plugins/quick-start/develop-plugins) and the main [README.md](README.md) of this repository for an overview.

## Plugin Development Best Practices

When developing your plugin, please consider the following:

- **Versioning:** Clearly version your plugin (e.g., `my-plugin-0.0.1.difypkg`). Follow semantic versioning (SemVer) if possible. The Dify Marketplace relies on versioning to manage updates.
- **Documentation:**
    - Include a `README.md` within your plugin's directory. This README should explain:
        - What your plugin does.
        - How to configure it.
        - Any dependencies or prerequisites.
        - Your contact information or a link to your plugin's repository.
    - Ensure your plugin's manifest file (`*.difypkg`'s internal manifest) is complete and accurate, including the path to your plugin's privacy policy.
- **Testing:** Test your plugin thoroughly in a Dify environment to ensure it functions as expected. While this repository doesn't currently enforce automated tests for plugins, well-tested plugins are more likely to be approved and used.
- **Privacy:** If your plugin handles user data, you must provide a clear privacy policy. Link to this policy in your plugin's manifest file as described in the main [README.md](README.md).
- **Clarity:** Ensure your plugin's purpose and functionality are clear. Good descriptions and documentation will help users understand and use your plugin.

## Submission Process

The process for submitting a plugin is outlined in the main [README.md](README.md#publishing-to-dify-marketplace) and summarized here:

1.  **Fork** this repository (`langgenius/dify-plugins`).
2.  **Create a directory** for your plugin. This should be structured as `your_organization_or_username/your_plugin_name/`. For example, if your GitHub username is `octocat` and your plugin is `super-widget`, the path would be `octocat/super-widget/`.
3.  **Add your plugin files**: Place your packaged plugin (`.difypkg` file) and any associated source code or documentation (like a specific `README.md` for your plugin) into this directory.
4.  **Submit a Pull Request (PR)** to the `main` branch of the `langgenius/dify-plugins` repository.
    - Ensure your PR title is clear and descriptive (e.g., "Add SuperWidget plugin by Octocat").
    - Follow the PR template provided.
    - Adhere to the "Tips for contributing" mentioned in the main README:
        - Only **one plugin change** (new plugin or update to an existing one) per PR.
        - **Check the plugin version** carefully. The same version of a plugin cannot be merged if it already exists in the target directory.

## Getting Help

If you have questions about contributing, plugin development, or the submission process:
- Join the [Dify Discord server](https://discord.gg/FngNHpbcY7) and ask in the relevant channels.
- You can open an issue on this GitHub repository for discussions related to the contribution process or the marketplace itself. For plugin-specific issues, please refer to the plugin developer's contact information or repository.

Thank you for your contribution!
