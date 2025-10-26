"""
Configuration Module

Handles application configuration and environment variables.
"""

import os
from typing import Optional


class Config:
    """Application configuration manager."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#kube-bench')
        self.kube_bench_output_dir = os.getenv('KUBE_BENCH_OUTPUT_DIR', '/tmp/kube-bench-results')
        self.max_wait_time = int(os.getenv('MAX_WAIT_TIME', '300'))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
    
    def validate(self) -> bool:
        """
        Validate required configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.slack_bot_token:
            return False
        return True
    
    def get_slack_token(self) -> Optional[str]:
        """Get Slack bot token."""
        return self.slack_bot_token
    
    def get_slack_channel(self) -> str:
        """Get Slack channel."""
        return self.slack_channel
    
    def get_output_dir(self) -> str:
        """Get kube-bench output directory."""
        return self.kube_bench_output_dir
    
    def get_max_wait_time(self) -> int:
        """Get maximum wait time for kube-bench output."""
        return self.max_wait_time
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug
    
    def is_test_mode(self) -> bool:
        """Check if test mode is enabled."""
        return self.test_mode
