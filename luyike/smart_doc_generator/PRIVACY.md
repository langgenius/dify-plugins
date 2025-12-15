# Privacy Policy

## Overview

Smart Doc Generator (the "Plugin") is a Dify plugin that converts Markdown content to Word documents. This privacy policy explains how the Plugin handles user data and information.

## Data Collection

**The Plugin does NOT collect, store, or transmit any user data.**

### What We Don't Collect

- Personal information
- Markdown content or document data
- User credentials or authentication information
- Usage statistics or analytics
- IP addresses or device information
- Any other user-generated content

### Local Processing Only

All data processing occurs **locally** on the Dify instance where the Plugin is installed:

- Markdown content is processed entirely within your Dify environment
- Generated Word documents are created locally
- No data is sent to external servers or third-party services
- No network requests are made for data processing
- All operations are performed on-premises or within your cloud infrastructure

## Data Processing

### What Happens to Your Data

1. **Input Processing**: When you provide Markdown text to the Plugin:
   - The content is processed locally within the Dify plugin runtime
   - No copy of the content is stored permanently
   - Processing is done in memory and temporary files (if needed)

2. **Document Generation**: During Word document generation:
   - Charts and images are generated locally using matplotlib and other libraries
   - All processing happens within the plugin's execution environment
   - Generated files are returned directly to the Dify workflow

3. **Temporary Files**: 
   - Any temporary files created during processing are cleaned up automatically
   - No persistent storage of user content is maintained

### Data Retention

- **No data retention**: The Plugin does not retain any user data after processing
- **No logging**: User content is not logged or stored in any persistent format
- **No caching**: Generated documents are not cached or stored by the Plugin

## Third-Party Services

The Plugin does not integrate with any third-party services that would collect or process user data. All dependencies are open-source libraries used for local processing:

- `python-docx`: For Word document generation (local processing)
- `matplotlib`: For chart generation (local processing)
- `markdown`: For Markdown parsing (local processing)
- Other dependencies: All used for local data processing only

## Security

### Data Security

- All processing occurs within your secure Dify environment
- No data transmission over networks
- No external API calls for data processing
- Follows your Dify instance's security policies and configurations

### Best Practices

- Ensure your Dify instance is properly secured
- Follow your organization's data handling policies
- The Plugin respects all security configurations of your Dify deployment

## Compliance

This Plugin is designed to comply with data privacy regulations including:

- **GDPR (General Data Protection Regulation)**: No personal data collection or processing
- **CCPA (California Consumer Privacy Act)**: No data collection or sale
- **Other privacy regulations**: As no data is collected, the Plugin inherently complies with most privacy requirements

## User Rights

Since the Plugin does not collect or store any user data:

- **Right to Access**: No data is stored, so there is no data to access
- **Right to Deletion**: No data is stored, so there is no data to delete
- **Right to Portability**: No data is stored, so there is no data to export
- **Right to Correction**: No data is stored, so there is no data to correct

All your data remains under your control within your Dify instance.

## Changes to This Privacy Policy

We may update this privacy policy from time to time. Any changes will be reflected in this document. The version of the privacy policy is tied to the Plugin version.

## Contact

If you have any questions about this privacy policy or the Plugin's data handling practices, please:

- Open an issue on the GitHub repository
- Contact the plugin author through the Dify plugin marketplace

## Summary

**In short: This Plugin processes your data locally and does not collect, store, or transmit any information. Your data stays within your Dify instance and is never shared with external services or third parties.**

---

*Last Updated: 2025-01-XX*  
*Plugin Version: 1.0.0*
