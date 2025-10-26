"""
Slack Notifier Module

Handles sending kube-bench results to Slack with proper formatting.
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .client import SlackClient
from .formatter import SlackFormatter

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Handles sending kube-bench results to Slack."""
    
    def __init__(self, client: SlackClient):
        """
        Initialize the Slack notifier.
        
        Args:
            client: SlackClient instance for API interactions
        """
        self.client = client
        self.formatter = SlackFormatter()
    
    def send_kube_bench_report(self, kube_bench_data: Dict[str, Any], channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a formatted kube-bench security report to Slack.
        
        Args:
            kube_bench_data: Parsed kube-bench JSON output
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
        
        Returns:
            Response from Slack API
        """
        # Extract key information from kube-bench results
        summary = self.formatter.parse_kube_bench_summary(kube_bench_data)
        
        # Create rich blocks for the report
        blocks = self.formatter.create_kube_bench_blocks(summary, kube_bench_data)
        
        try:
            response = self.client.send_rich_message(
                channel=channel,
                text=f"🔒 Kube-bench Security Scan Results - {summary['total_tests']} tests, {summary['passed']} passed, {summary['failed']} failed",
                blocks=blocks
            )
            logger.info(f"Kube-bench report sent successfully to {channel or self.client.default_channel}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending kube-bench report: {e}")
            raise
    
    def send_test_message(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a test message to verify Slack connection.
        
        Args:
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
        
        Returns:
            Response from Slack API
        """
        try:
            # Send simple test message
            response = self.client.send_message(
                "🧪 Test message from kube-bench security scanner! 🐍",
                channel=channel
            )
            
            # Send rich test message
            blocks = self.formatter.create_test_blocks()
            self.client.send_rich_message(blocks, channel=channel)
            
            logger.info(f"Test messages sent successfully to {channel or self.client.default_channel}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            raise
    
    def send_data_as_json(self, data: Dict[str, Any], channel: Optional[str] = None, 
                         title: str = "Data Export") -> Dict[str, Any]:
        """
        Send structured data as a formatted JSON message.
        
        Args:
            data: Dictionary of data to send
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
            title: Title for the data
        
        Returns:
            Response from Slack API
        """
        blocks = self.formatter.format_json_data(data, title)
        
        try:
            response = self.client.send_rich_message(blocks, channel=channel)
            logger.info(f"JSON data sent successfully to {channel or self.client.default_channel}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending JSON data: {e}")
            raise
    
    def monitor_kube_bench_output(self, output_dir: str, channel: Optional[str] = None, 
                                 max_wait_time: int = 300) -> bool:
        """
        Monitor kube-bench output directory and send results when available.
        
        Args:
            output_dir: Directory to monitor for kube-bench output files
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
            max_wait_time: Maximum time to wait for output files (seconds)
        
        Returns:
            True if report was sent successfully, False otherwise
        """
        output_path = Path(output_dir)
        
        logger.info(f"Monitoring kube-bench output directory: {output_dir}")
        
        # Wait for kube-bench to complete and generate output files
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # Look for JSON output files
            json_files = list(output_path.glob("*.json"))
            if json_files:
                logger.info(f"Found kube-bench output files: {json_files}")
                
                # Process the most recent JSON file
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                
                try:
                    with open(latest_file, 'r') as f:
                        kube_bench_data = json.load(f)
                    
                    # Send the report
                    self.send_kube_bench_report(kube_bench_data, channel)
                    logger.info("Kube-bench report sent successfully!")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error processing kube-bench output: {e}")
                    # Send error notification
                    self.client.send_message(f"❌ Error processing kube-bench results: {str(e)}", channel)
                    return False
            
            time.sleep(5)  # Check every 5 seconds
        
        logger.warning(f"No kube-bench output found after {max_wait_time} seconds")
        self.client.send_message("⚠️ Kube-bench scan timed out - no results found", channel)
        return False
