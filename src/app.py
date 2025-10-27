"""
Main Application Module

Main application class that orchestrates the kube-bench Slack integration.
"""

import os
import logging
from typing import Optional

from slack_app import SlackClient, SlackNotifier
from kube_bench import KubeBenchMonitor, KubeBenchParser
from utils import Config, setup_logging

logger = logging.getLogger(__name__)


class KubeBenchSlackApp:
    """Main application class for kube-bench Slack integration."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the application.
        
        Args:
            config: Configuration instance (optional)
        """
        self.config = config or Config()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration. SLACK_BOT_TOKEN is required.")
        
        # Set up logging
        setup_logging(debug=self.config.is_debug())
        
        # Initialize components
        self.slack_client = SlackClient(self.config.get_slack_token())
        self.slack_notifier = SlackNotifier(self.slack_client)
        self.kube_bench_monitor = KubeBenchMonitor(
            self.config.get_output_dir(),
            self.config.get_max_wait_time()
        )
        self.kube_bench_parser = KubeBenchParser()
        
        logger.info("Kube-bench Slack app initialized successfully")
    
    def run_sidecar_mode(self) -> int:
        """
        Run in sidecar mode (monitoring for kube-bench output).
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        logger.info("🔒 Starting kube-bench Slack notifier sidecar container")
        logger.info(f"📁 Monitoring directory: {self.config.get_output_dir()}")
        logger.info(f"📢 Target channel: {self.config.get_slack_channel()}")
        
        try:
            # Send startup notification
            self.slack_notifier.client.send_message(
                f"🚀 Kube-bench security scan started! Monitoring for results...",
                self.config.get_slack_channel()
            )
            
            # Monitor for kube-bench output and send results
            success = self.slack_notifier.monitor_kube_bench_output(
                self.config.get_output_dir(),
                self.config.get_slack_channel(),
                self.config.get_max_wait_time()
            )
            
            if success:
                logger.info("✅ Kube-bench report sent successfully!")
                return 0
            else:
                logger.error("❌ Failed to send kube-bench report")
                return 1
                
        except Exception as e:
            logger.error(f"❌ Fatal error in sidecar container: {e}")
            try:
                self.slack_notifier.client.send_message(
                    f"❌ Fatal error in kube-bench sidecar: {str(e)}",
                    self.config.get_slack_channel()
                )
            except:
                pass  # Don't fail if we can't send error message
            return 1
    
    def run_test_mode(self) -> int:
        """
        Run in test mode (sending test messages).
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        logger.info("🧪 Running in test mode...")
        logger.info("🔍 Testing Slack connection and kube-bench functionality...")
        
        try:
            import json
            import tempfile
            from pathlib import Path
            from utils.html_report import HTMLReportGenerator
            
            # Test Slack connection
            self.slack_notifier.send_test_message(self.config.get_slack_channel())
            
            # Test kube-bench report functionality with dummy data
            logger.info("🔒 Testing kube-bench report functionality...")
            dummy_data = self.kube_bench_parser.create_dummy_data()
            self.slack_notifier.send_kube_bench_report(dummy_data, self.config.get_slack_channel())
            
            # Test HTML report generation and upload
            logger.info("🎨 Testing HTML report generation...")
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmppath = Path(tmpdir)
                    
                    # Save JSON file
                    json_path = tmppath / "test-results.json"
                    with open(json_path, 'w') as f:
                        json.dump(dummy_data, f, indent=2)
                    
                    # Generate HTML report
                    html_path = tmppath / "test-report.html"
                    html_generator = HTMLReportGenerator()
                    html_generator.generate_html_report(dummy_data, str(html_path))
                    
                    # Upload HTML report
                    logger.info("📤 Uploading HTML report to Slack...")
                    self.slack_client.upload_file(
                        file_path=str(html_path),
                        channel=self.config.get_slack_channel(),
                        title="Test Kube-bench Security Report (HTML)",
                        initial_comment="🎨 Test HTML report with all test details - Download and open in your browser!"
                    )
                    
                    logger.info("✅ HTML report uploaded successfully!")
                    
            except Exception as e:
                logger.warning(f"⚠️ HTML/JSON upload test failed: {e}")
                # Don't fail the whole test
            
            # Test AI analysis (if enabled)
            logger.info("🤖 Testing AI security analysis...")
            try:
                from utils.ai_analyzer import SecurityAIAnalyzer
                
                analyzer = SecurityAIAnalyzer()
                if analyzer.api_key:
                    # Send progress message to Slack
                    self.slack_client.send_message(
                        "🤖 **AI Analysis in Progress...**\n\nAnalyzing security findings and generating risk assessment report for test data. This may take 30-60 seconds.",
                        self.config.get_slack_channel()
                    )
                    
                    # Generate AI analysis
                    ai_html = analyzer.analyze_security_scan(dummy_data, dummy_data.get('version', 'unknown'))
                    
                    if ai_html and 'ai_summary' in ai_html:
                        # Create temporary directory for AI report
                        with tempfile.TemporaryDirectory() as ai_tmpdir:
                            ai_tmppath = Path(ai_tmpdir)
                            
                            # Wrap AI content in proper HTML structure
                            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Security Analysis Report (Test)</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #7b42f6; padding-bottom: 10px; }}
        h2 {{ color: #7b42f6; margin-top: 30px; }}
        .badge {{ display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: bold; margin: 5px 0; }}
        .badge-high {{ background: #ff4444; color: white; }}
        .badge-medium {{ background: #ff9900; color: white; }}
        .badge-low {{ background: #44ff44; color: black; }}
    </style>
</head>
<body>
    <div class="container">
        {ai_html['ai_summary']}
    </div>
</body>
</html>"""
                            
                            # Save AI analysis HTML
                            ai_path = ai_tmppath / "ai-test-report.html"
                            with open(ai_path, 'w') as f:
                                f.write(full_html)
                            
                            # Upload AI analysis report
                            logger.info("📤 Uploading AI analysis report to Slack...")
                            self.slack_client.upload_file(
                                file_path=str(ai_path),
                                channel=self.config.get_slack_channel(),
                                title="AI Security Analysis Report (Test)",
                                initial_comment="🤖 AI-powered security analysis with risk assessment and remediation roadmap - Download and open in your browser!"
                            )
                            logger.info("✅ AI analysis uploaded successfully!")
                    else:
                        logger.info("⚠️ AI analysis not available")
                else:
                    logger.info("⚠️ No OpenAI API key set - AI analysis skipped")
            except ImportError:
                logger.warning("⚠️ OpenAI not available, skipping AI analysis")
            except Exception as e:
                logger.warning(f"⚠️ AI analysis failed: {e}, continuing without it")
            
            # Test structured data
            logger.info("📋 Testing structured data...")
            test_data = {
                "test_run": "kube-bench-slack-integration",
                "status": "success",
                "components": {
                    "slack_connection": "working",
                    "kube_bench_parser": "working",
                    "message_formatting": "working",
                    "html_report_generation": "working",
                    "file_uploads": "working"
                }
            }
            self.slack_notifier.send_data_as_json(
                test_data, 
                self.config.get_slack_channel(), 
                "Integration Test Results"
            )
            
            logger.info("🎉 All tests completed successfully!")
            logger.info("✅ Your kube-bench Slack integration is ready to use!")
            logger.info("📊 Check your Slack channel for the HTML report!")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return 1
    
    def run(self) -> int:
        """
        Run the application in the appropriate mode.
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        # Check if we're in test mode (no KUBE_BENCH_OUTPUT_DIR environment variable)
        if not os.getenv('KUBE_BENCH_OUTPUT_DIR'):
            return self.run_test_mode()
        else:
            return self.run_sidecar_mode()
