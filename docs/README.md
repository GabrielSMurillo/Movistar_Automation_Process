# 🚀 Movistar Automation Process

Sistema automatizado de procesamiento, validación y consolidación de reportes de ventas para múltiples segmentos de negocio de Movistar (Digital, Fija, Móvil).

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![Status: Production](https://img.shields.io/badge/Status-Production-green.svg)]()

## 📖 Quick Links

- **[Getting Started](./user_guides/INSTALLATION.md)** - Installation and setup
- **[Configuration Guide](./user_guides/CONFIGURATION.md)** - How to configure the system
- **[Architecture Overview](./architecture/SYSTEM_DESIGN.md)** - System design and architecture
- **[Business Rules](./business/BUSINESS_RULES.md)** - Business logic documentation
- **[Development Guide](./development/CONTRIBUTING.md)** - How to contribute

## 🎯 What Does This System Do?

This system automates the complete sales report processing for Movistar, including:

1. **Data Loading** from multiple sources (CSV from Google Sheets)
2. **Comprehensive Validation** (phones, names, logins, formats)
3. **Duplicate Detection & Elimination** with historical tracking
4. **Automatic Segmentation** (Digital, Fija, Móvil)
5. **Consolidated Report Generation** in Excel format
6. **Output Validation** against business rules
7. **Novelty Report Generation** for invalid records

## ⚡ Quick Start

```bash
# Clone repository
git clone https://github.com/GabrielSMurillo/Movistar_Automation_Process.git
cd Movistar_Automation_Process

# Install dependencies
pip install -r requirements.txt

# Configure dates (edit config.py or use .env)
# START_DATE=2024-10-23
# END_DATE=2024-10-31

# Run the pipeline
python main_refactored.py
```

## 📊 Key Features

- ✅ **Automated Processing** of multiple CSV files
- ✅ **Smart Duplicate Detection** with multiple criteria
- ✅ **Comprehensive Validation** of input and output data
- ✅ **Historical Tracking** of processed records
- ✅ **Segmented Reports** by business unit
- ✅ **Detailed Logging** of all operations
- ✅ **Execution Summaries** with statistics
- ✅ **Robust Error Handling**
- ✅ **Unit Tests** for critical components
- ✅ **Automatic Line Type Classification** (Mobile/Fixed)
- ✅ **Novelty Files** for invalid records

## 🏗️ System Architecture

The system uses a clean, layered architecture:

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                  │
│  (main.py, CLI, future API)                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       Application Layer                      │
│  (Pipeline Orchestrator, Stages)            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Domain Layer                        │
│  (Business Logic, Models, Services)         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Infrastructure Layer                    │
│  (Data Access, External Services)           │
└─────────────────────────────────────────────┘
```

For detailed architecture information, see [System Design](./architecture/SYSTEM_DESIGN.md).

## 📁 Project Structure

```
workspace/
├── src/                          # Source code
│   ├── core/                     # Core components (models, config, exceptions)
│   ├── domain/                   # Business logic (processors)
│   ├── services/                 # Domain services (validators, mappers)
│   ├── pipeline/                 # Data pipeline (orchestrator, stages)
│   ├── generators/               # Output file generators
│   ├── analytics/                # Analytics and monitoring
│   └── governance/               # Audit and lineage tracking
├── tests/                        # Test suite
├── docs/                         # Documentation
│   ├── architecture/             # Architecture docs
│   ├── user_guides/              # User guides
│   ├── development/              # Development docs
│   └── business/                 # Business rules
├── data/                         # Data directories (not in git)
├── main.py                       # Main entry point (legacy)
├── main_refactored.py            # Refactored entry point (recommended)
└── config.py                     # Configuration (deprecated, use .env)
```

## 📝 Documentation Index

### 🚀 Getting Started
- [Installation Guide](./user_guides/INSTALLATION.md)
- [Configuration Guide](./user_guides/CONFIGURATION.md)
- [Usage Guide](./user_guides/USAGE.md)
- [Troubleshooting](./user_guides/TROUBLESHOOTING.md)

### 🏗️ Architecture
- [System Design](./architecture/SYSTEM_DESIGN.md)
- [Data Flow](./architecture/DATA_FLOW.md)
- [Module Overview](./architecture/MODULES.md)
- [Refactoring Analysis](./COMPREHENSIVE_REFACTORING_ANALYSIS.md)

### 💼 Business
- [Business Rules](./business/BUSINESS_RULES.md)
- [Service Codes Reference](./business/SERVICE_CODES.md)
- [Validation Rules](./business/VALIDATION_RULES.md)
- [File Formats](./business/FILE_FORMATS.md)

### 👨‍💻 Development
- [Contributing Guide](./development/CONTRIBUTING.md)
- [Testing Guide](./development/TESTING.md)
- [Code Standards](./development/CODE_STANDARDS.md)
- [Implementation Guide](./development/IMPLEMENTATION_GUIDE.md)

### 📋 Changelog
- [Version History](./changelog/CHANGELOG.md)
- [Migration Guides](./changelog/MIGRATION_GUIDES.md)

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_processors.py
```

Current test coverage: **60%** (target: >85%)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./development/CONTRIBUTING.md) for details.

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on [GitHub Issues](https://github.com/GabrielSMurillo/Movistar_Automation_Process/issues)
- Contact the development team

## 👤 Author

**Gabriel S. Murillo**
- GitHub: [@GabrielSMurillo](https://github.com/GabrielSMurillo)

## 📄 License

This project is **private** and for internal use only.

---

**Last Updated**: November 4, 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready
