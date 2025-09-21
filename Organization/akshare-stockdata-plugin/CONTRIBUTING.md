# Contributing to AKShare Stock Data Plugin

Thank you for your interest in contributing to the AKShare Stock Data Plugin! This document provides guidelines and information for contributors.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Use the latest version of the plugin
3. Provide detailed information about the problem

When creating an issue, please include:
- Plugin version
- Dify version
- Python version
- Error messages (if any)
- Steps to reproduce
- Expected vs actual behavior

### Suggesting Enhancements

We welcome suggestions for new features or improvements. Please:
1. Check if the feature request already exists
2. Provide a clear description of the proposed feature
3. Explain why this feature would be useful
4. Consider the impact on existing functionality

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**:
   - Ensure all tests pass
   - Test with different Dify versions
   - Verify multi-language support
5. **Commit your changes**: `git commit -m 'Add some feature'`
6. **Push to the branch**: `git push origin feature/your-feature-name`
7. **Create a Pull Request**

## Development Setup

### Prerequisites

- Python 3.12+
- Dify platform
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   cd akshare-stockdata-plugin
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. Set up pre-commit hooks (optional):
   ```bash
   pre-commit install
   ```

### Code Style

We follow Python PEP 8 style guidelines. Please use:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking

Run the following commands before committing:
```bash
black .
flake8 .
mypy .
```

### Testing

Run tests with:
```bash
pytest
```

### Documentation

When adding new features:
1. Update the README.md if needed
2. Add or update interface documentation
3. Update parameter descriptions in YAML files
4. Ensure multi-language support

## Plugin Structure

```
akshare-stockdata-plugin/
├── manifest.yaml              # Plugin manifest
├── main.py                    # Plugin entry point
├── provider/                  # Provider configuration
│   ├── akshare_stockdata.yaml
│   ├── akshare_stockdata.py
│   └── akshare_registry.py
├── tools/                     # Tool definitions
│   ├── stockdata_em.yaml
│   └── stockdata_em.py
├── _assets/                   # Resources
│   └── icon.png
├── README.md                  # Documentation
├── LICENSE                    # License file
├── PRIVACY.md                 # Privacy policy
└── requirements.txt           # Dependencies
```

## Adding New Data Interfaces

To add a new AKShare data interface:

1. **Update the registry** (`provider/akshare_registry.py`):
   - Add the interface configuration
   - Define required and optional parameters
   - Set up parameter preprocessing

2. **Update tool options** (`tools/stockdata_em.yaml`):
   - Add the new interface to the options list
   - Provide multi-language labels
   - Update descriptions

3. **Test the interface**:
   - Verify parameter handling
   - Test error scenarios
   - Check output format

4. **Update documentation**:
   - Add to README.md
   - Update interface descriptions
   - Provide usage examples

## Multi-language Support

The plugin supports four languages:
- English (en_US)
- Simplified Chinese (zh_Hans)
- Portuguese (pt_BR)
- Traditional Chinese (zh_Hant)

When adding new text:
1. Add translations for all four languages
2. Keep translations consistent
3. Use clear and concise language
4. Consider cultural differences

## Release Process

1. Update version numbers in:
   - `manifest.yaml`
   - `pyproject.toml`
   - `README.md`

2. Update changelog in README.md

3. Create a release tag

4. Test the release

## Questions?

If you have questions about contributing:
1. Check existing issues and discussions
2. Create a new issue with the "question" label
3. Contact the maintainer: sxxiefg@163.com

Thank you for contributing to the AKShare Stock Data Plugin!
