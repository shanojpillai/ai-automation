#!/usr/bin/env python3
"""
Setup script for creating initial n8n workflows via API.
"""

import json
import sys
import time
import requests

def load_config():
    """Load configuration from config.json"""
    try:
        with open('/app/config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def load_workflow(workflow_path):
    """Load workflow JSON from file"""
    try:
        with open(workflow_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading workflow from {workflow_path}: {e}")
        return None

def setup_n8n_workflows():
    """Create initial n8n workflows via API"""
    config = load_config()
    n8n_config = config['n8n']
    
    # Wait for n8n to be ready
    n8n_api_url = f"{n8n_config['host']}/api/v1"
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(f"{n8n_api_url}/health")
            if response.status_code == 200:
                print("n8n is ready!")
                break
        except:
            pass
        
        print(f"Waiting for n8n to be ready... ({retry_count+1}/{max_retries})")
        time.sleep(5)
        retry_count += 1
    
    if retry_count >= max_retries:
        print("n8n is not available. Exiting.")
        return False
    
    # Setup API headers
    headers = {
        "Content-Type": "application/json"
    }
    
    if n8n_config['api_key']:
        headers["X-N8N-API-KEY"] = n8n_config['api_key']
    
    # Import workflows
    for workflow_name, workflow_path in n8n_config['workflows'].items():
        workflow_data = load_workflow(workflow_path)
        if not workflow_data:
            continue
        
        try:
            # Check if workflow already exists
            response = requests.get(
                f"{n8n_api_url}/workflows",
                headers=headers
            )
            
            if response.status_code == 200:
                existing_workflows = response.json()
                workflow_exists = any(w['name'] == workflow_data['name'] for w in existing_workflows['data'])
                
                if workflow_exists:
                    print(f"Workflow '{workflow_data['name']}' already exists. Skipping.")
                    continue
            
            # Create new workflow
            response = requests.post(
                f"{n8n_api_url}/workflows",
                headers=headers,
                json=workflow_data
            )
            
            if response.status_code in (200, 201):
                print(f"Successfully imported workflow: {workflow_name}")
            else:
                print(f"Failed to import workflow {workflow_name}: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error importing workflow {workflow_name}: {e}")
    
    return True

if __name__ == "__main__":
    success = setup_n8n_workflows()
    sys.exit(0 if success else 1)
