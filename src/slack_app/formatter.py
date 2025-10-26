"""
Slack Formatter Module

Handles formatting of kube-bench results into Slack message blocks.
"""

import json
import time
from typing import Dict, Any, List


class SlackFormatter:
    """Formats kube-bench results into Slack message blocks."""
    
    @staticmethod
    def parse_kube_bench_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse kube-bench data to extract summary information."""
        summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warned': 0,
            'info': 0,
            'controls': []
        }
        
        if 'Controls' in data:
            for control in data['Controls']:
                control_name = control.get('id', 'Unknown')
                control_results = control.get('results', [])
                
                control_summary = {
                    'name': control_name,
                    'total': len(control_results),
                    'passed': 0,
                    'failed': 0,
                    'warned': 0,
                    'info': 0
                }
                
                for result in control_results:
                    status = result.get('status', '').lower()
                    if status == 'pass':
                        control_summary['passed'] += 1
                        summary['passed'] += 1
                    elif status == 'fail':
                        control_summary['failed'] += 1
                        summary['failed'] += 1
                    elif status == 'warn':
                        control_summary['warned'] += 1
                        summary['warned'] += 1
                    elif status == 'info':
                        control_summary['info'] += 1
                        summary['info'] += 1
                    
                    summary['total_tests'] += 1
                
                summary['controls'].append(control_summary)
        
        return summary
    
    @staticmethod
    def create_kube_bench_blocks(summary: Dict[str, Any], full_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Slack blocks for kube-bench report."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔒 Kube-bench Security Scan Results"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tests:*\n{summary['total_tests']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Passed:*\n✅ {summary['passed']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n❌ {summary['failed']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Warnings:*\n⚠️ {summary['warned']}"
                    }
                ]
            }
        ]
        
        # Add control summaries
        if summary['controls']:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Control Results:*"
                }
            })
            
            for control in summary['controls'][:5]:  # Show first 5 controls
                status_emoji = "✅" if control['failed'] == 0 else "❌"
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{status_emoji} *{control['name']}*\nPassed: {control['passed']}, Failed: {control['failed']}, Warnings: {control['warned']}"
                    }
                })
        
        # Add timestamp
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Scan completed at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
                }
            ]
        })
        
        return blocks
    
    @staticmethod
    def create_test_blocks() -> List[Dict[str, Any]]:
        """Create blocks for test messages."""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔒 Kube-bench Security Test Report"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Test Status:*\n✅ Connection Working"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Bot Status:*\n🤖 Ready for kube-bench"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a *test message* to verify the kube-bench Slack integration is working correctly! 🎉"
                }
            }
        ]
    
    @staticmethod
    def format_json_data(data: Dict[str, Any], title: str = "Data Export") -> List[Dict[str, Any]]:
        """Format structured data as JSON blocks."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```json\n{json.dumps(data, indent=2)}\n```"
                }
            }
        ]
        
        return blocks
