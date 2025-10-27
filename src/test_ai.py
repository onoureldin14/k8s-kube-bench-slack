#!/usr/bin/env python3
"""
Test AI generation and send result to Slack
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from utils.ai_analyzer import SecurityAIAnalyzer
from kube_bench.parser import KubeBenchParser
from slack_app.client import SlackClient
from slack_app.formatter import SlackFormatter
import tempfile
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    # Check if testing retry mechanism
    test_retry = os.getenv('TEST_RETRY_MECHANISM', 'false').lower() == 'true'
    
    print("🤖 Testing AI Security Analysis Generation...")
    if test_retry:
        print("🔄 SIMULATING RETRY MECHANISM (limited to 15 findings)...")
    
    # Create dummy data
    parser = KubeBenchParser()
    dummy_data = parser.create_dummy_data()
    
    # If testing retry, create excessive findings to trigger token limit
    if test_retry:
        # Add many more failed tests to force retry
        controls = dummy_data.get('Controls', [])
        for i in range(20):  # Add 20 more failed controls
            controls.append({
                'id': f'99.{i+1}',
                'text': f'Simulated control {i+1} for retry testing',
                'total_pass': 0,
                'total_fail': 1,
                'total_warn': 0,
                'tests': [{
                    'results': [{
                        'status': 'FAIL',
                        'test_number': f'99.{i+1}.1',
                        'test_desc': 'This is a simulated failure for retry mechanism testing. ' + 'A' * 200,  # Long description
                        'remediation': 'Apply security fix. ' + 'B' * 200  # Long remediation
                    }]
                }]
            })
        dummy_data['Totals']['total_fail'] = len(controls) + 20
        dummy_data['Controls'] = controls
        print(f"✅ Created {len(controls)} controls with {dummy_data['Totals']['total_fail']} failures for retry testing")
    
    # Generate AI analysis
    print("📊 Generating AI analysis from dummy data...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set in environment")
        print("💡 Run: export OPENAI_API_KEY=sk-your-key")
        sys.exit(1)
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    try:
        analyzer = SecurityAIAnalyzer()
        print(f"✅ Analyzer created, client: {analyzer.client is not None}")
    except Exception as e:
        print(f"❌ Failed to create analyzer: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if not analyzer.client:
        print("❌ Failed to initialize OpenAI client")
        print(f"   API key present: {analyzer.api_key is not None}")
        print(f"   API key length: {len(analyzer.api_key) if analyzer.api_key else 0}")
        sys.exit(1)
    
    ai_html = analyzer.analyze_security_scan(dummy_data, dummy_data.get('version', '1.32'))
    
    if not ai_html or 'ai_summary' not in ai_html:
        print("❌ AI analysis failed")
        sys.exit(1)
    
    print("✅ AI analysis generated successfully!")
    
    # Send AI analysis as Slack blocks (like regular kube-bench report)
    print("📤 Sending AI analysis report to Slack...")
    client = SlackClient()
    
    try:
        # Create blocks for AI analysis
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 AI Security Analysis Report",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*AI-Powered Security Analysis*\nGenerated from kube-bench scan results"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{ai_html['ai_summary'][:2900]}```"  # Limit to avoid Slack's 3000 char limit
                }
            }
        ]
        
        # Send as rich message (blocks)
        client.send_rich_message(
            blocks=blocks,
            channel=os.getenv('SLACK_CHANNEL', '#kube-bench'),
            text="🤖 AI Security Analysis Report - AI-powered insights from kube-bench scan"
        )
        print("✅ AI analysis report sent to Slack successfully!")
        print("📊 Check your Slack channel for the AI analysis!")
    except Exception as e:
        print(f"❌ Failed to send AI analysis to Slack: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

