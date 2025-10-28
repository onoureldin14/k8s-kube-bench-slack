# Kube-bench Security Scanner with Slack Notifications

A complete Kubernetes solution that runs [kube-bench](https://github.com/aquasecurity/kube-bench) security scans and automatically sends formatted results to Slack.

![Status](https://img.shields.io/badge/status-ready-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📑 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Architecture](#-architecture)
- [Deployment Options](#-deployment-options)
  - [Local Testing](#-local-testing)
  - [Kubernetes Job](#-kubernetes-job)
  - [Helm Chart](#-helm-chart)
  - [Scheduled CronJob](#-scheduled-cronjob)
- [Slack Setup](#-slack-app-setup)
- [What You'll Get](#-what-youll-get-in-slack)
- [Monitoring & Logs](#-monitoring--logs)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Cleanup](#-cleanup)

---

## 🚀 Quick Start

### Prerequisites

- Docker installed
- Minikube running (for Kubernetes)
- Slack app configured with bot token
- Docker Hub account (for public deployment)
- **OpenAI API key** (optional - for AI-powered analysis)

### Configuration Setup

The application uses a `config.yaml` file for configuration (instead of environment variables).

1. **Copy the example config:**
```bash
cp config.yaml.example config.yaml
```

2. **Edit `config.yaml` with your values:**
```yaml
slack:
  bot_token: "xoxb-your-actual-token"
  channel: "#kube-bench"

docker:
  username: "your-dockerhub-username"

openai:
  api_key: "sk-your-openai-key"  # Optional
  enabled: true
```

3. **Note:** `config.yaml` is in `.gitignore` and will NOT be committed

**Environment Variables Still Work:** You can still use environment variables if you prefer. They are used as fallback when not in config.yaml.

### Fastest Deployment

**1. Setup Configuration:**
```bash
# Create config file from example
make config

# Edit config.yaml with your secrets
# - slack.bot_token
# - docker.username  
# - openai.api_key (optional)
```

**2. Deploy:**
```bash
# Build and push to Docker Hub
make docker-login
make docker-build  # Uses docker.username from config.yaml

# Setup Kubernetes
make setup-minikube

# Deploy (uses secrets from config.yaml)
make helm-deploy
```

**3. Check Results:**
```bash
make logs
```

**Note:** All secrets are in `config.yaml` (not committed to git). Environment variables still work as fallback.

📖 **For detailed instructions, see the sections below.**

---

## ✨ Features

### 🔒 Security Scanning
- Comprehensive CIS benchmark compliance checks
- Scans control plane, worker nodes, etcd, and policies
- JSON output for detailed analysis

### 📱 Slack Integration
- **Rich formatted messages** with real-time status
- **Interactive HTML reports** with complete test details
- **Critical area highlighting** for urgent issues
- **Control-by-control breakdown** with pass rates
- **Color-coded status indicators** (Pass/Warn/Fail)

### 🤖 AI-Powered Analysis (Optional)
- **OpenAI integration** for intelligent security insights
- **Risk prioritization** of findings
- **Actionable remediation roadmaps**
- **Business impact assessment**
- **Estimated fix time estimates**
- **Compliance gap analysis**

### ☸️ Kubernetes Native
- Runs as Kubernetes Job or CronJob
- Sidecar container design for flexibility
- Secure secret management
- RBAC for safe execution
- Resource limits and health checks

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│           kube-bench-security-scan           │
│                                              │
│  ┌──────────────┐     ┌───────────────────┐  │
│  │  kube-bench  │     │  slack-notifier   │  │
│  │  Container   │◄────┤  Container        │  │
│  │  Scans K8s   │     │  Reads Results    │  │
│  └──────┬───────┘     └────────┬──────────┘  │
│         │                      │             │
│         ▼                      ▼             │
│      Shared Volume        Slack Channel      │
└──────────────────────────────────────────────┘
```

---

## 📋 Deployment Options

### 🤖 AI-Enhanced Deployment

**Get intelligent security insights with AI analysis:**

```bash
# Full deployment with AI
make setup-minikube
make helm-deploy SLACK_TOKEN=xoxb-... OPENAI_API_KEY=sk-... DOCKER_USERNAME=your-username
```

**What you'll get:**
- Standard kube-bench security scan
- Beautiful HTML report with all test details
- **AI-powered risk assessment** (HIGH/MEDIUM/LOW)
- **Top 10 critical findings** with business impact
- **Prioritized remediation roadmap** with time estimates
- **Compliance gap analysis**

📖 See [OpenAI Setup](#-openai-setup-optional-ai-analysis) for API key configuration.

---

### 🐍 Local Testing

**Perfect for development and quick tests:**

```bash
# Install dependencies
make install

# Set Slack token
export SLACK_BOT_TOKEN=xoxb-your-token-here

# Test with dummy data
make test
```

**What you'll see:**
- ✅ Test messages in Slack
- ✅ Formatted reports with sample data
- ✅ HTML report generation

---

### ☸️ Kubernetes Job (One-Time Scan)

**For running a single scan:**

```bash
# 1. Setup minikube
make setup-minikube

# 2. Create secret
make secret SLACK_TOKEN=xoxb-your-token

# 3. Build and deploy (local image)
make build
make deploy

# OR use Docker Hub image
make docker-login DOCKER_USERNAME=your-username
make docker-build DOCKER_USERNAME=your-username
make deploy DOCKER_USERNAME=your-username

# 4. Monitor
make status
make logs
```

---

### 🎛️ Helm Chart (Recommended)

**Production-ready with easy configuration:**

```bash
# 1. Setup
make setup-minikube

# 2. Deploy with local image
make helm-deploy SLACK_TOKEN=xoxb-your-token

# OR with Docker Hub image
make docker-login DOCKER_USERNAME=your-username
make docker-build DOCKER_USERNAME=your-username
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username

# 3. Monitor
make helm-status
make logs
```

**Custom configuration:**

Edit `helm/kube-bench-slack/values.yaml` or override values:

```bash
helm install kube-bench-slack helm/kube-bench-slack \
  --namespace kube-bench \
  --create-namespace \
  --set slack.channel="#security-alerts" \
  --set kubebench.targets="master,node"
```

---

### ⏰ Scheduled CronJob

**Automated recurring scans:**

```bash
# Default: daily at midnight GMT
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username

# Custom schedule: every 6 hours
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username CRON_SCHEDULE="0 */6 * * *"

# Custom schedule: every Monday at 9 AM
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username CRON_SCHEDULE="0 9 * * 1"
```

**Cron Schedule Examples:**
- `"0 0 * * *"` - Daily at midnight GMT
- `"0 */6 * * *"` - Every 6 hours
- `"0 9 * * 1"` - Every Monday at 9 AM
- `"0 0 * * 0"` - Every Sunday at midnight

**Managing CronJobs:**
```bash
# Check status
kubectl get cronjobs -n kube-bench

# Suspend scheduling
kubectl patch cronjob kube-bench-security-scan -n kube-bench -p '{"spec":{"suspend":true}}'

# Resume scheduling
kubectl patch cronjob kube-bench-security-scan -n kube-bench -p '{"spec":{"suspend":false}}'

# Trigger manual run
kubectl create job --from=cronjob/kube-bench-security-scan manual-scan-$(date +%s) -n kube-bench
```

---

## 🔧 Slack App Setup

### Step 1: Create Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create an App"** → **"From scratch"**
3. Name: `kube-bench-security-scanner`
4. Choose your workspace
5. Click **"Create App"**

### Step 2: Configure Bot Permissions

1. Go to **Features → OAuth & Permissions**
2. Scroll to **"Bot Token Scopes"** and add:
   ```
   - app_mentions:read
   - channels:join
   - channels:read       ← Required for file uploads!
   - chat:write
   - files:write
   ```

3. Click **"Install to Workspace"**
4. **Copy the Bot User OAuth Token** (starts with `xoxb-`)

### Step 3: Add Bot to Channel

```bash
# In your Slack channel (e.g., #kube-bench)
/invite @kube-bench-security-scanner
```

### Step 4: Test

```bash
export SLACK_BOT_TOKEN=xoxb-your-token-here
make test
```

✅ **You should see test messages in your Slack channel!**

---

## 🤖 OpenAI Setup (Optional AI Analysis)

AI analysis provides intelligent security insights, risk prioritization, and remediation roadmaps.

### Step 1: Create OpenAI Account

1. Go to [platform.openai.com](https://platform.openai.com)
2. Click **"Sign up"** and create an account
3. Verify your email address

### Step 2: Add Payment Method

1. Go to **Settings → Billing**
2. Click **"Add payment method"**
3. Add a credit card (needed for API access)

### Step 3: Create API Key

1. Go to **API Keys** in the sidebar
2. Click **"Create new secret key"**
3. Name it: `kube-bench-security-analyzer`
4. **Copy the API key** (starts with `sk-`)
5. ⚠️ **Save it immediately** - you won't be able to view it again!

### Step 4: Configure

**Local Testing:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
make test
```

**Kubernetes Deployment:**
```bash
# Create secret
kubectl create secret generic openai-credentials \
  --from-literal=openai-api-key="sk-your-key-here" \
  --namespace kube-bench
```

**What you'll get with AI enabled:**
- ✅ Risk assessment (HIGH/MEDIUM/LOW)
- ✅ Top 5 critical findings with business impact
- ✅ Prioritized remediation roadmap
- ✅ Estimated fix time (hours/days)
- ✅ CIS compliance status and gaps

**Cost:** ~$0.03 per analysis (GPT-4) or $0.002 per analysis (GPT-3.5-turbo)

⚠️ **To disable AI**, simply omit the `OPENAI_API_KEY` environment variable.

---

## 📊 What You'll Get in Slack

### 1. 📱 Formatted Slack Message

A rich message with:
- **Overall Status**: ✅ PASSED / ⚠️ NEEDS ATTENTION / ❌ CRITICAL
- **Summary Statistics**: Total tests, passed, failed, warnings
- **Critical Areas**: Controls with >5 failures highlighted
- **Control Breakdown**: Pass rates for each security control
- **Timestamp**: When the scan was completed

### 2. 🎨 Interactive HTML Report

A beautiful, downloadable HTML file with:
- **Executive Summary**: Visual dashboard with color-coded stats
- **Progress Bar**: Visual pass rate indicator
- **Expandable Controls**: Click to expand/collapse sections
- **Complete Test Results**: Every test with status, description, remediation
- **Color Coding**: ✅ Pass (green), ❌ Fail (red), ⚠️ Warn (yellow)
- **Mobile Responsive**: Works on any device
- **Print Friendly**: Ready for PDF export

**How to use:**
1. Download the HTML file from Slack
2. Open in any web browser
3. Click controls to expand/collapse details
4. Use "Expand/Collapse All" button
5. Print or save as PDF for compliance

### 3. 🤖 AI-Powered Security Analysis Report (Optional)

**If OpenAI is enabled**, you'll receive an additional **beautiful HTML report** with:

- **🔴 Risk Assessment** - Overall security posture (HIGH/MEDIUM/LOW) with color-coded badges
- **📋 Executive Summary** - Brief overview of the security state
- **⚠️ Prioritized Findings** - Ranked from #1 (critical) to N, with severity badges:
  - 🔴 **Critical** - Fix immediately
  - 🟠 **High** - Fix within 24 hours
  - 🟡 **Medium** - Fix within 1 week
  - 🟢 **Low** - Plan for next sprint
- **💡 WHY IT'S DANGEROUS** - Business impact, attack vectors, and compliance risk for each finding
- **🔍 EXPLANATION** - What attackers could do and what systems are at risk
- **🗺️ Prioritized Remediation Roadmap** - Step-by-step action plan with time estimates
- **⏱️ Time Estimates** - Total hours/days needed for remediation
- **✅ Compliance Status** - CIS benchmark alignment and gaps

**What makes it special:**
- **HTML file** (not JSON blocks) - Download and open in browser
- **Color-coded severity badges** - Visual priority indicators
- **Styled with CSS** - Professional appearance
- **Actionable insights** - Not just a list, but a roadmap with business context
- **Explain WHY** - Each finding explains the business impact and attack scenarios
- **Prioritized by risk** - Ranked from most critical to least critical
- **Smart retry mechanism** - If too many findings exceed token limits, analyzes top 15 automatically

**How to use:**
1. AI analysis runs automatically after each scan (if enabled)
2. "AI Analysis in Progress..." message appears
3. AI analysis HTML file is uploaded to Slack (takes 30-60 seconds)
4. Download and open in browser for detailed insights
5. If your cluster has many findings (>15), the report will analyze the top 15 critical issues and note this

**Important notes:**
- Analyzes **ONLY failed tests** - ignores PASS/WARN/INFO
- Automatically retries with limited findings if token limit is exceeded
- Focuses on actionable, business-impact focused analysis

---

## 📊 Monitoring & Logs

### Quick Commands

```bash
# Check job status
make status           # Kubernetes deployment
make helm-status      # Helm deployment

# View logs
make logs             # Sidecar container logs
```

### Detailed Monitoring

```bash
# Check all resources
kubectl get all -n kube-bench

# View job details
kubectl describe job kube-bench-security-scan -n kube-bench

# View kube-bench logs
kubectl logs job/kube-bench-security-scan -n kube-bench -c kube-bench

# View Slack notifier logs
kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier

# View recent jobs (for CronJob)
kubectl get jobs -n kube-bench --sort-by=.status.startTime
```

---

## ⚙️ Configuration

The application supports configuration via **YAML file** or **environment variables**.

### Primary Method: config.yaml (Recommended)

1. **Create config file:**
```bash
make config  # Creates config.yaml from config.yaml.example
```

2. **Edit config.yaml:**
```yaml
slack:
  bot_token: "xoxb-your-token-here"
  channel: "#kube-bench"

docker:
  username: "your-dockerhub-username"

openai:
  api_key: "sk-your-key"  # Optional
  enabled: true
```

3. **Benefits:**
- All secrets in one file
- Version control excluded (`.gitignore`)
- Easy to manage

### Alternative: Environment Variables

You can still use environment variables (they work as fallback):
| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | Required | Bot OAuth token |
| `SLACK_CHANNEL` | `#kube-bench` | Target channel |
| `OPENAI_API_KEY` | Optional | For AI-powered security analysis |

### 🤖 AI Analysis Configuration

**Enable AI analysis:**

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or set via Kubernetes secret
make openai-secret OPENAI_API_KEY=sk-your-key

# Or add to Kubernetes secret
kubectl create secret generic openai-credentials \
  --from-literal=openai-api-key="sk-..." \
  --namespace kube-bench
```

**AI analysis provides:**
- ✅ Overall risk assessment with color-coded severity badges
- 🎯 Ranked findings from #1 (most critical) to N
- 💡 **WHY IT'S DANGEROUS** - Business impact and attack vectors for each finding
- 🔍 **EXPLANATION** - What attackers could do and what systems are at risk
- 📋 Prioritized remediation roadmap with time estimates
- ⚠️ Smart retry: automatically analyzes top 15 if token limit exceeded
- ✅ CIS compliance status

**Disable AI analysis:**
- Simply omit the `OPENAI_API_KEY` environment variable
- The system will skip AI analysis gracefully
- All other features continue to work normally

### Helm Values

Key configuration in `helm/kube-bench-slack/values.yaml`:

```yaml
# Slack configuration
slack:
  channel: "#kube-bench"
  
# Kube-bench targets
kubebench:
  targets: "master,node,etcd,policies"
  outputFormat: json
  
# Resource limits
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Custom values file:**

```yaml
# custom-values.yaml
slack:
  channel: "#security-alerts"
  
kubebench:
  targets: "master,node"
  resources:
    limits:
      memory: "1Gi"
```

Deploy:
```bash
helm install kube-bench-slack helm/kube-bench-slack \
  --namespace kube-bench \
  --values custom-values.yaml
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "channel_not_found" error**
```bash
# Invite bot to channel
/invite @kube-bench-security-scanner

# Verify token
curl -H "Authorization: Bearer xoxb-your-token" \
  https://slack.com/api/auth.test
```

**2. "missing_scope" error**
- Add required scopes in OAuth & Permissions
- Reinstall the app after adding scopes

**3. Job fails to start**
```bash
# Check minikube
minikube status
minikube start

# Verify image
minikube image ls | grep slack-kube-bench

# Load image if missing
make build
```

**4. No notifications in Slack**
```bash
# Check notifier logs
kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier

# Verify secret
kubectl get secret slack-credentials -n kube-bench -o yaml

# Test token
make test
```

### Debug Commands

```bash
# View all resources
kubectl get all -n kube-bench

# Describe job
kubectl describe job kube-bench-security-scan -n kube-bench

# Check secret
kubectl get secret slack-credentials -n kube-bench

# Test Slack locally
export SLACK_BOT_TOKEN=xoxb-your-token
make test
```

---

## 🧹 Cleanup

### Remove Resources

```bash
# Kubernetes deployment
make clean

# Helm deployment
make helm-clean

# Both
make clean && make helm-clean
```

### Complete Cleanup

```bash
# Remove all resources
make clean
make helm-clean

# Remove Docker images
docker rmi slack-kube-bench:latest
docker rmi aquasec/kube-bench:latest

# Remove namespace
kubectl delete namespace kube-bench
```

---

## 📚 Project Structure

```
├── src/                          # Source code
│   ├── slack_app/                # Slack integration
│   │   ├── client.py            # Slack API client
│   │   ├── formatter.py         # Message formatting
│   │   └── notifier.py          # Notification logic
│   ├── kube_bench/               # Kube-bench integration
│   │   ├── parser.py            # JSON parsing
│   │   └── monitor.py           # File monitoring
│   ├── utils/                    # Utilities
│   │   ├── html_report.py       # HTML report generation
│   │   ├── config.py            # Configuration
│   │   └── logger.py            # Logging setup
│   ├── app.py                   # Main application
│   ├── main.py                  # Entry point
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Container image
├── k8s/                          # Kubernetes manifests
│   ├── namespace.yaml            # Namespace definition
│   ├── rbac.yaml                # RBAC configuration
│   ├── kube-bench-job.yaml      # Job definition
│   ├── kube-bench-cronjob.yaml  # CronJob definition
│   └── kustomization.yaml       # Kustomize config
├── helm/                         # Helm chart
│   └── kube-bench-slack/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── scripts/                      # Deployment scripts
│   ├── build.sh
│   ├── deploy.sh
│   └── helm-deploy.sh
├── Makefile                      # Project commands
└── README.md                     # This file
```

---

## 🛠️ Available Commands

```bash
make help              # Show all available commands

# Setup
make install           # Install Python dependencies
make setup-minikube    # Install and start minikube

# Testing
make test              # Test Slack connection locally

# Docker Hub
make docker-login DOCKER_USERNAME=your-username
make docker-build DOCKER_USERNAME=your-username

# Kubernetes (kubectl)
make build             # Build Docker image
make secret SLACK_TOKEN=xoxb-your-token
make deploy            # Deploy Job
make deploy-cron       # Deploy CronJob
make status            # Check status
make logs              # View logs
make clean             # Clean up

# Helm
make helm-deploy SLACK_TOKEN=xoxb-your-token
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token
make helm-status       # Check Helm release
make helm-clean        # Clean up Helm

# Minikube
make start-minikube    # Start cluster
make stop-minikube    # Stop cluster
make check-minikube    # Check status
```

---

## 📖 Quick Reference

### One-Time Scan (Docker Hub)
```bash
make docker-login DOCKER_USERNAME=your-username
make docker-build DOCKER_USERNAME=your-username
make setup-minikube
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username
make logs
```

### Scheduled Scans
```bash
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username
```

### Local Testing
```bash
make install
export SLACK_BOT_TOKEN=xoxb-your-token
make test
```

### Local Kubernetes (No Docker Hub)
```bash
make setup-minikube
make secret SLACK_TOKEN=xoxb-your-token
make deploy
make logs
```

---

## 🔐 Security Notes

- ✅ **Never commit tokens** - Use Kubernetes secrets or env vars
- ✅ **Use Docker Hub access tokens** instead of passwords
- ✅ **Enable 2FA** on Docker Hub
- ✅ **Use private repos** for sensitive workloads
- ✅ **Rotate tokens regularly** in production

---

## 🤝 Contributing

Contributions welcome! Feel free to submit issues and enhancement requests.

---

## 📄 License

MIT License - See LICENSE file for details.

---

**Need help?** Check the [Troubleshooting](#-troubleshooting) section or open an issue on GitHub.
