# HTML Preview Renderer

Wrap any HTML string into a self-contained page for preview in Dify workflows.

## Features

- Accepts raw HTML (e.g. ECharts output) and returns a renderable, self-contained HTML page
- Ideal for previewing chart/visualization output inside Dify

## Usage

Add the **HTML Render** tool to your Dify workflow, pass in an HTML string, and receive a complete HTML page ready for preview.

## Privacy

This plugin processes HTML strings locally within the Dify runtime and does not send any data to external services. Note that the HTML you provide may itself reference external resources (e.g. CDN scripts); the plugin does not add or fetch any such resources on its own. See `PRIVACY.md` for details.
