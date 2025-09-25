"""
Demo script to showcase the Knowledge Graph functionality
"""

import requests
import json
import time
from pathlib import Path

API_BASE = "http://localhost:8000"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def demo_ingestion():
    """Demonstrate data ingestion"""
    print_header(" ADAPTIVE PERSONAL KNOWLEDGE GRAPH DEMO")
    
    print("This demo showcases how the system:")
    print("• Ingests markdown notes and saved links")
    print("• Builds semantic connections using AI embeddings") 
    print("• Adapts based on user interactions")
    print("• Discovers surprising connections between ideas")
    
    print_section("📥 Step 1: Data Ingestion")
    
    # Prepare files for upload
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
    
    # Add links JSON
    links_file = test_data_dir / "saved_links.json"
    if links_file.exists():
        with open(links_file, 'r') as f:
            links_data = json.load(f)
        print(f"\nFound {len(links_data)} saved links:")
        for link in links_data[:3]:
            print(f"  • {link['title']}")
        if len(links_data) > 3:
            print(f"  • ... and {len(links_data) - 3} more")
        
        fh = open(links_file, 'rb')
        file_handles.append(fh)
        files.append(('links_file', (links_file.name, fh, 'application/json')))
    
    # Ingest data
    print("\n🔄 Processing data and building semantic graph...")
    try:
        response = requests.post(f"{API_BASE}/ingest", files=files)
    finally:
        # Close all file handles
        for fh in file_handles:
            fh.close()
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: Success! Processed {result['items_processed']} items")
        print(f"   📝 Created {result['nodes_created']} knowledge nodes")
        print(f"   🔗 Generated {result['edges_created']} semantic connections")
    else:
        print(f"ERROR: Error: {response.text}")
        return False
    
    return True

def demo_graph_exploration():
    """Demonstrate graph exploration"""
    print_section("🕸️ Step 2: Graph Exploration")
    
    response = requests.get(f"{API_BASE}/graph")
    if response.status_code != 200:
        print(f"ERROR: Error retrieving graph: {response.text}")
        return None
    
    graph_data = response.json()
    print(f" Graph contains {graph_data['total_nodes']} nodes and {graph_data['total_edges']} edges")
    
    print("\n📝 Knowledge Nodes:")
    for i, node in enumerate(graph_data['nodes'], 1):
        node_type_emoji = "📝" if node['node_type'] == 'note' else "🔗"
        print(f"   {i}. {node_type_emoji} {node['title']}")
        if node['keywords']:
            keywords = ', '.join(node['keywords'][:4])
            if len(node['keywords']) > 4:
                keywords += f", +{len(node['keywords']) - 4} more"
            print(f"      🏷️ {keywords}")
    
    # Show strongest connections
    print("\n🔗 Strongest Semantic Connections:")
    sorted_edges = sorted(graph_data['edges'], key=lambda x: x['weight'], reverse=True)
    
    for i, edge in enumerate(sorted_edges[:5], 1):
        source_node = next(n for n in graph_data['nodes'] if n['id'] == edge['source'])
        target_node = next(n for n in graph_data['nodes'] if n['id'] == edge['target'])
        
        print(f"   {i}. {source_node['title']}")
        print(f"      ↔ {target_node['title']}")
        print(f"      💪 Similarity: {edge['weight']:.3f}")
    
    return graph_data

def demo_adaptive_learning(graph_data):
    """Demonstrate adaptive learning"""
    print_section("🧠 Step 3: Adaptive Learning")
    
    if not graph_data or not graph_data['nodes']:
        print("⚠️ No graph data available")
        return
    
    # Simulate user interactions
    print("Simulating user interactions to demonstrate adaptive learning...")
    
    # Click on AI-related nodes multiple times
    ai_nodes = [n for n in graph_data['nodes'] if 'ai' in n['title'].lower() or 'machine learning' in n['content'].lower()]
    
    if ai_nodes:
        target_node = ai_nodes[0]
        print(f"\n👆 User frequently clicks on: '{target_node['title']}'")
        
        # Record multiple interactions
        for i in range(3):
            feedback_data = {
                "node_id": target_node['id'],
                "interaction_type": "click",
                "duration": 20.0 + i * 5
            }
            
            response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
            if response.status_code == 200:
                print(f"   📈 Interaction {i+1} recorded - boosting connected edges")
            time.sleep(0.5)  # Small delay for demo effect
        
        print(f"\n Result: Edges connected to '{target_node['title']}' are now stronger!")
        print("   This helps the system learn your interests and surface related content.")

def demo_statistics():
    """Show graph statistics and insights"""
    print_section(" Step 4: Analytics & Insights")
    
    response = requests.get(f"{API_BASE}/stats")
    if response.status_code != 200:
        print(f"ERROR: Error getting stats: {response.text}")
        return
    
    stats = response.json()
    
    print("📈 Graph Statistics:")
    print(f"   • Total nodes: {stats['total_nodes']}")
    print(f"   • Total edges: {stats['total_edges']}")
    print(f"   • Graph density: {stats['density']:.3f}")
    print(f"   • Connected: {'Yes' if stats['is_connected'] else 'No'}")
    print(f"   • Total user clicks: {stats['total_clicks']}")
    
    if 'node_types' in stats:
        print(f"\n📋 Content Types:")
        for node_type, count in stats['node_types'].items():
            emoji = "📝" if node_type == 'note' else "🔗"
            print(f"   • {emoji} {node_type.title()}: {count}")
    
    if 'most_connected_nodes' in stats:
        print(f"\n🌟 Most Connected Nodes (Knowledge Hubs):")
        for i, node in enumerate(stats['most_connected_nodes'][:3], 1):
            print(f"   {i}. {node['title']} ({node['connections']} connections)")

def demo_conclusion():
    """Show conclusion and next steps"""
    print_section("🎉 Demo Complete!")
    
    print("What we've demonstrated:")
    print("SUCCESS: Semantic ingestion of personal knowledge")
    print("SUCCESS: AI-powered connection discovery")  
    print("SUCCESS: Adaptive learning from user behavior")
    print("SUCCESS: Analytics and insights generation")
    
    print("\n Next Steps:")
    print("• Build React frontend with Cytoscape.js visualization")
    print("• Add more data sources (PDFs, bookmarks, etc.)")
    print("• Implement clustering and community detection")
    print("• Add collaborative features and sharing")
    
    print("\n📚 API Documentation:")
    print("• Interactive docs: http://localhost:8000/docs")
    print("• Alternative docs: http://localhost:8000/redoc")
    
    print("\n🔧 Try the API yourself:")
    print("• py test_api.py - Run comprehensive API tests")
    print("• Use curl or Postman to interact with endpoints")
    print("• Upload your own markdown notes and links!")

def main():
    """Run the complete demo"""
    try:
        # Check if server is running
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            raise requests.exceptions.ConnectionError()
        
        # Run demo steps
        if demo_ingestion():
            graph_data = demo_graph_exploration()
            demo_adaptive_learning(graph_data)
            demo_statistics()
            demo_conclusion()
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server first:")
        print("   py start_server.py")
        print("   OR")
        print("   py -m uvicorn main:app --reload")
    except Exception as e:
        print(f"ERROR: Demo failed with error: {e}")

if __name__ == "__main__":
    main()
