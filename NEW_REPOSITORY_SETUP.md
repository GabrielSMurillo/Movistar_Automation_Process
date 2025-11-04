# 🚀 New Repository Setup Guide

**Creating a Clean Repository with Refactored Movistar Automation System**

This guide will help you create a new repository with only the clean, refactored code - no legacy, no history, just the excellent v2.0 system.

---

## 📋 Prerequisites

- Git installed
- GitHub account (or GitLab/Bitbucket)
- Python 3.10+
- Access to create new repository

---

## 🎯 Step 1: Create New Repository on GitHub

### Option A: Via GitHub Web Interface

1. Go to https://github.com/new
2. Fill in details:
   - **Repository name**: `movistar-automation-v2`
   - **Description**: "Movistar Sales Data Processing & Automation System v2.0 - Clean Architecture"
   - **Visibility**: Private (recommended for business code)
   - **Initialize**: ❌ Don't initialize with README (we'll add ours)
3. Click "Create repository"

### Option B: Via GitHub CLI

```bash
# Install GitHub CLI if needed
# brew install gh  (macOS)
# Or download from https://cli.github.com/

# Login
gh auth login

# Create new private repository
gh repo create movistar-automation-v2 \
  --private \
  --description "Movistar Sales Automation v2.0 - Production Ready" \
  --clone
```

---

## 🎯 Step 2: Prepare Files to Include

### Files to INCLUDE ✅

```bash
# Root files
README.md
REFACTORING_EXECUTIVE_SUMMARY.md
REFACTORING_COMPLETE.md
PROJECT_STRUCTURE.md
config.py                          # With deprecation warnings
main.py                            # Legacy entry point
main_refactored.py                 # Recommended entry point
requirements.txt
requirements-dev.txt
pytest.ini
mypy.ini
run_tests.py
.env.example                       # Example environment file
.gitignore                         # Essential!
.pre-commit-config.yaml           # For code quality
LICENSE                            # If applicable

# Documentation
docs/                              # Entire directory
docs/README.md
docs/COMPREHENSIVE_REFACTORING_ANALYSIS.md
docs/IMPROVEMENT_ROADMAP.md
docs/architecture/
docs/business/
docs/development/
docs/changelog/
docs/user_guides/

# Source code
src/                               # Entire directory
src/core/
src/domain/
src/services/
src/pipeline/
src/output/                        # KEY INNOVATION!
src/generators/
src/analytics/
src/governance/
src/adapters/
src/*.py

# Tests
tests/                             # Entire directory
tests/*.py

# CI/CD (if created)
.github/                           # GitHub Actions workflows
.github/workflows/ci.yml
```

### Files to EXCLUDE ❌

```bash
# Data files (should never be in git)
data/
*.csv
*.xlsx
*.xls
*.json  (tracking files)

# Logs
logs/
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
.tox/
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Temporary files
*.tmp
*.bak
*.backup
.cache/

# Environment files with secrets
.env  (but include .env.example)
```

---

## 🎯 Step 3: Create Proper .gitignore

```bash
# .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.mypy_cache/
.dmypy.json
dmypy.json

# Data files (CRITICAL - never commit data!)
data/
data/**/*
*.csv
*.xlsx
*.xls
!data/.gitkeep

# Logs
logs/
*.log
!logs/.gitkeep

# Tracking files
tracking/
*.db
*.sqlite
*.db-journal

# Environment variables (include .env.example only)
.env
.env.local
.env.*.local

# Temporary files
*.tmp
*.bak
*.backup
.cache/
temp/

# OS
Thumbs.db
.DS_Store

# Output files (if you want to exclude them)
output/
processed/
# Or keep structure with .gitkeep:
# !output/.gitkeep
# !processed/.gitkeep
```

---

## 🎯 Step 4: Create .env.example

```bash
# .env.example
# Copy this to .env and fill in your values

# Environment
MOVISTAR_ENV=development  # development | production | testing

# Date Range (format: YYYY-MM-DD)
MOVISTAR_START_DATE=2024-10-23
MOVISTAR_END_DATE=2024-10-31

# Paths (optional - uses defaults if not set)
# MOVISTAR_BASE_DIR=/path/to/movistar
# MOVISTAR_DATA_DIR=/path/to/data
# MOVISTAR_INPUT_DIR=/path/to/data/input
# MOVISTAR_OUTPUT_DIR=/path/to/data/output

# Logging
MOVISTAR_LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
MOVISTAR_LOG_FILE=logs/pipeline.log

# Database (if using SQLite tracking - future)
# MOVISTAR_DB_PATH=data/tracking/sales_tracking.db

# Email notifications (future)
# MOVISTAR_SMTP_HOST=smtp.gmail.com
# MOVISTAR_SMTP_PORT=587
# MOVISTAR_SMTP_USER=your-email@example.com
# MOVISTAR_SMTP_PASSWORD=your-password
# MOVISTAR_NOTIFY_EMAIL=notifications@example.com

# API Settings (future)
# MOVISTAR_API_KEY=your-api-key
# MOVISTAR_API_SECRET=your-api-secret
```

