#!/bin/bash

# Helm deployment script for kube-bench with Slack notifications
# Supports both local minikube and Docker Hub deployment

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
IMAGE_NAME="${IMAGE_NAME:-slack-kube-bench}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
SLACK_TOKEN="${SLACK_TOKEN:-}"
RELEASE_NAME="kube-bench-slack"

echo "🚀 Deploying kube-bench security scanner with Helm..."

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first:"
    echo "   https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if minikube is running
if ! minikube status >/dev/null 2>&1; then
    echo "❌ Minikube is not running. Please start minikube first:"
    echo "   minikube start"
    exit 1
fi

echo "✅ Minikube is running"

# Prepare Helm values
HELM_ARGS=(
    "--namespace" "kube-bench"
    "--create-namespace"
    "--wait"
)

# Determine deployment mode and configure image
if [ -n "$DOCKER_USERNAME" ]; then
    FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
    DEPLOY_MODE="dockerhub"
    echo "🐳 Using Docker Hub image: ${FULL_IMAGE_NAME}"
    HELM_ARGS+=(
        "--set" "image.repository=${DOCKER_USERNAME}/${IMAGE_NAME}"
        "--set" "image.tag=${IMAGE_TAG}"
        "--set" "image.pullPolicy=Always"
    )
else
    DEPLOY_MODE="local"
    echo "📦 Using local minikube image"
    # Build and load the Docker image
    echo "🔨 Building Docker image..."
    docker build -t slack-kube-bench:latest -f src/Dockerfile src/
    
    echo "📦 Loading image into minikube..."
    minikube image load slack-kube-bench:latest
fi

# Add Slack token if provided
if [ -n "$SLACK_TOKEN" ]; then
    echo "🔐 Using provided Slack token"
    HELM_ARGS+=(
        "--set" "slack.token=${SLACK_TOKEN}"
    )
fi

# Check if release exists
if helm list -n kube-bench -q 2>/dev/null | grep -q "^${RELEASE_NAME}$"; then
    echo "📦 Upgrading existing release..."
    helm upgrade ${RELEASE_NAME} helm/kube-bench-slack "${HELM_ARGS[@]}"
else
    echo "📦 Installing new release..."
    helm install ${RELEASE_NAME} helm/kube-bench-slack "${HELM_ARGS[@]}"
fi

echo "✅ Helm deployment complete!"
echo ""
echo "📊 To monitor the deployment:"
echo "   helm status ${RELEASE_NAME} -n kube-bench"
echo "   kubectl get jobs -n kube-bench"
echo "   kubectl get pods -n kube-bench"
echo ""
echo "📝 To view logs:"
echo "   kubectl logs job/kube-bench-security-scan -n kube-bench -c kube-bench"
echo "   kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier"
echo ""

if [ -z "$SLACK_TOKEN" ]; then
    echo "🔐 To set your Slack token:"
    echo "   kubectl create secret generic slack-credentials \\"
    echo "     --from-literal=slack-bot-token=\"xoxb-your-slack-token-here\" \\"
    echo "     --namespace=kube-bench"
    echo ""
fi

echo "🧹 To clean up:"
echo "   helm uninstall ${RELEASE_NAME} -n kube-bench"
echo ""

if [ "$DEPLOY_MODE" = "dockerhub" ]; then
    echo "💡 Tip: Your image is on Docker Hub at ${FULL_IMAGE_NAME}"
    echo "   You can deploy to any Kubernetes cluster with:"
    echo "   DOCKER_USERNAME=${DOCKER_USERNAME} ./scripts/helm-deploy.sh"
fi
