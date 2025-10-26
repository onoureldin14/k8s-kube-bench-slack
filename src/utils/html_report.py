"""
HTML Report Generator Module

Converts kube-bench JSON results into a beautiful HTML report.
"""

import json
import time
from typing import Dict, Any
from pathlib import Path


class HTMLReportGenerator:
    """Generates HTML reports from kube-bench JSON data."""
    
    @staticmethod
    def generate_html_report(data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a styled HTML report from kube-bench JSON data.
        
        Args:
            data: Parsed kube-bench JSON data
            output_path: Optional path to save the HTML file
            
        Returns:
            HTML content as string
        """
        # Extract summary data
        totals = data.get('Totals', {})
        total_pass = totals.get('total_pass', 0)
        total_fail = totals.get('total_fail', 0)
        total_warn = totals.get('total_warn', 0)
        total_info = totals.get('total_info', 0)
        total_tests = total_pass + total_fail + total_warn + total_info
        
        # Calculate pass rate
        pass_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall status
        if total_fail == 0:
            status = "PASSED"
            status_color = "#10b981"
        elif total_fail < 10:
            status = "NEEDS ATTENTION"
            status_color = "#f59e0b"
        else:
            status = "CRITICAL"
            status_color = "#ef4444"
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kube-bench Security Report - {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .status-banner {{
            background: {status_color};
            color: white;
            padding: 30px;
            text-align: center;
            font-size: 1.8em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f9fafb;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .summary-card .number {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .summary-card .label {{
            color: #6b7280;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .pass {{ color: #10b981; }}
        .fail {{ color: #ef4444; }}
        .warn {{ color: #f59e0b; }}
        .info {{ color: #3b82f6; }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #1f2937;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .control {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s;
        }}
        
        .control:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .control-header {{
            background: #f9fafb;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .control-header:hover {{
            background: #f3f4f6;
        }}
        
        .control-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .control-stats {{
            display: flex;
            gap: 15px;
            font-size: 0.9em;
        }}
        
        .control-stats span {{
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
        }}
        
        .stat-pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .stat-fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .stat-warn {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .control-body {{
            display: none;
            padding: 20px;
        }}
        
        .control.expanded .control-body {{
            display: block;
        }}
        
        .control.expanded .control-header {{
            background: #667eea;
            color: white;
        }}
        
        .control.expanded .control-title {{
            color: white;
        }}
        
        .test {{
            background: #f9fafb;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #e5e7eb;
            border-radius: 4px;
        }}
        
        .test.fail {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}
        
        .test.warn {{
            border-left-color: #f59e0b;
            background: #fffbeb;
        }}
        
        .test.pass {{
            border-left-color: #10b981;
            background: #f0fdf4;
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .test-number {{
            font-weight: 600;
            color: #6b7280;
        }}
        
        .test-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-pass {{
            background: #10b981;
            color: white;
        }}
        
        .status-fail {{
            background: #ef4444;
            color: white;
        }}
        
        .status-warn {{
            background: #f59e0b;
            color: white;
        }}
        
        .test-desc {{
            color: #1f2937;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .test-remediation {{
            background: white;
            padding: 12px;
            border-radius: 4px;
            color: #4b5563;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .test-remediation strong {{
            color: #1f2937;
            display: block;
            margin-bottom: 5px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            transition: width 1s ease;
        }}
        
        .footer {{
            background: #f9fafb;
            padding: 30px;
            text-align: center;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }}
        
        .toggle-all {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            margin-bottom: 20px;
            transition: background 0.3s;
        }}
        
        .toggle-all:hover {{
            background: #5568d3;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .toggle-all {{
                display: none;
            }}
            
            .control-body {{
                display: block !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Kube-bench Security Report</h1>
            <div class="timestamp">Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</div>
            <div class="timestamp">Version: {data.get('version', 'Unknown')}</div>
        </div>
        
        <div class="status-banner">
            {status}
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Total Tests</div>
                <div class="number">{total_tests}</div>
            </div>
            <div class="summary-card">
                <div class="label">Passed</div>
                <div class="number pass">✓ {total_pass}</div>
            </div>
            <div class="summary-card">
                <div class="label">Failed</div>
                <div class="number fail">✗ {total_fail}</div>
            </div>
            <div class="summary-card">
                <div class="label">Warnings</div>
                <div class="number warn">⚠ {total_warn}</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Pass Rate</h2>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pass_rate}%">
                        {pass_rate:.1f}%
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Control Results</h2>
                <button class="toggle-all" onclick="toggleAll()">Expand/Collapse All</button>
"""
        
        # Add controls
        for control in data.get('Controls', []):
            control_id = control.get('id', 'Unknown')
            control_text = control.get('text', 'Unknown')
            control_pass = control.get('total_pass', 0)
            control_fail = control.get('total_fail', 0)
            control_warn = control.get('total_warn', 0)
            
            html += f"""
                <div class="control" onclick="toggleControl(this)">
                    <div class="control-header">
                        <div class="control-title">
                            {control_id}: {control_text}
                        </div>
                        <div class="control-stats">
                            <span class="stat-pass">✓ {control_pass}</span>
                            <span class="stat-fail">✗ {control_fail}</span>
                            <span class="stat-warn">⚠ {control_warn}</span>
                        </div>
                    </div>
                    <div class="control-body">
"""
            
            # Real kube-bench structure: Controls[].tests[].results[]
            test_sections = control.get('tests', [])
            if test_sections:
                for section in test_sections:
                    # Each section has results array with actual tests
                    results = section.get('results', [])
                    if results:
                        for test in results:
                            test_number = test.get('test_number', 'N/A')
                            test_desc = test.get('test_desc', 'No description')
                            test_status = test.get('status', 'UNKNOWN').upper()
                            test_remediation = test.get('remediation', 'No remediation provided')
                            
                            status_class = test_status.lower()
                            
                            html += f"""
                        <div class="test {status_class}">
                            <div class="test-header">
                                <span class="test-number">{test_number}</span>
                                <span class="test-status status-{status_class}">{test_status}</span>
                            </div>
                            <div class="test-desc">{test_desc}</div>
"""
                            
                            if test_remediation and test_status == 'FAIL':
                                html += f"""
                            <div class="test-remediation">
                                <strong>🔧 Remediation:</strong>
                                {test_remediation}
                            </div>
"""
                            
                            html += """
                        </div>
"""
            else:
                html += """
                        <p style="color: #6b7280; font-style: italic;">No detailed test information available for this control.</p>
"""
            
            html += """
                    </div>
                </div>
"""
        
        # Close HTML
        html += f"""
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Kube-bench Security Scanner</strong></p>
            <p>CIS Kubernetes Benchmark Assessment</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Report generated by kube-bench Slack integration<br>
                For more information, visit <a href="https://github.com/aquasecurity/kube-bench" style="color: #667eea;">github.com/aquasecurity/kube-bench</a>
            </p>
        </div>
    </div>
    
    <script>
        function toggleControl(element) {{
            element.classList.toggle('expanded');
        }}
        
        function toggleAll() {{
            const controls = document.querySelectorAll('.control');
            const allExpanded = Array.from(controls).every(c => c.classList.contains('expanded'));
            
            controls.forEach(control => {{
                if (allExpanded) {{
                    control.classList.remove('expanded');
                }} else {{
                    control.classList.add('expanded');
                }}
            }});
        }}
        
        // Animate progress bar on load
        window.addEventListener('load', () => {{
            const progressFill = document.querySelector('.progress-fill');
            const width = progressFill.style.width;
            progressFill.style.width = '0%';
            setTimeout(() => {{
                progressFill.style.width = width;
            }}, 100);
        }});
    </script>
</body>
</html>
"""
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html

