#!/bin/bash
# Script for ingesting documents into the vector database

# Set script to exit on error
set -e

echo "Starting document ingestion process..."

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "Error: Docker is not running or you don't have permission to access it."
    exit 1
fi

# Check if the helper container is running
if ! docker ps | grep -q "ai-automation_helper"; then
    echo "Error: Helper container is not running. Please start the platform first with ./startup.sh"
    exit 1
fi

# Navigate to the docker directory
cd "$(dirname "$0")/docker"

# Run the ingest_documents.py script in the helper container
echo "Running document ingestion script..."
docker-compose exec helper python /app/scripts/ingest_documents.py

echo "Document ingestion complete!"
exit 0