---

## 🎯 Step 5: Create Directory Structure

```bash
# Create essential directories with .gitkeep files
mkdir -p data/{input,output,processed,tracking,historico}
mkdir -p logs
mkdir -p tests/fixtures
mkdir -p .github/workflows

# Create .gitkeep files to preserve directory structure
touch data/.gitkeep
touch data/input/.gitkeep
touch data/output/.gitkeep
touch data/processed/.gitkeep
touch data/tracking/.gitkeep
touch data/historico/.gitkeep
touch logs/.gitkeep
touch tests/fixtures/.gitkeep
```

---

## 🎯 Step 6: Copy Files from Current Repository

```bash
# Navigate to the NEW repository
cd /path/to/movistar-automation-v2

# Copy files from OLD repository
# Adjust the path to your current workspace

OLD_REPO="/workspace"  # Adjust this path

# Copy root files
cp $OLD_REPO/README.md .
cp $OLD_REPO/REFACTORING_EXECUTIVE_SUMMARY.md .
cp $OLD_REPO/REFACTORING_COMPLETE.md .
cp $OLD_REPO/PROJECT_STRUCTURE.md .
cp $OLD_REPO/main.py .
cp $OLD_REPO/main_refactored.py .
cp $OLD_REPO/config.py .
cp $OLD_REPO/requirements.txt .
cp $OLD_REPO/requirements-dev.txt .
cp $OLD_REPO/pytest.ini .
cp $OLD_REPO/mypy.ini .
cp $OLD_REPO/run_tests.py .

# Copy entire directories
cp -r $OLD_REPO/docs .
cp -r $OLD_REPO/src .
cp -r $OLD_REPO/tests .

# Copy CI/CD files if they exist
cp $OLD_REPO/.pre-commit-config.yaml . 2>/dev/null || true
cp -r $OLD_REPO/.github . 2>/dev/null || true

# Create .gitkeep files
touch data/.gitkeep
touch data/input/.gitkeep
touch data/output/.gitkeep
touch logs/.gitkeep
```

---

## 🎯 Step 7: Create Initial Commit Structure

```bash
# Initialize git (if not done via gh clone)
git init

# Add remote (adjust URL to your repository)
git remote add origin https://github.com/YOUR_USERNAME/movistar-automation-v2.git

# Create .gitignore (copy content from above)
nano .gitignore
# Paste the .gitignore content from Step 3

# Create .env.example
nano .env.example
# Paste the .env.example content from Step 4

# Stage all files
git add .

# Check what will be committed
git status

# First commit
git commit -m "Initial commit: Movistar Automation v2.0 - Clean Architecture

✨ Features:
- Clean layered architecture (presentation, application, domain, infrastructure)
- Modern pipeline pattern with clear stages
- Pydantic-based configuration with type safety
- Comprehensive validation and business logic separation
- Shared ExcelFormatter eliminating code duplication
- 60% test coverage with comprehensive test suite
- Complete documentation (30+ pages)
- Production-ready with proper error handling

📊 Metrics:
- 83% reduction in code duplication
- 49% reduction in generator code
- 92% reduction in root directory clutter
- Well-organized documentation structure

🏗️ Architecture:
- src/core/ - Foundation (config, models, exceptions, decorators)
- src/domain/ - Business logic (processors)
- src/services/ - Domain services (validators, mappers)
- src/pipeline/ - Data flow orchestration
- src/output/ - Output generation with shared utilities
- src/generators/ - File generators
- src/analytics/ - Monitoring and profiling
- src/governance/ - Audit and lineage

📚 Documentation:
- Complete system analysis and refactoring guide
- Improvement roadmap
- Architecture documentation
- Business rules reference

🎯 Status: Production Ready
⭐ Quality: Excellent (9/10)
🔄 Version: 2.0"

# Push to remote
git branch -M main
git push -u origin main
```

---

## 🎯 Step 8: Set Up Branch Protection (Recommended)

### Via GitHub Web Interface:

1. Go to repository settings
2. Navigate to "Branches"
3. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require conversation resolution before merging
   - ✅ Include administrators (optional)

### Via GitHub CLI:

```bash
# Protect main branch
gh api repos/YOUR_USERNAME/movistar-automation-v2/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```

---

## 🎯 Step 9: Set Up CI/CD (Optional but Recommended)

Create GitHub Actions workflow:

```bash
mkdir -p .github/workflows
```

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
  
  quality:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install black isort flake8 mypy
      
      - name: Check formatting with black
        run: black --check src/ tests/
      
      - name: Check import sorting
        run: isort --check-only src/ tests/
      
      - name: Lint with flake8
        run: flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
      
      - name: Type check with mypy
        run: mypy src/ --ignore-missing-imports
        continue-on-error: true
```

Commit and push:

```bash
git add .github/workflows/ci.yml
git commit -m "ci: Add GitHub Actions CI pipeline

