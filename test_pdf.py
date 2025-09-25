"""
Test script for PDF ingestion into the Knowledge Graph
"""

import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_pdf_ingestion(pdf_path: str):
    """
    Test PDF file ingestion
    
    Args:
        pdf_path: Path to the PDF file to upload
    """
    print(f" Testing PDF ingestion with: {pdf_path}")
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"ERROR: PDF file not found: {pdf_path}")
        return False
    
    try:
        # Prepare the PDF file for upload
        with open(pdf_file, 'rb') as f:
            files = [('pdf_files', (pdf_file.name, f, 'application/pdf'))]
            
            # Make the request
            response = requests.post(f"{API_BASE}/ingest", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Success! Processed {result['items_processed']} items")
            print(f"   📝 Created {result['nodes_created']} nodes")
            print(f"   🔗 Generated {result['edges_created']} connections")
            return True
        else:
            print(f"ERROR: Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error during PDF upload: {e}")
        return False

def get_graph_info():
    """Get current graph information"""
    try:
        response = requests.get(f"{API_BASE}/graph")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"\n Current Graph Status:")
            print(f"   Total nodes: {graph_data['total_nodes']}")
            print(f"   Total edges: {graph_data['total_edges']}")
            
            # Count node types
            node_types = {}
            for node in graph_data['nodes']:
                node_type = node['node_type']
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            print(f"   Node types: {dict(node_types)}")
            
            # Show PDF nodes specifically
            pdf_nodes = [n for n in graph_data['nodes'] if n['node_type'] == 'pdf']
            if pdf_nodes:
                print(f"\n📄 PDF Documents in Graph:")
                for node in pdf_nodes:
                    print(f"   • {node['title']}")
                    print(f"     Keywords: {', '.join(node['keywords'][:5])}")
            
        else:
            print(f"ERROR: Error getting graph info: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Error: {e}")

def main():
    """Main test function"""
    print("🚀 PDF Ingestion Test")
    print("Make sure the API server is running: py start_server.py\n")
    
    # Test server connection
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            raise requests.exceptions.ConnectionError()
        print("SUCCESS: Server is running\n")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server with: py start_server.py")
        return
    
    # Get current graph info
    get_graph_info()
    
    print("\n" + "="*50)
    print("To test PDF ingestion:")
    print("1. Place a PDF file in this directory")
    print("2. Run: test_pdf_ingestion('your_file.pdf')")
    print("3. Or modify this script to point to your PDF file")
    print("="*50)
    
    # Example usage (uncomment and modify path as needed):
    test_pdf_ingestion("test_data/Resume_Fall25.pdf")

if __name__ == "__main__":
    main()
