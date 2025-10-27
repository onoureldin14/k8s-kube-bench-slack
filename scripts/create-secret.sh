#!/bin/bash

# Script to create Kubernetes secret for Slack token and OpenAI API key
# This is more secure than storing the token in YAML

set -e

echo "🔐 Creating Kubernetes secret for credentials..."

# Check if token is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your Slack bot token as an argument:"
    echo "   ./create-secret.sh xoxb-your-token-here [sk-your-openai-key]"
    exit 1
fi

SLACK_TOKEN="$1"
OPENAI_KEY="${2:-}"  # Optional second argument for OpenAI API key

# Create the secret using kubectl (more secure than YAML)
if [ -n "$OPENAI_KEY" ]; then
    echo "🤖 Including OpenAI API key in secret..."
    kubectl create secret generic slack-credentials \
        --from-literal=slack-bot-token="$SLACK_TOKEN" \
        --from-literal=openai-api-key="$OPENAI_KEY" \
        --dry-run=client -o yaml > slack-secret-generated.yaml
else
    kubectl create secret generic slack-credentials \
        --from-literal=slack-bot-token="$SLACK_TOKEN" \
        --dry-run=client -o yaml > slack-secret-generated.yaml
fi

echo "✅ Secret created and saved to slack-secret-generated.yaml"
echo ""
echo "To apply the secret:"
echo "   kubectl apply -f slack-secret-generated.yaml"
echo ""
echo "Or create it directly:"
if [ -n "$OPENAI_KEY" ]; then
    echo "   kubectl create secret generic slack-credentials --from-literal=slack-bot-token=\"$SLACK_TOKEN\" --from-literal=openai-api-key=\"$OPENAI_KEY\""
else
    echo "   kubectl create secret generic slack-credentials --from-literal=slack-bot-token=\"$SLACK_TOKEN\""
fi
