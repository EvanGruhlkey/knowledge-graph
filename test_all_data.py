"""
Test script to ingest ALL data types including PDF
"""

import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_comprehensive_ingestion():
    """
    Test ingestion of all data types together
    """
    print(" Testing comprehensive data ingestion (Markdown + PDF + Links)")
    
    try:
        # Prepare all files for upload
        files = []
        file_handles = []
        
        # Add markdown files
        test_data_dir = Path("test_data")
        md_files = list(test_data_dir.glob("*.md"))
        print(f"Found {len(md_files)} markdown files:")
        for md_file in md_files:
            print(f"  • {md_file.name}")
            fh = open(md_file, 'rb')
            file_handles.append(fh)
            files.append(('markdown_files', (md_file.name, fh, 'text/markdown')))
        
        # Add PDF files
        pdf_files = list(test_data_dir.glob("*.pdf"))
        if pdf_files:
            print(f"Found {len(pdf_files)} PDF files:")
            for pdf_file in pdf_files:
                print(f"  • {pdf_file.name}")
                fh = open(pdf_file, 'rb')
                file_handles.append(fh)
                files.append(('pdf_files', (pdf_file.name, fh, 'application/pdf')))
        else:
            print("No PDF files found in test_data/")
        
        # Add links JSON
        links_file = test_data_dir / "saved_links.json"
        if links_file.exists():
            print(f"Found links file: {links_file.name}")
            fh = open(links_file, 'rb')
            file_handles.append(fh)
            files.append(('links_file', (links_file.name, fh, 'application/json')))
        
        # Make the request
        print(f"\n🔄 Uploading {len(files)} files...")
        response = requests.post(f"{API_BASE}/ingest", files=files)
        
        # Close all files
        for fh in file_handles:
            fh.close()
        
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
        print(f"ERROR: Error during upload: {e}")
        return False

def get_detailed_graph_info():
    """Get detailed graph information"""
    try:
        response = requests.get(f"{API_BASE}/graph")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"\n Complete Graph Analysis:")
            print(f"   Total nodes: {graph_data['total_nodes']}")
            print(f"   Total edges: {graph_data['total_edges']}")
            
            # Count node types
            node_types = {}
            for node in graph_data['nodes']:
                node_type = node['node_type']
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            print(f"\n📋 Node Types:")
            for node_type, count in node_types.items():
                emoji = "📝" if node_type == 'note' else "📄" if node_type == 'pdf' else "🔗"
                print(f"   {emoji} {node_type.title()}: {count}")
            
            # Show all nodes by type
            for node_type in ['note', 'pdf', 'link']:
                nodes = [n for n in graph_data['nodes'] if n['node_type'] == node_type]
                if nodes:
                    emoji = "📝" if node_type == 'note' else "📄" if node_type == 'pdf' else "🔗"
                    print(f"\n{emoji} {node_type.title()} Documents:")
                    for node in nodes:
                        print(f"   • {node['title']}")
                        if node['keywords']:
                            keywords = ', '.join(node['keywords'][:4])
                            print(f"     Keywords: {keywords}")
            
        else:
            print(f"ERROR: Error getting graph info: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Error: {e}")

def main():
    """Main test function"""
    print("🎯 Comprehensive Knowledge Graph Test")
    print("Testing Markdown + PDF + Links ingestion\n")
    
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
    
    # Run comprehensive test
    if test_comprehensive_ingestion():
        get_detailed_graph_info()
        
        print("\n🎉 Success! Your knowledge graph now includes:")
        print("   📝 Markdown notes")
        print("   📄 PDF documents") 
        print("   🔗 Saved links")
        print("   🕸️ Semantic connections between all content types")
        
        print("\n🌐 View your graph at: http://localhost:3000")
        print("   Look for purple rectangular PDF nodes!")

if __name__ == "__main__":
    main()
