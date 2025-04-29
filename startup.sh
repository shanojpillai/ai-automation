#!/bin/bash
# Main script to start the AI Automation environment

# Set script to exit on error
set -e

echo "Starting AI Automation Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker and Docker Compose."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

# Navigate to the docker directory
cd "$(dirname "$0")/docker"

# Start the services
echo "Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run setup scripts in the helper container
echo "Running setup scripts..."
docker-compose exec helper python /app/scripts/setup_vectordb.py
docker-compose exec helper python /app/scripts/test_ollama.py
docker-compose exec helper python /app/scripts/setup_n8n_workflow.py

echo "AI Automation Platform is now running!"
echo "n8n: http://localhost:5678"
echo "Qdrant: http://localhost:6333"
echo "Ollama: http://localhost:11434"
echo ""
echo "To ingest documents, place them in the data/documents directory and run:"
echo "./ingest_documents.sh"

exit 0
