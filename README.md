# Kube-bench Security Scanner with Slack Notifications

A complete Kubernetes solution that runs [kube-bench](https://github.com/aquasecurity/kube-bench) security scans and automatically sends formatted results to Slack.

## 🏗️ Architecture

This solution consists of:
- **Kubernetes Job**: Runs kube-bench security scanning
- **Sidecar Container**: Python Slack app that monitors scan results and sends notifications
- **Shared Volume**: Allows communication between containers
- **Kubernetes Secrets**: Secure storage for Slack credentials

## 🚀 Quick Start

### Prerequisites

- Docker installed
- Docker Hub account (for public deployment)
- For Kubernetes: Minikube running, kubectl configured
- For Helm: Helm installed
- **Slack App**: You'll need to create a Slack app first (see setup guide below)

### Fastest Way to Deploy

```bash
# 1. Login to Docker Hub
make docker-login DOCKER_USERNAME=your-dockerhub-username

# 2. Build and push image
make docker-build DOCKER_USERNAME=your-dockerhub-username

# 3. Setup minikube
make setup-minikube

# 4. Deploy with Helm
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-dockerhub-username

# 5. Check logs
make logs
```

## 🔧 Slack App Setup

Before you can use this project, you need to create a Slack app and get the necessary tokens. Follow this step-by-step guide:

### 1. Create a Slack App

1. **Navigate to Slack API Dashboard**
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click **"Create an App"**
   - Select **"Create your app from scratch"**

2. **Configure Basic Information**
   - Enter app name: `kube-bench-security-scanner`
   - Choose your workspace
   - Click **"Create App"**

### 2. Configure Bot Permissions

1. **Go to OAuth & Permissions**
   - In the left sidebar, click **"Features" → "OAuth & Permissions"**
   - Scroll down to **"Bot Token Scopes"**
   - Add the following scopes:
     - `app_mentions:read` - Read messages that mention the bot
     - `channels:join` - Join channels
     - `channels:read` - View basic channel information (required for file uploads)
     - `chat:write` - Send messages
     - `files:read` - Read files (for kube-bench results)
     - `files:write` - Upload files

2. **Install App to Workspace**
   - Scroll up to **"Install App"** section
   - Click **"Install to Workspace"**
   - Review permissions and click **"Allow"**
   - **Copy the Bot User OAuth Token** (starts with `xoxb-`) - you'll need this!

### 3. Configure Event Subscriptions (Optional)

For advanced features, you can enable event subscriptions:

1. **Go to Event Subscriptions**
   - Click **"Features" → "Event Subscriptions"**
   - Toggle **"Enable Events"** to ON
   - In **"Subscribe to bot events"**, add:
     - `app_mention` - Respond when bot is mentioned
     - `message.channels` - Read channel messages

### 4. Add Bot to Channels

1. **Invite Bot to Your Channel**
   - Go to your desired channel (e.g., `#kube-bench`)
   - Type: `/invite @kube-bench-security-scanner`
   - Or mention the bot: `@kube-bench-security-scanner`

### 5. Test Your Setup

```bash
# Test with your token
export SLACK_BOT_TOKEN=xoxb-your-bot-token-here
make test
```

**Expected Result:** You should see test messages appear in your Slack channel!

### 🔑 Required Tokens

You'll need these tokens for the project:

| Token Type | Format | Where to Find | Usage |
|------------|--------|---------------|-------|
| **Bot User OAuth Token** | `xoxb-...` | OAuth & Permissions → Bot User OAuth Token | Main authentication |
| **App-Level Token** | `xapp-...` | Settings → Basic Information → App-Level Tokens | Socket Mode (optional) |

### 🚨 Security Notes

- **Never commit tokens to code** - Use environment variables or Kubernetes secrets
- **Store tokens securely** - Use Kubernetes secrets or secure vaults
- **Rotate tokens regularly** - For production environments
- **Limit bot permissions** - Only grant necessary scopes

### 🐛 Troubleshooting

**Common Issues:**

1. **"channel_not_found" error**
   - Ensure bot is added to the target channel
   - Check channel name format (`#channel-name`)

2. **"missing_scope" error**
   - Add required scopes in OAuth & Permissions
   - Reinstall the app after adding scopes

3. **"not_authed" error**
   - Verify your Bot User OAuth Token
   - Ensure token starts with `xoxb-`

4. **Bot not responding**
   - Check if bot is invited to the channel
   - Verify event subscriptions are enabled
   - Check bot permissions

**Test Commands:**
```bash
# Test token validity
curl -H "Authorization: Bearer xoxb-your-token" \
  https://slack.com/api/auth.test

# Test channel access
curl -H "Authorization: Bearer xoxb-your-token" \
  https://slack.com/api/conversations.list
```

## 📋 Deployment Options

### 0. 🐳 Build and Push to Docker Hub (Recommended for Public Repos)

**For sharing your image publicly or deploying to remote clusters:**

```bash
# 1. Login to Docker Hub
make docker-login DOCKER_USERNAME=your-dockerhub-username

# 2. Build and push image
make docker-build DOCKER_USERNAME=your-dockerhub-username

# Optional: Specify custom tag
make docker-build DOCKER_USERNAME=your-dockerhub-username IMAGE_TAG=v1.0.0
```

**What happens:**
- ✅ Builds Docker image with your Docker Hub username
- ✅ Pushes to Docker Hub (e.g., `your-username/slack-kube-bench:latest`)
- ✅ Makes image accessible from any Kubernetes cluster
- ✅ No need to load image into minikube manually

**Then deploy with Docker Hub image:**
```bash
# Deploy with Helm (recommended)
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-dockerhub-username

# Or deploy with kubectl
make deploy DOCKER_USERNAME=your-dockerhub-username
```

### 1. 🐍 Run Python Script Locally (Testing)

**Perfect for development and testing with dummy data:**

```bash
# Install dependencies (auto-detects Python version)
make install

# Set your Slack token
export SLACK_BOT_TOKEN=xoxb-your-slack-token-here

# Run the script locally
make test
```

**Manual installation (if make install fails):**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd src
pip install -r requirements.txt

# Deactivate when done
deactivate
```

**What happens:**
- ✅ Sends test messages to your Slack channel
- ✅ Tests rich formatting and JSON data
- ✅ Validates Slack connection
- ✅ No Kubernetes required

### 2. ☸️ Deploy with Kubernetes (kubectl/kustomize)

**For direct Kubernetes deployment (local):**

```bash
# 1. Setup minikube (installs if needed and starts cluster)
make setup-minikube

# 2. Create secret (this also creates the namespace)
make secret SLACK_TOKEN=xoxb-your-slack-token-here

# 3. Deploy the application
make deploy

# 4. Monitor the deployment
make status
make logs
```

**For direct Kubernetes deployment (Docker Hub):**

```bash
# 1. Build and push to Docker Hub
make docker-build DOCKER_USERNAME=your-username

# 2. Setup minikube
make setup-minikube

# 3. Create secret
make secret SLACK_TOKEN=xoxb-your-slack-token-here

# 4. Deploy with Docker Hub image
make deploy DOCKER_USERNAME=your-username

# 5. Monitor
make status
make logs
```

**Using scripts directly:**

```bash
# Local deployment
./scripts/build.sh
./scripts/deploy.sh

# Docker Hub deployment
export DOCKER_USERNAME=your-username
./scripts/build.sh
./scripts/deploy.sh
```

**Manual minikube setup:**
```bash
# Install minikube
make setup-minikube

# Start minikube cluster
make start-minikube

# Check minikube status
make check-minikube

# Stop minikube cluster
make stop-minikube
```

**What happens:**
- ✅ Creates namespace, RBAC, and job
- ✅ Runs actual kube-bench security scan
- ✅ Sends real security results to Slack
- ✅ Uses kustomize for manifest management

### 3. 🎛️ Deploy with Helm (Recommended)

**For production-ready deployment (local):**

```bash
# 1. Setup minikube (installs if needed and starts cluster)
make setup-minikube

# 2. Deploy with Helm (includes secret creation)
make helm-deploy SLACK_TOKEN=xoxb-your-slack-token-here

# 3. Monitor the deployment
make helm-status
make logs
```

**For production-ready deployment (Docker Hub):**

```bash
# 1. Build and push to Docker Hub
make docker-build DOCKER_USERNAME=your-username

# 2. Setup minikube
make setup-minikube

# 3. Deploy with Helm using Docker Hub image
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username

# 4. Monitor
make helm-status
make logs
```

**Using scripts directly:**

```bash
# Local deployment
./scripts/helm-deploy.sh

# Docker Hub deployment
export DOCKER_USERNAME=your-username
export SLACK_TOKEN=xoxb-your-token
./scripts/helm-deploy.sh
```

**What happens:**
- ✅ Deploys with Helm chart
- ✅ Configurable via values.yaml
- ✅ Production-ready with RBAC
- ✅ Easy upgrades and rollbacks
- ✅ Supports both local and Docker Hub images

### 4. ⏰ Deploy as CronJob (Scheduled Scans)

**For automated recurring security scans:**

```bash
# Deploy with default schedule (daily at midnight GMT)
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username

# Deploy with custom schedule (every 6 hours)
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username CRON_SCHEDULE="0 */6 * * *"

# Deploy with custom schedule (every Monday at 9 AM)
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username CRON_SCHEDULE="0 9 * * 1"

# Deploy with kubectl (default schedule)
make deploy-cron DOCKER_USERNAME=your-username

# Deploy with kubectl (custom schedule)
make deploy-cron DOCKER_USERNAME=your-username CRON_SCHEDULE="0 0 * * 0"
```

**Cron Schedule Examples:**
- `"0 0 * * *"` - Daily at midnight GMT
- `"0 */6 * * *"` - Every 6 hours
- `"0 9 * * 1"` - Every Monday at 9 AM
- `"0 0 * * 0"` - Every Sunday at midnight
- `"0 2 * * *"` - Daily at 2 AM GMT

**What happens:**
- ✅ Automated security scans on schedule
- ✅ Results sent to Slack after each scan
- ✅ Job history maintained (last 3 successful, 3 failed)
- ✅ Can suspend/resume without deleting

**Managing CronJobs:**
```bash
# Check CronJob status
kubectl get cronjobs -n kube-bench

# View recent jobs
kubectl get jobs -n kube-bench

# Suspend CronJob (pause scheduling)
kubectl patch cronjob kube-bench-security-scan -n kube-bench -p '{"spec":{"suspend":true}}'

# Resume CronJob
kubectl patch cronjob kube-bench-security-scan -n kube-bench -p '{"spec":{"suspend":false}}'

# Trigger manual run
kubectl create job --from=cronjob/kube-bench-security-scan manual-scan-$(date +%s) -n kube-bench

# Delete CronJob
make helm-clean
```

## 📖 Detailed Instructions

### 🐍 Local Python Script Testing

**Step-by-step for local development:**

```bash
# 1. Install Python dependencies
cd src
pip install -r requirements.txt

# 2. Set your Slack token
export SLACK_BOT_TOKEN=xoxb-your-slack-token-here

# 3. Run the test script
python main.py
```

**What you'll see:**
- 🚀 Test messages sent to your Slack channel
- 📊 Rich formatted messages with blocks
- 📋 JSON data examples
- ✅ Connection validation

**Troubleshooting:**

**Python Setup Issues:**
```bash
# If "externally-managed-environment" error on macOS
# The Makefile automatically handles this with virtual environments
make install

# Manual virtual environment setup
python3 -m venv venv
source venv/bin/activate
cd src
pip install -r requirements.txt

# To activate virtual environment later
source venv/bin/activate
```

**Test Slack connection only:**
```bash
# Test with python3
python3 -c "
from main import SlackApp
app = SlackApp()
app.send_message('Test from Python! 🐍')
"

# Test with python
python -c "
from main import SlackApp
app = SlackApp()
app.send_message('Test from Python! 🐍')
"
```

### ☸️ Kubernetes Deployment (kubectl/kustomize)

**Step-by-step for Kubernetes:**

```bash
# 1. Start minikube
minikube start

# 2. Build and load Docker image
make build

# 3. Create secret with your token
make secret SLACK_TOKEN=xoxb-your-slack-token-here

# 4. Deploy to Kubernetes
make deploy

# 5. Monitor the deployment
make status
make logs
```

**Manual deployment:**
```bash
# Create secret manually
kubectl create secret generic slack-credentials \
  --from-literal=slack-bot-token="xoxb-your-slack-token-here" \
  --namespace=kube-bench

# Deploy with kustomize
kubectl apply -k k8s/

# Check status
kubectl get all -n kube-bench
```

### 🎛️ Helm Deployment (Recommended)

**Step-by-step for Helm:**

```bash
# 1. Start minikube and install Helm
minikube start
# Install Helm: https://helm.sh/docs/intro/install/

# 2. Build and load Docker image
make build

# 3. Deploy with Helm
make helm-deploy

# 4. Set your Slack token
kubectl create secret generic slack-credentials \
  --from-literal=slack-bot-token="xoxb-your-slack-token-here" \
  --namespace=kube-bench

# 5. Monitor the deployment
make helm-status
make logs
```

**Custom Helm deployment:**
```bash
# Deploy with custom values
helm install kube-bench-slack helm/kube-bench-slack \
  --namespace kube-bench \
  --create-namespace \
  --set slack.channel="#security-alerts" \
  --set kubebench.targets="master,node" \
  --set kubebench.resources.limits.memory="1Gi"
```

## 📊 Monitoring & Logs

**Check deployment status:**
```bash
# Kubernetes deployment
make status

# Helm deployment  
make helm-status

# View logs
make logs
```

**Manual monitoring:**
```bash
# Check job status
kubectl get jobs -n kube-bench

# View kube-bench logs
kubectl logs job/kube-bench-security-scan -n kube-bench -c kube-bench

# View Slack notifier logs
kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier
```

## 📊 Slack Report Format

When a kube-bench scan completes, you'll receive **two deliverables** in your Slack channel:

### 1. 📱 Formatted Slack Message

A rich, interactive message with:
- **Overall Status**: PASSED / NEEDS ATTENTION / CRITICAL
- **Summary Statistics**: Total tests, passed, failed, warnings
- **Critical Areas**: Controls with >5 failures highlighted
- **Control Breakdown**: Pass rates for each security control
- **Sample Failed Tests**: Top 10 failed tests with remediation steps
- **Timestamp**: When the scan was completed

### 2. 🎨 Interactive HTML Report

A **beautiful, styled HTML report** that includes:
- **Executive Summary**: Visual dashboard with color-coded stats
- **Progress Bar**: Visual pass rate indicator
- **Expandable Controls**: Click to expand/collapse each control section
- **Complete Test Results**: Every single test with status, description, and remediation
- **Color Coding**: Pass (green), Fail (red), Warn (yellow)
- **Mobile Responsive**: Works on any device
- **Print Friendly**: Clean formatting for PDF export

**How to use:**
1. Download the HTML file from Slack
2. Open in any web browser
3. Click on controls to expand/collapse details
4. Use "Expand/Collapse All" button for quick navigation
5. Print or save as PDF for compliance records

## 📁 Project Structure

```
├── src/                   # Source code
│   ├── main.py           # Python Slack app with kube-bench integration
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container image for Slack app
├── k8s/                  # Kubernetes manifests
│   ├── namespace.yaml    # Namespace definition
│   ├── rbac.yaml         # RBAC configuration
│   ├── slack-secret.yaml # Kubernetes secret template
│   ├── kube-bench-job.yaml # Kubernetes job with sidecar containers
│   └── kustomization.yaml # Kustomize configuration
├── scripts/              # Deployment scripts
│   ├── deploy.sh         # Complete deployment script
│   ├── helm-deploy.sh    # Helm deployment script
│   ├── create-secret.sh   # Secure secret creation
│   └── build.sh          # Docker build script
├── helm/                 # Helm chart
│   └── kube-bench-slack/ # Helm chart directory
│       ├── Chart.yaml    # Chart metadata
│       ├── values.yaml   # Default values
│       └── templates/     # Kubernetes templates
├── config/               # Configuration files
│   └── env.example       # Environment variables template
├── Makefile              # Project management commands
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 📊 Deployment Comparison

| Method | Use Case | Complexity | Configuration | Production Ready |
|--------|----------|------------|---------------|-----------------|
| **🐍 Local Python** | Testing, Development | ⭐ Simple | Environment variables | ❌ No |
| **☸️ Kubernetes** | Direct K8s deployment | ⭐⭐ Medium | YAML manifests | ✅ Yes |
| **🎛️ Helm** | Production, CI/CD | ⭐⭐⭐ Advanced | values.yaml | ✅ Yes |

## 🛠️ Available Commands

### Using Makefile (Recommended)

```bash
# Show all available commands
make help

# Local testing
make install          # Install Python dependencies
make test             # Test Slack connection locally

# Kubernetes deployment
make secret SLACK_TOKEN=xoxb-your-slack-token-here
make deploy           # Deploy with kubectl/kustomize
make status           # Check deployment status
make logs             # View application logs
make clean            # Clean up resources

# Helm deployment (recommended)
make helm-deploy      # Deploy with Helm
make helm-status      # Check Helm release status
make helm-clean       # Clean up Helm release
```

### Manual Setup

#### 1. Create Kubernetes Secret

**Option A: Using Makefile**
```bash
make secret SLACK_TOKEN=xoxb-your-slack-token-here
```

**Option B: Using script**
```bash
./scripts/create-secret.sh xoxb-your-slack-token-here
kubectl apply -f slack-secret-generated.yaml
```

**Option C: Direct kubectl**
```bash
kubectl create secret generic slack-credentials \
  --from-literal=slack-bot-token="xoxb-your-slack-token-here" \
  --namespace=kube-bench
```

#### 2. Build and Deploy

**Using Makefile:**
```bash
make build
make deploy
```

**Using scripts:**
```bash
# Build the image
docker build -t slack-kube-bench:latest -f src/Dockerfile src/

# Load into minikube
minikube image load slack-kube-bench:latest

# Deploy using kustomize
kubectl apply -k k8s/
```

## 📊 What You'll See in Slack

The Slack bot will send:

1. **Startup notification**: "🚀 Kube-bench security scan started!"
2. **Rich security report** with:
   - Total tests count
   - Passed/Failed/Warning counts
   - Control-by-control breakdown
   - Timestamp

## 🔍 Features

### Kube-bench Integration
- Runs comprehensive security scans
- Scans master, node, etcd, and policies
- Outputs structured JSON results

### Slack Notifications
- **Rich formatting** with blocks and emojis
- **Summary statistics** at a glance
- **Control-by-control** breakdown with pass rates
- **Critical areas** highlighting (controls with >5 failures)
- **Sample failed tests** with remediation steps
- **Beautiful HTML report** - Interactive, styled report with all test details
- **Error handling** with timeout notifications
- **Secure token storage** using Kubernetes secrets

### Monitoring & Logging
- Comprehensive logging for debugging
- Health checks for container monitoring
- Graceful error handling

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | Required | Your Slack bot OAuth token |
| `SLACK_CHANNEL` | `#kube-bench` | Target Slack channel |
| `KUBE_BENCH_OUTPUT_DIR` | `/tmp/kube-bench-results` | Shared volume path |
| `MAX_WAIT_TIME` | `300` | Max wait time for results (seconds) |

### Kubernetes Job Configuration

The job includes:
- **Resource limits** for both containers
- **Security context** for kube-bench
- **Volume mounts** for shared data
- **Node selector** for Linux nodes

## 🧹 Cleanup Instructions

### 🐍 Local Python Script
```bash
# No cleanup needed - just stop the script
# Ctrl+C to stop the running script
```

### ☸️ Kubernetes Deployment
```bash
# Using Makefile
make clean

# Manual cleanup
kubectl delete -k k8s/
kubectl delete secret slack-credentials -n kube-bench --ignore-not-found

# Remove Docker image (optional)
docker rmi slack-kube-bench:latest
```

### 🎛️ Helm Deployment
```bash
# Using Makefile
make helm-clean

# Manual cleanup
helm uninstall kube-bench-slack -n kube-bench
kubectl delete secret slack-credentials -n kube-bench --ignore-not-found

# Remove Docker image (optional)
docker rmi slack-kube-bench:latest
```

### 🧽 Complete Cleanup
```bash
# Remove all resources
make clean
make helm-clean

# Remove Docker images
docker rmi slack-kube-bench:latest
docker rmi aquasec/kube-bench:latest

# Remove namespace (if created)
kubectl delete namespace kube-bench --ignore-not-found
```

## 🎛️ Helm Configuration

The Helm chart provides extensive configuration options through `values.yaml`:

### Key Configuration Options

```yaml
# Slack configuration
slack:
  channel: "#kube-bench"
  image:
    repository: slack-kube-bench
    tag: latest
  
# Kube-bench configuration  
kubebench:
  targets: "master,node,etcd,policies"
  outputFormat: json
  
# Resource limits
kubebench:
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

### Custom Values

Create a custom `values.yaml` file:

```yaml
# custom-values.yaml
slack:
  channel: "#security-alerts"
  maxWaitTime: 600

kubebench:
  targets: "master,node"
  resources:
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

Deploy with custom values:
```bash
helm install kube-bench-slack helm/kube-bench-slack \
  --namespace kube-bench \
  --create-namespace \
  --values custom-values.yaml
```

## 🔒 Security Features

- **Kubernetes Secrets** for token storage
- **Non-root user** in container
- **Minimal base image** (Python slim)
- **Resource limits** to prevent resource exhaustion
- **Security contexts** for kube-bench execution

## 🐛 Troubleshooting

### Common Issues

1. **"channel_not_found" error**
   - Ensure your bot is added to the target channel
   - Check channel name format (#channel-name)

2. **"missing_scope" error**
   - Verify your bot has `chat:write` permission
   - Reinstall the bot with proper scopes

3. **Job fails to start**
   - Check minikube is running: `minikube status`
   - Verify image is loaded: `minikube image ls`

4. **No Slack notifications**
   - Check sidecar container logs
   - Verify secret is created correctly
   - Test token manually

### Debug Commands

```bash
# Check all resources
kubectl get all

# View detailed job info
kubectl describe job kube-bench-security-scan

# Check secret
kubectl get secret slack-credentials -o yaml

# Test Slack connection locally
python main.py  # (with SLACK_BOT_TOKEN set)
```

## 📈 Advanced Usage

### Custom Scan Targets

Edit `kube-bench-job.yaml` to modify scan targets:
```yaml
command: ["kube-bench", "run", "--targets", "master,node,etcd,policies", "--json"]
```

### Multiple Channels

Modify the Slack app to send to multiple channels or use different channels for different severity levels.

### Scheduled Scans

Use Kubernetes CronJob instead of Job for regular security scans:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: kube-bench-scheduled
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      # ... same template as Job
```

## 🐳 Docker Hub Best Practices

### Why Use Docker Hub?

- ✅ **Public Repos**: Share your image with the community
- ✅ **Remote Clusters**: Deploy to any Kubernetes cluster without rebuilding
- ✅ **CI/CD**: Integrate with automated pipelines
- ✅ **Version Control**: Tag and track different versions

### Recommended Workflow

```bash
# 1. Set up environment (optional)
cp config/docker.env.example config/docker.env
# Edit docker.env with your Docker Hub username
source config/docker.env

# 2. Build and push
make docker-login DOCKER_USERNAME=${DOCKER_USERNAME}
make docker-build DOCKER_USERNAME=${DOCKER_USERNAME}

# 3. Deploy anywhere
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=${DOCKER_USERNAME}
```

### Versioning

```bash
# Tag with version
make docker-build DOCKER_USERNAME=your-username IMAGE_TAG=v1.0.0

# Deploy specific version
make helm-deploy SLACK_TOKEN=xoxb-your-token \
  DOCKER_USERNAME=your-username \
  IMAGE_TAG=v1.0.0
```

### Security Notes

- 🔒 **Never commit** `config/docker.env` (it's in .gitignore)
- 🔒 Use **Docker Hub access tokens** instead of passwords
- 🔒 Consider **private repositories** for sensitive workloads
- 🔒 Enable **2FA** on your Docker Hub account

## 🚀 Quick Reference

### For One-Time Scan (Docker Hub)
```bash
make docker-login DOCKER_USERNAME=your-username
make docker-build DOCKER_USERNAME=your-username
make setup-minikube
make helm-deploy SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username
make logs
```

### For Scheduled Scans (CronJob)
```bash
# Daily at midnight GMT (default)
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username

# Custom schedule (every 6 hours)
make helm-deploy-cron SLACK_TOKEN=xoxb-your-token DOCKER_USERNAME=your-username CRON_SCHEDULE="0 */6 * * *"

# Check CronJob status
kubectl get cronjobs -n kube-bench
kubectl get jobs -n kube-bench
```

### For Testing (Local Python)
```bash
make install                    # Install dependencies
export SLACK_BOT_TOKEN=xoxb-your-token-here
make test                       # Test Slack connection
```

### For Local Kubernetes (No Docker Hub)
```bash
make setup-minikube            # Install and start minikube
make secret SLACK_TOKEN=xoxb-your-token-here
make deploy                    # One-time scan
# OR
make deploy-cron CRON_SCHEDULE="0 0 * * *"  # Scheduled scans
make status
```

### Minikube Management
```bash
make check-minikube            # Check if minikube is installed
make start-minikube            # Start minikube cluster
make stop-minikube             # Stop minikube cluster
```

### Cleanup Everything
```bash
make clean
make helm-clean
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
