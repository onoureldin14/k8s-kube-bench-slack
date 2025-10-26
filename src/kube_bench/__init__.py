"""
Kube-bench Package

This package contains components for handling kube-bench security scan results.
"""

from .parser import KubeBenchParser
from .monitor import KubeBenchMonitor

__all__ = ['KubeBenchParser', 'KubeBenchMonitor']
