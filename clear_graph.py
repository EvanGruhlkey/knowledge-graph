"""
Clear all data from the knowledge graph
"""

import requests

API_BASE = "http://localhost:8000"

def clear_graph():
    """Clear the entire knowledge graph"""
    print("Clearing knowledge graph...")
    
    try:
        # Check if server is running
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            print("ERROR: Server not running. Please start with: py start_server.py")
            return False
        
        # Clear the graph using the API endpoint
        response = requests.delete(f"{API_BASE}/clear")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Knowledge graph cleared successfully!")
            print(f"   {result['message']}")
            print("\nReady for new documents!")
            print("   Use: py add_documents.py")
            print("   Or visit: http://localhost:8000/docs")
            return True
        else:
            print(f"ERROR: Error clearing graph: {response.text}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure it's running.")
        return False

if __name__ == "__main__":
    clear_graph()
