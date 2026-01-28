# Troubleshooting Guide

## Phase IV - Deployment Issues and Solutions

**Last Updated**: 2026-01-18

This guide covers common issues encountered during deployment and their solutions.

---

## Quick Diagnosis

```bash
# Check all services status
docker-compose ps                    # Docker Compose
kubectl get all                      # Kubernetes

# View recent logs
docker-compose logs --tail=50        # Docker Compose
kubectl logs -l app=todo-backend     # Kubernetes
```

---

## Docker Compose Issues

### 1. Docker Daemon Not Running

**Symptoms:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solutions:**
```bash
# Windows: Start Docker Desktop from Start Menu
# Verify Docker is running
docker info

# If using WSL2, ensure WSL integration is enabled in Docker Desktop settings
```

### 2. Port Already in Use

**Symptoms:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solutions:**
```bash
# Find process using the port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

### 3. Image Build Failures

**Symptoms:**
```
failed to solve: failed to compute cache key
```

**Solutions:**
```bash
# Clean Docker build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache

# Check for missing files
ls -la backend/requirements.txt
ls -la frontend/package.json
```

### 4. Container Exits Immediately

**Symptoms:**
```
Container todo-backend exited with code 1
```

**Solutions:**
```bash
# Check logs for error
docker-compose logs backend

# Common causes:
# - Missing environment variables
# - Invalid database URL
# - Python/Node.js syntax errors

# Verify .env file exists and has all required variables
cat .env | grep -E "(DATABASE_URL|SECRET_KEY|OPENAI_API_KEY)"
```

### 5. Health Check Failures

**Symptoms:**
```
Container is unhealthy
```

**Solutions:**
```bash
# Check health check configuration
docker inspect todo-backend --format='{{json .State.Health}}'

# Test health endpoint manually
curl -v http://localhost:8000/health

# Check application logs for errors
docker-compose logs backend --tail=100
```

---

## Kubernetes/Helm Issues

### 1. Pods Stuck in Pending State

**Symptoms:**
```
NAME                           READY   STATUS    RESTARTS   AGE
todo-backend-xxx               0/1     Pending   0          5m
```

**Solutions:**
```bash
# Check events for reason
kubectl describe pod todo-backend-xxx

# Common causes:
# - Insufficient resources
kubectl top nodes
# - Node selector/affinity issues
# - Volume provisioning failures
```

### 2. ImagePullBackOff

**Symptoms:**
```
NAME                           READY   STATUS             RESTARTS   AGE
todo-backend-xxx               0/1     ImagePullBackOff   0          5m
```

**Solutions:**
```bash
# For kind cluster - load images
kind load docker-image todo-backend:latest --name todo-local
kind load docker-image todo-frontend:latest --name todo-local

# Verify images are loaded
docker exec -it todo-local-control-plane crictl images | grep todo

# For Minikube - build in Minikube's Docker
eval $(minikube docker-env)
docker build -f docker/backend/Dockerfile -t todo-backend:latest ./backend
```

### 3. CrashLoopBackOff

**Symptoms:**
```
NAME                           READY   STATUS             RESTARTS   AGE
todo-backend-xxx               0/1     CrashLoopBackOff   5          10m
```

**Solutions:**
```bash
# Check logs from crashed container
kubectl logs todo-backend-xxx --previous

# Check if secrets are properly mounted
kubectl describe pod todo-backend-xxx | grep -A 10 "Environment"

# Verify secrets exist
kubectl get secrets
kubectl describe secret todo-backend-secrets
```

### 4. Service Not Accessible

**Symptoms:**
- `curl http://localhost:8000` fails
- Browser shows "Connection refused"

**Solutions:**
```bash
# Check service and endpoints
kubectl get svc
kubectl get endpoints todo-backend

# Port forward to test directly
kubectl port-forward svc/todo-backend 8000:8000

# For NodePort, verify kind port mapping
docker ps | grep kindest
# Should show port mapping like 0.0.0.0:30080->30080/tcp
```

### 5. Helm Install Fails

**Symptoms:**
```
Error: INSTALLATION FAILED: cannot re-use a name that is still in use
```

**Solutions:**
```bash
# List existing releases
helm list

# Uninstall existing release
helm uninstall todo-backend

# Or upgrade instead of install
helm upgrade --install todo-backend ./helm/backend
```

### 6. Secrets Not Found

