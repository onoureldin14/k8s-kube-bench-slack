# Kube-bench Security Scanner with Slack Notifications
# Makefile for easy project management

# Docker Hub configuration
DOCKER_USERNAME ?= $(shell bash -c 'read -p "Docker Hub username: " username; echo $$username')
IMAGE_NAME = slack-kube-bench
IMAGE_TAG ?= latest
FULL_IMAGE_NAME = $(DOCKER_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: help build deploy deploy-cron clean test logs status helm-deploy helm-deploy-cron helm-clean helm-status setup-minikube check-minikube start-minikube stop-minikube reset-minikube docker-build docker-push docker-login

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
	@echo "  deploy         - Deploy one-time job using kubectl/kustomize"
	@echo "  deploy-cron    - Deploy CronJob using kubectl/kustomize"
	@echo "  helm-deploy    - Deploy one-time job using Helm (recommended)"
	@echo "  helm-deploy-cron - Deploy CronJob using Helm"
	@echo "  clean          - Clean up all resources (kubectl)"
	@echo "  helm-clean     - Clean up Helm release"
	@echo "  install        - Install Python dependencies in virtual environment"
	@echo "  activate       - Show how to activate virtual environment"
	@echo "  test           - Test Slack connection locally [OPENAI_API_KEY=sk-... for AI]"
	@echo "  test-ai        - Test only AI generation (DEPRECATED: use 'make test' instead)"
	@echo "  logs           - View application logs"
	@echo "  status         - Check deployment status"
	@echo "  helm-status    - Check Helm release status"
	@echo "  secret         - Create Kubernetes secret (requires SLACK_TOKEN)"
	@echo "  openai-secret  - Create OpenAI API key secret (requires OPENAI_API_KEY)"
	@echo ""
	@echo "Quick Start (Docker Hub):"
	@echo "  make docker-login DOCKER_USERNAME=your-username"
	@echo "  make docker-build DOCKER_USERNAME=your-username"
	@echo "  make setup-minikube"
	@echo "  make secret SLACK_TOKEN=xoxb-..."
	@echo "  make openai-secret OPENAI_API_KEY=sk-... (optional)"
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

# Deploy CronJob using kubectl/kustomize
deploy-cron:
	@if [ -n "$(DOCKER_USERNAME)" ]; then \
		echo "🐳 Using Docker Hub image: $(FULL_IMAGE_NAME)"; \
		echo "📋 Deploying kube-bench CronJob..."; \
		sed "s|image: slack-kube-bench:latest|image: $(FULL_IMAGE_NAME)|g; s|imagePullPolicy: Never|imagePullPolicy: Always|g" k8s/kube-bench-cronjob.yaml | kubectl apply -f -; \
	else \
		echo "📦 Using local minikube image (building first...)"; \
		$(MAKE) build; \
		echo "📋 Deploying kube-bench CronJob..."; \
		kubectl apply -f k8s/kube-bench-cronjob.yaml; \
	fi
	@if [ -n "$(CRON_SCHEDULE)" ]; then \
		echo "⏰ Updating CronJob schedule to: $(CRON_SCHEDULE)"; \
		kubectl patch cronjob kube-bench-security-scan -n kube-bench -p '{"spec":{"schedule":"$(CRON_SCHEDULE)"}}'; \
	else \
		echo "⏰ Using default schedule: Daily at midnight GMT (0 0 * * *)"; \
	fi
	@echo "✅ CronJob deployment complete!"
	@echo ""
	@echo "📊 To check CronJob status:"
	@echo "  kubectl get cronjobs -n kube-bench"
	@echo "  kubectl get jobs -n kube-bench"

# Deploy using Helm (recommended)
helm-deploy: check-minikube
ifndef SLACK_TOKEN
	@echo "❌ SLACK_TOKEN is required. Usage: make helm-deploy SLACK_TOKEN=xoxb-your-token [DOCKER_USERNAME=your-username] [OPENAI_API_KEY=sk-your-key]"
	@exit 1
endif
	@echo "📦 Ensuring namespace exists..."
	@kubectl create namespace kube-bench --dry-run=client -o yaml | kubectl apply -f -
	@if [ -n "$(DOCKER_USERNAME)" ]; then \
		echo "🐳 Using Docker Hub image: $(FULL_IMAGE_NAME)"; \
		if [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI AI analysis enabled"; \
			echo "📋 Deploying kube-bench with Helm (with AI)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set openai.apiKey="$(OPENAI_API_KEY)" \
				--set openai.enabled=true \
				--set image.repository="$(DOCKER_USERNAME)/$(IMAGE_NAME)" \
				--set image.tag="$(IMAGE_TAG)" \
				--set image.pullPolicy="Always" \
				--namespace kube-bench \
				--wait; \
		else \
			echo "📋 Deploying kube-bench with Helm (AI disabled)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set image.repository="$(DOCKER_USERNAME)/$(IMAGE_NAME)" \
				--set image.tag="$(IMAGE_TAG)" \
				--set image.pullPolicy="Always" \
				--namespace kube-bench \
				--wait; \
		fi; \
	else \
		echo "📦 Using local minikube image (building first...)"; \
		$(MAKE) build; \
		if [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI AI analysis enabled"; \
			echo "📋 Deploying kube-bench with Helm (with AI)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set openai.apiKey="$(OPENAI_API_KEY)" \
				--set openai.enabled=true \
				--namespace kube-bench \
				--wait; \
		else \
			echo "📋 Deploying kube-bench with Helm (AI disabled)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--namespace kube-bench \
				--wait; \
		fi; \
	fi
	@echo "✅ Helm deployment complete!"
	@echo ""
	@echo "📊 Deployment status:"
	@kubectl get jobs -n kube-bench
	@echo ""
	@echo "📝 To view logs:"
	@echo "  make logs"

# Deploy CronJob using Helm
helm-deploy-cron: check-minikube
ifndef SLACK_TOKEN
	@echo "❌ SLACK_TOKEN is required. Usage: make helm-deploy-cron SLACK_TOKEN=xoxb-your-token [DOCKER_USERNAME=your-username] [OPENAI_API_KEY=sk-your-key] [CRON_SCHEDULE=\"0 0 * * *\"]"
	@exit 1
endif
	@echo "📦 Ensuring namespace exists..."
	@kubectl create namespace kube-bench --dry-run=client -o yaml | kubectl apply -f -
	@if [ -n "$(DOCKER_USERNAME)" ]; then \
		echo "🐳 Using Docker Hub image: $(FULL_IMAGE_NAME)"; \
		if [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI AI analysis enabled"; \
			echo "📋 Deploying kube-bench CronJob with Helm (with AI)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set openai.apiKey="$(OPENAI_API_KEY)" \
				--set openai.enabled=true \
				--set image.repository="$(DOCKER_USERNAME)/$(IMAGE_NAME)" \
				--set image.tag="$(IMAGE_TAG)" \
				--set image.pullPolicy="Always" \
				--set cronjob.enabled=true \
				--set cronjob.schedule="$(or $(CRON_SCHEDULE),0 0 * * *)" \
				--namespace kube-bench \
				--wait; \
		else \
			echo "📋 Deploying kube-bench CronJob with Helm (AI disabled)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set image.repository="$(DOCKER_USERNAME)/$(IMAGE_NAME)" \
				--set image.tag="$(IMAGE_TAG)" \
				--set image.pullPolicy="Always" \
				--set cronjob.enabled=true \
				--set cronjob.schedule="$(or $(CRON_SCHEDULE),0 0 * * *)" \
				--namespace kube-bench \
				--wait; \
		fi; \
	else \
		echo "📦 Using local minikube image (building first...)"; \
		$(MAKE) build; \
		if [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI AI analysis enabled"; \
			echo "📋 Deploying kube-bench CronJob with Helm (with AI)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set openai.apiKey="$(OPENAI_API_KEY)" \
				--set openai.enabled=true \
				--set cronjob.enabled=true \
				--set cronjob.schedule="$(or $(CRON_SCHEDULE),0 0 * * *)" \
				--namespace kube-bench \
				--wait; \
		else \
			echo "📋 Deploying kube-bench CronJob with Helm (AI disabled)..."; \
			helm upgrade --install kube-bench-slack ./helm/kube-bench-slack \
				--set slack.token="$(SLACK_TOKEN)" \
				--set cronjob.enabled=true \
				--set cronjob.schedule="$(or $(CRON_SCHEDULE),0 0 * * *)" \
				--namespace kube-bench \
				--wait; \
		fi; \
	fi
	@echo "✅ Helm CronJob deployment complete!"
	@echo ""
	@echo "📊 CronJob status:"
	@kubectl get cronjobs -n kube-bench
	@echo ""
	@echo "⏰ Schedule: $(or $(CRON_SCHEDULE),0 0 * * * (Daily at midnight GMT))"
	@echo ""
	@echo "📝 To view CronJob details:"
	@echo "  kubectl describe cronjob -n kube-bench"
	@echo "  kubectl get jobs -n kube-bench"

# Create Kubernetes secret
secret:
ifndef SLACK_TOKEN
	@echo "❌ SLACK_TOKEN is required. Usage: make secret SLACK_TOKEN=xoxb-your-token [OPENAI_API_KEY=sk-your-key]"
	@exit 1
endif
	@echo "🔐 Creating Kubernetes secret..."
	@echo "📦 Ensuring namespace exists..."
	@kubectl create namespace kube-bench --dry-run=client -o yaml | kubectl apply -f -
	@echo "🔑 Creating secret..."
	@if [ -n "$(OPENAI_API_KEY)" ]; then \
		echo "🤖 Including OpenAI API key in secret..."; \
		kubectl create secret generic slack-credentials \
			--from-literal=slack-bot-token="$(SLACK_TOKEN)" \
			--from-literal=openai-api-key="$(OPENAI_API_KEY)" \
			--namespace=kube-bench \
			--dry-run=client -o yaml | kubectl apply -f -; \
	else \
		kubectl create secret generic slack-credentials \
			--from-literal=slack-bot-token="$(SLACK_TOKEN)" \
			--namespace=kube-bench \
			--dry-run=client -o yaml | kubectl apply -f -; \
	fi
	@echo "✅ Secret created!"

# Create OpenAI API key secret (optional)
openai-secret:
ifndef OPENAI_API_KEY
	@echo "❌ OPENAI_API_KEY is required. Usage: make openai-secret OPENAI_API_KEY=sk-your-key"
	@exit 1
endif
	@echo "🤖 Creating OpenAI secret..."
	@echo "📦 Ensuring namespace exists..."
	@kubectl create namespace kube-bench --dry-run=client -o yaml | kubectl apply -f -
	@echo "🔑 Creating secret..."
	@kubectl create secret generic openai-credentials \
		--from-literal=openai-api-key="$(OPENAI_API_KEY)" \
		--namespace=kube-bench \
		--dry-run=client -o yaml | kubectl apply -f -
	@echo "✅ OpenAI secret created!"
	@echo "💡 AI analysis will now be enabled for security scans"

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
		if [ -n "$$OPENAI_API_KEY" ]; then \
			echo "🤖 OpenAI API key detected in environment - AI analysis will be enabled"; \
			OPENAI_API_KEY="$$OPENAI_API_KEY" . venv/bin/activate && cd src && python main.py; \
		elif [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI API key provided via argument - AI analysis will be enabled"; \
			OPENAI_API_KEY="$(OPENAI_API_KEY)" . venv/bin/activate && cd src && python main.py; \
		else \
			echo "⚠️  No OpenAI API key set - AI analysis will be skipped"; \
			echo "💡 To enable AI analysis: export OPENAI_API_KEY=sk-your-key"; \
			. venv/bin/activate && cd src && python main.py; \
		fi; \
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

# Test AI generation only (sends to Slack)
test-ai:
	@echo "🤖 Testing AI generation and sending to Slack..."
	@if [ -d "venv" ]; then \
		echo "✅ Using virtual environment..."; \
		if [ -z "$$SLACK_BOT_TOKEN" ] && [ -z "$(SLACK_BOT_TOKEN)" ]; then \
			echo "❌ SLACK_BOT_TOKEN is required for AI testing"; \
			echo "💡 To test: export SLACK_BOT_TOKEN=xoxb-your-token or make test-ai SLACK_BOT_TOKEN=xoxb-your-token"; \
			exit 1; \
		fi; \
		if [ -n "$$OPENAI_API_KEY" ]; then \
			echo "🤖 OpenAI API key detected in environment"; \
			OPENAI_API_KEY="$$OPENAI_API_KEY" SLACK_BOT_TOKEN="$$SLACK_BOT_TOKEN" . venv/bin/activate && cd src && python test_ai.py; \
		elif [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI API key provided via argument"; \
			OPENAI_API_KEY="$(OPENAI_API_KEY)" SLACK_BOT_TOKEN="$(SLACK_BOT_TOKEN)" . venv/bin/activate && cd src && python test_ai.py; \
		else \
			echo "❌ OPENAI_API_KEY is required for AI testing"; \
			echo "💡 To test: export OPENAI_API_KEY=sk-your-key or make test-ai OPENAI_API_KEY=sk-your-key"; \
			exit 1; \
		fi; \
	else \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

# Test AI retry mechanism (simulates token limit)
test-ai-retry:
	@echo "🔄 Testing AI retry mechanism with many findings..."
	@if [ -d "venv" ]; then \
		echo "✅ Using virtual environment..."; \
		if [ -z "$$SLACK_BOT_TOKEN" ] && [ -z "$(SLACK_BOT_TOKEN)" ]; then \
			echo "❌ SLACK_BOT_TOKEN is required for AI testing"; \
			echo "💡 To test: export SLACK_BOT_TOKEN=xoxb-your-token or make test-ai-retry SLACK_BOT_TOKEN=xoxb-your-token"; \
			exit 1; \
		fi; \
		if [ -n "$$OPENAI_API_KEY" ]; then \
			echo "🤖 OpenAI API key detected in environment"; \
			echo "🔄 Testing retry mechanism with limited findings..."; \
			TEST_RETRY_MECHANISM="true" OPENAI_API_KEY="$$OPENAI_API_KEY" SLACK_BOT_TOKEN="$$SLACK_BOT_TOKEN" . venv/bin/activate && cd src && python test_ai.py; \
		elif [ -n "$(OPENAI_API_KEY)" ]; then \
			echo "🤖 OpenAI API key provided via argument"; \
			echo "🔄 Testing retry mechanism with limited findings..."; \
			TEST_RETRY_MECHANISM="true" OPENAI_API_KEY="$(OPENAI_API_KEY)" SLACK_BOT_TOKEN="$(SLACK_BOT_TOKEN)" . venv/bin/activate && cd src && python test_ai.py; \
		else \
			echo "❌ OPENAI_API_KEY is required for AI testing"; \
			echo "💡 To test: export OPENAI_API_KEY=sk-your-key or make test-ai-retry OPENAI_API_KEY=sk-your-key"; \
			exit 1; \
		fi; \
	else \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
