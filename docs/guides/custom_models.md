# Using Custom Models with the AI Automation Platform

This guide explains how to use custom models with the AI Automation Platform.

## Supported Model Types

The platform supports two main types of models:

1. **LLM Models**: For text generation, reasoning, and conversation
2. **Embedding Models**: For converting text to vector representations

## Using Custom Models with Ollama

Ollama supports a variety of open-source models that you can easily download and use.

### Available Models

Some popular models you can use with Ollama include:

- llama3 (default)
- mistral
- mixtral
- phi
- gemma
- vicuna
- codellama
- And many more

### Downloading a Model

To download a model with Ollama:

1. Access the helper container:
   ```bash
   docker exec -it ai-automation_helper_1 bash
   ```

2. Use the Ollama API to pull a model:
   ```bash
   curl -X POST http://ollama:11434/api/pull -d '{"name": "mistral"}'
   ```

   Or from your host machine:
   ```bash
   curl -X POST http://localhost:11434/api/pull -d '{"name": "mistral"}'
   ```

3. Wait for the download to complete (this may take some time depending on the model size)

### Configuring the Platform to Use a Different Model

To change the default model:

1. Edit the `config.json` file:
   ```json
   "llm": {
     "provider": "ollama",
     "host": "http://ollama:11434",
     "model": "mistral",  // Change this to your preferred model
     "parameters": {
       "temperature": 0.7,
       "max_tokens": 2048
     }
   }
   ```

2. Restart the platform or the helper container

### Using Multiple Models

You can use different models for different workflows:

1. In n8n, modify the HTTP Request node that calls Ollama:
   - Change the `model` parameter in the request body to your desired model

2. For programmatic access, specify the model in your API calls:
   ```python
   payload = {
       "model": "codellama",  # Specialized model for code
       "prompt": "Write a Python function to sort a list",
       "stream": False
   }
   ```

## Custom Embedding Models

The platform uses sentence-transformers for embeddings by default, but you can change this:

1. Edit the `config.json` file:
   ```json
   "vectordb": {
     "provider": "qdrant",
     "host": "http://qdrant:6333",
     "collection_name": "documents",
     "embedding_model": "sentence-transformers/all-mpnet-base-v2",  // Change this
     "dimension": 768  // Make sure to update the dimension to match the model
   }
   ```

2. Common embedding models and their dimensions:
   - `sentence-transformers/all-MiniLM-L6-v2`: 384 dimensions
   - `sentence-transformers/all-mpnet-base-v2`: 768 dimensions
   - `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`: 384 dimensions

3. After changing the embedding model, you'll need to:
   - Create a new collection in Qdrant with the correct dimension
   - Re-ingest your documents

## Using Quantized Models

For better performance on limited hardware, you can use quantized versions of models:

1. With Ollama, append a quantization suffix:
   ```
   llama3:8b-q4_0
   ```

2. Update your config or API calls to use the quantized model name

## Creating Model Modelfiles for Ollama

You can create custom Modelfiles to configure model behavior:

1. Create a Modelfile:
   ```
   FROM llama3
   
   # Set a system message
   SYSTEM """
   You are a helpful AI assistant specialized in technical support.
   Always provide clear, concise answers with examples when possible.
   """
   
   # Set default parameters
   PARAMETER temperature 0.7
   PARAMETER top_p 0.9
   ```

2. Build the model:
   ```bash
   curl -X POST http://ollama:11434/api/create -d '{
     "name": "tech-support",
     "modelfile": "FROM llama3\n\nSYSTEM \"\"\"You are a helpful AI assistant specialized in technical support.\nAlways provide clear, concise answers with examples when possible.\"\"\"\n\nPARAMETER temperature 0.7\nPARAMETER top_p 0.9"
   }'
   ```

3. Use your custom model in workflows by specifying `tech-support` as the model name

## Performance Considerations

- Larger models provide better quality but require more resources
- Consider these trade-offs when selecting models:
  - Model size vs. quality
  - Inference speed vs. accuracy
  - Memory usage vs. capabilities

- For production use, consider:
  - Using GPU acceleration if available
  - Implementing request queuing for high-traffic scenarios
  - Monitoring resource usage and scaling as needed

## Troubleshooting

If you encounter issues with custom models:

1. Check Ollama logs:
   ```bash
   docker logs ai-automation_ollama_1
   ```

2. Verify model download status:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Test the model directly:
   ```bash
   curl -X POST http://localhost:11434/api/generate -d '{
     "model": "your-model-name",
     "prompt": "Hello, world!",
     "stream": false
   }'
   ```

4. For embedding model issues, check the helper container logs and verify the model dimensions match your Qdrant collection configuration
