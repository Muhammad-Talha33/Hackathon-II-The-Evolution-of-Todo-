# AI-Assisted DevOps Tools

This guide documents AI tools that can enhance Kubernetes operations for the Todo AI Chatbot deployment.

## Overview

AI-assisted tools can help developers interact with Kubernetes using natural language, reducing the learning curve and speeding up common operations.

| Tool | Purpose | Installation |
|------|---------|--------------|
| kubectl-ai | Natural language to kubectl commands | `pip install kubectl-ai` |
| kagent | AI-powered cluster analysis and optimization | See installation guide below |

---

## kubectl-ai

### Installation

```bash
# Install via pip
pip install kubectl-ai

# Or with pipx for isolated environment
pipx install kubectl-ai

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key"
```

### Configuration

```bash
# Configure default model (optional)
kubectl-ai config --model gpt-4

# Verify installation
kubectl-ai --version
```

### Usage Examples

#### Example 1: Deploy Frontend with 2 Replicas

**Natural Language Input:**
```bash
kubectl-ai "deploy the todo frontend with 2 replicas"
```

**Expected kubectl Command:**
```bash
kubectl scale deployment todo-frontend --replicas=2
# Or if deploying fresh:
kubectl apply -f k8s/frontend/ && kubectl scale deployment todo-frontend --replicas=2
```

**Verification:**
```bash
kubectl get pods -l app=todo-frontend
# Should show 2 pods running
```

#### Example 2: Scale Backend for More Load

**Natural Language Input:**
```bash
kubectl-ai "scale the backend to handle more load"
```

**Expected kubectl Commands:**
```bash
# Scale replicas
kubectl scale deployment todo-backend --replicas=3

# Or with HPA (Horizontal Pod Autoscaler)
kubectl autoscale deployment todo-backend --min=2 --max=5 --cpu-percent=70
```

**Verification:**
```bash
kubectl get hpa
kubectl get pods -l app=todo-backend
```

#### Example 3: Diagnose Pod Failures

**Natural Language Input:**
```bash
kubectl-ai "check why the pods are failing"
```

**Expected Diagnostic Steps:**
```bash
# List pods with status
kubectl get pods -A

# Describe failing pod for events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name> --tail=100

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check resource constraints
kubectl top pods
```

**Common Issues Identified:**
- `ImagePullBackOff`: Image not found or registry auth issues
- `CrashLoopBackOff`: Application crashes on startup
- `Pending`: Insufficient resources or node issues
- `OOMKilled`: Out of memory - increase limits

### Best Practices

1. **Review Commands**: Always review generated commands before execution
2. **Dry Run**: Use `--dry-run=client` for testing
3. **Context Awareness**: Ensure correct cluster context is set
4. **Namespace**: Specify namespace when operating on multiple environments

---

## kagent

### Installation

```bash
# Clone kagent repository
git clone https://github.com/kagent-dev/kagent.git
cd kagent

# Install dependencies
pip install -r requirements.txt

# Or install via pip (if available)
pip install kagent
```

### Configuration

```bash
# Set up kagent configuration
kagent init

# Configure cluster access
kagent config --kubeconfig ~/.kube/config

# Set AI backend
export OPENAI_API_KEY="your-api-key"
```

### Usage Examples

#### Example 1: Analyze Cluster Health

**Natural Language Input:**
```bash
kagent analyze "analyze the cluster health"
```

**Expected Health Report Format:**
```
========================================
CLUSTER HEALTH REPORT
========================================

Overall Status: HEALTHY (or WARNING/CRITICAL)

Nodes:
  - Total: 1
  - Ready: 1 (100%)
  - Not Ready: 0

Workloads:
  - Deployments: 2/2 available
  - Pods: 2/2 running
  - Services: 2 exposed

Resource Utilization:
  - CPU: 45% (of allocatable)
  - Memory: 60% (of allocatable)
  - Storage: 30% used

Recent Events:
  - No warning events in last 1 hour

Recommendations:
  - None - cluster is healthy
========================================
```

