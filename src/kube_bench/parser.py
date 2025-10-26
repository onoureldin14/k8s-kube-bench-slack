"""
Kube-bench Parser Module

Handles parsing and processing of kube-bench security scan results.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class KubeBenchParser:
    """Parses and processes kube-bench security scan results."""
    
    def __init__(self):
        """Initialize the kube-bench parser."""
        pass
    
    def parse_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a kube-bench JSON output file.
        
        Args:
            file_path: Path to the JSON file
        
        Returns:
            Parsed kube-bench data
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Successfully parsed kube-bench JSON file: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error parsing kube-bench JSON file {file_path}: {e}")
            raise
    
    def extract_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract summary information from kube-bench data.
        
        Args:
            data: Parsed kube-bench data
        
        Returns:
            Summary statistics
        """
        summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warned': 0,
            'info': 0,
            'controls': []
        }
        
        if 'Controls' in data:
            for control in data['Controls']:
                control_name = control.get('id', 'Unknown')
                control_results = control.get('results', [])
                
                control_summary = {
                    'name': control_name,
                    'total': len(control_results),
                    'passed': 0,
                    'failed': 0,
                    'warned': 0,
                    'info': 0
                }
                
                for result in control_results:
                    status = result.get('status', '').lower()
                    if status == 'pass':
                        control_summary['passed'] += 1
                        summary['passed'] += 1
                    elif status == 'fail':
                        control_summary['failed'] += 1
                        summary['failed'] += 1
                    elif status == 'warn':
                        control_summary['warned'] += 1
                        summary['warned'] += 1
                    elif status == 'info':
                        control_summary['info'] += 1
                        summary['info'] += 1
                    
                    summary['total_tests'] += 1
                
                summary['controls'].append(control_summary)
        
        return summary
    
    def get_failed_tests(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all failed tests from kube-bench data.
        
        Args:
            data: Parsed kube-bench data
        
        Returns:
            List of failed test results
        """
        failed_tests = []
        
        if 'Controls' in data:
            for control in data['Controls']:
                control_id = control.get('id', 'Unknown')
                for result in control.get('results', []):
                    if result.get('status', '').lower() == 'fail':
                        failed_tests.append({
                            'control_id': control_id,
                            'test_desc': result.get('test_desc', ''),
                            'status': result.get('status', ''),
                            'remediation': result.get('remediation', '')
                        })
        
        return failed_tests
    
    def get_warning_tests(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all warning tests from kube-bench data.
        
        Args:
            data: Parsed kube-bench data
        
        Returns:
            List of warning test results
        """
        warning_tests = []
        
        if 'Controls' in data:
            for control in data['Controls']:
                control_id = control.get('id', 'Unknown')
                for result in control.get('results', []):
                    if result.get('status', '').lower() == 'warn':
                        warning_tests.append({
                            'control_id': control_id,
                            'test_desc': result.get('test_desc', ''),
                            'status': result.get('status', ''),
                            'remediation': result.get('remediation', '')
                        })
        
        return warning_tests
    
    def create_dummy_data(self) -> Dict[str, Any]:
        """
        Create realistic dummy kube-bench data for testing based on actual scan output.
        
        Returns:
            Dummy kube-bench data matching real kube-bench structure
        """
        return {
            "version": "cis-1.11",
            "Controls": [
                {
                    "id": "1",
                    "version": "cis-1.11",
                    "text": "Control Plane Security Configuration",
                    "node_type": "master",
                    "total_pass": 12,
                    "total_fail": 3,
                    "total_warn": 8,
                    "total_info": 0,
                    "tests": [
                        {
                            "section": "1.2",
                            "type": "",
                            "pass": 1,
                            "fail": 2,
                            "warn": 0,
                            "info": 0,
                            "desc": "API Server",
                            "results": [
                                {
                                    "test_number": "1.2.1",
                                    "test_desc": "Ensure that the --anonymous-auth argument is set to false",
                                    "status": "FAIL",
                                    "remediation": "Edit the API server pod specification file /etc/kubernetes/manifests/kube-apiserver.yaml on the control plane node and set the below parameter: --anonymous-auth=false"
                                },
                                {
                                    "test_number": "1.2.2",
                                    "test_desc": "Ensure that the --basic-auth-file argument is not set",
                                    "status": "PASS",
                                    "remediation": ""
                                },
                                {
                                    "test_number": "1.2.5",
                                    "test_desc": "Ensure that the --kubelet-certificate-authority argument is set as appropriate",
                                    "status": "FAIL",
                                    "remediation": "Follow the Kubernetes documentation and setup the TLS connection between the apiserver and kubelets. Then, edit the API server pod specification file /etc/kubernetes/manifests/kube-apiserver.yaml and set the --kubelet-certificate-authority parameter."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "2",
                    "version": "cis-1.11",
                    "text": "Etcd Node Configuration",
                    "node_type": "etcd",
                    "total_pass": 5,
                    "total_fail": 2,
                    "total_warn": 1,
                    "total_info": 0,
                    "tests": [
                        {
                            "section": "2",
                            "type": "",
                            "pass": 5,
                            "fail": 2,
                            "warn": 1,
                            "info": 0,
                            "desc": "Etcd Node Configuration",
                            "results": [
                                {
                                    "test_number": "2.1",
                                    "test_desc": "Ensure that the --cert-file and --key-file arguments are set as appropriate",
                                    "status": "FAIL",
                                    "remediation": "Follow the etcd service documentation and configure TLS encryption. Then edit the etcd pod specification file and set the below parameters: --cert-file=</path/to/ca-file> --key-file=</path/to/key-file>"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "3",
                    "version": "cis-1.11",
                    "text": "Control Plane Configuration",
                    "node_type": "controlplane",
                    "total_pass": 8,
                    "total_fail": 6,
                    "total_warn": 1,
                    "total_info": 0,
                    "tests": [
                        {
                            "section": "3",
                            "type": "",
                            "pass": 8,
                            "fail": 6,
                            "warn": 1,
                            "info": 0,
                            "desc": "Control Plane Configuration",
                            "results": [
                                {
                                    "test_number": "3.2.1",
                                    "test_desc": "Ensure that a minimal audit policy is created",
                                    "status": "FAIL",
                                    "remediation": "Create an audit policy file and pass it to the API server using the --audit-policy-file parameter."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "4",
                    "version": "cis-1.11",
                    "text": "Worker Node Security Configuration",
                    "node_type": "node",
                    "total_pass": 1,
                    "total_fail": 5,
                    "total_warn": 10,
                    "total_info": 0,
                    "tests": [
                        {
                            "section": "4",
                            "type": "",
                            "pass": 1,
                            "fail": 5,
                            "warn": 10,
                            "info": 0,
                            "desc": "Worker Node Security Configuration",
                            "results": [
                                {
                                    "test_number": "4.2.1",
                                    "test_desc": "Ensure that the --anonymous-auth argument is set to false",
                                    "status": "FAIL",
                                    "remediation": "Edit the kubelet service file on each worker node and set the parameter: --anonymous-auth=false"
                                },
                                {
                                    "test_number": "4.2.2",
                                    "test_desc": "Ensure that the --authorization-mode argument is not set to AlwaysAllow",
                                    "status": "FAIL",
                                    "remediation": "Edit the kubelet service file and set: --authorization-mode=Webhook"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "5",
                    "version": "cis-1.11",
                    "text": "Kubernetes Policies",
                    "node_type": "policies",
                    "total_pass": 3,
                    "total_fail": 0,
                    "total_warn": 32,
                    "total_info": 0,
                    "tests": []
                }
            ],
            "Totals": {
                "total_pass": 29,
                "total_fail": 16,
                "total_warn": 52,
                "total_info": 0
            }
        }