**Symptoms:**
```
Error: secret "todo-backend-secrets" not found
```

**Solutions:**
```bash
# Create secrets manually
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL='...' \
  --from-literal=SECRET_KEY='...' \
  --from-literal=OPENAI_API_KEY='...'

# Or use values-local.yaml with Helm
helm install todo-backend ./helm/backend -f helm/backend/values-local.yaml
```

---

## Application Issues

### 1. Database Connection Errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection refused
```

**Solutions:**
```bash
# Verify DATABASE_URL is correct
# Check Neon dashboard for:
# - Connection limits (free tier: 100 connections)
# - Project status (not suspended)
# - Correct endpoint URL

# Test connection
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://...'))"
```

### 2. OpenAI API Errors

**Symptoms:**
```
openai.AuthenticationError: Incorrect API key provided
```

**Solutions:**
```bash
# Verify API key
echo $OPENAI_API_KEY  # Should start with sk-

# Check OpenAI dashboard for:
# - API key validity
# - Usage limits
# - Account status
```

### 3. CORS Errors

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**
```bash
# Verify CORS_ORIGINS in .env includes frontend URL
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Restart backend after changing
docker-compose restart backend
```

### 4. Frontend Can't Connect to Backend

**Symptoms:**
- Network errors in browser console
- API calls fail

**Solutions:**
```bash
# Verify NEXT_PUBLIC_API_URL
# For browser access, must be localhost, not container name
NEXT_PUBLIC_API_URL=http://localhost:8000

# Rebuild frontend after changing
docker-compose build frontend
docker-compose up -d frontend
```

---

## SLAT Limitation Issues

### What is SLAT?

SLAT (Second Level Address Translation) is a CPU virtualization feature required by Minikube with VM-based drivers.

### Check SLAT Support

```powershell
# Windows PowerShell
systeminfo | findstr /C:"Hyper-V Requirements"
# Look for: "Second Level Address Translation: Yes"
```

### Workarounds

1. **Use Docker Compose** (Track A)
   - Doesn't require virtualization
   - Full functionality without K8s

2. **Use kind instead of Minikube** (Track B)
   - Runs K8s in Docker containers
   - No hypervisor required

3. **Use GitHub Codespaces**
   - Cloud-based development environment
   - Full K8s support

---

## Performance Issues

### 1. Slow Image Builds

**Solutions:**
```bash
# Use build cache effectively
docker-compose build  # Uses cache by default

# Optimize Dockerfile order
# - Copy package files first
# - Install dependencies
# - Copy source code last

# Use .dockerignore to exclude unnecessary files
```

### 2. Slow Container Startup

**Solutions:**
```bash
# Check resource allocation
docker stats

# Increase resources in Docker Desktop settings

# Optimize health check intervals
healthcheck:
  interval: 30s
  timeout: 10s
  start_period: 15s
```

### 3. High Memory Usage

**Solutions:**
```bash
# Set resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
```

---

## Debugging Tips

### Enable Debug Logging

```bash
# Backend
ENVIRONMENT=development  # More verbose logging

# Docker Compose
docker-compose --verbose up
```

### Interactive Debugging

```bash
# Access container shell
docker-compose exec backend sh
kubectl exec -it todo-backend-xxx -- sh

# Run Python interactively
docker-compose exec backend python
```

### View Full Logs

```bash
# Docker Compose
docker-compose logs --no-log-prefix backend 2>&1 | less

# Kubernetes
kubectl logs todo-backend-xxx --all-containers
```

---

## Getting Help

1. **Check Documentation**
   - [Docker Compose Guide](./docker-compose.md)
   - [Kubernetes Guide](./kubernetes.md)
   - [Prerequisites](./prerequisites.md)

2. **Common Fixes**
   - Restart containers: `docker-compose restart`
   - Rebuild images: `docker-compose build --no-cache`
   - Check logs: `docker-compose logs`

3. **Report Issues**
   - Include error messages
   - Include relevant logs
   - Include system information (OS, Docker version)

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Docker not running | Start Docker Desktop |
| Port in use | Kill process or change port |
| Image not found | Build with `docker-compose build` |
| Container crashes | Check logs with `docker-compose logs` |
| K8s ImagePullBackOff | Load image into kind |
| Secret not found | Create with kubectl |
| CORS error | Check CORS_ORIGINS |
| DB connection error | Verify DATABASE_URL |
