"""
Slack Client Module

Handles the core Slack API interactions and authentication.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackClient:
    """Core Slack client for API interactions."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Slack client.
        
        Args:
            token: Slack OAuth token. If not provided, will try to get from environment.
        """
        self.token = token or os.getenv('SLACK_BOT_TOKEN')
        if not self.token:
            raise ValueError("Slack OAuth token is required. Set SLACK_BOT_TOKEN environment variable or pass token directly.")
        
        self.client = WebClient(token=self.token)
        self.default_channel = os.getenv('DEFAULT_CHANNEL', '#general')
    
    def send_message(self, text: str, channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a simple text message to Slack.
        
        Args:
            text: Message text to send
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
            **kwargs: Additional parameters for the Slack API
        
        Returns:
            Response from Slack API
        """
        channel = channel or self.default_channel
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                **kwargs
            )
            logger.info(f"Message sent successfully to {channel}")
            return response.data
            
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")
            raise
    
    def send_rich_message(self, blocks: List[Dict], channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a rich message with blocks to Slack.
        
        Args:
            blocks: List of block elements for rich formatting
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
            **kwargs: Additional parameters for the Slack API
        
        Returns:
            Response from Slack API
        """
        channel = channel or self.default_channel
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                **kwargs
            )
            logger.info(f"Rich message sent successfully to {channel}")
            return response.data
            
        except SlackApiError as e:
            logger.error(f"Error sending rich message: {e.response['error']}")
            raise
    
    def send_file(self, file_path: str, channel: Optional[str] = None, 
                  title: Optional[str] = None, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a file to Slack.
        
        Args:
            file_path: Path to the file to upload
            channel: Channel to send to (defaults to DEFAULT_CHANNEL)
            title: Title for the file
            comment: Comment to include with the file
        
        Returns:
            Response from Slack API
        """
        channel = channel or self.default_channel
        
        try:
            response = self.client.files_upload(
                channels=channel,
                file=file_path,
                title=title,
                initial_comment=comment
            )
            logger.info(f"File sent successfully to {channel}")
            return response.data
            
        except SlackApiError as e:
            logger.error(f"Error sending file: {e.response['error']}")
            raise
    
    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        Get information about a channel.
        
        Args:
            channel: Channel name or ID
        
        Returns:
            Channel information
        """
        try:
            response = self.client.conversations_info(channel=channel)
            return response.data
            
        except SlackApiError as e:
            logger.error(f"Error getting channel info: {e.response['error']}")
            raise
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """
        List all channels the bot has access to.
        
        Returns:
            List of channel information
        """
        try:
            response = self.client.conversations_list()
            return response.data.get('channels', [])
            
        except SlackApiError as e:
            logger.error(f"Error listing channels: {e.response['error']}")
            raise
