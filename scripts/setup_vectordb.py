#!/usr/bin/env python3
"""
Setup script for initializing the Qdrant vector database.
"""

import json
import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models

def load_config():
    """Load configuration from config.json"""
    try:
        with open('/app/config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def setup_vectordb():
    """Initialize the Qdrant vector database"""
    config = load_config()
    vectordb_config = config['vectordb']
    
    # Connect to Qdrant
    client = QdrantClient(url=vectordb_config['host'])
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if vectordb_config['collection_name'] in collection_names:
        print(f"Collection {vectordb_config['collection_name']} already exists.")
        return
    
    # Create collection
    client.create_collection(
        collection_name=vectordb_config['collection_name'],
        vectors_config=models.VectorParams(
            size=vectordb_config['dimension'],
            distance=models.Distance.COSINE
        )
    )
    
    print(f"Created collection {vectordb_config['collection_name']} successfully.")

if __name__ == "__main__":
    setup_vectordb()
