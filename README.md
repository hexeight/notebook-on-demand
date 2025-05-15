# Notebook on Demand

A Docker container for running Jupyter notebooks with parameter support and webhook notifications.

## Features

- Runs Jupyter notebooks from a provided URL
- Supports parameter injection via JSON
- Sends execution status to a webhook URL
- Automatically shuts down after execution
- Extensible with custom Python dependencies
- Configurable Python version (3.8, 3.9, 3.10, 3.11, 3.12)

## Usage

Build the Docker image:

```bash
# Build with default Python 3.11
docker build -t notebook-on-demand .

# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.12 -t notebook-on-demand .
```

Run the container:

```bash
# Run with default Python 3.11
docker run -e NOTEBOOK="https://example.com/notebook.ipynb" \
           -e PARAMETERS='{"param1": "value1", "param2": "value2"}' \
           -e WEBHOOK="https://example.com/webhook" \
           notebook-on-demand

# Run with specific Python version
docker run -e NOTEBOOK="https://example.com/notebook.ipynb" \
           -e PYTHON_VERSION="3.12" \
           -e PARAMETERS='{"param1": "value1", "param2": "value2"}' \
           -e WEBHOOK="https://example.com/webhook" \
           notebook-on-demand
```

### Environment Variables

- `NOTEBOOK`: URL of the Jupyter notebook to execute (required)
- `PARAMETERS`: JSON-encoded parameters to pass to the notebook (optional)
- `WEBHOOK`: URL to send execution status notifications (optional)
- `WEBHOOK_SECRET`: Secret token for webhook authentication (optional, but recommended for security)
- `PYTHON_VERSION`: Python version to use (optional, defaults to 3.11, supported versions: 3.8, 3.9, 3.10, 3.11, 3.12)

> **Note on Python 3.12**: While Python 3.12 is supported, some scientific and data science packages might not be fully compatible yet. If you encounter package compatibility issues, consider using Python 3.11 or earlier versions.

### Webhook Payload

The webhook will receive a POST request with the following JSON payload:

```json
{
    "status": "success|failed",
    "message": "Execution status message"
}
```

If `WEBHOOK_SECRET` is provided, the request will include an `Authorization: Bearer <secret>` header for authentication.

### Adding Custom Dependencies

There are two ways to add your own Python dependencies to the container:

1. **Using a requirements.txt file (Recommended)**:
   Create a `requirements.txt` file in your project directory and build a custom image:

   ```dockerfile
   # Dockerfile
   FROM notebook-on-demand
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   ```

   Build and run:
   ```bash
   # Build with specific Python version
   docker build --build-arg PYTHON_VERSION=3.12 -t my-notebook-runner .
   docker run -e NOTEBOOK="..." -e PYTHON_VERSION="3.12" my-notebook-runner
   ```

2. **Using a setup script**:
   Create a setup script to install dependencies:

   ```dockerfile
   # Dockerfile
   FROM notebook-on-demand
   
   COPY setup.sh .
   RUN chmod +x setup.sh && ./setup.sh
   ```

   ```bash
   # setup.sh
   #!/bin/bash
   pip install pandas numpy scikit-learn
   ```

   Build and run:
   ```bash
   # Build with specific Python version
   docker build --build-arg PYTHON_VERSION=3.12 -t my-notebook-runner .
   docker run -e NOTEBOOK="..." -e PYTHON_VERSION="3.12" my-notebook-runner
   ```

## Example

```bash
# Run a notebook with parameters, webhook authentication, and specific Python version
docker run -e NOTEBOOK="https://raw.githubusercontent.com/user/repo/main/analysis.ipynb" \
           -e PYTHON_VERSION="3.12" \
           -e PARAMETERS='{"input_file": "https://raw.githubusercontent.com/user/repo/main/data.csv", "threshold": 0.5}' \
           -e WEBHOOK="https://api.example.com/notifications" \
           -e WEBHOOK_SECRET="your-secret-token" \
           notebook-on-demand
```
