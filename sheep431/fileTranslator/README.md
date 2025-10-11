## txtgenarator

**Author:** xyy
**Version:** 0.0.1
**Type:** tool

### Description

# Txt Generator Tool for Dify

A simple and efficient Dify plugin that allows users to input a title and content, then automatically generates and returns a downloadable `.txt` file encoded in UTF-8. Ideal for scenarios such as automatic report generation, LLM output exporting, and document automation workflows.

---

## ✨ Features

- ✅ Accepts dynamic input: `title` and `content`
- ✅ Automatically generates `.txt` file with UTF-8 encoding
- ✅ Returns downloadable file blob, no local file write needed
- ✅ Suitable for batch processing and integration into workflows
- ✅ No external API or internet required

---

## 🔧 Setup Instructions

This plugin runs within the Dify plugin system and requires no external services or credentials. To install and use the plugin:

1. Deploy the plugin in your Dify instance.
2. Add the plugin to your Dify App or Workflow.
3. Provide `title` and `content` as tool parameters.
4. The plugin will return a `.txt` file encoded in UTF-8, ready for download.

---

## 🧪 How to Use in Workflow

### Input Schema

| Parameter | Type   | Required | Description                     |
|-----------|--------|----------|---------------------------------|
| content   | string | Yes      | Body content of the TXT file    |
| title     | string | Yes      | Title of the TXT file           |

### Sample Parameters

```json
{
  "content": "This is the summary of our meeting held on 2025-05-01..."
  "title": "Meeting_Summary",
}

