"""
Kube-bench Monitor Module

Handles monitoring for kube-bench output files and processing results.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .parser import KubeBenchParser

logger = logging.getLogger(__name__)


class KubeBenchMonitor:
    """Monitors kube-bench output directory for scan results."""
    
    def __init__(self, output_dir: str, max_wait_time: int = 300):
        """
        Initialize the kube-bench monitor.
        
        Args:
            output_dir: Directory to monitor for kube-bench output files
            max_wait_time: Maximum time to wait for output files (seconds)
        """
        self.output_dir = Path(output_dir)
        self.max_wait_time = max_wait_time
        self.parser = KubeBenchParser()
    
    def wait_for_output(self) -> Optional[Dict[str, Any]]:
        """
        Wait for kube-bench output files and return the latest results.
        
        Returns:
            Parsed kube-bench data or None if timeout
        """
        logger.info(f"Monitoring kube-bench output directory: {self.output_dir}")
        
        start_time = time.time()
        while time.time() - start_time < self.max_wait_time:
            # Look for JSON output files
            json_files = list(self.output_dir.glob("*.json"))
            if json_files:
                logger.info(f"Found kube-bench output files: {json_files}")
                
                # Process the most recent JSON file
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                
                try:
                    data = self.parser.parse_json_file(str(latest_file))
                    logger.info("Kube-bench output processed successfully!")
                    return data
                    
                except Exception as e:
                    logger.error(f"Error processing kube-bench output: {e}")
                    return None
            
            time.sleep(5)  # Check every 5 seconds
        
        logger.warning(f"No kube-bench output found after {self.max_wait_time} seconds")
        return None
    
    def get_latest_output(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest kube-bench output without waiting.
        
        Returns:
            Parsed kube-bench data or None if no files found
        """
        json_files = list(self.output_dir.glob("*.json"))
        if not json_files:
            logger.info("No kube-bench output files found")
            return None
        
        # Get the most recent file
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        try:
            data = self.parser.parse_json_file(str(latest_file))
            logger.info(f"Retrieved latest kube-bench output from {latest_file}")
            return data
        except Exception as e:
            logger.error(f"Error processing latest kube-bench output: {e}")
            return None
    
    def is_output_available(self) -> bool:
        """
        Check if kube-bench output files are available.
        
        Returns:
            True if output files exist, False otherwise
        """
        json_files = list(self.output_dir.glob("*.json"))
        return len(json_files) > 0
