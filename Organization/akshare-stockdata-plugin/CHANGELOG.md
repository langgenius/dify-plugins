# Changelog

All notable changes to the AKShare Stock Data Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-09-18

### Added
- **113个数据接口**: 从103个接口扩展到113个接口，新增10个数据接口
- **服务对象说明**: 添加了针对学术研究人员和AI应用开发者的服务对象描述
- **巨潮资讯接口优化**: 更新了巨潮资讯接口的标签和描述信息
- **财务分析参数重构**: 将indicator参数拆分为indicator_ths、indicator_hk、indicator_us三个独立参数

### Changed
- **接口数量更新**: 所有文档中的接口数量从103个更新为113个
- **参数描述优化**: 财务分析工具的参数描述更加清晰和具体
- **文档结构改进**: 简化了服务对象部分，突出核心用户群体
- **编码兼容性**: 改进了Windows环境下的Unicode编码处理

### Fixed
- **Unicode编码问题**: 解决了Windows环境下GBK编码导致的UnicodeEncodeError
- **跨平台兼容性**: 确保插件在Windows、Linux、macOS上的稳定运行
- **参数验证**: 修复了财务分析工具中参数验证的逻辑问题

### Removed
- **乐咕乐股接口**: 移除了5个乐咕乐股相关接口（stock_a_indicator_lg等）

---

## [Unreleased]

### Added
- Comprehensive parameter validation with detailed format descriptions
- Multi-language support for all parameter descriptions
- Enhanced error handling with specific suggestions
- GitHub repository structure with proper documentation
- **Legal compliance documentation (LEGAL.md)**
- **Enhanced acknowledgments and AKShare attribution**
- **Open source compliance notices**

### Changed
- Improved parameter descriptions with examples and format requirements
- Updated interface labels to match AKShare documentation exactly
- Enhanced README.md with installation and usage instructions
- **Updated all descriptions to clearly indicate AKShare wrapper nature**
- **Added proper attribution to AKShare, FuShare, and TuShare projects**

### Fixed
- Corrected interface display names for US and HK stock data
- Fixed parameter validation for date formats and stock codes
- Improved error messages for better user experience

### Legal & Compliance
- Added comprehensive legal disclaimers
- Enhanced privacy policy with AKShare dependency information
- Added proper open source compliance notices
- Included financial data usage disclaimers
- Added academic research purpose clarifications

## [0.0.2] - 2025-01-03

### Added
- 15 comprehensive stock data interfaces
- Multi-language support (English, Chinese, Portuguese, Traditional Chinese)
- Robust error handling with retry mechanisms
- Parameter validation and preprocessing
- Support for A-shares, B-shares, US stocks, HK stocks, and STAR market data

### Features
- **A-Share Data**: Daily frequency data, pre-market data, risk warning board, new stocks, delisted stocks
- **B-Share Data**: Real-time B-share data
- **US Stock Data**: Real-time, daily, and minute data
- **Hong Kong Stock Data**: Minute-level data
- **Other Data**: Individual stock info, quotes, company news, STAR board reports, A/H share comparison

### Technical
- Built on AKShare library for reliable data access
- No token required for data access
- Markdown and JSON output formats
- Configurable retry and timeout parameters
- Memory-efficient processing

## [0.0.1] - 2025-01-01

### Added
- Initial release
- Basic plugin structure
- Core AKShare integration
- Basic error handling
- Simple parameter validation

---

## Version History

- **0.0.1**: Initial release with basic functionality
- **0.0.2**: Enhanced with comprehensive interfaces and multi-language support
- **0.5.0**: Major update with 113 interfaces, improved encoding, and parameter refactoring
- **Unreleased**: Improved documentation and GitHub repository structure
