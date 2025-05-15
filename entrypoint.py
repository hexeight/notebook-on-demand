#!/usr/bin/env python3

import os
import sys
import json
import tempfile
import subprocess
import requests
from pathlib import Path
from jupyter_client.kernelspec import KernelSpecManager

def send_webhook(webhook_url, status, message):
    """Send webhook notification with execution status."""
    if not webhook_url:
        return
    
    try:
        # Get webhook secret from environment variable
        webhook_secret = os.environ.get('WEBHOOK_SECRET')
        headers = {}
        
        # Add Authorization header if secret is provided
        if webhook_secret:
            headers['Authorization'] = f'Bearer {webhook_secret}'
        
        response = requests.post(
            webhook_url,
            json={"status": status, "message": message},
            headers=headers
        )
        response.raise_for_status()
        print(f"Webhook sent successfully: {response.json()}")
    except Exception as e:
        print(f"Warning: Failed to send webhook: {str(e)}", file=sys.stderr)

def format_parameters(parameters_str):
    """Format and validate JSON parameters."""
    try:
        data = json.loads(parameters_str)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON parameters: {str(e)}")

def get_python_version():
    """Get the Python version from environment variable or use default."""
    return os.environ.get('PYTHON_VERSION', '3.11')

def get_python_kernel():
    """Get the Python kernel matching the specified version."""
    try:
        ksm = KernelSpecManager()
        kernels = ksm.get_all_specs()
        python_version = get_python_version()
        
        # Look for exact version match first
        version_kernels = [k for k, v in kernels.items() if f'python{python_version}' in k.lower()]
        if version_kernels:
            return version_kernels[0]
            
        # Fallback to any Python kernel if exact match not found
        python_kernels = [k for k, v in kernels.items() if 'python' in k.lower()]
        if not python_kernels:
            raise ValueError(f"No Python kernel found for version {python_version}")
        return python_kernels[0]
    except Exception as e:
        raise ValueError(f"Error getting kernel: {str(e)}")

def download_notebook(url, output_path):
    """Download notebook from URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        raise ValueError(f"Failed to download notebook: {str(e)}")

def execute_notebook(notebook_path, output_path, parameters=None, kernel_name=None):
    """Execute notebook using papermill."""
    cmd = ["papermill", notebook_path, output_path]
    
    if kernel_name:
        cmd.extend(["--kernel", kernel_name])
    
    if parameters:
        # Create a temporary file for parameters
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(parameters)
            param_file = f.name
        
        try:
            cmd.extend(["-f", param_file])
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Notebook execution failed: {result.stderr}")
        finally:
            # Clean up the temporary file
            os.unlink(param_file)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Notebook execution failed: {result.stderr}")

def main():
    # Get environment variables
    notebook_url = os.environ.get('NOTEBOOK')
    parameters_str = os.environ.get('PARAMETERS')
    webhook_url = os.environ.get('WEBHOOK')
    python_version = get_python_version()

    if not notebook_url:
        print("Error: NOTEBOOK environment variable is not set", file=sys.stderr)
        send_webhook(webhook_url, "failed", "NOTEBOOK environment variable is not set")
        sys.exit(1)

    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            notebook_path = temp_dir / "notebook.ipynb"
            output_path = temp_dir / "output.ipynb"

            # Download notebook
            print(f"Downloading notebook from {notebook_url}")
            download_notebook(notebook_url, notebook_path)

            # Get Python kernel
            print(f"Checking available kernels for Python {python_version}...")
            kernel_name = get_python_kernel()
            print(f"Using kernel: {kernel_name}")

            # Format parameters if provided
            formatted_params = None
            if parameters_str:
                print("Executing notebook with parameters")
                formatted_params = format_parameters(parameters_str)
                print("Formatted parameters:")
                print(formatted_params)
            else:
                print("Executing notebook without parameters")

            # Execute notebook
            execute_notebook(notebook_path, output_path, formatted_params, kernel_name)
            
            print("Notebook execution completed successfully")
            send_webhook(webhook_url, "success", "Notebook execution completed successfully")

    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}", file=sys.stderr)
        send_webhook(webhook_url, "failed", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main() 