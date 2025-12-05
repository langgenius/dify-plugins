# Upstage Document AI Plugin

Advanced Document AI plugin using Upstage API. Parse documents into text/HTML/Markdown or extract structured data with custom schemas.

## Plugin Information

- **Developer:** omiya0555
- **Organization:** Fusic
- **Version:** 0.0.1
- **Type:** Tool Plugin
- **Contact:** omiya@fusic.co.jp
- **Repository:** https://github.com/omiya0555/dify-upstage-plugin

## Features

### 1. Document Parser
Parse PDFs, images, and office documents into text, HTML, or Markdown format with high accuracy OCR.

- Multi-format support: PDF, DOCX, XLSX, PPTX, JPEG, PNG, BMP, TIFF, HEIC
- Multiple output formats: Markdown, HTML, Plain Text
- Advanced OCR with chart detection

### 2. Information Extract
Extract structured data from documents using custom JSON schemas.

- Custom schema definition
- Structured JSON output
- 90-95% accuracy on complex documents
- Works with any document type

## Setup Instructions

1. Get your Upstage API key from [Upstage Console](https://console.upstage.ai/api-keys)
2. Install the plugin in Dify
3. Configure the API key in plugin settings
4. **Configure File Access (Required):**
   - For local: `FILES_URL=http://api:5001`
   - For production: Set both `FILES_URL` and `INTERNAL_FILES_URL` to `http://localhost:5001` (adjust port as needed)

## Required APIs and Credentials

- **API Key:** Upstage API key (required)
- **API Endpoint:** https://api.upstage.ai
- **Supported Models:**
  - Document Parse: `document-parse`
  - Information Extract: `information-extract`

## Connection Requirements

- Network access to `api.upstage.ai`
- HTTPS connection support
- Minimum 5-minute timeout for large documents

## Configuration Details

### Document Parser
- **Input:** Document file (PDF, images, office formats)
- **Output Format:** Markdown, HTML, or Plain Text
- **Max File Size:** Determined by Upstage API limits

### Information Extract
- **Input:** Document file + JSON schema
- **Output:** Structured JSON data
- **Schema Format:** Simple key-value pairs with descriptions

## Privacy Policy

This plugin complies with Dify Plugin Privacy Protection Guidelines. See [PRIVACY.md](../../upstage-source-code/PRIVACY.md) for full details.

### Data Handling
- Files are sent to Upstage API for processing
- Temporary in-memory caching (max 1 hour)
- No permanent storage of user data
- All connections use HTTPS encryption

## Performance Features

- Intelligent memory cache system
- MD5-based cache key generation
- Automatic cache expiration (1 hour)
- LRU eviction policy (max 100 items)
- Thread-safe operations

## Source Code

Full source code is available in this repository under the `upstage-source-code` directory.

## Support

For issues, questions, or support:
- **Email:** omiya@fusic.co.jp
- **Repository:** https://github.com/Fusic-Company/dify-plugin-upstage

## License

This plugin is provided as-is. Please refer to the repository for license information.
