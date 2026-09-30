#!/bin/bash
set -e

echo "Starting SplitEasy Git Upload..."
echo ""

# Stage all files (respects .gitignore)
echo "Step 1: Staging all files..."
git add .

# Check what's staged
echo "Step 2: Verifying staged files..."
git status --short

# Commit with descriptive message
echo "Step 3: Creating commit..."
git commit -m "Add complete SplitEasy: implementation, specs, hooks, MCP servers, custom agents

- Core app: Streamlit UI, algorithm library, SQLite database
- 38 files: ~1350 LOC source, ~1500 LOC docs, ~2000 LOC specs
- Features: Groups, members, expenses, fair balance calculation, minimal settlement
- Fair remainder distribution: First N participants get +1 paise if remainder
- Settlement algorithm: Greedy O(N log N) matching, guaranteed N-1 transfers
- Testing: 13 unit tests, integration test, demo script (all passing)
- Kiro Integration:
  - Specs: Requirements (7 user stories), Design (architecture/algorithms), Tasks (27 tasks)
  - Hooks: 4 automation hooks (lint, security, init, test verification)
  - MCP Servers: 2 Python servers with 10 tools (database + calculations)
  - Custom Agents: 4 specialized agents (data analyst, settlement expert, documentation expert, code reviewer)
- Documentation: 11 markdown files covering guide, architecture, API reference
- Python 3.12 compatible, secure by default, proper error handling"

# Push to remote
echo "Step 4: Pushing to remote..."
git push -u origin main

echo ""
echo "✅ Upload complete! All 38 files pushed to repository."
