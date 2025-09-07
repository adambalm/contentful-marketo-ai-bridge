#!/bin/bash

# Comprehensive security check script
# Run this before every git push

set -e

echo "🔒 Running comprehensive security check..."
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Function to print status
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        FAILED=1
    fi
}

# Function for reverse logic (0 = bad, non-zero = good)
check_status_reverse() {
    if [ $1 -eq 0 ]; then
        echo -e "${RED}❌ $2${NC}"
        FAILED=1
    else
        echo -e "${GREEN}✅ $2${NC}"
    fi
}

# 1. Check .env files contain only templates
echo -e "\n🔍 Checking environment files..."

if [ -f "backend/.env" ]; then
    # Check for real values (not starting with 'your_' and not 'mock')
    REAL_VALUES=$(grep -E "^[A-Z_]+=" backend/.env | grep -v -E "(your_|mock|localhost|example\.com|true|false|^[A-Z_]+=?$)" | grep -E "=.{6,}" | wc -l)
    check_status $REAL_VALUES ".env contains only template values"
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
fi

# 2. Check .env.local is gitignored
echo -e "\n🔍 Checking .env.local is properly ignored..."
if git ls-files | grep -q "\.env\.local"; then
    check_status 1 ".env.local files are not tracked by git"
else
    check_status 0 ".env.local files are not tracked by git"
fi

# 3. Scan current files for secrets
echo -e "\n🔍 Scanning current files for hardcoded secrets..."

SECRET_PATTERNS=(
    "CFPAT-[A-Za-z0-9_-]{59}"
    "sk-[A-Za-z0-9]{48}"
    "AIza[A-Za-z0-9_-]{35}"
    "['\"][A-Za-z0-9+/]{40,}['\"]"
)

SECRETS_FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if git ls-files | grep -E '\.(py|js|ts|json|yaml|yml|env)$' | xargs grep -l -E "$pattern" 2>/dev/null; then
        echo -e "${RED}Found potential secret pattern: $pattern${NC}"
        SECRETS_FOUND=1
    fi
done

check_status $SECRETS_FOUND "No secrets found in tracked files"

# 4. Check git history for secrets (last 10 commits)
echo -e "\n🔍 Checking recent git history for secrets..."

HISTORY_SECRETS=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if git log -10 --all -p | grep -q -E "$pattern"; then
        echo -e "${RED}Found potential secret in recent git history: $pattern${NC}"
        HISTORY_SECRETS=1
    fi
done

check_status $HISTORY_SECRETS "No secrets found in recent git history"

# 5. Check file permissions
echo -e "\n🔍 Checking file permissions..."

WRITABLE_FILES=$(find . -type f -perm -002 -not -path './.git/*' -not -path './node_modules/*' -not -path './.venv/*' | wc -l)
check_status $WRITABLE_FILES "No world-writable files found"

# 6. Check for large files
echo -e "\n🔍 Checking for large files..."

LARGE_FILES=$(find . -type f -size +1M -not -path './.git/*' -not -path './node_modules/*' -not -path './.venv/*' | wc -l)
check_status $LARGE_FILES "No large files (>1MB) found"

# 7. Check environment loading works
echo -e "\n🔍 Testing environment loading..."

if [ -f "backend/load_env.py" ]; then
    cd backend
    if source .venv/bin/activate 2>/dev/null && python load_env.py >/dev/null 2>&1; then
        check_status 0 "Environment loading works correctly"
    else
        check_status 1 "Environment loading works correctly"
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  load_env.py not found${NC}"
fi

# 8. Check pre-commit hooks are installed
echo -e "\n🔍 Checking pre-commit setup..."

if [ -f ".pre-commit-config.yaml" ] && command -v pre-commit &> /dev/null; then
    if pre-commit run --all-files --show-diff-on-failure 2>/dev/null; then
        check_status 0 "Pre-commit hooks pass"
    else
        check_status 1 "Pre-commit hooks pass"
    fi
else
    echo -e "${YELLOW}⚠️  Pre-commit not installed or configured${NC}"
fi

# Final result
echo -e "\n======================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All security checks passed!${NC}"
    echo -e "${GREEN}✅ Repository is safe to push to GitHub${NC}"
    exit 0
else
    echo -e "${RED}🚨 Security issues found!${NC}"
    echo -e "${RED}❌ Do NOT push until issues are resolved${NC}"
    echo -e "${YELLOW}📖 See SECURITY_EMERGENCY_RESPONSE.md for help${NC}"
    exit 1
fi