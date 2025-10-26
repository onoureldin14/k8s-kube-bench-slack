#!/bin/bash

# Script to create Kubernetes secret for Slack token
# This is more secure than storing the token in YAML

set -e

echo "🔐 Creating Kubernetes secret for Slack credentials..."

# Check if token is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your Slack bot token as an argument:"
    echo "   ./create-secret.sh xoxb-your-token-here"
    exit 1
fi

SLACK_TOKEN="$1"

# Create the secret using kubectl (more secure than YAML)
kubectl create secret generic slack-credentials \
    --from-literal=slack-bot-token="$SLACK_TOKEN" \
    --dry-run=client -o yaml > slack-secret-generated.yaml

echo "✅ Secret created and saved to slack-secret-generated.yaml"
echo ""
echo "To apply the secret:"
echo "   kubectl apply -f slack-secret-generated.yaml"
echo ""
echo "Or create it directly:"
echo "   kubectl create secret generic slack-credentials --from-literal=slack-bot-token=\"$SLACK_TOKEN\""
