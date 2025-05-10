#!/bin/bash

# Make the Python script executable
chmod +x /app/entrypoint.py

# Execute the Python script
exec /app/entrypoint.py 