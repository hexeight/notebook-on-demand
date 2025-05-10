#!/bin/bash

# Function to send webhook notification
send_webhook() {
    local status=$1
    local message=$2
    
    if [ -n "$WEBHOOK" ]; then
        curl -X POST "$WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"status\": \"$status\", \"message\": \"$message\"}"
    fi
}

# Check if required environment variables are set
if [ -z "$NOTEBOOK" ]; then
    echo "Error: NOTEBOOK environment variable is not set"
    send_webhook "failed" "NOTEBOOK environment variable is not set"
    exit 1
fi

# Create a temporary directory for the notebook
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download the notebook
echo "Downloading notebook from $NOTEBOOK"
if ! curl -L "$NOTEBOOK" -o notebook.ipynb; then
    echo "Error: Failed to download notebook"
    send_webhook "failed" "Failed to download notebook"
    exit 1
fi

# Execute the notebook with parameters if provided
if [ -n "$PARAMETERS" ]; then
    echo "Executing notebook with parameters"
    papermill notebook.ipynb output.ipynb -f <(echo "$PARAMETERS")
else
    echo "Executing notebook without parameters"
    papermill notebook.ipynb output.ipynb
fi

# Check if notebook execution was successful
if [ $? -eq 0 ]; then
    echo "Notebook execution completed successfully"
    send_webhook "success" "Notebook execution completed successfully"
else
    echo "Notebook execution failed"
    send_webhook "failed" "Notebook execution failed"
    exit 1
fi

# Cleanup
rm -rf "$TEMP_DIR" 