#### Example 2: Optimize Resource Allocation

**Natural Language Input:**
```bash
kagent optimize "optimize resource allocation"
```

**Expected Recommendations:**
```
========================================
RESOURCE OPTIMIZATION RECOMMENDATIONS
========================================

1. Backend Deployment (todo-backend)
   Current:
     - CPU Request: 250m, Limit: 500m
     - Memory Request: 256Mi, Limit: 512Mi
   Actual Usage (avg last 24h):
     - CPU: 150m
     - Memory: 180Mi
   Recommendation:
     - Reduce CPU limit to 300m (save 40%)
     - Keep memory as is (headroom for spikes)

2. Frontend Deployment (todo-frontend)
   Current:
     - CPU Request: 100m, Limit: 250m
     - Memory Request: 128Mi, Limit: 256Mi
   Actual Usage:
     - CPU: 80m
     - Memory: 100Mi
   Recommendation:
     - Current limits appropriate
     - Consider HPA for traffic spikes

3. Cluster-Level:
   - Node utilization: 52%
   - No immediate scaling needed
   - Enable cluster autoscaler for production

Commands to Apply:
  kubectl set resources deployment todo-backend \
    --limits=cpu=300m,memory=512Mi \
    --requests=cpu=150m,memory=256Mi
========================================
```

### Best Practices

1. **Regular Analysis**: Run health checks weekly
2. **Pre-deployment**: Analyze before major changes
3. **Post-incident**: Use for root cause analysis
4. **Cost Optimization**: Regular resource optimization reviews

---

## Manual Fallbacks

If AI tools are unavailable, use these standard kubectl commands:

### Health Checks
```bash
# Cluster health
kubectl cluster-info
kubectl get nodes
kubectl get componentstatuses

# Workload health
kubectl get deployments
kubectl get pods -o wide
kubectl get services
```

### Debugging
```bash
# Pod issues
kubectl describe pod <pod-name>
kubectl logs <pod-name> --tail=100
kubectl logs <pod-name> --previous  # crashed containers

# Events
kubectl get events --sort-by='.lastTimestamp'
kubectl get events --field-selector type=Warning
```

### Scaling
```bash
# Manual scaling
kubectl scale deployment <name> --replicas=N

# Autoscaling
kubectl autoscale deployment <name> --min=2 --max=10 --cpu-percent=70
```

### Resource Analysis
```bash
# Resource usage
kubectl top nodes
kubectl top pods
kubectl describe nodes | grep -A5 "Allocated resources"
```

---

## Integration with Todo AI Chatbot

These AI tools can be particularly useful for:

1. **Development**: Quick iteration on deployment configurations
2. **Troubleshooting**: Faster diagnosis of deployment issues
3. **Learning**: Understanding Kubernetes commands through natural language
4. **Optimization**: Identifying resource inefficiencies

### Example Workflow

```bash
# 1. Deploy the application
kubectl-ai "deploy the todo chatbot application"

# 2. Check health
kagent analyze "check if all pods are healthy"

# 3. Scale if needed
kubectl-ai "scale frontend to handle 100 concurrent users"

# 4. Optimize after load test
kagent optimize "analyze resource usage and recommend optimizations"
```

---

## Troubleshooting

### kubectl-ai Issues

| Problem | Solution |
|---------|----------|
| "API key not set" | Export `OPENAI_API_KEY` environment variable |
| "Command not found" | Ensure pip install location is in PATH |
| "Rate limit exceeded" | Wait or upgrade OpenAI plan |

### kagent Issues

| Problem | Solution |
|---------|----------|
| "Cannot connect to cluster" | Check kubeconfig and context |
| "Permission denied" | Verify RBAC permissions |
| "Analysis timeout" | Reduce cluster scope or increase timeout |

---

## Additional Resources

- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
