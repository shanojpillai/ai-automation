# Getting Started with AI Automation Platform

This guide will help you set up and start using the AI Automation Platform.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- Basic knowledge of AI concepts and workflows

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-automation.git
   cd ai-automation
   ```

2. Make the startup script executable:
   ```bash
   chmod +x startup.sh
   chmod +x ingest_documents.sh
   ```

3. Start the platform:
   ```bash
   ./startup.sh
   ```

   This will:
   - Start all Docker containers (n8n, Ollama, Qdrant)
   - Initialize the vector database
   - Test the Ollama LLM connection
   - Set up initial n8n workflows

4. Access the services:
   - n8n: http://localhost:5678
   - Qdrant: http://localhost:6333
   - Ollama: http://localhost:11434

## Basic Usage

### Using n8n Workflows

1. Open n8n in your browser: http://localhost:5678
2. You'll find two pre-configured workflows:
   - Basic LLM Query: Simple workflow to query the LLM
   - RAG AI Agent: Workflow that uses RAG (Retrieval Augmented Generation)

3. To test the Basic LLM Query workflow:
   - Activate the workflow if it's not already active
   - Send a POST request to `http://localhost:5678/webhook/query` with a JSON body:
     ```json
     {
       "query": "What is artificial intelligence?"
     }
     ```

### Ingesting Documents

1. Place your text documents in the `data/documents` directory
2. Run the ingestion script:
   ```bash
   ./ingest_documents.sh
   ```
3. The documents will be processed, embedded, and stored in the Qdrant vector database

### Using the RAG AI Agent

After ingesting documents, you can use the RAG AI Agent to query information from your documents:

1. Send a POST request to `http://localhost:5678/webhook/rag-query` with a JSON body:
   ```json
   {
     "query": "What does the document say about machine learning?"
   }
   ```
2. The agent will:
   - Convert your query to an embedding
   - Search for relevant document chunks in Qdrant
   - Provide the relevant context to the LLM
   - Return an answer based on your documents

## Next Steps

- Check out the [Building Agents](building_agents.md) guide to create custom AI agents
- Learn about using [Custom Models](custom_models.md) with the platform
- Explore the n8n interface to customize and create new workflows
