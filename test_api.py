"""
Simple test script to demonstrate the Knowledge Graph API
"""

import requests
import json
import os
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health_check():
    """Test the root endpoint"""
    print(" Testing health check...")
    response = requests.get(f"{API_BASE}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_ingest_data():
    """Test data ingestion with sample files"""
    print(" Testing data ingestion...")
    
    # Prepare files for upload
    files = []
    file_handles = []
    
    # Add markdown files
    test_data_dir = Path("test_data")
    for md_file in test_data_dir.glob("*.md"):
        fh = open(md_file, 'rb')
        file_handles.append(fh)
        files.append(('markdown_files', (md_file.name, fh, 'text/markdown')))
    
    # Add links JSON
    links_file = test_data_dir / "saved_links.json"
    if links_file.exists():
        fh = open(links_file, 'rb')
        file_handles.append(fh)
        files.append(('links_file', (links_file.name, fh, 'application/json')))
    
    try:
        # Make the request
        response = requests.post(f"{API_BASE}/ingest", files=files)
    finally:
        # Close all opened files
        for fh in file_handles:
            fh.close()
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: Success! Processed {result['items_processed']} items")
        print(f"   Created {result['nodes_created']} nodes and {result['edges_created']} edges")
    else:
        print(f"ERROR: Error: {response.text}")
    print()

def test_get_graph():
    """Test retrieving the graph data"""
    print("🕸️ Testing graph retrieval...")
    
    response = requests.get(f"{API_BASE}/graph")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        graph_data = response.json()
        print(f"SUCCESS: Graph retrieved successfully!")
        print(f"   Nodes: {graph_data['total_nodes']}")
        print(f"   Edges: {graph_data['total_edges']}")
        
        # Show some sample nodes
        print("\n📝 Sample nodes:")
        for i, node in enumerate(graph_data['nodes'][:3]):
            print(f"   {i+1}. {node['title']} ({node['node_type']})")
            print(f"      Keywords: {', '.join(node['keywords'][:5])}")
        
        # Show some sample edges
        print("\n🔗 Sample edges:")
        for i, edge in enumerate(graph_data['edges'][:3]):
            source_title = next(n['title'] for n in graph_data['nodes'] if n['id'] == edge['source'])
            target_title = next(n['title'] for n in graph_data['nodes'] if n['id'] == edge['target'])
            print(f"   {i+1}. {source_title} ↔ {target_title} (weight: {edge['weight']:.3f})")
        
        return graph_data
    else:
        print(f"ERROR: Error: {response.text}")
        return None
    print()

def test_feedback(graph_data):
    """Test feedback recording"""
    if not graph_data or not graph_data['nodes']:
        print("⚠️ No graph data available for feedback test")
        return
    
    print("💡 Testing feedback recording...")
    
    # Get the first node for testing
    test_node = graph_data['nodes'][0]
    
    feedback_data = {
        "node_id": test_node['id'],
        "interaction_type": "click",
        "duration": 15.5
    }
    
    response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: Feedback recorded for: {test_node['title']}")
        print(f"   Updated {len(result['updated_connections'])} connections")
    else:
        print(f"ERROR: Error: {response.text}")
    print()

def test_stats():
    """Test graph statistics"""
    print(" Testing graph statistics...")
    
    response = requests.get(f"{API_BASE}/stats")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print("SUCCESS: Statistics retrieved:")
        print(f"   Total nodes: {stats['total_nodes']}")
        print(f"   Total edges: {stats['total_edges']}")
        print(f"   Graph density: {stats['density']:.3f}")
        print(f"   Is connected: {stats['is_connected']}")
        
        if 'most_connected_nodes' in stats:
            print("\n🌟 Most connected nodes:")
            for node in stats['most_connected_nodes'][:3]:
                print(f"   • {node['title']} ({node['connections']} connections)")
    else:
        print(f"ERROR: Error: {response.text}")
    print()

def main():
    """Run all API tests"""
    print("🚀 Starting Knowledge Graph API Tests\n")
    print("Make sure the API server is running: uvicorn main:app --reload\n")
    
    try:
        # Test basic functionality
        test_health_check()
        test_ingest_data()
        graph_data = test_get_graph()
        test_feedback(graph_data)
        test_stats()
        
        print("🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server with: uvicorn main:app --reload")
    except Exception as e:
        print(f"ERROR: Test failed with error: {e}")

if __name__ == "__main__":
    main()
