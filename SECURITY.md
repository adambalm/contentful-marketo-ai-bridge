# Security Configuration

## Environment Variables Setup

This project uses a secure environment variable configuration to protect API keys and secrets.

### ⚠️ NEVER commit real secrets to Git

### Setup Instructions

1. **Copy environment template:**
   ```bash
   cp backend/.env.example backend/.env.local
   ```

2. **Edit `.env.local` with your real secrets:**
   ```bash
   # backend/.env.local (gitignored - safe for real secrets)
   CONTENTFUL_SPACE_ID=your_real_space_id
   CONTENTFUL_ACCESS_TOKEN=your_real_access_token
   CONTENTFUL_PREVIEW_TOKEN=your_real_preview_token
   CONTENTFUL_MANAGEMENT_TOKEN=your_real_management_token
   OPENAI_API_KEY=your_real_openai_api_key
   # ... etc
   ```

3. **The `.env` file contains only template values** (safe to commit)

### File Priority

The application loads environment variables in this order:
1. `.env.local` (your real secrets - gitignored)
2. `.env` (template values - committed to Git)

### Gitignored Files (contain secrets)

These files are automatically ignored by Git and safe for secrets:

- `backend/.env.local`
- `backend/*.env.local`
- `contentful_auth_info.json`
- `**/secrets.json`
- `**/*_secrets.*`
- `**/*_credentials.*`
- `playwright_auth/`

### Safe Files (no secrets)

These files contain only placeholder values and are safe to commit:

- `backend/.env`
- `backend/.env.example`
- `.env.template`

### Contentful API Tokens

Get your tokens from:
- Space ID: https://app.contentful.com/spaces/[SPACE_ID]/settings/general
- Access Tokens: https://app.contentful.com/spaces/[SPACE_ID]/api/keys
- Management Token: https://app.contentful.com/account/profile/cma_tokens

### Security Checklist Before Git Push

- [ ] No real API keys in committed files
- [ ] All secrets are in `.env.local` (gitignored)
- [ ] Template files contain only `your_*` placeholder values
- [ ] No hardcoded tokens in code files
- [ ] Test files don't contain real credentials

### Testing Security Setup

Run this to verify your setup:
```bash
cd backend
python load_env.py
```

You should see:
- ✅ `Using real environment values from .env.local` (for local development)
- ⚠️ `Using template environment values` (if secrets not configured)

### Production Deployment

For production deployment:
1. Set environment variables directly in your hosting platform
2. Do not use `.env.local` in production
3. Use your platform's secrets management (e.g., Railway, Heroku, AWS)

## Vision Model Security

The local Qwen 2.5VL vision model requires no external API keys and processes images locally for enhanced privacy.