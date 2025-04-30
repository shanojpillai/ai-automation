#!/usr/bin/env python3
"""
Test script for verifying the Ollama LLM connection.
"""

import json
import sys
import requests

def load_config():
    """Load configuration from config.json"""
    # Try multiple possible locations for the config file
    config_paths = [
        '/app/config.json',  # Docker container path
        './config.json',     # Repository root path
        '../config.json'     # One level up (if running from scripts directory)
    ]

    for path in config_paths:
        try:
            with open(path, 'r') as f:
                print(f"Loaded config from {path}")
                return json.load(f)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error reading config from {path}: {e}")
            continue

    # If we get here, we couldn't find the config file
    print("Error: Could not find config.json in any of the expected locations")
    sys.exit(1)

def test_ollama():
    """Test the connection to Ollama LLM"""
    config = load_config()
    llm_config = config['llm']

    # Construct the API URL
    base_url = llm_config.get('base_url', llm_config.get('host', 'http://localhost:11434'))
    api_url = f"{base_url}/api/generate"

    # Test prompt
    prompt = "Hello, can you tell me what you are?"

    # Prepare the request payload
    payload = {
        "model": llm_config['model'],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": llm_config['parameters']['temperature'],
            "num_predict": llm_config['parameters']['max_tokens']
        }
    }

    try:
        # Make the request to Ollama
        response = requests.post(api_url, json=payload)
        response.raise_for_status()

        # Parse the response
        result = response.json()

        print("Ollama LLM connection successful!")
        print(f"Model: {llm_config['model']}")
        print(f"Response: {result['response'][:100]}...")

        return True
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)
