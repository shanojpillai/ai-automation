#!/usr/bin/env python3
"""
Advanced AI Assistant Workflow

This script implements a more complex AI workflow that combines:
1. LLM query processing
2. Vector database for semantic search
3. Multi-step processing
4. Conditional logic

It provides a REST API endpoint that accepts different types of queries
and processes them accordingly.
"""

import json
import os
import re
import requests
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional, Union

# Configuration
CONFIG = {
    "llm": {
        "base_url": "http://localhost:11434",
        "model": "mistral"
    },
    "vectordb": {
        "url": "http://localhost:6333",
        "collection_name": "documents"
    },
    "server": {
        "port": 8080
    }
}

# Sample documents for vector search (in a real scenario, these would be in the vector DB)
SAMPLE_DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves."
    },
    {
        "id": "doc2",
        "title": "Natural Language Processing",
        "content": "Natural Language Processing (NLP) is a field of artificial intelligence that gives computers the ability to understand text and spoken words in much the same way human beings can. NLP combines computational linguistics with statistical, machine learning, and deep learning models."
    },
    {
        "id": "doc3",
        "title": "Computer Vision",
        "content": "Computer vision is a field of artificial intelligence that trains computers to interpret and understand the visual world. Using digital images from cameras and videos and deep learning models, machines can accurately identify and classify objects and then react to what they 'see'."
    }
]

class QueryType:
    GENERAL = "general"
    SEARCH = "search"
    SUMMARIZE = "summarize"

def detect_query_type(query: str) -> str:
    """Detect the type of query based on its content."""
    query_lower = query.lower()
    
    # Check for search-related keywords
    if any(keyword in query_lower for keyword in ["find", "search", "look for", "documents about", "information on"]):
        return QueryType.SEARCH
    
    # Check for summarization-related keywords
    if any(keyword in query_lower for keyword in ["summarize", "summary", "summarization", "brief overview"]):
        return QueryType.SUMMARIZE
    
    # Default to general query
    return QueryType.GENERAL

def call_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Call the LLM API with the given prompt."""
    api_url = f"{CONFIG['llm']['base_url']}/api/generate"
    
    payload = {
        "model": CONFIG['llm']['model'],
        "prompt": prompt,
        "stream": False
    }
    
    if system_prompt:
        payload["system"] = system_prompt
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except Exception as e:
        print(f"Error calling LLM API: {e}")
        return f"Error: {str(e)}"

def search_documents(query: str) -> List[Dict[str, Any]]:
    """
    Search for documents related to the query.
    In a real implementation, this would use the vector database.
    Here we use a simple keyword matching for demonstration.
    """
    results = []
    query_terms = set(re.findall(r'\w+', query.lower()))
    
    for doc in SAMPLE_DOCUMENTS:
        doc_terms = set(re.findall(r'\w+', doc['content'].lower()))
        # Calculate a simple relevance score based on term overlap
        overlap = len(query_terms.intersection(doc_terms))
        if overlap > 0:
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["content"],
                "relevance": overlap / len(query_terms)
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results

def process_general_query(query: str) -> Dict[str, Any]:
    """Process a general query using the LLM."""
    system_prompt = "You are a helpful AI assistant. Provide accurate and concise information."
    response = call_llm(query, system_prompt)
    
    return {
        "type": QueryType.GENERAL,
        "query": query,
        "response": response,
        "metadata": {
            "processing_steps": ["LLM query"]
        }
    }

def process_search_query(query: str) -> Dict[str, Any]:
    """Process a search query using document search and LLM."""
    # Extract the search topic from the query
    search_topic = re.sub(r'^.*?(find|search|look for|documents about|information on)\s+', '', query, flags=re.IGNORECASE).strip()
    if search_topic.endswith('?'):
        search_topic = search_topic[:-1]
    
    # Search for relevant documents
    search_results = search_documents(search_topic)
    
    if not search_results:
        # Fall back to general query if no documents found
        result = process_general_query(query)
        result["metadata"]["processing_steps"].append("Document search (no results)")
        return result
    
    # Prepare context from search results
    context = "\n\n".join([f"Document: {doc['title']}\nContent: {doc['content']}" for doc in search_results[:2]])
    
    # Generate response with context
    system_prompt = "You are a helpful AI assistant. Use the provided document context to answer the question. If the context doesn't contain relevant information, say so and provide a general response."
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    response = call_llm(prompt, system_prompt)
    
    return {
        "type": QueryType.SEARCH,
        "query": query,
        "response": response,
        "metadata": {
            "processing_steps": ["Document search", "Context preparation", "LLM query with context"],
            "search_results": [{"id": doc["id"], "title": doc["title"], "relevance": doc["relevance"]} for doc in search_results[:2]]
        }
    }

def process_summarize_query(query: str) -> Dict[str, Any]:
    """Process a summarization query."""
    # Extract what needs to be summarized
    match = re.search(r'summarize\s+(.*)', query, re.IGNORECASE)
    if match:
        topic = match.group(1).strip()
    else:
        topic = re.sub(r'^.*?(summarize|summary|summarization|brief overview)\s+', '', query, flags=re.IGNORECASE).strip()
    
    # Search for relevant documents
    search_results = search_documents(topic)
    
    if not search_results:
        # Fall back to general query if no documents found
        result = process_general_query(query)
        result["metadata"]["processing_steps"].append("Document search (no results)")
        return result
    
    # Prepare content to summarize
    content_to_summarize = "\n\n".join([doc['content'] for doc in search_results[:2]])
    
    # Generate summary
    system_prompt = "You are a helpful AI assistant. Provide a concise summary of the given content."
    prompt = f"Please summarize the following content:\n\n{content_to_summarize}"
    summary = call_llm(prompt, system_prompt)
    
    return {
        "type": QueryType.SUMMARIZE,
        "query": query,
        "response": summary,
        "metadata": {
            "processing_steps": ["Document search", "Content preparation", "Summarization"],
            "summarized_documents": [{"id": doc["id"], "title": doc["title"]} for doc in search_results[:2]]
        }
    }

def process_query(query: str) -> Dict[str, Any]:
    """Process a query based on its detected type."""
    query_type = detect_query_type(query)
    
    if query_type == QueryType.SEARCH:
        return process_search_query(query)
    elif query_type == QueryType.SUMMARIZE:
        return process_summarize_query(query)
    else:
        return process_general_query(query)

class AdvancedAIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self._set_headers()
            response = {'status': 'healthy', 'version': '1.0.0'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_headers(404)
            response = {'error': 'Endpoint not found'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        if self.path == '/query':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                query = request_data.get('query', '')
                
                if not query:
                    self._set_headers(400)
                    response = {'error': 'Query parameter is required'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                # Process the query
                result = process_query(query)
                
                # Return the response
                self._set_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except json.JSONDecodeError:
                self._set_headers(400)
                response = {'error': 'Invalid JSON'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                response = {'error': f'Server error: {str(e)}'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_headers(404)
            response = {'error': 'Endpoint not found'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AdvancedAIHandler)
    print(f'Starting Advanced AI Workflow server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    # Start the server in a separate thread
    port = CONFIG['server']['port']
    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    print(f'Advanced AI Workflow server is running on port {port}. Press Ctrl+C to stop.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Server stopped.')
