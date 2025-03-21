![Dify Logo](.assets/bar.jpeg)

<p align="center">
  <a href="https://cloud.dify.ai">Dify Cloud</a> ·
  <a href="https://docs.dify.ai/getting-started/install-self-hosted">Self-hosting</a> ·
  <a href="https://docs.dify.ai">Documentation</a> ·
  <a href="https://udify.app/chat/22L1zSxg6yW1cWQg">Enterprise inquiry</a>
</p>

<p align="center">
    <a href="https://dify.ai" target="_blank">
        <img alt="Static Badge" src="https://img.shields.io/badge/Product-F04438"></a>
    <a href="https://dify.ai/pricing" target="_blank">
        <img alt="Static Badge" src="https://img.shields.io/badge/free-pricing?logo=free&color=%20%23155EEF&label=pricing&labelColor=%20%23528bff"></a>
    <a href="https://discord.gg/FngNHpbcY7" target="_blank">
        <img src="https://img.shields.io/discord/1082486657678311454?logo=discord&labelColor=%20%235462eb&logoColor=%20%23f5f5f5&color=%20%235462eb"
            alt="chat on Discord"></a>
    <a href="https://reddit.com/r/difyai" target="_blank">  
        <img src="https://img.shields.io/reddit/subreddit-subscribers/difyai?style=plastic&logo=reddit&label=r%2Fdifyai&labelColor=white"
            alt="join Reddit"></a>
    <a href="https://twitter.com/intent/follow?screen_name=dify_ai" target="_blank">
        <img src="https://img.shields.io/twitter/follow/dify_ai?logo=X&color=%20%23f5f5f5"
            alt="follow on X(Twitter)"></a>
    <a href="https://www.linkedin.com/company/langgenius/" target="_blank">
        <img src="https://custom-icon-badges.demolab.com/badge/LinkedIn-0A66C2?logo=linkedin-white&logoColor=fff"
            alt="follow on LinkedIn"></a>
    <a href="https://hub.docker.com/u/langgenius" target="_blank">
        <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/langgenius/dify-web?labelColor=%20%23FDB062&color=%20%23f79009"></a>
    <a href="https://github.com/langgenius/dify/graphs/commit-activity" target="_blank">
        <img alt="Commits last month" src="https://img.shields.io/github/commit-activity/m/langgenius/dify?labelColor=%20%2332b583&color=%20%2312b76a"></a>
    <a href="https://github.com/langgenius/dify/" target="_blank">
        <img alt="Issues closed" src="https://img.shields.io/github/issues-search?query=repo%3Alanggenius%2Fdify%20is%3Aclosed&label=issues%20closed&labelColor=%20%237d89b0&color=%20%235d6b98"></a>
    <a href="https://github.com/langgenius/dify/discussions/" target="_blank">
        <img alt="Discussion posts" src="https://img.shields.io/github/discussions/langgenius/dify?labelColor=%20%239b8afb&color=%20%237a5af8"></a>
</p>

### Introducing Dify Plugins

[Dify](https://dify.ai/) is an open-source platform for developing LLM-powered AI applications, designed to help developers and businesses efficiently build, deploy, and manage AI-driven solutions. With Dify, users can easily create and test complex AI workflows, integrate a wide range of advanced models and tools, and optimize their performance in real-world applications. The platform offers an intuitive interface, supporting RAG (Retrieval-Augmented Generation) pipelines, intelligent agent capabilities, and robust model management, enabling developers to seamlessly transition from prototype to production.

[Dify Marketplace](https://marketplace.dify.ai/) is a vibrant center that allows developers, businesses, and AI enthusiasts to explore, share, and deploy plugins designed to enhance Dify Apps' capabilities. It serves as a platform where users can discover a wide range of models, tools, agent strategies, extensions, and bundles, all of which can be seamlessly integrated into their AI applications. By providing a collaborative space for both official and community-contributed plugins, the Dify Marketplace encourages innovation and resource sharing. 

### Plugin Development

#### Types of Plugin

##### Models

These plugins integrate various AI models (including mainstream LLM providers and custom model) to handle configuration and requests for LLM APIs. For more on creating a model plugin, take refer to [Quick Start: Model Plugin](https://docs.dify.ai/plugins/quick-start/develop-plugins/model-plugin).

##### Tools

Tools refer to third-party services that can be invoked by Chatflow, Workflow, or Agent-type applications. They provide a complete API implementation to enhance the capabilities of Dify applications. For example, developing a Google Search plugin, please refer to [Quick Start: Tool Plugin](https://docs.dify.ai/plugins/quick-start/develop-plugins/tool-plugin).

##### Agent Strategies

The Agent Strategy plugin defines the reasoning and decision-making logic within an Agent node, including tool selection, invocation, and result processing.

Agent strategy plugins define the internal reasoning and decision-making logic within agent nodes. They encompass the logic for tool selection, invocation, and handling of returned results by the LLM. For further development guidance, please refer to the [Quick Start: Agent Strategy Plugin](https://docs.dify.ai/plugins/quick-start/develop-plugins/agent-strategy-plugin).

##### Extensions

Lightweight plugins that only provide endpoint capabilities for simpler scenarios, enabling fast expansions via HTTP services. This approach is ideal for straightforward integrations requiring basic API invoking. For more details, refer to [Quick Start: Extension Plugin](https://docs.dify.ai/plugins/quick-start/develop-plugins/extension-plugin).

##### Bundles

A “plugin bundle” is a collection of multiple plugins. Bundles allow you to install a curated set of plugins all at once—no more adding them one by one. For more information on creating plugin bundles, see [Plugin Development: Bundle Plugin](https://docs.dify.ai/plugins/quick-start/develop-plugins/bundle).

#### Plugin Docs

Check the [Plugins documentation](https://docs.dify.ai/plugins/quick-start/develop-plugins) to learn how to develop and publish plugins.

### Publishing to Dify Marketplace

To publish your plugin on the Dify Marketplace, follow these steps:

#### Development
1. Develop and test your plugin according to the [Plugin Developer Guidelines](https://docs.dify.ai/plugins/publish-plugins/publish-to-dify-marketplace/plugin-developer-guidelines).

2. Write a [Plugin Privacy Policy](https://docs.dify.ai/plugins/publish-plugins/publish-to-dify-marketplace/plugin-privacy-protection-guidelines) for your plugin in line with Dify’s privacy policy requirements. In your plugin’s [Manifest](https://docs.dify.ai/plugins/schema-definition/manifest) file, include the file path or URL for this privacy policy.

3. Leave your contact infomation and repository URL in `README.md`.

#### Publishing

1. Package your plugin into `.difypkg` file for distribution.

2. [Fork the this repository](https://github.com/langgenius/dify-plugins/fork).

3. Create an organization directory under the repository’s main structure, then create a subdirectory named after your plugin. Place your plugin’s source code and the packaged `.difypkg` file in that subdirectory (eg. `langgenius/dify-plugin/dify-plugin-0.0.1.difypkg`). You can place different versions in the same subdirectory. 

4. [Submit a Pull Request (PR)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) following the required PR template format, then wait for the review;

5. Once approved, your plugin code will merge into the main branch, and the plugin will be automatically listed on the [Dify Marketplace](https://marketplace.dify.ai/).

> **Tips for contributing:**
> - Only **one file change** can be made in a PR request.
> - Check the version of the plugin before publishing. Same version cannot be merged into the same subdirectory.

### Security disclosure

To protect your privacy, please avoid posting security issues on GitHub. Instead, send your questions to [security@dify.ai](mailto:security@dify.ai) and we will provide you with a more detailed answer.
