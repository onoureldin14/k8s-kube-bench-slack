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
            # Test Slack connection
            self.slack_notifier.send_test_message(self.config.get_slack_channel())
            
            # Test kube-bench report functionality with dummy data
            logger.info("🔒 Testing kube-bench report functionality...")
            dummy_data = self.kube_bench_parser.create_dummy_data()
            self.slack_notifier.send_kube_bench_report(dummy_data, self.config.get_slack_channel())
            
            # Test structured data
            logger.info("📋 Testing structured data...")
            test_data = {
                "test_run": "kube-bench-slack-integration",
                "status": "success",
                "components": {
                    "slack_connection": "working",
                    "kube_bench_parser": "working",
                    "message_formatting": "working"
                }
            }
            self.slack_notifier.send_data_as_json(
                test_data, 
                self.config.get_slack_channel(), 
                "Integration Test Results"
            )
            
            logger.info("🎉 All tests completed successfully!")
            logger.info("✅ Your kube-bench Slack integration is ready to use!")
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
