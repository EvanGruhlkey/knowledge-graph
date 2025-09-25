"""
Easy document management for the Knowledge Graph
"""

import requests
from pathlib import Path
import os

API_BASE = "http://localhost:8000"

def add_documents_from_folder(folder_path: str = "."):
    """
    Add all documents from a folder to the knowledge graph
    
    Args:
        folder_path: Path to folder containing documents (default: current directory)
    """
    print(f"Scanning folder: {folder_path}")
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"ERROR: Folder not found: {folder_path}")
        return False
    
    # Find all supported files
    markdown_files = list(folder.glob("*.md"))
    pdf_files = list(folder.glob("*.pdf"))
    json_files = list(folder.glob("*links*.json")) + list(folder.glob("*bookmarks*.json"))
    
    total_files = len(markdown_files) + len(pdf_files) + len(json_files)
    
    if total_files == 0:
        print("No supported documents found")
        print("Supported formats: .md, .pdf, .json (for links)")
        return False
    
    print(f"\n Found {total_files} documents:")
    if markdown_files:
        print(f"  * {len(markdown_files)} Markdown files:")
        for f in markdown_files:
            print(f"    • {f.name}")
    
    if pdf_files:
        print(f"  * {len(pdf_files)} PDF files:")
        for f in pdf_files:
            print(f"    • {f.name}")
    
    if json_files:
        print(f"  * {len(json_files)} Link files:")
        for f in json_files:
            print(f"    • {f.name}")
    
    # Prepare files for upload
    files = []
    file_handles = []
    
    try:
        # Add markdown files
        for md_file in markdown_files:
            fh = open(md_file, 'rb')
            file_handles.append(fh)
            files.append(('markdown_files', (md_file.name, fh, 'text/markdown')))
        
        # Add PDF files
        for pdf_file in pdf_files:
            fh = open(pdf_file, 'rb')
            file_handles.append(fh)
            files.append(('pdf_files', (pdf_file.name, fh, 'application/pdf')))
        
        # Add JSON files (assume they're link collections)
        for json_file in json_files:
            fh = open(json_file, 'rb')
            file_handles.append(fh)
            files.append(('links_file', (json_file.name, fh, 'application/json')))
        
        print(f"\n Uploading {len(files)} files to knowledge graph...")
        response = requests.post(f"{API_BASE}/ingest", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Success! Processed {result['items_processed']} items")
            print(f"   * Created {result['nodes_created']} nodes")
            print(f"   * Generated {result['edges_created']} semantic connections")
            return True
        else:
            print(f"ERROR: Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Please start with: py start_server.py")
        return False
    except Exception as e:
        print(f"ERROR: Error: {e}")
        return False
    finally:
        # Always close file handles
        for fh in file_handles:
            fh.close()

def add_single_document(file_path: str):
    """
    Add a single document to the knowledge graph
    
    Args:
        file_path: Path to the document file
    """
    print(f"* Adding document: {file_path}")
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False
    
    # Determine file type
    extension = file_path.suffix.lower()
    
    if extension == '.md':
        file_type = 'markdown_files'
        content_type = 'text/markdown'
    elif extension == '.pdf':
        file_type = 'pdf_files'
        content_type = 'application/pdf'
    elif extension == '.json':
        file_type = 'links_file'
        content_type = 'application/json'
    else:
        print(f"ERROR: Unsupported file type: {extension}")
        print("Supported formats: .md, .pdf, .json")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = [(file_type, (file_path.name, f, content_type))]
            
            print(f" Uploading {file_path.name}...")
            response = requests.post(f"{API_BASE}/ingest", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Success! Processed {result['items_processed']} items")
            print(f"   * Created {result['nodes_created']} nodes")
            print(f"   * Generated {result['edges_created']} connections")
            return True
        else:
            print(f"ERROR: Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Please start with: py start_server.py")
        return False
    except Exception as e:
        print(f"ERROR: Error: {e}")
        return False

def show_graph_status():
    """Show current graph status"""
    try:
        response = requests.get(f"{API_BASE}/graph")
        if response.status_code == 200:
            graph_data = response.json()
            print(f" Knowledge Graph Status:")
            print(f"   Total nodes: {graph_data['total_nodes']}")
            print(f"   Total edges: {graph_data['total_edges']}")
            
            if graph_data['total_nodes'] > 0:
                # Count node types
                node_types = {}
                for node in graph_data['nodes']:
                    node_type = node['node_type']
                    node_types[node_type] = node_types.get(node_type, 0) + 1
                
                print(f"   Node breakdown:")
                for node_type, count in node_types.items():
                    emoji = "*" if node_type == 'note' else "*" if node_type == 'pdf' else "*"
                    print(f"     {emoji} {node_type.title()}: {count}")
        else:
            print(" Knowledge Graph: Empty (no data ingested)")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Please start with: py start_server.py")
    except Exception as e:
        print(f"ERROR: Error: {e}")

def main():
    """Interactive document management"""
    print(" Knowledge Graph Document Manager")
    print("="*50)
    
    # Check server status
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            raise requests.exceptions.ConnectionError()
        print("SUCCESS: Server is running")
    except requests.exceptions.ConnectionError:
        print("ERROR: Server not running. Please start with: py start_server.py")
        return
    
    # Show current status
    show_graph_status()
    
    print(f"\n Quick Actions:")
    print(f"1. Add all documents from current folder:")
    print(f"   add_documents_from_folder()")
    print(f"")
    print(f"2. Add documents from specific folder:")
    print(f"   add_documents_from_folder('path/to/your/documents')")
    print(f"")
    print(f"3. Add single document:")
    print(f"   add_single_document('path/to/document.pdf')")
    print(f"")
    print(f"4. Check graph status:")
    print(f"   show_graph_status()")
    
    print(f"\n Pro Tips:")
    print(f"   • Place documents in this folder and run: add_documents_from_folder()")
    print(f"   • Drag & drop files here, then run the script")
    print(f"   • The system auto-detects file types (.md, .pdf, .json)")
    print(f"   • View your graph at: http://localhost:3000")

if __name__ == "__main__":
    main()
