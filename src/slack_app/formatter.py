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
        # Extract version from first control if available
        version = 'Unknown'
        if 'Controls' in data and len(data['Controls']) > 0:
            first_control = data['Controls'][0]
            # Prefer detected_version (actual k8s version) over version (CIS benchmark version)
            version = first_control.get('detected_version', first_control.get('version', 'Unknown'))
        
        summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warned': 0,
            'info': 0,
            'controls': [],
            'critical_failures': [],
            'version': version
        }
        
        # Get totals from the top level if available
        if 'Totals' in data:
            totals = data['Totals']
            summary['passed'] = totals.get('total_pass', 0)
            summary['failed'] = totals.get('total_fail', 0)
            summary['warned'] = totals.get('total_warn', 0)
            summary['info'] = totals.get('total_info', 0)
            summary['total_tests'] = summary['passed'] + summary['failed'] + summary['warned'] + summary['info']
        
        if 'Controls' in data:
            for control in data['Controls']:
                control_id = control.get('id', 'Unknown')
                control_text = control.get('text', 'Unknown')
                control_type = control.get('node_type', 'Unknown')
                
                control_summary = {
                    'id': control_id,
                    'text': control_text,
                    'type': control_type,
                    'passed': control.get('total_pass', 0),
                    'failed': control.get('total_fail', 0),
                    'warned': control.get('total_warn', 0),
                    'info': control.get('total_info', 0)
                }
                
                summary['controls'].append(control_summary)
                
                # Collect critical failures (high fail count)
                if control_summary['failed'] > 5:
                    summary['critical_failures'].append({
                        'control': f"{control_id}: {control_text}",
                        'failed': control_summary['failed']
                    })
        
        return summary
    
    @staticmethod
    def create_kube_bench_blocks(summary: Dict[str, Any], full_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Slack blocks for kube-bench report."""
        # Determine overall status
        total_issues = summary['failed'] + summary['warned']
        if summary['failed'] == 0:
            status_emoji = "✅"
            status_text = "PASSED"
            status_color = "#36a64f"
        elif summary['failed'] < 10:
            status_emoji = "⚠️"
            status_text = "NEEDS ATTENTION"
            status_color = "#ff9900"
        else:
            status_emoji = "❌"
            status_text = "CRITICAL"
            status_color = "#ff0000"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} Kube-bench Security Scan Results",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Status:* {status_text}\n*Version:* {summary.get('version', 'Unknown')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tests:*\n`{summary['total_tests']}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Passed:*\n✅ `{summary['passed']}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n❌ `{summary['failed']}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Warnings:*\n⚠️ `{summary['warned']}`"
                    }
                ]
            }
        ]
        
        # Add critical failures section if any
        if summary.get('critical_failures'):
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🚨 Critical Areas (>5 failures):*"
                }
            })
            for failure in summary['critical_failures'][:3]:  # Show top 3
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {failure['control']}\n  Failed: `{failure['failed']}` tests"
                    }
                })
        
        # Add control summaries
        if summary['controls']:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Control Summary:*"
                }
            })
            
            for control in summary['controls']:
                # Calculate pass rate
                total = control['passed'] + control['failed'] + control['warned']
                pass_rate = (control['passed'] / total * 100) if total > 0 else 0
                
                # Choose emoji based on pass rate
                if pass_rate == 100:
                    emoji = "✅"
                elif pass_rate >= 80:
                    emoji = "⚠️"
                else:
                    emoji = "❌"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *{control['id']}: {control['text']}*\n"
                               f"Pass: `{control['passed']}` | Fail: `{control['failed']}` | Warn: `{control['warned']}` | Pass Rate: `{pass_rate:.1f}%`"
                    }
                })
        
        # Add timestamp and footer
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"⏰ Scan completed: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} | 📄 Full HTML report attached below"
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
