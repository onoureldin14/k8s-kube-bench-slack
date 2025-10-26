#!/bin/bash

# Deployment script for kube-bench with Slack notifications
# Supports both local minikube and Docker Hub deployment

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
IMAGE_NAME="${IMAGE_NAME:-slack-kube-bench}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 Deploying kube-bench security scan with Slack notifications..."

# Check if minikube is running
if ! minikube status >/dev/null 2>&1; then
    echo "❌ Minikube is not running. Please start minikube first:"
    echo "   minikube start"
    exit 1
fi

echo "✅ Minikube is running"

# Determine deployment mode
if [ -n "$DOCKER_USERNAME" ]; then
    FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
    DEPLOY_MODE="dockerhub"
    echo "🐳 Using Docker Hub image: ${FULL_IMAGE_NAME}"
    echo "📋 Updating kustomization with Docker Hub image..."
    cd k8s
    kustomize edit set image slack-kube-bench=${FULL_IMAGE_NAME}
    cd ..
else
    DEPLOY_MODE="local"
    echo "📦 Using local minikube image"
    # Build and load the Docker image
    echo "🔨 Building Docker image..."
    docker build -t slack-kube-bench:latest -f src/Dockerfile src/
    
    echo "📦 Loading image into minikube..."
    minikube image load slack-kube-bench:latest
fi

# Deploy using kustomize
echo "📋 Deploying kube-bench with kustomize..."
kubectl apply -k k8s/

echo "✅ Deployment complete!"
echo ""
echo "📊 To monitor the deployment:"
echo "   kubectl get jobs -n kube-bench"
echo "   kubectl get pods -n kube-bench"
echo ""
echo "📝 To view logs:"
echo "   kubectl logs job/kube-bench-security-scan -n kube-bench -c kube-bench"
echo "   kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier"
echo ""
echo "🧹 To clean up:"
echo "   kubectl delete -k k8s/"
