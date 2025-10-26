"""
Main Entry Point

This is the main entry point for the kube-bench Slack integration application.
"""

import sys
import os
from app import KubeBenchSlackApp
from utils import Config

def main():
    """Main entry point."""
    try:
        # Create configuration
        config = Config()
        
        # Create and run application
        app = KubeBenchSlackApp(config)
        exit_code = app.run()
        sys.exit(exit_code)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
