# Migration Plan: champi-gen-ui → champi-imgui

**Target Repository:** `champi-ai/champi-imgui`
**Migration Date:** 2025-10-20
**Purpose:** Create a clean repository with proper versioning (v prefix), renamed package, and streamlined history

---

## 🤖 Instructions for LLM Assistants

This migration plan is designed to be executed by an LLM assistant in a new session. When executing this plan:

### Critical Execution Rules

1. **⏸️ STOP at Checkpoints**: Before executing ANY command that modifies state (git operations, file creation, API calls), you MUST:
   - Present the command to the user
   - Explain what it will do and why
   - Wait for explicit user confirmation with "proceed", "continue", or "yes"

2. **✅ Validate After Each Step**: After executing each operation:
   - Run the validation command provided
   - Compare output to the expected result
   - If validation fails, STOP and report the issue to the user

3. **💡 Provide Context**: Before each major section:
   - Explain WHY this step is needed
   - Describe WHAT will change
   - Warn about potential risks

4. **📊 Track Progress**: Use the TodoWrite tool to:
   - Create tasks for each stage
   - Mark tasks as in_progress when starting
   - Mark tasks as completed only after successful validation
   - Update user on progress after each checkpoint

5. **🔄 Handle Failures**: If any step fails:
   - STOP immediately
   - Report the error to the user with full details
   - Suggest rollback procedures
   - Wait for user decision before proceeding

6. **📋 Document Actions**: After completing each stage:
   - Summarize what was accomplished
   - List any deviations from the plan
   - Confirm all validations passed

### Expected LLM Behavior

```
✓ Skim Table of Contents to understand overall flow
✓ Read current stage section just-in-time (not entire plan upfront)
✓ Ask user if ready to begin
✓ Execute stages IN ORDER: Stage 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → Verification
✓ Understand that Stages 1-3 are combined in one branch (feat/setup-initial-infrastructure)
✓ Understand that Stage 4 uses chore: commits and doesn't trigger version bump (stays v0.0.1)
✓ Understand that Stages 5-8 are feature PRs that bump minor versions:
  - Stage 5: v0.0.1 → v0.1.0 (Core Canvas and Widget System)
  - Stage 6: v0.1.0 → v0.2.0 (MCP Tools and Extensions)
  - Stage 7: v0.2.0 → v0.3.0 (Animation, Data Binding, Templates)
  - Stage 8: v0.3.0 → v0.4.0 (Export and Non-blocking UI)
✓ NEVER skip stages or jump ahead
✓ Read each stage section only when starting it
✓ Stop and confirm before destructive operations
✓ Validate after each step
✓ Report validation results
✓ Track progress with todos
✓ Summarize at checkpoints
✗ Never assume user intent
✗ Never skip validation steps
✗ Never proceed without user confirmation on stop points
✗ Never modify state without explicit permission
✗ Never let user skip stages (enforce sequential order)
```

---

## Table of Contents

