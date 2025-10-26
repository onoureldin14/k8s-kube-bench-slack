#!/bin/bash

# Build script for kube-bench Slack notifier
# Supports both local minikube and Docker Hub deployment

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
IMAGE_NAME="${IMAGE_NAME:-slack-kube-bench}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Determine build mode
if [ -n "$DOCKER_USERNAME" ]; then
    FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
    BUILD_MODE="dockerhub"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
    BUILD_MODE="local"
fi

echo "🔨 Building kube-bench Slack notifier Docker image..."
echo "📦 Mode: ${BUILD_MODE}"
echo "🏷️  Image: ${FULL_IMAGE_NAME}"
echo ""

# Build the Docker image
docker build -t ${FULL_IMAGE_NAME} -f src/Dockerfile src/

echo "✅ Docker image built successfully!"

if [ "$BUILD_MODE" = "dockerhub" ]; then
    # Docker Hub mode - push to registry
    echo "📤 Pushing image to Docker Hub..."
    docker push ${FULL_IMAGE_NAME}
    echo "✅ Image pushed to Docker Hub!"
    echo ""
    echo "🎉 Build complete! Image is available at: ${FULL_IMAGE_NAME}"
    echo ""
    echo "To deploy with Docker Hub image:"
    echo "  DOCKER_USERNAME=${DOCKER_USERNAME} kubectl apply -k k8s/"
    echo "  # Or with Helm:"
    echo "  helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \\"
    echo "    --set image.repository=${DOCKER_USERNAME}/${IMAGE_NAME} \\"
    echo "    --set image.tag=${IMAGE_TAG} \\"
    echo "    --set image.pullPolicy=Always"
else
    # Local mode - load into minikube
    echo "📦 Loading image into minikube..."
    minikube image load ${FULL_IMAGE_NAME}
    echo "✅ Image loaded into minikube!"
    echo ""
    echo "🎉 Build complete! Image is ready for use in minikube."
    echo ""
    echo "To deploy the kube-bench job:"
    echo "  kubectl apply -k k8s/"
fi

echo ""
echo "To check the job status:"
echo "  kubectl get jobs -n kube-bench"
echo "  kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier"
