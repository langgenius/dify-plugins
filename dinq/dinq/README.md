# Dinq - Talent Analysis Plugin

Dinq is a talent analysis platform that provides in-depth profile analysis for:
- **GitHub** developers
- **LinkedIn** professionals
- **Google Scholar** researchers

## Features

- Comprehensive profile analysis
- AI-generated summaries and insights
- Skills and experience extraction
- Publications and contributions analysis

## Usage

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type | select | Yes | Platform to analyze: `github`, `linkedin`, or `scholar` |
| query | string | Yes | The query to search for |

### Query Format

- **GitHub**: Username (e.g., `torvalds`, `octocat`)
- **LinkedIn**: Profile URL (e.g., `https://linkedin.com/in/satyanadella`) or full name
- **Scholar**: Google Scholar profile URL, Scholar ID, or researcher name (e.g., `Geoffrey Hinton`)

## Examples

Analyze a GitHub developer:
- Type: `github`
- Query: `torvalds`

Analyze a LinkedIn professional:
- Type: `linkedin`
- Query: `https://linkedin.com/in/satyanadella`

Analyze a researcher:
- Type: `scholar`
- Query: `Geoffrey Hinton`

## Contact

- Website: https://dinq.me
- Repository: https://github.com/nickelulz/dinq-plugins

## Privacy Policy

This plugin sends the query to Dinq API (https://api.dinq.me) for analysis. No personal data is stored beyond what is necessary for the analysis request.
