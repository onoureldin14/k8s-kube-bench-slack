"""
AI Security Analyzer Module

Uses OpenAI to analyze kube-bench security scan results and provide:
- Risk prioritization
- Remediation suggestions
- Business impact assessment
- Compliance insights
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class SecurityAIAnalyzer:
    """AI-powered security analysis for kube-bench results."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI analyzer.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            # Initialize OpenAI client
            try:
                # For OpenAI 2.x+, initialize client with api_key parameter
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error details: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                self.client = None
        else:
            self.client = None
            logger.warning("⚠️ OpenAI API key not found. AI analysis will be skipped.")
    
    def analyze_security_scan(self, kube_bench_data: Dict[str, Any], 
                                k8s_version: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Analyze kube-bench results using AI to provide actionable insights.
        
        Args:
            kube_bench_data: Full kube-bench JSON output
            k8s_version: Kubernetes version detected
            
        Returns:
            Dictionary with AI analysis including:
            - overall_risk: HIGH/MEDIUM/LOW
            - priority_findings: Top 5 most critical issues
            - remediation_roadmap: Step-by-step fix plan
            - compliance_status: CIS benchmark compliance summary
            - estimated_fix_time: Time estimate for remediation
        """
        if not self.api_key or not self.client:
            logger.warning("⚠️ OpenAI client not available - API key missing or initialization failed")
            return None
        
        try:
            # Extract key information
            totals = kube_bench_data.get('Totals', {})
            controls = kube_bench_data.get('Controls', [])
            
            failed_count = totals.get('total_fail', 0)
            failed_controls = [c for c in controls if c.get('total_fail', 0) > 0]
            
            # Prepare focused prompt (ONLY failed tests, no full_data)
            prompt = self._create_analysis_prompt(
                k8s_version, failed_count, failed_controls
            )
            
            logger.info("🤖 Sending security scan to OpenAI for AI analysis...")
            
            # Try full analysis first with fresh conversation
            response = self._try_analysis(self._get_system_prompt(), prompt)
            if response:
                return response
            
            # If we get here, it failed but not with token limit
            raise Exception("Analysis failed")
        except Exception as e:
            # If token limit exceeded, retry with limited findings
            error_str = str(e)
            if 'context_length_exceeded' in error_str or 'maximum context length' in error_str:
                logger.warning(f"⚠️ Token limit exceeded, retrying with limited findings...")
                
                # Retry with only top 15 failed tests - FRESH conversation
                if len(failed_controls) > 0:
                    limited_tests_data = self._get_limited_failed_tests(failed_controls, limit=15)
                    limited_prompt = self._create_limited_prompt(
                        k8s_version, failed_count, len(limited_tests_data), limited_tests_data
                    )
                    
                    # Retry with LIMITED prompt - fresh conversation, no previous context
                    retry_response = self._try_analysis(self._get_system_prompt(), limited_prompt, limited=True, total_failures=failed_count)
                    if retry_response:
                        return retry_response
                
                # If retry also failed, give up
                logger.error("❌ Both full and limited analysis failed")
                return None
            else:
                logger.error(f"❌ Error during AI analysis: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None
    
    def _try_analysis(self, system_prompt: str, user_prompt: str, limited: bool = False, total_failures: int = 0) -> Optional[Dict[str, Any]]:
        """Try to get AI analysis with given prompts."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Add note if limited
            if limited:
                analysis_text = f"⚠️ NOTE: Due to large number of findings ({total_failures} total), this report analyzes the top 15 most critical issues.\n\n{analysis_text}"
            
            logger.debug(f"AI response preview: {analysis_text[:200]}...")
            analysis = self._parse_ai_response(analysis_text)
            logger.info("✅ AI analysis completed successfully")
            return analysis
            
        except Exception as e:
            if limited:
                # Retry failed too, return None
                logger.error(f"❌ Limited retry also failed: {e}")
                return None
            else:
                # Original failure, re-raise to trigger retry logic
                raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI context."""
        return """You are a Kubernetes security expert analyzing kube-bench scan results. 

Generate a comprehensive security analysis that:
1. ONLY focuses on FAILED tests (ignore PASS/PASS/WARN/INFO)
2. Ranks findings from HIGHEST risk (fix ASAP) to LOWEST risk
3. Explains WHY each finding is dangerous and its business impact
4. Includes: Executive Summary, Prioritized Findings with explanations, Remediation steps

Return your analysis as clean text (not HTML). Rank by severity (1 being most critical)."""

    def _get_limited_failed_tests(self, failed_controls: list, limit: int = 15) -> list:
        """Get only the first N failed tests to avoid token limits."""
        limited_tests = []
        count = 0
        for control in failed_controls:
            if count >= limit:
                break
            control_id = control.get('id', 'Unknown')
            
            for test_section in control.get('tests', []):
                if count >= limit:
                    break
                for test in test_section.get('results', []):
                    if count >= limit:
                        break
                    if test.get('status', '').upper() == 'FAIL':
                        limited_tests.append({
                            'control_id': control_id,
                            'test_number': test.get('test_number', 'N/A'),
                            'test_desc': test.get('test_desc', 'No description'),
                            'remediation': test.get('remediation', 'No remediation provided')
                        })
                        count += 1
        return limited_tests
    
    def _create_limited_prompt(self, k8s_version: str, total_failures: int, limited_count: int, limited_tests: list) -> str:
        """Create prompt for limited analysis."""
        return f"""Analyze ONLY the FAILED kube-bench tests and generate a security analysis report.

⚠️ NOTE: Only analyzing top {limited_count} of {total_failures} total failures due to token limits.

Kubernetes Version: {k8s_version}
Total Failures: {total_failures}
Analyzing: {limited_count} most critical issues

FAILED TESTS TO ANALYZE (analyze these ONLY):
{json.dumps(limited_tests, indent=2)}

Provide a comprehensive security analysis including:

1. Executive Summary (overall risk assessment)

2. Critical Findings section with ranked list (#1 to #{limited_count}, highest risk first) where EACH finding includes:
   - Rank/priority number (#1 = fix ASAP)
   - Severity rating (Critical/High/Medium/Low)
   - Test number and description
   - WHY IT'S DANGEROUS: Explain business impact, attack vectors, compliance risk
   - EXPLANATION: What could attackers do? What data/systems are at risk?
   - Remediation steps with time estimate

CRITICAL: You MUST list ALL {limited_count} findings in full detail. Do NOT use placeholders like "[...continue...]" or "[...13 more...]". List every single finding #1 through #{limited_count}.

3. Risk Assessment section explaining why these findings are dangerous

4. Remediation Roadmap with prioritized action items

5. Compliance Status section

IMPORTANT:
- ONLY analyze the tests provided
- Rank by severity (1 is most critical)
- Explain WHY each finding is dangerous
- Return your analysis as clear, structured text (not HTML)"""

    def _create_analysis_prompt(self, k8s_version: str, failed_count: int, 
                               failed_controls: list) -> str:
        """Create the user prompt with scan details."""
        
        # Collect ALL failed tests with full details (limit description length to avoid token limits)
        all_failed_tests = []
        for control in failed_controls:
            control_id = control.get('id', 'Unknown')
            control_text = control.get('text', 'Unknown')
            
            for test_section in control.get('tests', []):
                for test in test_section.get('results', []):
                    if test.get('status', '').upper() == 'FAIL':
                        all_failed_tests.append({
                            'control_id': control_id,
                            'test_number': test.get('test_number', 'N/A'),
                            'test_desc': test.get('test_desc', 'No description'),
                            'remediation': test.get('remediation', 'No remediation provided')
                        })
        
        return f"""Analyze ONLY the FAILED kube-bench tests and generate a security analysis report.

Kubernetes Version: {k8s_version}
Total Failures: {failed_count}
Failed Controls: {len(failed_controls)}

ALL FAILED TESTS (analyze these ONLY, ignore all PASS/WARN/INFO):
{json.dumps(all_failed_tests, indent=2)}

Provide a comprehensive security analysis including:

1. Executive Summary (overall risk assessment)

2. Critical Findings section with ranked list (#1 to #{len(all_failed_tests)}, highest risk first) where EACH finding includes:
   - Rank/priority number (#1 = fix ASAP)
   - Severity rating (Critical/High/Medium/Low)
   - Test number and description
   - WHY IT'S DANGEROUS: Explain business impact, attack vectors, compliance risk
   - EXPLANATION: What could attackers do? What data/systems are at risk?
   - Remediation steps with time estimate

3. Risk Assessment section explaining why these findings are dangerous

4. Remediation Roadmap with prioritized action items

5. Compliance Status section

IMPORTANT:
- ONLY analyze FAILED tests
- Rank by severity (1 is most critical)
- Explain WHY each finding is dangerous
- Return your analysis as clear, structured text (not HTML)"""

    def _format_controls_summary(self, controls: list) -> str:
        """Format control summaries for prompt."""
        summary = []
        for ctrl in controls:
            summary.append(
                f"Control {ctrl.get('id')}: {ctrl.get('text')} - "
                f"Fail: {ctrl.get('total_fail')}, Pass: {ctrl.get('total_pass')}"
            )
        return "\n".join(summary)

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format.
        This is a simple parser - you could make it smarter with regex/formatting.
        """
        try:
            # Clean up the response if needed
            cleaned_text = response_text.strip()
            
            # Convert the text analysis to HTML with our styling
            html_content = self._wrap_ai_content_in_html(cleaned_text)
            
            return {
                'ai_summary': html_content,
                'raw_response': cleaned_text
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            # Return the raw response wrapped in basic HTML
            html_content = self._wrap_ai_content_in_html(response_text)
        return {
                'ai_summary': html_content,
            'raw_response': response_text
        }
    
    def _wrap_ai_content_in_html(self, text_content: str) -> str:
        """Wrap AI text content in styled HTML with enhanced colors and styling."""
        import time
        import re
        
        # Process the text to add color-coded severity badges
        processed_content = self._add_severity_badges(text_content)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Security Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #7b42f6;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #7b42f6;
            margin-top: 30px;
            font-size: 1.5em;
        }}
        .severity-critical {{
            background: #ff4444;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
            display: inline-block;
        }}
        .severity-high {{
            background: #ff9900;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
            display: inline-block;
        }}
        .severity-medium {{
            background: #ffcc00;
            color: black;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
            display: inline-block;
        }}
        .severity-low {{
            background: #44ff44;
            color: black;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
            display: inline-block;
        }}
        .finding-box {{
            background: #fff5f5;
            border-left: 4px solid #ff4444;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .finding-box-high {{
            background: #fff8f0;
            border-left: 4px solid #ff9900;
        }}
        .finding-box-medium {{
            background: #fffef0;
            border-left: 4px solid #ffcc00;
        }}
        .rank-number {{
            font-size: 1.3em;
            font-weight: bold;
            color: #7b42f6;
            display: inline-block;
            margin-right: 10px;
        }}
        .label {{
            font-weight: bold;
            color: #333;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .content-text {{
            white-space: pre-wrap;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Security Analysis Report</h1>
        <div class="timestamp">Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</div>
        <div class="content-text">{processed_content}</div>
    </div>
</body>
</html>"""
    
    def _add_severity_badges(self, text: str) -> str:
        """Add HTML styling to severity levels in the AI response."""
        import re
        
        # Replace severity: Critical
        text = re.sub(
            r'Severity:\s*Critical',
            lambda m: f'<span class="severity-critical">🔴 Critical</span>',
            text,
            flags=re.IGNORECASE
        )
        
        # Replace severity: High
        text = re.sub(
            r'Severity:\s*High',
            lambda m: f'<span class="severity-high">🟠 High</span>',
            text,
            flags=re.IGNORECASE
        )
        
        # Replace severity: Medium
        text = re.sub(
            r'Severity:\s*Medium',
            lambda m: f'<span class="severity-medium">🟡 Medium</span>',
            text,
            flags=re.IGNORECASE
        )
        
        # Replace severity: Low
        text = re.sub(
            r'Severity:\s*Low',
            lambda m: f'<span class="severity-low">🟢 Low</span>',
            text,
            flags=re.IGNORECASE
        )
        
        # Style section headers
        text = re.sub(r'^(EXECUTIVE SUMMARY:|CRITICAL FINDINGS:|RISK ASSESSMENT:|REMEDIATION ROADMAP:|COMPLIANCE STATUS:)', 
                     r'<h2>\1</h2>', 
                     text, 
                     flags=re.MULTILINE)
        
        # Style the Rank: X lines
        text = re.sub(r'(\d+)\.\s*Rank:\s*(\d+)', r'<div style="margin-top: 25px;"><span class="rank-number">#\2</span>', text)
        
        # Add label styling
        text = re.sub(r'(Test:|WHY IT\'S DANGEROUS:|EXPLANATION:|Remediation:|Estimated time:)', 
                     r'<span class="label">\1</span>', 
                     text, 
                     flags=re.IGNORECASE)
        
        return text

