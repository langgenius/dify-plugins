# Contributing to Huoban Dify Plugin

Thank you for your interest in contributing to the Huoban Dify Plugin! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

### Reporting Issues
1. Check if the issue already exists in the issue tracker
2. Use the issue template if available
3. Provide detailed information:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Dify version and environment details

### Feature Requests
1. Explain the feature and its use case
2. Describe the expected behavior
3. Consider if it aligns with the plugin's scope

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

### Prerequisites
- Node.js 16+ (for testing)
- Dify development environment
- Huoban API access

### Local Development
1. Clone the repository
2. Install dependencies (if any)
3. Make your changes
4. Test locally with Dify

### Testing
- Test all API endpoints with sample data
- Verify error handling
- Ensure compatibility with Dify's plugin system
- Test with different Huoban workspace configurations

## Code Guidelines

### OpenAPI Specification
- Follow OpenAPI 3.1.0 standards
- Include comprehensive descriptions for all operations
- Provide clear examples
- Document all parameters and responses

### Manifest File
- Keep `manifest.json` up to date
- Include proper localization (en_US and zh_Hans)
- Update version numbers appropriately
- Maintain accurate metadata

### Documentation
- Update README.md with new features
- Include usage examples
- Document breaking changes
- Keep changelog updated

## Release Process

1. Update version in `manifest.json`
2. Update changelog in README.md
3. Create release notes
4. Tag the release
5. Submit to Dify Marketplace

## Questions?

Feel free to open an issue for questions about contributing or development.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
