# Kube-bench Security Scanner with Slack Notifications
# Makefile for easy project management

# Docker Hub configuration
DOCKER_USERNAME ?= $(shell bash -c 'read -p "Docker Hub username: " username; echo $$username')
IMAGE_NAME = slack-kube-bench
IMAGE_TAG ?= latest
FULL_IMAGE_NAME = $(DOCKER_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: help build deploy clean test logs status helm-deploy helm-clean helm-status setup-minikube check-minikube start-minikube stop-minikube reset-minikube docker-build docker-push docker-login

# Default target
help:
	@echo "🔒 Kube-bench Security Scanner with Slack Notifications"
	@echo ""
	@echo "Available targets:"
	@echo "  setup-minikube - Install and setup minikube (if needed)"
	@echo "  start-minikube - Start minikube cluster"
	@echo "  stop-minikube  - Stop minikube cluster"
	@echo "  reset-minikube - Delete and recreate minikube cluster"
	@echo "  check-minikube - Check minikube status"
	@echo "  docker-login   - Login to Docker Hub"
	@echo "  docker-build   - Build and push Docker image to Docker Hub"
	@echo "  docker-push    - Push existing image to Docker Hub"
	@echo "  build          - Build Docker image (for local use)"
	@echo "  deploy         - Deploy using kubectl/kustomize"
	@echo "  helm-deploy    - Deploy using Helm (recommended)"
	@echo "  clean          - Clean up all resources (kubectl)"
	@echo "  helm-clean     - Clean up Helm release"
	@echo "  install        - Install Python dependencies in virtual environment"
	@echo "  activate       - Show how to activate virtual environment"
	@echo "  test           - Test Slack connection locally"
	@echo "  logs           - View application logs"
	@echo "  status         - Check deployment status"
	@echo "  helm-status    - Check Helm release status"
	@echo "  secret         - Create Kubernetes secret (requires SLACK_TOKEN)"
	@echo ""
	@echo "Quick Start (Docker Hub):"
	@echo "  make docker-login DOCKER_USERNAME=your-username"
	@echo "  make docker-build DOCKER_USERNAME=your-username"
	@echo "  make setup-minikube"
	@echo "  make secret SLACK_TOKEN=xoxb-..."
	@echo "  make helm-deploy DOCKER_USERNAME=your-username"

# Check if minikube is installed
check-minikube:
	@echo "🔍 Checking minikube installation..."
	@if command -v minikube >/dev/null 2>&1; then \
		echo "✅ Minikube is installed"; \
		minikube version; \
	else \
		echo "❌ Minikube is not installed"; \
		echo "Run 'make setup-minikube' to install it"; \
		exit 1; \
	fi

# Install minikube (macOS, Linux, Windows)
setup-minikube:
	@echo "🔧 Setting up minikube..."
	@if command -v minikube >/dev/null 2>&1; then \
		echo "✅ Minikube is already installed"; \
		minikube version; \
	else \
		echo "📦 Installing minikube..."; \
		if [ "$$(uname)" = "Darwin" ]; then \
			echo "🍎 Detected macOS"; \
			if command -v brew >/dev/null 2>&1; then \
				echo "Installing via Homebrew..."; \
				brew install minikube; \
			else \
				echo "❌ Homebrew not found. Please install Homebrew first:"; \
				echo "   /bin/bash -c \"\$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""; \
				exit 1; \
			fi; \
		elif [ "$$(uname)" = "Linux" ]; then \
			echo "🐧 Detected Linux"; \
			curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64; \
			sudo install minikube-linux-amd64 /usr/local/bin/minikube; \
			rm minikube-linux-amd64; \
		else \
			echo "❌ Unsupported OS. Please install minikube manually:"; \
			echo "   https://minikube.sigs.k8s.io/docs/start/"; \
			exit 1; \
		fi; \
		echo "✅ Minikube installed successfully!"; \
	fi
	@echo ""
	@echo "🚀 Starting minikube cluster..."
	@$(MAKE) start-minikube

# Start minikube cluster
start-minikube:
	@echo "🚀 Starting minikube cluster..."
	@if ! command -v minikube >/dev/null 2>&1; then \
		echo "❌ Minikube not found. Run 'make setup-minikube' first"; \
		exit 1; \
	fi
	@echo "🔍 Checking cluster state..."
	@if minikube status 2>&1 | grep -q "host: Running"; then \
		echo "✅ Minikube is already running"; \
		minikube status; \
	else \
		echo "🔄 Starting minikube (this may take a few minutes)..."; \
		minikube delete 2>/dev/null || true; \
		minikube start --driver=docker --cpus=2 --memory=3072; \
		echo "✅ Minikube started successfully!"; \
	fi
	@echo ""
	@echo "📊 Cluster info:"
	@kubectl cluster-info
	@echo ""
	@echo "✅ Minikube is ready!"

# Stop minikube cluster
stop-minikube:
	@echo "🛑 Stopping minikube cluster..."
	@if ! command -v minikube >/dev/null 2>&1; then \
		echo "❌ Minikube not found"; \
		exit 1; \
	fi
	@if minikube status 2>&1 | grep -q "host: Running"; then \
		minikube stop; \
		echo "✅ Minikube stopped successfully!"; \
	else \
		echo "ℹ️  Minikube is not running"; \
	fi

# Reset minikube cluster (delete and recreate)
reset-minikube:
	@echo "🔄 Resetting minikube cluster..."
	@if ! command -v minikube >/dev/null 2>&1; then \
		echo "❌ Minikube not found. Run 'make setup-minikube' first"; \
		exit 1; \
	fi
	@echo "⚠️  This will delete the existing cluster and all data!"
	@echo "🗑️  Deleting existing cluster..."
	@minikube delete 2>/dev/null || true
	@echo "✅ Cluster deleted"
	@echo ""
	@echo "🚀 Creating new cluster..."
	@minikube start --driver=docker --cpus=2 --memory=3072
	@echo "✅ New cluster created successfully!"
	@echo ""
	@echo "📊 Cluster info:"
	@kubectl cluster-info
	@echo ""
	@echo "✅ Minikube reset complete!"

# Login to Docker Hub
docker-login:
ifndef DOCKER_USERNAME
	@echo "❌ DOCKER_USERNAME is required. Usage: make docker-login DOCKER_USERNAME=your-username"
	@exit 1
endif
	@echo "🔐 Logging in to Docker Hub as $(DOCKER_USERNAME)..."
	@docker login -u $(DOCKER_USERNAME)
	@echo "✅ Logged in successfully!"

# Build and push Docker image to Docker Hub
docker-build:
ifndef DOCKER_USERNAME
	@echo "❌ DOCKER_USERNAME is required. Usage: make docker-build DOCKER_USERNAME=your-username"
	@exit 1
endif
	@echo "🔨 Building Docker image for Docker Hub..."
	@echo "📦 Image: $(FULL_IMAGE_NAME)"
	docker build -t $(FULL_IMAGE_NAME) -f src/Dockerfile src/
	@echo "📤 Pushing image to Docker Hub..."
	docker push $(FULL_IMAGE_NAME)
	@echo "✅ Image built and pushed successfully!"
	@echo "📋 Image name: $(FULL_IMAGE_NAME)"

# Push existing image to Docker Hub
docker-push:
ifndef DOCKER_USERNAME
	@echo "❌ DOCKER_USERNAME is required. Usage: make docker-push DOCKER_USERNAME=your-username"
	@exit 1
endif
	@echo "📤 Pushing image to Docker Hub..."
	@echo "📦 Image: $(FULL_IMAGE_NAME)"
	docker push $(FULL_IMAGE_NAME)
	@echo "✅ Image pushed successfully!"

# Build Docker image for local minikube use
build: check-minikube
	@echo "🔨 Building Docker image for local use..."
	docker build -t slack-kube-bench:latest -f src/Dockerfile src/
	@echo "📦 Loading image into minikube..."
	minikube image load slack-kube-bench:latest
	@echo "✅ Build complete!"

# Deploy the complete solution using kubectl/kustomize
deploy:
	@if [ -n "$(DOCKER_USERNAME)" ]; then \
		echo "🐳 Using Docker Hub image: $(FULL_IMAGE_NAME)"; \
		echo "📋 Updating kustomization with Docker Hub image..."; \
		cd k8s && kustomize edit set image slack-kube-bench=$(FULL_IMAGE_NAME); \
		echo "📋 Deploying kube-bench with kustomize..."; \
		kubectl apply -k k8s/; \
	else \
		echo "📦 Using local minikube image (building first...)"; \
		$(MAKE) build; \
		echo "📋 Deploying kube-bench with kustomize..."; \
		kubectl apply -k k8s/; \
	fi
	@echo "✅ Deployment complete!"

# Deploy using Helm (recommended)
helm-deploy: check-minikube
ifndef SLACK_TOKEN
	@echo "❌ SLACK_TOKEN is required. Usage: make helm-deploy SLACK_TOKEN=xoxb-your-token [DOCKER_USERNAME=your-username]"
	@exit 1
endif
	@if [ -n "$(DOCKER_USERNAME)" ]; then \
		echo "🐳 Using Docker Hub image: $(FULL_IMAGE_NAME)"; \
		echo "📋 Deploying kube-bench with Helm..."; \
		helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
			--set slack.token="$(SLACK_TOKEN)" \
			--set image.repository="$(DOCKER_USERNAME)/$(IMAGE_NAME)" \
			--set image.tag="$(IMAGE_TAG)" \
			--set image.pullPolicy="Always" \
			--create-namespace \
			--namespace kube-bench \
			--wait; \
	else \
		echo "📦 Using local minikube image (building first...)"; \
		$(MAKE) build; \
		echo "📋 Deploying kube-bench with Helm..."; \
		helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
			--set slack.token="$(SLACK_TOKEN)" \
			--create-namespace \
			--namespace kube-bench \
			--wait; \
	fi
	@echo "✅ Helm deployment complete!"
	@echo ""
	@echo "📊 Deployment status:"
	@kubectl get jobs -n kube-bench
	@echo ""
	@echo "📝 To view logs:"
	@echo "  make logs"

# Create Kubernetes secret
secret:
ifndef SLACK_TOKEN
	@echo "❌ SLACK_TOKEN is required. Usage: make secret SLACK_TOKEN=xoxb-your-token"
	@exit 1
endif
	@echo "🔐 Creating Kubernetes secret..."
	@echo "📦 Ensuring namespace exists..."
	@kubectl create namespace kube-bench --dry-run=client -o yaml | kubectl apply -f -
	@echo "🔑 Creating secret..."
	@kubectl create secret generic slack-credentials \
		--from-literal=slack-bot-token="$(SLACK_TOKEN)" \
		--namespace=kube-bench \
		--dry-run=client -o yaml | kubectl apply -f -
	@echo "✅ Secret created!"

# Activate virtual environment
activate:
	@echo "🔧 Activating virtual environment..."
	@if [ -d "venv" ]; then \
		echo "✅ Virtual environment found!"; \
		echo "💡 Run: source venv/bin/activate"; \
		echo "💡 Then you can run: cd src && python main.py"; \
	else \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

# Test Slack connection locally
test:
	@echo "🧪 Testing Slack connection..."
	@if [ -d "venv" ]; then \
		echo "✅ Using virtual environment..."; \
		. venv/bin/activate && cd src && python main.py; \
	else \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

# View application logs
logs:
	@echo "📝 Viewing application logs..."
	@echo "Kube-bench logs:"
	kubectl logs job/kube-bench-security-scan -n kube-bench -c kube-bench --tail=50
	@echo ""
	@echo "Slack notifier logs:"
	kubectl logs job/kube-bench-security-scan -n kube-bench -c slack-notifier --tail=50

# Check deployment status
status:
	@echo "📊 Deployment status:"
	kubectl get all -n kube-bench
	@echo ""
	@echo "Job details:"
	kubectl describe job kube-bench-security-scan -n kube-bench

# Check Helm release status
helm-status:
	@echo "📊 Helm release status:"
	helm status kube-bench-slack -n kube-bench
	@echo ""
	@echo "Release history:"
	helm history kube-bench-slack -n kube-bench

# Clean up all resources (kubectl)
clean:
	@echo "🧹 Cleaning up resources..."
	kubectl delete -k k8s/ --ignore-not-found=true
	@echo "✅ Cleanup complete!"

# Clean up Helm release
helm-clean:
	@echo "🧹 Cleaning up Helm release..."
	helm uninstall kube-bench-slack -n kube-bench --ignore-not-found
	@echo "✅ Helm cleanup complete!"

# Install dependencies for local development
install:
	@echo "📦 Installing Python dependencies..."
	@echo "🔍 Setting up Python environment..."
	@if [ -d "venv" ]; then \
		echo "✅ Virtual environment found, activating..."; \
		. venv/bin/activate && cd src && pip install -r requirements.txt; \
	else \
		echo "🔧 Creating virtual environment..."; \
		python3 -m venv venv; \
		echo "✅ Virtual environment created, activating..."; \
		. venv/bin/activate && cd src && pip install -r requirements.txt; \
	fi
	@echo "✅ Dependencies installed!"
	@echo "💡 To activate the virtual environment manually: source venv/bin/activate"

# Run linting
lint:
	@echo "🔍 Running linting..."
	cd src && python -m flake8 main.py --max-line-length=100
	@echo "✅ Linting complete!"

# Format code
format:
	@echo "🎨 Formatting code..."
	cd src && python -m black main.py
	@echo "✅ Code formatted!"
