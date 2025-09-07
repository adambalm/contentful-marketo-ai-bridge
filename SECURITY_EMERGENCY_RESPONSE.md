# 🚨 Security Emergency Response Guide

## If Secrets Are Accidentally Committed

### IMMEDIATE ACTION CHECKLIST (within 5 minutes)

1. **🔴 STOP** - Do not push any more commits
2. **🔄 ROTATE** - Immediately rotate/revoke exposed secrets:
   - Contentful: https://app.contentful.com/account/profile/cma_tokens
   - OpenAI: https://platform.openai.com/api-keys
   - HubSpot: https://app.hubspot.com/private-apps
   - Marketo: Contact admin to revoke tokens

3. **🧹 CLEAN GIT HISTORY** (Choose one method):

### Method 1: BFG Repo Cleaner (Recommended)
```bash
# Install BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Remove secrets from ALL history
java -jar bfg-1.14.0.jar --replace-text secrets.txt .git
java -jar bfg-1.14.0.jar --delete-files contentful_auth_info.json .git

# Force push clean history
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force-with-lease origin main
```

### Method 2: Git Filter-Branch
```bash
# Remove specific file from all history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch backend/.env.local' \
  --prune-empty --tag-name-filter cat -- --all

# Remove secrets from all files
git filter-branch --force --tree-filter \
  'find . -name "*.py" -exec sed -i "s/CFPAT-[A-Za-z0-9_-]\{59\}/REDACTED/g" {} \;' \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
git push origin --force --tags
```

### Method 3: Nuclear Option (Start Fresh)
```bash
# Backup current work
cp -r . ../backup-$(date +%Y%m%d)

# Create fresh repo
git checkout --orphan clean-main
git add .
git commit -m "feat: clean repository without secrets"
git branch -D main
git branch -m main
git push origin --force --set-upstream main
```

## Prevention Setup

### 1. Install Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### 2. Setup Git Secrets Detection
```bash
# Install git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && make install

# Configure for this repo
git secrets --register-aws
git secrets --install
git secrets --add 'CFPAT-[A-Za-z0-9_-]{59}'
git secrets --add 'sk-[A-Za-z0-9]{48}'
```

### 3. Configure IDE/Editor
Add to `.vscode/settings.json`:
```json
{
  "files.watcherExclude": {
    "**/.env.local": true
  },
  "search.exclude": {
    "**/.env.local": true
  }
}
```

## Monitoring & Detection

### Daily Security Scan
```bash
# Run in CI/CD daily
git log --all -p --since="1 day ago" | grep -E "(CFPAT-|sk-|password|secret)" || echo "Clean"
```

### GitHub Security Features
1. Enable Dependabot alerts
2. Enable Secret scanning (GitHub Advanced Security)
3. Enable Code scanning with CodeQL

## Emergency Contacts

### If Production Secrets Exposed:
1. **Contentful Support**: support@contentful.com
2. **OpenAI Support**: https://help.openai.com/
3. **Team Lead**: [Add contact info]

### Incident Response Steps:
1. Document time of exposure
2. Identify affected systems
3. Rotate ALL potentially exposed secrets
4. Review access logs for unauthorized usage
5. Update security procedures
6. Post-incident review

## Recovery Verification

After cleaning git history, verify:
```bash
# Check no secrets in current files
grep -r -E "(CFPAT-|sk-|password.*=)" . --exclude-dir=.git --exclude-dir=.venv

# Check git history is clean
git log --all -p | grep -E "(CFPAT-|sk-)" || echo "History is clean"

# Verify remote is updated
git ls-remote origin
```

## Post-Incident

1. **Team Training**: Review what went wrong
2. **Process Update**: Strengthen prevention measures
3. **Tool Improvement**: Add additional security scanners
4. **Documentation**: Update this guide with lessons learned

---

**Remember: It's better to be overly cautious than to expose secrets. When in doubt, rotate the secret.**