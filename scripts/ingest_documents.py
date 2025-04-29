#!/usr/bin/env python3
"""
Script for processing and embedding documents into the vector database.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
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

def get_document_files(documents_path: str) -> List[Path]:
    """Get all document files from the specified directory"""
    documents_dir = Path(documents_path)
    if not documents_dir.exists():
        print(f"Documents directory {documents_path} does not exist.")
        return []
    
    # Get all text files
    return list(documents_dir.glob("**/*.txt"))

def chunk_document(file_path: Path, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """Split document into chunks with metadata"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Simple chunking by character count
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size]
            if len(chunk_text.strip()) > 0:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "chunk_index": len(chunks)
                    }
                })
        
        return chunks
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

def embed_chunks(chunks: List[Dict[str, Any]], model_name: str) -> List[Dict[str, Any]]:
    """Generate embeddings for document chunks"""
    try:
        model = SentenceTransformer(model_name)
        
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Add embeddings to chunks
        for i, embedding in enumerate(embeddings):
            chunks[i]["embedding"] = embedding.tolist()
        
        return chunks
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

def upload_to_qdrant(chunks: List[Dict[str, Any]], config: Dict[str, Any]):
    """Upload chunks to Qdrant vector database"""
    try:
        vectordb_config = config['vectordb']
        client = QdrantClient(url=vectordb_config['host'])
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if vectordb_config['collection_name'] not in collection_names:
            # Create collection if it doesn't exist
            client.create_collection(
                collection_name=vectordb_config['collection_name'],
                vectors_config=models.VectorParams(
                    size=vectordb_config['dimension'],
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created collection {vectordb_config['collection_name']}.")
        
        # Prepare points for upload
        points = []
        for i, chunk in enumerate(chunks):
            points.append(
                models.PointStruct(
                    id=i + 1,  # Start IDs from 1
                    vector=chunk["embedding"],
                    payload={
                        "text": chunk["text"],
                        **chunk["metadata"]
                    }
                )
            )
        
        # Upload points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(
                collection_name=vectordb_config['collection_name'],
                points=batch
            )
            print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
        print(f"Successfully uploaded {len(points)} document chunks to Qdrant.")
        return True
    except Exception as e:
        print(f"Error uploading to Qdrant: {e}")
        return False

def ingest_documents():
    """Main function to ingest documents into the vector database"""
    config = load_config()
    documents_path = config['data']['documents_path']
    
    # Get document files
    document_files = get_document_files(documents_path)
    if not document_files:
        print("No documents found to ingest.")
        return False
    
    print(f"Found {len(document_files)} documents to process.")
    
    # Process each document
    all_chunks = []
    for file_path in tqdm(document_files, desc="Processing documents"):
        chunks = chunk_document(file_path)
        all_chunks.extend(chunks)
    
    if not all_chunks:
        print("No document chunks were generated.")
        return False
    
    print(f"Generated {len(all_chunks)} chunks from {len(document_files)} documents.")
    
    # Generate embeddings
    embedded_chunks = embed_chunks(all_chunks, config['vectordb']['embedding_model'])
    if not embedded_chunks:
        print("Failed to generate embeddings.")
        return False
    
    # Upload to Qdrant
    success = upload_to_qdrant(embedded_chunks, config)
    return success

if __name__ == "__main__":
    success = ingest_documents()
    sys.exit(0 if success else 1)
