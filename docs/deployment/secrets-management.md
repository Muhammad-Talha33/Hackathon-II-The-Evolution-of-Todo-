# Secrets Management Guide

## Phase IV - Secure Secrets Handling

**Last Updated**: 2026-01-18

This guide covers secure management of secrets for the Todo AI Chatbot deployment.

---

## Overview

The application requires several sensitive values:

| Secret | Purpose | Example Format |
|--------|---------|----------------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | JWT signing | Random 32-byte hex string |
| `OPENAI_API_KEY` | AI API access | `sk-proj-...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | `7` |

---

## Golden Rules

1. **Never commit secrets to Git**
2. **Use templates, not actual values**
3. **Rotate secrets regularly**
4. **Use environment-specific secrets**
5. **Audit secret access**

---

## Docker Compose Secrets

### Setup

1. **Copy template to .env**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with actual values**
   ```bash
   # Use a secure editor
   nano .env
   # Or on Windows
   notepad .env
   ```

3. **Verify .gitignore includes .env**
   ```bash
   cat .gitignore | grep ".env"
   # Should show: .env
   ```

### File Permissions

```bash
# Linux/macOS: Restrict .env access
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw-------
```

### Verification

```bash
# Check secrets are loaded (without exposing values)
docker-compose exec backend env | grep -E "(DATABASE|SECRET|OPENAI)" | sed 's/=.*/=***/'
```

---

## Kubernetes Secrets

### Method 1: kubectl create secret

```bash
# Create secret from literal values
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://user:pass@host/db?ssl=require' \
  --from-literal=SECRET_KEY='your-32-byte-hex-key' \
  --from-literal=OPENAI_API_KEY='sk-proj-...' \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES='15' \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS='7'

# Verify
kubectl get secrets
kubectl describe secret todo-backend-secrets
```

### Method 2: Helm values-local.yaml

1. **Create values-local.yaml**
   ```yaml
   # helm/backend/values-local.yaml
   # THIS FILE IS GITIGNORED - NEVER COMMIT
   secrets:
     openaiApiKey: "sk-proj-..."
     databaseUrl: "postgresql+asyncpg://..."
     secretKey: "your-32-byte-hex-key"
     accessTokenExpireMinutes: "15"
     refreshTokenExpireDays: "7"
   ```

2. **Install with values file**
   ```bash
   helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml
   ```

### Method 3: External Secret Manager

For production, consider:
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Secret Manager**

---

## Secret Rotation

### Rotating JWT Secret Key

1. **Generate new key**
   ```bash
   # Generate 32-byte hex key
   openssl rand -hex 32
   ```

2. **Update secret**
   ```bash
   # Docker Compose
   # Edit .env file with new SECRET_KEY
   docker-compose restart backend

   # Kubernetes
   kubectl create secret generic todo-backend-secrets \
     --from-literal=SECRET_KEY='new-key' \
     --dry-run=client -o yaml | kubectl apply -f -
   kubectl rollout restart deployment/todo-backend
   ```

3. **Note**: Rotating JWT secret invalidates all existing tokens. Users will need to re-authenticate.

### Rotating Database Password

1. **Update in database**
   - Log into Neon dashboard
   - Reset role password

2. **Update application secret**
   - Update DATABASE_URL with new password
   - Restart containers

### Rotating OpenAI API Key

1. **Generate new key**
   - Go to OpenAI dashboard
   - Create new API key
   - Note the key (shown only once)

2. **Update secret**
   - Update OPENAI_API_KEY
   - Restart containers

3. **Revoke old key**
   - Delete old key in OpenAI dashboard

---

## Security Best Practices

### 1. Use Strong Secrets

```bash
# Generate secure SECRET_KEY
openssl rand -hex 32

# Output: 64-character hex string
# Example: a3b2c1d4e5f6...
```

### 2. Environment-Specific Secrets

```
development/
  .env              # Dev secrets
production/
  .env.production   # Prod secrets (different values)
```

### 3. Audit Access

```bash
# View secret access (Kubernetes)
kubectl get events --field-selector reason=SecretAccess

# Check who can read secrets
kubectl auth can-i get secrets --as=system:serviceaccount:default:default
```

### 4. Encrypt at Rest

- Use encrypted storage for .env files
- Enable encryption in Kubernetes secrets store
- Use encrypted EBS volumes in production

### 5. Minimal Permissions

```yaml
# Kubernetes: Pod only needs specific secrets
envFrom:
  - secretRef:
      name: todo-backend-secrets  # Only this secret
```

---

## Gitignore Configuration

Ensure these patterns are in `.gitignore`:

```gitignore
# Environment files
.env
.env.local
.env.*.local
*.env.local

# Kubernetes secrets
*-secrets.yaml
secrets.yaml
values-local.yaml

# Helm values with secrets
helm/*/values-local.yaml

# Any file with "secret" in name
*secret*
*Secret*
```

### Verify

```bash
# Check if secrets are tracked
git status | grep -E "(\.env|secret)"
# Should show nothing or "nothing to commit"

# Check git history for accidental commits
git log --all --oneline -- "*.env" "*secret*"
# Should be empty for properly managed repos
```

---

## Recovery Procedures

### Lost .env File

1. Create new .env from template:
   ```bash
   cp .env.example .env
   ```

2. Retrieve secrets from:
   - Password manager
   - Neon dashboard (DATABASE_URL)
   - OpenAI dashboard (API key)
   - Generate new SECRET_KEY

### Compromised Secret

1. **Immediately rotate** the compromised secret
2. **Review access logs** for unauthorized use
3. **Notify stakeholders** if data breach possible
4. **Update all environments** with new secret

---

## Checklist

### Before Deployment

- [ ] `.env` file created from template
- [ ] All required secrets populated
- [ ] `.gitignore` includes secret files
- [ ] Secrets not visible in logs
- [ ] Proper file permissions set

### During Deployment

- [ ] Secrets loaded correctly (check env vars)
- [ ] Application connects to database
- [ ] OpenAI API calls succeed
- [ ] JWT authentication works

### Ongoing Maintenance

- [ ] Rotate secrets quarterly
- [ ] Audit access logs monthly
- [ ] Review .gitignore regularly
- [ ] Update secrets on password policy changes

---

## Quick Reference

| Task | Command |
|------|---------|
| Generate secret key | `openssl rand -hex 32` |
| Create K8s secret | `kubectl create secret generic NAME --from-literal=KEY=value` |
| View secret (base64) | `kubectl get secret NAME -o yaml` |
| Update secret | `kubectl apply -f secret.yaml` |
| Restart after rotation | `kubectl rollout restart deployment/NAME` |
