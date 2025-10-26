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
    
    def _is_file_complete(self, file_path: Path, stability_time: int = 3) -> bool:
        """
        Check if a file has finished being written by checking if its size is stable.
        
        Args:
            file_path: Path to the file to check
            stability_time: Time in seconds to wait for file size stability
            
        Returns:
            True if file appears complete, False otherwise
        """
        try:
            initial_size = file_path.stat().st_size
            time.sleep(stability_time)
            final_size = file_path.stat().st_size
            return initial_size == final_size and final_size > 0
        except Exception as e:
            logger.warning(f"Error checking file completion: {e}")
            return False
    
    def wait_for_output(self) -> Optional[Dict[str, Any]]:
        """
        Wait for kube-bench output files and return the latest results.
        Waits for the file to be completely written before parsing.
        
        Returns:
            Parsed kube-bench data or None if timeout
        """
        logger.info(f"Monitoring kube-bench output directory: {self.output_dir}")
        
        start_time = time.time()
        last_file_found = None
        
        while time.time() - start_time < self.max_wait_time:
            # Look for JSON output files
            json_files = list(self.output_dir.glob("*.json"))
            
            if json_files:
                # Process the most recent JSON file
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                
                # Only log once when we first find the file
                if latest_file != last_file_found:
                    logger.info(f"Found kube-bench output file: {latest_file}")
                    last_file_found = latest_file
                
                # Check if file is complete (size stable for 3 seconds)
                if self._is_file_complete(latest_file):
                    logger.info("File appears complete, attempting to parse...")
                    
                    try:
                        data = self.parser.parse_json_file(str(latest_file))
                        logger.info("✅ Kube-bench output processed successfully!")
                        return data
                        
                    except Exception as e:
                        logger.error(f"Error processing kube-bench output: {e}")
                        # Continue waiting in case the file is still being written
                        logger.info("Waiting for file to complete...")
                else:
                    logger.debug("File still being written, waiting...")
            
            time.sleep(2)  # Check every 2 seconds
        
        logger.warning(f"No complete kube-bench output found after {self.max_wait_time} seconds")
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