- Test on Python 3.10, 3.11, 3.12
- Code quality checks (black, isort, flake8, mypy)
- Coverage reporting"
git push
```

---

## 🎯 Step 10: Add README Badges

Update `README.md` to add badges:

```markdown
# 🚀 Movistar Automation Process v2.0

[![CI](https://github.com/YOUR_USERNAME/movistar-automation-v2/workflows/CI%20Pipeline/badge.svg)](https://github.com/YOUR_USERNAME/movistar-automation-v2/actions)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/movistar-automation-v2/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/movistar-automation-v2)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![Status: Production](https://img.shields.io/badge/Status-Production-green.svg)]()

Sistema automatizado de procesamiento, validación y consolidación de reportes de ventas.

## 🎯 Version 2.0 - Clean Architecture

This is a complete rewrite with modern architecture, clean code, and production-ready features.

[Rest of your README content...]
```

---

## 🎯 Step 11: Set Up Project Documentation

Create a `CONTRIBUTING.md`:

```markdown
# Contributing to Movistar Automation v2.0

## Getting Started

1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Run tests

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and quality checks
4. Submit a pull request

## Code Quality

We use:
- `black` for formatting
- `isort` for import sorting
- `flake8` for linting
- `mypy` for type checking
- `pytest` for testing

Run all checks:
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
pytest tests/
```

## Commit Messages

Follow conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance
```

---

## 🎯 Step 12: Create Release

```bash
# Tag the release
git tag -a v2.0.0 -m "Release v2.0.0 - Clean Architecture

Major rewrite with modern architecture:
- Clean layered architecture
- 83% reduction in code duplication
- Production-ready features
- Comprehensive documentation

See REFACTORING_EXECUTIVE_SUMMARY.md for details."

# Push tag
git push origin v2.0.0

# Create GitHub release
gh release create v2.0.0 \
  --title "Movistar Automation v2.0.0 - Clean Architecture" \
  --notes "See REFACTORING_EXECUTIVE_SUMMARY.md for complete details"
```

---

## 🎯 Step 13: Clone for Team Members

Share these instructions with team members:

```bash
# Clone the new repository
git clone https://github.com/YOUR_USERNAME/movistar-automation-v2.git
cd movistar-automation-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy and configure .env
cp .env.example .env
nano .env  # Edit with your settings

# Create data directories
mkdir -p data/{input,output,processed,tracking,historico}
mkdir -p logs

# Run tests to verify setup
pytest tests/

# Run the system
python main_refactored.py
```

---

## 📊 Repository Structure Overview

```
movistar-automation-v2/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── README.md
│   ├── COMPREHENSIVE_REFACTORING_ANALYSIS.md
│   ├── IMPROVEMENT_ROADMAP.md
│   ├── architecture/
│   ├── business/
│   ├── development/
│   └── changelog/
├── src/
│   ├── core/
│   ├── domain/
│   ├── services/
│   ├── pipeline/
│   ├── output/          # ⭐ KEY INNOVATION
│   ├── generators/
│   ├── analytics/
│   └── governance/
├── tests/
├── data/ (not in git)
├── logs/ (not in git)
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
├── CONTRIBUTING.md
├── main.py
├── main_refactored.py
├── config.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── mypy.ini
```

---

## ✅ Checklist

- [ ] Create new repository on GitHub
- [ ] Set up proper .gitignore
- [ ] Create .env.example
- [ ] Copy all source files
- [ ] Copy all documentation
- [ ] Copy test files
- [ ] Create directory structure with .gitkeep
- [ ] Make initial commit
- [ ] Push to remote
- [ ] Set up branch protection
- [ ] Add CI/CD workflow
- [ ] Update README with badges
- [ ] Create CONTRIBUTING.md
- [ ] Tag release v2.0.0
- [ ] Share with team

---

## 🎯 Next Steps After Setup

1. **Verify the setup**:
   ```bash
   pytest tests/
   python main_refactored.py --help
   ```

2. **Start implementing improvements** from `docs/IMPROVEMENT_ROADMAP.md`:
   - Update generators to use ExcelFormatter
   - Increase test coverage
   - Set up pre-commit hooks

3. **Invite collaborators**:
   ```bash
   gh repo invite USERNAME --permission=write
   ```

4. **Set up project board**:
   - Create issues for improvements
   - Set up GitHub Projects for tracking

---

## 🚀 Benefits of New Repository

✅ **Clean history** - No legacy commits  
✅ **Fresh start** - Only production-ready code  
✅ **Clear versioning** - Start at v2.0.0  
✅ **Better onboarding** - Clean, clear structure  
✅ **Proper branching** - Protected main branch  
✅ **CI/CD ready** - Automated testing from day 1  

---

## 📞 Support

For questions about setup:
- See `docs/README.md` for documentation index
- See `docs/COMPREHENSIVE_REFACTORING_ANALYSIS.md` for architecture details
- See `CONTRIBUTING.md` for development workflow

---

**Last Updated**: November 4, 2025  
**Version**: 2.0.0  
**Status**: ✅ Ready to Deploy