1. [Git History Analysis](#git-history-analysis)
2. [Stage 1: Repository Foundation](#stage-1-repository-foundation)
3. [Stage 2: Versioning System](#stage-2-versioning-system)
4. [Stage 3: Release Workflow](#stage-3-release-workflow)
5. [Stage 4: Documentation](#stage-4-documentation)
6. [Stage 5: Core Canvas and Widget System](#stage-5-core-canvas-and-widget-system)
7. [Stage 6: MCP Tools and Extensions](#stage-6-mcp-tools-and-extensions)
8. [Stage 7: Advanced Features (Animation, Data Binding, Templates)](#stage-7-advanced-features-animation-data-binding-templates)
9. [Stage 8: Export and Non-blocking UI](#stage-8-export-and-non-blocking-ui)
10. [Verification Steps](#verification-steps)
11. [Go-Live Checklist](#go-live-checklist)

---

## Git History Analysis

### Current Repository Commits

Below is the complete git history with annotations for migration:

| Hash | Short | Date | Author | Message | Action |
|------|-------|------|--------|---------|--------|
| `42e42fd` | 42e42fd | 2025-10-03 | Divagnz | first commit | **KEEP** - Initial setup |
| `6375c06` | 6375c06 | 2025-10-06 | Divagnz | feat: add comprehensive repository development infrastructure (#1) | **SKIP** - Duplicate of #2 |
| `960c073` | 960c073 | 2025-10-19 | Divagnz | feat: add comprehensive repository development infrastructure (#2) | **KEEP** - Main infrastructure |
| `dbf186e` | dbf186e | 2025-10-19 | Divagnz | feat: Add non-blocking UI rendering infrastructure (#3) | **KEEP** - Real feature |
| `0b6d2e6` | 0b6d2e6 | 2025-10-19 | Divagnz | fix: ensure tags are fetched in release workflow | **SKIP** - Test commit |
| `1f48d8f` | 1f48d8f | 2025-10-19 | Divagnz | fix: add explicit git fetch tags step in release workflow | **SKIP** - Test commit |
| `ac2de1f` | ac2de1f | 2025-10-19 | Divagnz | fix: correct commitizen changelog_start_rev to use v prefix | **SKIP** - Test commit |
| `5016f29` | 5016f29 | 2025-10-19 | Divagnz | fix: only push tags in release workflow, not commits | **SKIP** - Test commit |
| `d69f96a` | d69f96a | 2025-10-19 | Divagnz | revert: restore version bump push to main | **SKIP** - Revert commit |
| `79faeaf` | 79faeaf | 2025-10-20 | Divagnz | feat: use custom RELEASE_TOKEN for bypassing branch protection | **SKIP** - Test commit |
| `0335f42` | 0335f42 | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `0170347` | 0170347 | 2025-10-20 | Divagnz | Revert "bump: version 0.1.0 → 1.0.0" | **SKIP** - Revert commit |
| `7e4f892` | 7e4f892 | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `29dbc88` | 29dbc88 | 2025-10-20 | Divagnz | refactor: use official commitizen-action for releases (#4) | **SKIP** - Test commit |
| `380c84c` | 380c84c | 2025-10-20 | Divagnz | fix: pin commitizen-action to full commit SHA (#5) | **SKIP** - Test commit |
| `f08e714` | f08e714 | 2025-10-20 | Divagnz | fix: add Docker Hub logout workaround for auth issues (#6) | **SKIP** - Test commit |
| `6b02e9b` | 6b02e9b | 2025-10-20 | Divagnz | refactor: replace Docker-based commitizen-action with native implementation (#7) | **KEEP** - Important workflow change |
| `3c8050c` | 3c8050c | 2025-10-20 | Divagnz | fix: handle incremental changelog extraction properly (#8) | **SKIP** - Test commit |
| `11df497` | 11df497 | 2025-10-20 | Divagnz | fix: correct commitizen changelog configuration (#9) | **SKIP** - Test commit |
| `f61d94e` | f61d94e | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `4216bf7` | 4216bf7 | 2025-10-20 | Divagnz | bump: revert to 0.1.0 for testing release workflow | **SKIP** - Revert commit |
| `0898bb8` | 0898bb8 | 2025-10-20 | Divagnz | feat: test automated release workflow (#10) | **SKIP** - Test commit |
| `831e8de` | 831e8de | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `8228fc5` | 8228fc5 | 2025-10-20 | Divagnz | bump: revert to 0.1.0 to fix workflow | **SKIP** - Revert commit |
| `e6158e6` | e6158e6 | 2025-10-20 | Divagnz | fix: ensure release creation only runs when version changes (#11) | **SKIP** - Test commit |
| `de51486` | de51486 | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `5d9d98a` | 5d9d98a | 2025-10-20 | Divagnz | bump: revert to 0.1.0 and fix tag creation in workflow | **SKIP** - Revert commit |
| `ba9ea83` | ba9ea83 | 2025-10-20 | Divagnz | feat: test explicit tag creation in release workflow (#12) | **SKIP** - Test commit |
| `155c542` | 155c542 | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `e939778` | e939778 | 2025-10-20 | Divagnz | bump: revert to 0.1.0 and fix duplicate tag creation | **SKIP** - Revert commit |
| `1d13395` | 1d13395 | 2025-10-20 | Divagnz | chore: remove test and plan files (#15) | **SKIP** - Cleanup commit |
| `1306f8a` | 1306f8a | 2025-10-20 | github-actions[bot] | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `82e28e2` | 82e28e2 | 2025-10-20 | Divagnz | bump: revert to 0.1.0 and use owner identity for git config | **SKIP** - Revert commit |
| `6358d0d` | 6358d0d | 2025-10-20 | Divagnz | feat: use authenticated URL for git push with RELEASE_TOKEN (#16) | **SKIP** - Test commit |
| `791217b` | 791217b | 2025-10-20 | Divagnz | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |
| `a59a0b5` | a59a0b5 | 2025-10-20 | Divagnz | bump: revert to 0.1.0 and use tag format without v prefix | **SKIP** - Revert commit |
| `f5dfab4` | f5dfab4 | 2025-10-20 | Divagnz | feat: test tag creation without v prefix (#17) | **KEEP** - Final working solution |
| `6ea2a69` | 6ea2a69 | 2025-10-20 | Divagnz | bump: version 0.1.0 → 1.0.0 | **SKIP** - Test bump |

### Commits to Preserve in New Repository

**Total: 4 meaningful commits to keep**

**From 42e42fd to 960c073**: Initial Setup and Infrastructure
- Includes first commit (42e42fd) with basic repository structure
- Plus comprehensive development infrastructure (960c073): Ruff, MyPy, Pytest, pre-commit, CI/CD
- **Action**: SQUASH these into single initial commit in new repo

**From dbf186e to 6b02e9b**: Feature Development
- Non-blocking UI rendering infrastructure (dbf186e)
- Native release workflow replacing Docker-based commitizen (6b02e9b)
- **Action**: SQUASH these into single feature commit in new repo

**Hash f5dfab4**: Working Release Solution
- Final working release workflow (though uses tags without v prefix)
- **Action**: Will be reworked in new repo to use v prefix tags

**Result:** Squash down to 2 main commits in new repo:
- Initial setup with full infrastructure (42e42fd..960c073)
- Non-blocking UI feature with release workflow (dbf186e..6b02e9b)

---


## Stage 1: Repository Foundation

**Goal:** Set up PR templates, commit templates, and commitizen hooks for local auto-commit generation

**Note:** This stage is the first of three stages (1-3) that will be combined in a single branch and PR, resulting in v0.0.1 release.

### Create Branch

```bash
git checkout -b feat/setup-initial-infrastructure
```

### I. Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] feat: New feature
- [ ] fix: Bug fix
- [ ] docs: Documentation update
- [ ] refactor: Code refactoring
- [ ] test: Adding or updating tests
- [ ] chore: Maintenance or tooling changes
- [ ] ci: CI/CD changes

## Breaking Changes

<!-- Does this PR introduce breaking changes? If yes, describe them -->

- [ ] Yes, this PR includes breaking changes
- [ ] No breaking changes

## Checklist

- [ ] Code follows project style guidelines (ruff check passes)
- [ ] Type hints are correct (mypy passes)
- [ ] Tests pass locally
- [ ] Commit messages follow conventional commits format
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if this is a significant change)

## Related Issues

<!-- Link any related issues: Fixes #123, Relates to #456 -->

## Additional Context

<!-- Add any other context, screenshots, or information about the PR -->
```

### II. Commit Message Template

Create `.gitmessage`:

```
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>

# Type: feat, fix, docs, style, refactor, test, chore, ci
# Scope: Optional, indicates the area of change (e.g., ui, api, docs)
# Subject: Short summary (50 chars or less)
#
# Body: Detailed explanation (wrap at 72 chars)
#   - Why the change was made
#   - What problem it solves
#
# Footer: Breaking changes, issue references
#   BREAKING CHANGE: Description of breaking change
#   Fixes #123
#   Closes #456
#
# Examples:
# feat(canvas): add support for docking mode
# fix(widgets): correct button click detection
# docs(readme): update installation instructions
# BREAKING CHANGE: Canvas API now requires explicit mode parameter
```

Configure git to use this template:

```bash
git config --local commit.template .gitmessage
```

### III. Pre-commit Configuration with Commitizen

Create `.pre-commit-config.yaml`:

```yaml
# Pre-commit hooks for code quality and conventional commits
repos:
  # Conventional commits validation
  - repo: https://github.com/compwa/commitizen-pre-commit-hook
    rev: v3.0.0
    hooks:
      - id: commitizen
        name: Validate conventional commit message
        stages: [commit-msg]

  # Ruff for linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
        name: Run Ruff linter
      - id: ruff-format
        name: Run Ruff formatter

  # MyPy for type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        name: Run MyPy type checker
        additional_dependencies:
          - types-all
        args: [--config-file=pyproject.toml]

  # Detect secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        name: Detect secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-toml
```

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### IV. Initialize Detect Secrets Baseline

```bash
# Install detect-secrets
pip install detect-secrets

# Initialize baseline
detect-secrets scan > .secrets.baseline
```

### V. Create .gitignore

```
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

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Documentation
imgui-docs/
docs/_build/

# OS
.DS_Store
Thumbs.db

# Local development
.env
*.log
```

### VI. Commit Changes

```bash
# Stage all files
git add .

# Commit will trigger commitizen validation
git commit

# In the commit message editor, use:
# chore: add PR templates, commit templates, and pre-commit hooks
#
# - Add comprehensive pull request template for consistent PR descriptions
# - Add commit message template following conventional commits format
# - Configure pre-commit hooks for ruff, mypy, commitizen, and detect-secrets
# - Initialize detect-secrets baseline for security scanning
# - Add .gitignore for Python projects
#
# This is the first commit in the combined Stage 1-3 branch.

# Push branch (but don't create PR yet)
git push -u origin feat/setup-initial-infrastructure
```

**Note:** Do not create a PR yet. Continue to Stage 2 in the same branch.

---

## Stage 2: Versioning System

**Goal:** Configure commitizen with v prefix and set initial version to v0.0.0

**Note:** This stage continues in the same branch as Stage 1 (`feat/setup-initial-infrastructure`). This is the second commit in the combined Stage 1-3 branch.

### I. Update pyproject.toml - Version Configuration

Edit `pyproject.toml` and update the commitizen section:

```toml
# Commitizen configuration for conventional commits and semantic versioning
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.0.0"
tag_format = "v$version"  # Restore v prefix
version_files = [
    "pyproject.toml:version",
    "src/champi_imgui/__init__.py:__version__"
]
update_changelog_on_bump = true
changelog_file = "CHANGELOG.md"
changelog_incremental = true
changelog_start_rev = "v0.0.0"
changelog_merge_prerelease = true
bump_message = "bump: version $current_version → $new_version"
```

Also update the `[project]` section:

```toml
[project]
name = "champi-imgui"
version = "0.0.0"
```

### II. Initialize CHANGELOG.md

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.0.0 (2025-10-20)

### Feat

- Initial commit with repository structure
```

**Note:** This minimal changelog will be automatically updated by commitizen when versions are bumped. The actual features will be added in Stages 5-8.

### III. Install Commitizen

```bash
pip install commitizen
```

### IV. Commit Changes

```bash
git add .
git commit

# Commit message:
# chore: configure semantic versioning with commitizen
#
# - Set initial version to v0.0.0
# - Configure commitizen to use v prefix for tags (v$version)
# - Initialize CHANGELOG.md with unreleased features
# - Set up version files for automated version bumping
# - Configure incremental changelog generation
#
# This is the second commit in the combined Stage 1-3 branch.

# Push changes
git push origin feat/setup-initial-infrastructure
```

**Note:** Do not create a PR yet. Continue to Stage 3 in the same branch.

---

## Stage 3: Release Workflow

**Goal:** Set up automated GitHub Actions release workflow with v0.0.0 handling, and create the combined PR for stages 1-3

**Note:** This stage continues in the same branch as Stages 1-2 (`feat/setup-initial-infrastructure`). This stage will create the third and final commit, manually bump the version to v0.0.1, and create the PR for all three stages combined.

### I. Create GitHub Actions Workflows Directory

```bash
mkdir -p .github/workflows
```

### II. Create CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']

    steps:
    - name: Check out
      uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

    - name: Install uv
      uses: astral-sh/setup-uv@38f3f104447c67c051c4a08e39b64a148898af3a # v4.2.0

    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}

    - name: Install dependencies
      run: uv sync --all-extras --dev

    - name: Run ruff check
      run: uv run ruff check .

    - name: Run ruff format check
      run: uv run ruff format --check .

    - name: Run mypy
      run: uv run mypy src

    - name: Run tests
      run: uv run pytest

  security:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
    - name: Check out
      uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

    - name: Set up Python
      uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5.3.0
      with:
        python-version: '3.12'

    - name: Install detect-secrets
      run: pip install detect-secrets

    - name: Run detect-secrets scan
      run: |
        detect-secrets scan --baseline .secrets.baseline
        if [ $? -ne 0 ]; then
          echo "⚠️ Potential secrets detected! Please review the findings."
          exit 1
        fi
```

### III. Create Release Workflow with v0.0.0 Handling

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  release:
    name: Bump version and create release
    if: "!startsWith(github.event.head_commit.message, 'bump:')"
    runs-on: ubuntu-latest

    steps:
    - name: Check out
      uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      with:
        fetch-depth: 0
        token: ${{ secrets.RELEASE_TOKEN }}

    - name: Set up Python
      uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5.3.0
      with:
        python-version: '3.12'

    - name: Install commitizen
      run: pip install commitizen

    - name: Configure Git
      run: |
        git config --local user.name "Divagnz"
        git config --local user.email "oscar.liguori.bagnis@gmail.com"
        git config --local pull.rebase true

    - name: Run commitizen bump
      id: cz
      run: |
        # Get previous version
        PREV_REV=$(cz version --project)
        echo "Previous version: $PREV_REV"

        # Run commitizen bump with changelog
        # --no-raise 21: Don't fail on "No commits to bump" (exit code 21)
        cz --no-raise 21 bump --yes --changelog

        # Get new version
        REV=$(cz version --project)
        echo "New version: $REV"
        echo "version=v${REV}" >> $GITHUB_OUTPUT

        # Store whether version changed for later steps
        if [[ "$REV" != "$PREV_REV" ]]; then
          echo "version_changed=true" >> $GITHUB_OUTPUT
        else
          echo "version_changed=false" >> $GITHUB_OUTPUT
        fi

        # Extract incremental changelog for this version
        if [[ "$REV" != "$PREV_REV" ]]; then
          # Special handling for v0.0.0 (no previous version exists)
          if [[ "$PREV_REV" == "0.0.0" ]]; then
            echo "## v${REV}" > body.md
            echo "" >> body.md
            echo "Initial release" >> body.md
            echo "" >> body.md
            echo "See [CHANGELOG.md](CHANGELOG.md) for full details." >> body.md
          else
            # Extract changelog between versions
            sed -n "/## v${REV}/,/## v${PREV_REV}/p" CHANGELOG.md | sed '$d' > body.md

            # If body.md is empty, fall back to using the entire new version section
            if [[ ! -s body.md ]]; then
              sed -n "/## v${REV}/,/## /p" CHANGELOG.md | sed '$d' > body.md
            fi

            # If still empty, use a default message
            if [[ ! -s body.md ]]; then
              echo "Release v${REV}" > body.md
              echo "" >> body.md
              echo "See [CHANGELOG.md](CHANGELOG.md) for details." >> body.md
            fi
          fi

          echo "Incremental changelog:"
          cat body.md

          # Push commit and tags using authenticated URL
          git push https://Divagnz:${{ secrets.RELEASE_TOKEN }}@github.com/${{ github.repository }}.git HEAD:main --tags
        else
          echo "No version change, skipping release"
          echo "No changes" > body.md
        fi

    - name: Print Version
      run: echo "Bumped to version ${{ steps.cz.outputs.version }}"

    - name: Install uv
      uses: astral-sh/setup-uv@38f3f104447c67c051c4a08e39b64a148898af3a # v4.2.0

    - name: Set up Python for build
      run: uv python install 3.12

    - name: Build package
      if: steps.cz.outputs.version_changed == 'true'
      run: uv build

    - name: Create GitHub Release
      if: steps.cz.outputs.version_changed == 'true'
      uses: softprops/action-gh-release@6da8fa9354ddfdc4aeace5fc48d7f679b5214090 # v2.4.1
      with:
        body_path: body.md
        tag_name: ${{ steps.cz.outputs.version }}
        files: dist/*
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### IV. Manually Bump Version to 0.0.1

Before creating the final commit, manually set the version to 0.0.1:

```bash
# Update version in pyproject.toml (both [project] and [tool.commitizen] sections)
sed -i 's/version = "0.0.0"/version = "0.0.1"/' pyproject.toml

# Update version in __init__.py
sed -i 's/__version__ = "0.0.0"/__version__ = "0.0.1"/' src/champi_imgui/__init__.py

# Verify the changes
grep "version.*0.0.1" pyproject.toml
grep "__version__.*0.0.1" src/champi_imgui/__init__.py
```

### V. Commit and Create PR

```bash
git add .
git commit

# Commit message:
# chore: add automated release workflow with CI/CD
#
# - Add CI workflow for testing, linting, type checking, and security scanning
# - Add release workflow for automated version bumping and GitHub releases
# - Use commitizen for semantic versioning based on conventional commits
# - Handle v0.0.0 initial release gracefully
# - Use authenticated git push with RELEASE_TOKEN
# - Build and attach distribution artifacts to releases
# - Manually bump version to v0.0.1
#
# This is the third and final commit in the combined Stage 1-3 branch.

git push origin feat/setup-initial-infrastructure

gh pr create \
  --title "chore: setup initial infrastructure (templates, versioning, CI/CD)" \
  --body "$(cat <<'EOF'
## Summary

This PR combines Stages 1-3 of the migration plan to set up the initial repository infrastructure:

**Stage 1: Repository Foundation**
- PR templates and commit message templates
- Pre-commit hooks (ruff, mypy, commitizen, detect-secrets)
- .gitignore for Python projects

**Stage 2: Versioning System**
- Commitizen configuration with v prefix
- CHANGELOG.md initialization
- Version files configuration

**Stage 3: Release Workflow**
- CI workflow for testing, linting, and security scanning
- Release workflow for automated semantic versioning
- Manual version bump to v0.0.1

## Version

This PR manually sets the version to v0.0.1 for the initial infrastructure release.

## Test Plan

- Verify pre-commit hooks work
- Verify CI workflow runs successfully
- Verify release workflow is configured correctly
EOF
)"

# Merge PR
gh pr merge --squash --auto
```

---

## Stage 4: Documentation

**Goal:** Update all documentation with new repository information and add migration notes

**Note:** This stage creates a separate PR but uses `chore:` commits to avoid triggering a version bump. The repository will stay at v0.0.1 after this stage.

### Create Branch

```bash
git checkout main
git pull
git checkout -b docs/update-repository-references
```

### I. Update README.md

Ensure README.md has correct:
- Repository URLs
- Installation commands
- CLI commands
- Badge URLs (if any)

### II. Add Migration Plan to Documentation

The migration plan should already be in the repository (copied manually before LLM execution):

```bash
# Verify the file exists
ls MIGRATION_PLAN.md

# Stage for commit
git add MIGRATION_PLAN.md
```

### III. Update Documentation Files

Check and update all files in `docs/` directory:

```bash
# Find all markdown files and update references
find docs -name "*.md" -exec sed -i 's/champi-gen-ui/champi-imgui/g' {} +
find docs -name "*.md" -exec sed -i 's/champi_gen_ui/champi_imgui/g' {} +
```

### IV. Commit and Create PR

```bash
git add .
git commit

# Commit message:
# chore(docs): update all repository references and add migration plan
#
# - Update README with new repository URLs and commands
# - Update all documentation files with champi-imgui references
# - Add MIGRATION_PLAN.md documenting the migration from champi-gen-ui
#
# Note: Using chore: to avoid version bump. Repository stays at v0.0.1.

git push -u origin docs/update-repository-references

gh pr create \
  --title "chore(docs): update all repository references and add migration plan" \
  --body "Updates documentation with new repository information and preserves migration history. No version bump (stays at v0.0.1)."

# Merge PR
gh pr merge --squash --auto
```

---

## Stage 5: MCP Boilerplate + Canvas Rendering + IPC Communication

**Goal:** Implement MCP server infrastructure, ImGui canvas with non-blocking rendering, and IPC for dynamic updates

**Note:** This is the first feature PR. Uses `feat:` commits to trigger version bump from v0.0.1 → v0.1.0.

**Version:** v0.0.1 → v0.1.0

### Create Branch

```bash
git checkout main
git pull
git checkout -b feat/mcp-canvas-ipc
```

### Reference Materials

The following reference materials guide the implementation. Review these, assess integration, propose your plan, get user approval, then implement.

---

#### Reference 1: MCP Server Boilerplate

**Based on:** `src/champi_gen_ui/server/main.py:1-98`

**Core Pattern:**
```python
"""Main FastMCP server implementation."""

from fastmcp import FastMCP
from loguru import logger

from champi_imgui.core.canvas import CanvasManager

# Initialize FastMCP server with dependencies
mcp = FastMCP("champi-imgui", dependencies=["imgui-bundle", "pyglm"])

# Global managers
canvas_manager = CanvasManager()

# Helper function to ensure canvas is active
def _ensure_canvas_active(canvas_id: str) -> bool:
    """Ensure canvas exists and is running."""
    return canvas_manager.ensure_canvas_running(canvas_id)

# MCP Tool Example
@mcp.tool()
def create_canvas(
    canvas_id: str,
    width: int = 1280,
    height: int = 720,
    mode: str = "standard",
    title: str = "ImGui Canvas",
) -> dict[str, Any]:
    """Create a new canvas for rendering ImGui UI."""
    try:
        canvas = canvas_manager.create_canvas(
            canvas_id=canvas_id,
            width=width,
            height=height,
            mode=mode,
            title=title,
        )
        logger.info(f"Created canvas: {canvas_id}")
        return {"success": True, "data": canvas.serialize()}
    except Exception as e:
        logger.error(f"Error creating canvas: {e}")
        return {"success": False, "error": str(e)}

def create_server() -> FastMCP:
    """Create and return the FastMCP server instance."""
    return mcp

if __name__ == "__main__":
    mcp.run()
```

**Key Points:**
- FastMCP initialization with `dependencies` parameter
- Global manager instances (CanvasManager, etc.)
- Tool decorator pattern: `@mcp.tool()`
- Consistent error handling with try/except
- Return format: `{"success": bool, "data": dict, "error": str}`
- Logger integration (loguru)

---

#### Reference 2: Canvas with Threading and IPC

**Based on:** `src/champi_gen_ui/core/canvas.py:1-338`

**Canvas Class Pattern:**
```python
"""Canvas system for rendering UI."""

import threading
import time
from queue import Queue
from typing import Any, Callable

from imgui_bundle import hello_imgui, imgui, immapp
from loguru import logger

class Canvas:
    """Canvas for rendering ImGui UI."""

    def __init__(
        self,
        canvas_id: str,
        width: int = 1280,
        height: int = 720,
        mode: str = "standard",
        title: str = "ImGui Canvas",
    ):
        """Initialize canvas."""
        self.canvas_id = canvas_id
        self.width = width
        self.height = height
        self.mode = mode
        self.title = title
        self.widgets = {}

        # Threading and IPC
        self._running = False
        self._render_thread: threading.Thread | None = None
        self._command_queue: Queue = Queue()  # IPC mechanism

        logger.info(f"Created canvas {canvas_id} ({width}x{height}) in {mode} mode")

    def queue_command(self, command: Callable[[], Any]) -> None:
        """Queue a command for execution on the render thread (IPC)."""
        self._command_queue.put(command)

    def process_commands(self) -> None:
        """Process queued commands (called from render thread)."""
        while not self._command_queue.empty():
            try:
                command = self._command_queue.get_nowait()
                command()
            except Exception as e:
                logger.error(f"Error processing command: {e}")

    def render(self) -> None:
        """Render all widgets on the canvas."""
        # Begin ImGui window
        imgui.begin(self.title, None, imgui.WindowFlags_.no_collapse.value)

        # Render widgets
        for widget in self.widgets.values():
            widget.render()

        imgui.end()

    def run_async(self) -> None:
        """Run the canvas in non-blocking mode (for MCP server use)."""
        if self._running:
            logger.warning(f"Canvas {self.canvas_id} is already running")
            return

        self._running = True

        def render_loop():
            """Background rendering loop."""
            logger.info(f"Starting async render loop for canvas {self.canvas_id}")

            def gui_func():
                if self._running:
                    self.process_commands()  # Process IPC commands
                    self.render()  # Render widgets

            try:
                # Run ImGui loop (this blocks until window closed)
                immapp.run(
                    gui_function=gui_func,
                    window_title=self.title,
                    window_size=(self.width, self.height),
                    fps_idle=60,
                )
            except Exception as e:
                logger.error(f"Error in render loop: {e}")
            finally:
                self._running = False
                logger.info(f"Render loop stopped for canvas {self.canvas_id}")

        # Start render thread
        self._render_thread = threading.Thread(
            target=render_loop,
            name=f"Canvas-{self.canvas_id}",
            daemon=True
        )
        self._render_thread.start()
        time.sleep(0.1)  # Give thread time to initialize

    def stop(self) -> None:
        """Stop the canvas."""
        self._running = False

    def add_widget(self, widget) -> None:
        """Add a widget to the canvas."""
        self.widgets[widget.widget_id] = widget
        logger.debug(f"Added widget {widget.widget_id}")

    def serialize(self) -> dict:
        """Serialize canvas state to dictionary."""
        return {
            "canvas_id": self.canvas_id,
            "size": (self.width, self.height),
            "mode": self.mode,
            "title": self.title,
            "widgets": {wid: w.serialize() for wid, w in self.widgets.items()}
        }
```

**Key Points:**
- Threading with `daemon=True` for non-blocking execution
- Command queue (`Queue`) for IPC between MCP server and render thread
- `queue_command()` adds commands from MCP tools
- `process_commands()` executes commands on render thread
- `run_async()` starts background rendering loop
- `immapp.run()` is the ImGui main loop (blocking)

---

#### Reference 3: CanvasManager

**Based on:** `src/champi_gen_ui/core/canvas.py:230-338`

**CanvasManager Pattern:**
```python
class CanvasManager:
    """Manager for multiple canvases."""

    def __init__(self):
        """Initialize canvas manager."""
        self.canvases: dict[str, Canvas] = {}
        self.active_canvas: str | None = None
        self._auto_start = True  # Auto-start canvases for MCP use

    def create_canvas(self, canvas_id: str, **props) -> Canvas:
        """Create a new canvas."""
        if canvas_id in self.canvases:
            raise ValueError(f"Canvas {canvas_id} already exists")

        canvas = Canvas(canvas_id, **props)
        self.canvases[canvas_id] = canvas

        # Set as active if first canvas
        if self.active_canvas is None:
            self.active_canvas = canvas_id

        # Auto-start canvas
        if self._auto_start:
            canvas.run_async()

        logger.info(f"Created canvas {canvas_id}")
        return canvas

    def get_canvas(self, canvas_id: str) -> Canvas | None:
        """Get a canvas by ID."""
        return self.canvases.get(canvas_id)

    def ensure_canvas_running(self, canvas_id: str) -> bool:
        """Ensure a canvas is running, start it if not."""
        canvas = self.get_canvas(canvas_id)
        if not canvas:
            return False

        if not canvas._running:
            logger.info(f"Auto-starting canvas {canvas_id}")
            canvas.run_async()

        return True

    def list_canvases(self) -> list[str]:
        """List all canvas IDs."""
        return list(self.canvases.keys())
```

**Key Points:**
- Manages multiple canvases
- Auto-start feature for MCP server use
- `ensure_canvas_running()` for lazy initialization

---

### Implementation Steps

#### I. Review Reference Materials
- Study the MCP server pattern
- Understand Canvas threading and IPC mechanism
- Review CanvasManager multi-canvas support

#### II. Propose Implementation Plan
**⏸️ STOP - User Confirmation Required**

Before implementing, propose your plan:
- How you'll structure the MCP server
- Any simplifications to the threading model
- Canvas lifecycle management approach
- Wait for user approval

#### III. Implement MCP Server
Create `src/champi_imgui/server/main.py`:
- FastMCP initialization
- CanvasManager instance
- Basic MCP tools: `create_canvas`, `get_canvas_state`, `clear_canvas`, `list_canvases`

#### IV. Implement Canvas System
Create `src/champi_imgui/core/canvas.py`:
- Canvas class with threading
- Command queue for IPC
- Async rendering loop
- CanvasManager

#### V. Test Functionality
```bash
# Start MCP server
python -m champi_imgui.server.main

# Test canvas creation (via MCP client or Claude)
# Verify canvas opens in separate window
# Verify canvas responds to commands dynamically
```

#### VI. Validate
```bash
# Linters
ruff check src/
ruff format --check src/

# Type checking
mypy src/

# Tests
pytest tests/
```

#### VII. Fix Issues
- Fix any linter errors
- Fix type annotation issues
- Ensure all tests pass

### VIII. Commit and Create PR

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: add MCP server with canvas rendering and IPC

- Implement FastMCP server boilerplate with champi-imgui namespace
- Add Canvas class with non-blocking rendering using threading
- Implement IPC communication via command queue for dynamic updates
- Add CanvasManager for multi-canvas support with auto-start
- Create MCP tools: create_canvas, get_canvas_state, clear_canvas, list_canvases
- Integrate loguru for structured logging

This is the first feature release, bumping from v0.0.1 to v0.1.0.
EOF
)"

git push -u origin feat/mcp-canvas-ipc

gh pr create \
  --title "feat: add MCP server with canvas rendering and IPC" \
  --body "$(cat <<'EOF'
## Summary

Implements the core MCP server infrastructure with ImGui canvas rendering and IPC communication.

**MCP Server:**
- FastMCP initialization with imgui-bundle and pyglm dependencies
- Canvas management tools registered as MCP tools
- Consistent error handling and response format

**Canvas System:**
- Non-blocking async rendering using threading
- IPC via command queue for dynamic canvas updates
- CanvasManager for multi-canvas support
- Auto-start feature for seamless MCP integration

**IPC Communication:**
- Command queue pattern for thread-safe updates
- MCP tools can dynamically update running canvases
- Process commands on render thread to avoid race conditions

## Version

This PR triggers a version bump from v0.0.1 to v0.1.0 (first minor release).

## Test Plan

- [x] MCP server starts successfully
- [x] Canvas opens in separate window
- [x] Canvas responds to MCP commands dynamically
- [x] Multiple canvases can be created
- [x] Linters pass (ruff)
- [x] Type checking passes (mypy)
- [x] Tests pass (pytest)
EOF
)"

# Merge PR
gh pr merge --squash --auto
```

---

## Stage 6: Core Widget System

**Goal:** Implement widget infrastructure and basic widget types

**Note:** Uses `feat:` commits to trigger version bump from v0.1.0 → v0.2.0.

**Version:** v0.1.0 → v0.2.0

### Create Branch

```bash
git checkout main
git pull
git checkout -b feat/core-widget-system
```

### Reference Materials

The following reference materials guide the implementation. Review these, assess integration, propose your plan, get user approval, then implement.

---

#### Reference 1: Widget Base Class and Factory Pattern

**Based on:** `src/champi_gen_ui/core/widget.py:1-100`

**Widget Base Class Pattern:**
```python
"""Base widget class and registry."""

from abc import ABC, abstractmethod
from typing import Any, Callable

from loguru import logger

class Widget(ABC):
    """Base class for all widgets."""

    def __init__(self, widget_id: str, **props):
        """Initialize widget."""
        self.widget_id = widget_id
        self.widget_type = self.__class__.__name__
        self.properties = props
        self.visible = True
        self.enabled = True
        self.position: tuple[float, float] | None = None
        self._callbacks: dict[str, Callable] = {}

    @abstractmethod
    def render(self) -> Any:
        """Render the widget using ImGui calls."""
        pass

    def set_position(self, x: float, y: float) -> None:
        """Set widget position."""
        self.position = (x, y)

    def set_visible(self, visible: bool) -> None:
        """Set widget visibility."""
        self.visible = visible

    def serialize(self) -> dict[str, Any]:
        """Serialize widget state to dictionary."""
        return {
            "widget_id": self.widget_id,
            "widget_type": self.widget_type,
            "visible": self.visible,
            "enabled": self.enabled,
            "position": self.position,
            "properties": self.properties
        }


class WidgetFactory:
    """Factory for creating widgets."""

    def __init__(self):
        """Initialize factory."""
        self._creators: dict[str, type[Widget]] = {}

    def register(self, widget_type: str, creator: type[Widget]) -> None:
        """Register a widget creator."""
        self._creators[widget_type] = creator
        logger.info(f"Registered widget type: {widget_type}")

    def create(self, widget_type: str, widget_id: str, **props) -> Widget:
        """Create a widget instance."""
        creator = self._creators.get(widget_type)
        if not creator:
            raise ValueError(f"Unknown widget type: {widget_type}")

        widget = creator(widget_id, **props)
        logger.debug(f"Created widget {widget_id} of type {widget_type}")
        return widget


class WidgetRegistry:
    """Registry for managing widget instances."""

    def __init__(self):
        """Initialize registry."""
        self._widgets: dict[str, Widget] = {}
        self.factory = WidgetFactory()

    def add(self, widget: Widget) -> None:
        """Add a widget to the registry."""
        self._widgets[widget.widget_id] = widget

    def get(self, widget_id: str) -> Widget | None:
        """Get a widget by ID."""
        return self._widgets.get(widget_id)

    def remove(self, widget_id: str) -> bool:
        """Remove a widget."""
        if widget_id in self._widgets:
            del self._widgets[widget_id]
            return True
        return False

    def get_all(self) -> dict[str, Widget]:
        """Get all widgets."""
        return self._widgets
```

**Key Points:**
- ABC (Abstract Base Class) for type safety
- All widgets must implement `render()`
- Factory pattern for widget creation
- Registry pattern for widget management
- Serialization support

---

#### Reference 2: Basic Widget Implementations

**Based on:** `src/champi_gen_ui/widgets/basic.py`

**Button Widget Example:**
```python
from imgui_bundle import imgui
from champi_imgui.core.widget import Widget

class ButtonWidget(Widget):
    """Button widget."""

    def __init__(self, widget_id: str, label: str = "Button", size: tuple[float, float] | None = None, **props):
        super().__init__(widget_id, label=label, size=size, **props)
        self.label = label
        self.size = size or (0, 0)
        self.clicked = False

    def render(self) -> bool:
        """Render button and return click state."""
        self.clicked = imgui.button(self.label, self.size)
        return self.clicked
```

**Text Widget Example:**
```python
class TextWidget(Widget):
    """Text display widget."""

    def __init__(self, widget_id: str, text: str = "", color: tuple[float, float, float, float] | None = None, wrapped: bool = False, **props):
        super().__init__(widget_id, text=text, color=color, wrapped=wrapped, **props)
        self.text = text
        self.color = color
        self.wrapped = wrapped

    def render(self) -> None:
        """Render text."""
        if self.wrapped:
            imgui.text_wrapped(self.text)
        else:
            imgui.text(self.text)
```

**Input Text Widget Example:**
```python
class InputTextWidget(Widget):
    """Text input widget."""

    def __init__(self, widget_id: str, label: str = "Input", value: str = "", hint: str | None = None, multiline: bool = False, **props):
        super().__init__(widget_id, label=label, value=value, hint=hint, multiline=multiline, **props)
        self.label = label
        self.value = value
        self.hint = hint
        self.multiline = multiline

    def render(self) -> str:
        """Render input field and return current value."""
        if self.multiline:
            changed, self.value = imgui.input_text_multiline(
                self.label,
                self.value,
                imgui.ImVec2(0, 0)
            )
        else:
            if self.hint:
                changed, self.value = imgui.input_text_with_hint(
                    self.label,
                    self.hint,
                    self.value
                )
            else:
                changed, self.value = imgui.input_text(self.label, self.value)

        return self.value
```

**Checkbox Widget Example:**
```python
class CheckboxWidget(Widget):
    """Checkbox widget."""

    def __init__(self, widget_id: str, label: str = "Checkbox", checked: bool = False, **props):
        super().__init__(widget_id, label=label, checked=checked, **props)
        self.label = label
        self.checked = checked

    def render(self) -> bool:
        """Render checkbox and return checked state."""
        changed, self.checked = imgui.checkbox(self.label, self.checked)
        return self.checked
```

**Key Points:**
- Each widget extends `Widget` base class
- `__init__` stores widget-specific properties
- `render()` makes ImGui calls and returns widget state
- ImGui functions return `(changed, value)` tuples

---

#### Reference 3: Slider Widgets

**Based on:** `src/champi_gen_ui/widgets/slider.py`

**Slider Float Example:**
```python
class SliderFloatWidget(Widget):
    """Float slider widget."""

    def __init__(self, widget_id: str, label: str = "Slider", value: float = 0.0, v_min: float = 0.0, v_max: float = 1.0, **props):
        super().__init__(widget_id, label=label, value=value, v_min=v_min, v_max=v_max, **props)
        self.label = label
        self.value = value
        self.v_min = v_min
        self.v_max = v_max

    def render(self) -> float:
        """Render slider and return current value."""
        changed, self.value = imgui.slider_float(
            self.label,
            self.value,
            self.v_min,
            self.v_max
        )
        return self.value
```

**Slider Int Example:**
```python
class SliderIntWidget(Widget):
    """Integer slider widget."""

    def __init__(self, widget_id: str, label: str = "Slider", value: int = 0, v_min: int = 0, v_max: int = 100, **props):
        super().__init__(widget_id, label=label, value=value, v_min=v_min, v_max=v_max, **props)
        self.label = label
        self.value = value
        self.v_min = v_min
        self.v_max = v_max

    def render(self) -> int:
        """Render slider and return current value."""
        changed, self.value = imgui.slider_int(
            self.label,
            self.value,
            self.v_min,
            self.v_max
        )
        return self.value
```

---

#### Reference 4: MCP Tool Integration Pattern

**Based on:** `src/champi_gen_ui/server/main.py:107-538`

**Widget Factory Registration:**
```python
def register_widgets():
    """Register all widget types with factories."""
    for canvas in canvas_manager.canvases.values():
        registry = canvas.widget_registry
        registry.factory.register("button", ButtonWidget)
        registry.factory.register("text", TextWidget)
        registry.factory.register("input_text", InputTextWidget)
        registry.factory.register("checkbox", CheckboxWidget)
        registry.factory.register("slider_float", SliderFloatWidget)
        registry.factory.register("slider_int", SliderIntWidget)
```

**MCP Tool Example (add_button):**
```python
@mcp.tool()
def add_button(
    canvas_id: str,
    widget_id: str,
    label: str = "Button",
    position: list[float] | None = None,
    size: list[float] | None = None,
) -> dict[str, Any]:
    """Add a button widget to the canvas."""
    try:
        canvas = canvas_manager.get_canvas(canvas_id)
        if not canvas:
            return {"success": False, "error": f"Canvas {canvas_id} not found"}

        # Ensure canvas is running
        canvas_manager.ensure_canvas_running(canvas_id)

        # Create widget via factory
        widget = canvas.widget_registry.factory.create(
            "button", widget_id, label=label, size=size
        )

        # Set position if specified
        if position:
            widget.set_position(*position)

        # Add to canvas
        canvas.add_widget(widget)

        return {"success": True, "data": widget.serialize()}
    except Exception as e:
        logger.error(f"Error adding button: {e}")
        return {"success": False, "error": str(e)}
```

**Key Pattern for All Widget Tools:**
1. Get canvas from manager
2. Ensure canvas is running
3. Create widget via factory
4. Set position if provided
5. Add widget to canvas
6. Return serialized widget state

---

### Implementation Steps

#### I. Review Reference Materials
- Study Widget base class with ABC pattern
- Review widget implementations (Button, Text, Input, Checkbox, Sliders)
- Understand factory and registry patterns
- Review MCP tool integration

#### II. Propose Implementation Plan
**⏸️ STOP - User Confirmation Required**

Before implementing, propose your plan:
- Widget class hierarchy
- Which widgets to implement first
- Factory registration approach
- MCP tool structure
- Wait for user approval

#### III. Implement Widget Infrastructure
Create `src/champi_imgui/core/widget.py`:
- Widget base class (ABC)
- WidgetFactory
- WidgetRegistry

#### IV. Implement Basic Widgets
Create `src/champi_imgui/widgets/basic.py`:
- ButtonWidget
- TextWidget
- InputTextWidget
- CheckboxWidget
- ColorPickerWidget

#### V. Implement Slider Widgets
Create `src/champi_imgui/widgets/slider.py`:
- SliderFloatWidget
- SliderIntWidget

#### VI. Register Widget Factories
Update `src/champi_imgui/server/main.py`:
- Add `register_widgets()` function
- Call it after canvas creation

#### VII. Create MCP Tools
Add to `src/champi_imgui/server/main.py`:
- `add_button`
- `add_text`
- `add_input_text`
- `add_checkbox`
- `add_slider_float`
- `add_slider_int`
- `add_color_picker`

#### VIII. Integrate with Canvas
Update Canvas.add_widget() to work with new Widget system

#### IX. Test Functionality
```bash
# Start MCP server
python -m champi_imgui.server.main

# Test widget creation via MCP
# Verify widgets render correctly
# Test widget interactions
```

#### X. Validate
```bash
# Linters
ruff check src/
ruff format --check src/

# Type checking
mypy src/

# Tests
pytest tests/
```

#### XI. Fix Issues
- Fix any linter errors
- Fix type annotations
- Ensure all tests pass

### XII. Commit and Create PR

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: add core widget system

- Implement Widget base class with ABC pattern
- Add WidgetFactory for widget creation
- Add WidgetRegistry for widget management
- Implement basic widgets: Button, Text, InputText, Checkbox
- Implement slider widgets: SliderFloat, SliderInt
- Add ColorPicker widget
- Create MCP tools for all widget types
- Integrate widgets with Canvas rendering

This PR bumps version from v0.1.0 to v0.2.0.
EOF
)"

git push -u origin feat/core-widget-system

gh pr create \
  --title "feat: add core widget system" \
  --body "$(cat <<'EOF'
## Summary

Implements the core widget infrastructure and basic widget types.

**Widget Infrastructure:**
- Widget base class using ABC for type safety
- WidgetFactory for flexible widget creation
- WidgetRegistry for widget lifecycle management
- Serialization support for all widgets

**Basic Widgets:**
- ButtonWidget - clickable buttons
- TextWidget - text display with wrapping
- InputTextWidget - text input with hints and multiline support
- CheckboxWidget - boolean selection
- ColorPickerWidget - RGBA color selection

**Slider Widgets:**
- SliderFloatWidget - float value selection
- SliderIntWidget - integer value selection

**MCP Integration:**
- MCP tools for all widget types
- Consistent error handling
- Widget factory registration system

## Version

This PR triggers a version bump from v0.1.0 to v0.2.0.

## Test Plan

- [x] Widget creation via MCP tools works
- [x] Widgets render correctly on canvas
- [x] Widget interactions function properly
- [x] Position setting works
- [x] Serialization/deserialization works
- [x] Linters pass (ruff)
- [x] Type checking passes (mypy)
- [x] Tests pass (pytest)
EOF
)"

# Merge PR
gh pr merge --squash --auto
```

---

## Stage 7: Advanced UI Features

**Goal:** Implement themes, layouts, menus, display widgets, plotting, animations, data binding, file dialogs, and notifications

**Note:** Uses `feat:` commits to trigger version bump from v0.2.0 → v0.3.0.

**Version:** v0.2.0 → v0.3.0

### Create Branch

```bash
git checkout main
git pull
git checkout -b feat/advanced-ui-features
```

### Reference Materials

Concise references for implementing advanced features. Review, assess, propose plan, get approval, implement.

---

#### Reference 1: Themes System

**Based on:** `src/champi_gen_ui/themes/manager.py`, `src/champi_gen_ui/themes/presets.py`

```python
class ThemeManager:
    def __init__(self):
        self._themes: dict[str, Theme] = {}

    def register_theme(self, theme: Theme):
        self._themes[theme.name] = theme

    def apply_theme_by_name(self, name: str):
        theme = self._themes.get(name)
        if theme:
            theme.apply()  # Sets ImGui style colors

# Preset themes: dark, light, cherry, nord, dracula, gruvbox, solarized_dark, monokai, material

# MCP Tools
@mcp.tool()
def apply_theme(theme_name: str) -> dict:
    theme_manager.apply_theme_by_name(theme_name)
    return {"success": True}
```

---

#### Reference 2: Layout System

**Based on:** `src/champi_gen_ui/layout/manager.py`

```python
from enum import Enum

class LayoutMode(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    GRID = "grid"
    STACK = "stack"
    FREE = "free"

class LayoutManager:
    def __init__(self):
        self.mode = LayoutMode.FREE
        self.spacing = 0.0

    def set_mode(self, mode: LayoutMode):
        self.mode = mode

    def set_spacing(self, spacing: float):
        self.spacing = spacing
```

---

#### Reference 3: Menu Widgets

**Based on:** `src/champi_gen_ui/widgets/menu.py`

```python
class MenuBarWidget(Widget):
    def render(self):
        if imgui.begin_main_menu_bar():
            # Render menu items
            imgui.end_main_menu_bar()

class MenuWidget(Widget):
    def __init__(self, widget_id, label="Menu", enabled=True, **props):
        super().__init__(widget_id, label=label, enabled=enabled, **props)
        self.label = label
        self.enabled = enabled

    def render(self):
        if imgui.begin_menu(self.label, self.enabled):
            # Render menu items
            imgui.end_menu()
```

---

#### Reference 4: Plotting Widgets (ImPlot)

**Based on:** `src/champi_gen_ui/widgets/plotting.py`

```python
from imgui_bundle import implot

class LineChartWidget(Widget):
    def __init__(self, widget_id, title="Line Chart", x_data=None, y_data=None, **props):
        super().__init__(widget_id, title=title, x_data=x_data, y_data=y_data, **props)
        self.title = title
        self.x_data = x_data or []
        self.y_data = y_data or []

    def render(self):
        if implot.begin_plot(self.title):
            implot.plot_line("data", self.x_data, self.y_data)
            implot.end_plot()

# Similar patterns for: BarChartWidget, ScatterPlotWidget, PieChartWidget, HeatmapWidget
```

---

#### Reference 5: Animations

**Based on:** `src/champi_gen_ui/extensions/animation.py`

```python
from enum import Enum

class EasingFunction(Enum):
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    # ... more easing functions

class AnimationManager:
    def __init__(self):
        self._animations = {}

    def create(self, name, start_value, end_value, duration, easing, loop=False):
        self._animations[name] = {
            "start": start_value,
            "end": end_value,
            "duration": duration,
            "easing": easing,
            "loop": loop,
            "running": False
        }

    def start(self, name):
        if name in self._animations:
            self._animations[name]["running"] = True

    def get_value(self, name):
        # Calculate interpolated value based on time and easing
        pass
```

---

#### Reference 6: Data Binding

**Based on:** `src/champi_gen_ui/core/binding.py`

```python
class DataStore:
    def __init__(self):
        self._data = {}

    def set(self, path: str, value):
        # Set data at path (e.g., "user.name")
        keys = path.split(".")
        current = self._data
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

    def get(self, path: str, default=None):
        # Get data from path
        keys = path.split(".")
        current = self._data
        for key in keys:
            current = current.get(key)
            if current is None:
                return default
        return current

class BindingManager:
    def __init__(self, data_store):
        self.data_store = data_store
        self._bindings = {}

    def bind(self, source_path, target_widget, target_property, bidirectional=False):
        # Create binding between data and widget
        pass
```

---

#### Reference 7: File Dialogs & Notifications

**Based on:** `src/champi_gen_ui/extensions/file_dialog.py`, `notification.py`

```python
class FileDialogWidget(Widget):
    def __init__(self, widget_id, button_label="Browse...", mode="open_file", **props):
        super().__init__(widget_id, **props)
        self.button_label = button_label
        self.mode = mode  # open_file, open_folder, save_file
        self.selected_path = None

class NotificationManager:
    def __init__(self):
        self._notifications = []

    def add(self, title, message, type, duration):
        self._notifications.append({
            "title": title,
            "message": message,
            "type": type,
            "duration": duration
        })
```

---

### Implementation Steps

**I. Review References** → **II. Propose Plan (⏸️ STOP for approval)** → **III-X. Implement Features** → **XI. Validate (linters, mypy, tests)** → **XII. Fix Issues**

Implement in this order:
1. Themes and Layouts
2. Menu and Display Widgets
3. Plotting Widgets (ImPlot integration)
4. Animations
5. Data Binding
6. File Dialogs and Notifications

### XIII. Commit and Create PR

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: add advanced UI features

- Implement theme system with 9 preset themes
- Add layout manager (horizontal, vertical, grid, stack, free)
- Create menu widgets (MenuBar, Menu, MenuItem, Selectable, TreeNode)
- Add display widgets (ColoredText, BulletText, HelpMarker, ProgressBar)
- Integrate ImPlot for plotting (Line, Bar, Scatter, Pie, Heatmap)
- Implement animation system with easing functions
- Add data binding with reactive DataStore and BindingManager
- Create file dialog widget for file/folder selection
- Add notification system for toast messages
- Register all MCP tools for new features

This PR bumps version from v0.2.0 to v0.3.0.
EOF
)"

git push -u origin feat/advanced-ui-features

gh pr create \
  --title "feat: add advanced UI features" \
  --body "$(cat <<'EOF'
## Summary

Implements advanced UI features including themes, layouts, plotting, animations, and data binding.

**Themes & Layouts:**
- 9 preset themes (dark, light, cherry, nord, dracula, gruvbox, solarized, monokai, material)
- Layout modes for widget positioning
- Theme and layout MCP tools

**Menu & Display Widgets:**
- MenuBar, Menu, MenuItem for application menus
- Selectable, TreeNode for hierarchical data
- ColoredText, BulletText, HelpMarker, ProgressBar

**Plotting (ImPlot):**
- LineChart, BarChart, ScatterPlot
- PieChart, Heatmap
- Full ImPlot integration

**Animations:**
- AnimationManager with easing functions
- Create, start, stop, get_value MCP tools

**Data Binding:**
- Reactive DataStore with path-based access
- BindingManager for widget-data synchronization
- set_data, get_data, bind_data, unbind_data MCP tools

**Extensions:**
- FileDialog for file/folder selection
- NotificationManager for toast messages

## Version

This PR triggers a version bump from v0.2.0 to v0.3.0.

## Test Plan

- [x] Themes apply correctly
- [x] Layout modes work
- [x] Menu widgets render
- [x] Plotting widgets display charts
- [x] Animations run smoothly
- [x] Data binding updates widgets
- [x] File dialogs open
- [x] Notifications display
- [x] Linters pass
- [x] Type checking passes
- [x] Tests pass
EOF
)"

# Merge PR
gh pr merge --squash --auto
```

---

## Stage 8: Export, Serialization & Templates

**Goal:** Implement JSON/Python export, code generation, and template system

**Note:** Uses `feat:` commits to trigger version bump from v0.3.0 → v0.4.0. Final feature stage.

**Version:** v0.3.0 → v0.4.0

### Create Branch

```bash
git checkout main
git pull
git checkout -b feat/export-serialization
```

### Reference Materials

Concise references for export and serialization systems.

---

#### Reference 1: JSON Serialization

**Based on:** `src/champi_gen_ui/core/serialization.py`

```python
import json

class UIExporter:
    @staticmethod
    def export_to_json(canvas, filepath: str) -> bool:
        """Export canvas to JSON file."""
        try:
            data = canvas.serialize()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    @staticmethod
    def export_canvas_state(canvas) -> str:
        """Get canvas as JSON string."""
        return json.dumps(canvas.serialize(), indent=2)

class UIImporter:
    @staticmethod
    def import_from_json(filepath: str, canvas_manager) -> Canvas | None:
        """Import canvas from JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Create canvas
            canvas = canvas_manager.create_canvas(
                canvas_id=data['canvas_id'],
                width=data['size'][0],
                height=data['size'][1],
                mode=data['mode'],
                title=data['title']
            )

            # Recreate widgets
            for widget_data in data['widgets'].values():
                # Recreate widget from data
                pass

            return canvas
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return None

# MCP Tools
@mcp.tool()
def export_canvas_json(canvas_id: str, filepath: str) -> dict:
    canvas = canvas_manager.get_canvas(canvas_id)
    success = UIExporter.export_to_json(canvas, filepath)
    return {"success": success}
```

---

#### Reference 2: Code Generation

**Based on:** `src/champi_gen_ui/core/codegen.py`

```python
class CodeGenerator:
    @staticmethod
    def generate_canvas_code(canvas) -> str:
        """Generate Python code for canvas."""
        code = []

        # Imports
        code.append("from champi_imgui.core.canvas import CanvasManager")
        code.append("from champi_imgui.widgets.basic import ButtonWidget, TextWidget")
        code.append("")

        # Create canvas
        code.append("# Create canvas")
        code.append(f"canvas_manager = CanvasManager()")
        code.append(f"canvas = canvas_manager.create_canvas(")
        code.append(f"    canvas_id='{canvas.canvas_id}',")
        code.append(f"    width={canvas.width},")
        code.append(f"    height={canvas.height}")
        code.append(")")
        code.append("")

        # Add widgets
        code.append("# Add widgets")
        for widget in canvas.widgets.values():
            widget_code = CodeGenerator.generate_widget_code_snippet(
                widget.widget_type,
                widget.widget_id,
                **widget.properties
            )
            code.append(widget_code)

        return "\n".join(code)

    @staticmethod
    def generate_widget_code_snippet(widget_type, widget_id, **props) -> str:
        """Generate code snippet for a widget."""
        props_str = ", ".join(f"{k}={repr(v)}" for k, v in props.items())
        return f"{widget_type}('{widget_id}', {props_str})"

class TemplateCodeGenerator:
    @staticmethod
    def generate_component_template(name: str, widgets: list[str]) -> str:
        """Generate reusable component template."""
        code = []
        code.append(f"class {name}Component:")
        code.append("    def __init__(self, canvas):")
        code.append("        self.canvas = canvas")
        code.append("")
        code.append("    def create_widgets(self):")
        for widget in widgets:
            code.append(f"        # Add {widget}")
        return "\n".join(code)

# MCP Tools
@mcp.tool()
def generate_canvas_code(canvas_id: str) -> dict:
    canvas = canvas_manager.get_canvas(canvas_id)
    code = CodeGenerator.generate_canvas_code(canvas)
    return {"success": True, "data": {"code": code}}
```

---

#### Reference 3: Template System

**Based on:** `src/champi_gen_ui/core/serialization.py`

```python
import os
import json

class TemplateManager:
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        os.makedirs(template_dir, exist_ok=True)

    def save_template(self, name: str, canvas, description: str = "") -> bool:
        """Save canvas as template."""
        try:
            template_data = {
                "name": name,
                "description": description,
                "canvas": canvas.serialize()
            }

            filepath = os.path.join(self.template_dir, f"{name}.json")
            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Save template failed: {e}")
            return False

    def load_template(self, name: str, canvas_manager) -> Canvas | None:
        """Load template."""
        try:
            filepath = os.path.join(self.template_dir, f"{name}.json")
            with open(filepath, 'r') as f:
                template_data = json.load(f)

            # Import canvas from template
            return UIImporter.import_from_json(filepath, canvas_manager)
        except Exception as e:
            logger.error(f"Load template failed: {e}")
            return None

    def list_templates(self) -> list[dict]:
        """List available templates."""
        templates = []
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.template_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    templates.append({
                        "name": data["name"],
                        "description": data.get("description", "")
                    })
        return templates

    def delete_template(self, name: str) -> bool:
        """Delete template."""
        try:
            filepath = os.path.join(self.template_dir, f"{name}.json")
            os.remove(filepath)
            return True
        except Exception as e:
            logger.error(f"Delete template failed: {e}")
            return False

# MCP Tools
@mcp.tool()
def save_template(name: str, canvas_id: str, description: str = "") -> dict:
    canvas = canvas_manager.get_canvas(canvas_id)
    success = template_manager.save_template(name, canvas, description)
    return {"success": success}
```

---

### Implementation Steps

**I. Review References** → **II. Propose Plan (⏸️ STOP for approval)** → **III-VIII. Implement** → **IX. Validate** → **X. Fix Issues**

Implement in this order:
1. UIExporter/UIImporter (JSON serialization)
2. CodeGenerator (Python code generation)
3. TemplateManager (template save/load/list/delete)
4. MCP tools for all export/import/generation features

### XI. Commit and Create PR

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: add export, serialization and template system

- Implement UIExporter for JSON export (export_to_json, export_canvas_state)
- Implement UIImporter for JSON import (import_from_json)
- Add CodeGenerator for Python code generation
- Implement TemplateCodeGenerator for component templates
- Create TemplateManager for template save/load/list/delete
- Add MCP tools: export_canvas_json, export_canvas_python, import_canvas_json
- Add MCP tools: get_canvas_json, generate_canvas_code, generate_widget_snippet
- Add MCP tools: save_template, load_template, list_templates, delete_template
- Support full canvas state serialization

This PR bumps version from v0.3.0 to v0.4.0 (final feature release).
EOF
)"

git push -u origin feat/export-serialization

gh pr create \
  --title "feat: add export, serialization and template system" \
  --body "$(cat <<'EOF'
## Summary

Implements export, serialization, code generation, and template management.

**JSON Serialization:**
- UIExporter for exporting canvases to JSON
- UIImporter for importing canvases from JSON
- Full state preservation (widgets, properties, bindings)
- File and string export options

**Code Generation:**
- CodeGenerator for standalone Python scripts
- Generate clean, runnable code from UI definitions
- TemplateCodeGenerator for reusable components
- Proper imports and code formatting

**Template System:**
- TemplateManager for template lifecycle
- Save canvases as reusable templates
- Load templates to recreate UIs
- List and delete templates
- Template descriptions and metadata

**MCP Tools:**
- export_canvas_json, export_canvas_python
- import_canvas_json, get_canvas_json
- generate_canvas_code, generate_widget_snippet, generate_component_template
- save_template, load_template, list_templates, delete_template

## Version

This PR triggers a version bump from v0.3.0 to v0.4.0 (final feature release).

## Test Plan

- [x] JSON export creates valid files
- [x] JSON import recreates canvases correctly
- [x] Generated Python code runs successfully
- [x] Templates save and load correctly
- [x] Template list shows all templates
- [x] Template delete removes templates
- [x] All MCP tools function properly
- [x] Linters pass
- [x] Type checking passes
- [x] Tests pass
EOF
)"

# Merge PR
gh pr merge --squash --auto
```

---

## Verification Steps

After completing all stages, verify the setup:

### 1. Local Testing

```bash
# Clone fresh copy
git clone git@github.com:champi-ai/champi-imgui.git
cd champi-imgui

# Install dependencies
pip install uv
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format --check .

# Run type checking
uv run mypy src

# Test CLI
uv run champi-imgui --help
```

### 2. Pre-commit Hooks Testing

```bash
# Install hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Test hooks
pre-commit run --all-files

# Test commit message validation
git commit --allow-empty -m "invalid message"  # Should fail
git commit --allow-empty -m "feat: valid message"  # Should pass
```

### 3. Release Workflow Testing

```bash
# Create a test feature
git checkout -b feat/test-release-workflow
echo "# Test" > TEST.md
git add TEST.md
git commit -m "feat: test release workflow"
git push -u origin feat/test-release-workflow

# Create and merge PR
gh pr create --title "feat: test release workflow" --body "Testing automated releases"
gh pr merge --squash --auto

# Wait for release workflow to complete
# Check: https://github.com/champi-ai/champi-imgui/actions

# Verify release created at: https://github.com/champi-ai/champi-imgui/releases
# Should create v0.1.0 with changelog and distribution files
```

### 4. Version Bump Testing

```bash
# Verify version was bumped
git pull
cat pyproject.toml | grep "^version"  # Should show "0.1.0"
cat src/champi_imgui/__init__.py | grep "__version__"  # Should show "0.1.0"

# Verify tag exists
git fetch --tags
git tag -l  # Should show v0.1.0

# Verify CHANGELOG updated
cat CHANGELOG.md  # Should have ## v0.1.0 section
```

---

## Go-Live Checklist

Before announcing the new repository:

- [ ] All stages completed and merged to main
- [ ] CI workflow passing on main branch
- [ ] At least one successful release created (v0.1.0)
- [ ] README.md accurate and complete
- [ ] All documentation updated
- [ ] Pre-commit hooks working locally
- [ ] Package can be installed: `pip install git+https://github.com/champi-ai/champi-imgui.git`
- [ ] CLI command works: `champi-imgui --help`
- [ ] All references to champi-gen-ui removed
- [ ] LICENSE file present
- [ ] CHANGELOG.md following Keep a Changelog format
- [ ] GitHub repository settings configured (branch protection, secrets)
- [ ] Old champi-gen-ui repository archived with redirect notice

---

## Archive Old Repository

Once new repository is fully operational:

### 1. Add Archive Notice to Old README

Edit README.md in `champi-gen-ui`:

```markdown
# ⚠️ ARCHIVED - This repository has been migrated

This repository has been archived and is no longer maintained.

**New Repository:** [champi-ai/champi-imgui](https://github.com/champi-ai/champi-imgui)

The project has been renamed from `champi-gen-ui` to `champi-imgui` and migrated to the champi-ai organization with:
- Cleaned git history
- Proper semantic versioning with v prefix
- Improved release automation
- Updated package structure

Please use the new repository for all future development and issues.

---

# Original README

[Keep original README below for reference]
```

### 2. Archive Repository on GitHub

1. Go to: https://github.com/YOUR_USERNAME/champi-gen-ui/settings
2. Scroll to "Danger Zone"
3. Click "Archive this repository"
4. Confirm archival

---

## Notes

### Why v0.0.0 Initial Version?

Starting with v0.0.0 allows the first meaningful release to be v0.1.0 (after the test PR). This follows semantic versioning best practices:
- v0.0.0: Initial repository setup
- v0.1.0: First feature complete release
- v1.0.0: First stable public release

### Tag Format: v$version

Using `tag_format = "v$version"` creates tags like `v0.1.0`, `v1.0.0`, etc. This is the conventional format and is now possible because:
1. The new repository won't have the RELEASES ruleset that blocked v* tags
2. Tags are created by GitHub Actions using RELEASE_TOKEN with proper permissions

### Commit Squashing Rationale

The old repository has 40+ commits but most are test/revert commits from debugging the release workflow. Squashing preserves attribution while creating a clean, meaningful history in the new repository.

### Local Commitizen Usage

With the commit template and pre-commit hooks:
```bash
# Make changes
git add .

# Commit will prompt with template and validate format
git commit

# Or use commitizen interactive mode
cz commit
```

---

## Troubleshooting

### Release Workflow Fails to Create Tag

**Issue:** GH013 error "Cannot create ref due to creations being restricted"

**Solution:**
1. Check repository rulesets: Settings → Rules → Rulesets
2. Ensure no ruleset restricts `refs/tags/v*`
3. Verify RELEASE_TOKEN has `repo` and `workflow` scopes
4. Verify RELEASE_TOKEN is not expired

### Commitizen Can't Find Previous Version

**Issue:** Exit code 16 "No tag found to do an incremental changelog"

**Solution:**
```bash
# Create the initial v0.0.0 tag manually
git tag -a v0.0.0 -m "Initial version"
git push origin v0.0.0
```

### Pre-commit Hooks Failing

**Issue:** Hooks fail on commit

**Solution:**
```bash
# Update hooks
pre-commit autoupdate

# Run manually to see detailed errors
pre-commit run --all-files

# Skip hooks temporarily (NOT recommended)
git commit --no-verify
```

---

## References

- [Commitizen](https://commitizen-tools.github.io/commitizen/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Pre-commit](https://pre-commit.com/)

---

**Migration Plan Version:** 1.0
**Last Updated:** 2025-10-20
**Author:** Divagnz