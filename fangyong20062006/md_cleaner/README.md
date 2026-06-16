# Markdown Cleaner for RAG

Clean Markdown documents to boost retrieval quality in Dify parent-child knowledge bases.

## Features

A 12-step pipeline that handles:
- Header/footer noise removal
- Cross-page sentence repair
- Clause number protection
- Garbled symbol fixing
- Terminology normalization
- MD5-based chunk deduplication

It returns cleaned Markdown text plus a downloadable `.md` file.

## Usage

Add the **Clean Markdown** tool to your Dify workflow, pass in the Markdown text, and receive the cleaned result.

## Privacy

This plugin processes all text locally within the Dify runtime and does not collect or transmit any user data. See `PRIVACY.md` for details.
