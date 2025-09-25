"""
Graph construction and management using NetworkX and semantic embeddings
"""

import networkx as nx
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime
import json

from .models import NodeData, EdgeData, FeedbackRequest

logger = logging.getLogger(__name__)

class GraphBuilder:
    """Builds and manages the adaptive knowledge graph"""
    
    def __init__(self, similarity_threshold: float = 0.3, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the graph builder
        
        Args:
            similarity_threshold: Minimum similarity score to create an edge
            embedding_model: Name of the sentence transformer model to use
        """
        self.graph = nx.Graph()
        self.similarity_threshold = similarity_threshold
        self.embeddings_cache = {}
        self.node_data = {}
        
        # Load the embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def build_graph(self, items: List[Dict]) -> Dict[str, int]:
        """
        Build the knowledge graph from processed items
        
        Args:
            items: List of processed items from ingestion
            
        Returns:
            Dictionary with graph statistics
        """
        logger.info(f"Building graph from {len(items)} items...")
        
        # Clear existing graph
        self.graph.clear()
        self.embeddings_cache.clear()
        self.node_data.clear()
        
        # Add nodes
        for item in items:
            self._add_node(item)
        
        # Generate embeddings for all nodes
        self._generate_embeddings()
        
        # Calculate similarities and add edges
        self._add_similarity_edges()
        
        # Calculate graph statistics
        stats = {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges()
        }
        
        logger.info(f"Graph built: {stats['nodes']} nodes, {stats['edges']} edges")
        return stats
    
    def _add_node(self, item: Dict):
        """Add a single node to the graph"""
        node_id = item['id']
        
        # Create node data
        node_data = NodeData(
            id=node_id,
            title=item['title'],
            content=item['content'],
            node_type=item['node_type'],
            keywords=item.get('keywords', []),
            source_file=item.get('source_file'),
            created_at=item.get('created_at', datetime.now())
        )
        
        # Add to graph with attributes
        self.graph.add_node(node_id, **node_data.model_dump())
        
        # Store in our cache for quick access
        self.node_data[node_id] = node_data
        
        logger.debug(f"Added node: {node_id} - {item['title']}")
    
    def _generate_embeddings(self):
        """Generate embeddings for all nodes"""
        logger.info("Generating embeddings for all nodes...")
        
        # Prepare texts for embedding
        node_ids = list(self.node_data.keys())
        texts = []
        
        for node_id in node_ids:
            node = self.node_data[node_id]
            # Combine title, keywords, and content snippet for embedding
            keywords_text = " ".join(node.keywords)
            content_snippet = node.content[:500]  # First 500 chars
            combined_text = f"{node.title} {keywords_text} {content_snippet}"
            texts.append(combined_text)
        
        # Generate embeddings in batch for efficiency
        embeddings = self.embedding_model.encode(texts)
        
        # Cache embeddings
        for node_id, embedding in zip(node_ids, embeddings):
            self.embeddings_cache[node_id] = embedding
        
        logger.info(f"Generated embeddings for {len(node_ids)} nodes")
    
    def _add_similarity_edges(self):
        """Calculate similarities and add edges between similar nodes"""
        logger.info("Calculating similarities and adding edges...")
        
        node_ids = list(self.embeddings_cache.keys())
        embeddings = np.array([self.embeddings_cache[node_id] for node_id in node_ids])
        
        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        edges_added = 0
        for i, node1_id in enumerate(node_ids):
            for j, node2_id in enumerate(node_ids):
                if i >= j:  # Skip diagonal and duplicate pairs
                    continue
                
                similarity_score = similarity_matrix[i][j]
                
                # Add edge if similarity is above threshold
                if similarity_score >= self.similarity_threshold:
                    self._add_edge(node1_id, node2_id, similarity_score)
                    edges_added += 1
        
        logger.info(f"Added {edges_added} similarity edges")
    
    def _add_edge(self, node1_id: str, node2_id: str, weight: float, edge_type: str = "semantic"):
        """Add an edge between two nodes"""
        # Create edge data
        edge_data = EdgeData(
            source=node1_id,
            target=node2_id,
            weight=weight,
            similarity_type=edge_type,
            created_at=datetime.now()
        )
        
        # Add to graph
        self.graph.add_edge(node1_id, node2_id, **edge_data.model_dump())
    
    def get_graph_data(self) -> Dict[str, Any]:
        """
        Get complete graph data for API response
        
        Returns:
            Dictionary containing nodes, edges, and metadata
        """
        nodes = []
        edges = []
        
        # Collect nodes
        for node_id, node_attrs in self.graph.nodes(data=True):
            node_data = NodeData(**node_attrs)
            nodes.append(node_data)
        
        # Collect edges
        for source, target, edge_attrs in self.graph.edges(data=True):
            edge_data = EdgeData(**edge_attrs)
            edges.append(edge_data)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "last_updated": datetime.now()
        }
    
    def update_weights_from_feedback(self, feedback: FeedbackRequest):
        """
        Update graph weights based on user feedback (adaptive learning)
        
        Args:
            feedback: User interaction feedback
        """
        node_id = feedback.node_id
        
        if node_id not in self.graph:
            logger.warning(f"Node {node_id} not found in graph")
            return
        
        # Update click count for the node
        if node_id in self.node_data:
            self.node_data[node_id].click_count += 1
            self.graph.nodes[node_id]['click_count'] = self.node_data[node_id].click_count
        
        # Boost weights of edges connected to this node
        boost_factor = 1.1  # 10% boost
        max_weight = 1.0
        
        for neighbor in self.graph.neighbors(node_id):
            edge_data = self.graph[node_id][neighbor]
            current_weight = edge_data.get('weight', 0.0)
            
            # Apply boost but cap at max_weight
            new_weight = min(current_weight * boost_factor, max_weight)
            
            # Update edge weight
            self.graph[node_id][neighbor]['weight'] = new_weight
            self.graph[node_id][neighbor]['user_boosted'] = True
            
            logger.debug(f"Boosted edge {node_id}-{neighbor}: {current_weight:.3f} -> {new_weight:.3f}")
        
        logger.info(f"Applied feedback boost to node {node_id} and {len(list(self.graph.neighbors(node_id)))} connected edges")
    
    def get_node_connections(self, node_id: str) -> List[Dict]:
        """Get all connections for a specific node"""
        if node_id not in self.graph:
            return []
        
        connections = []
        for neighbor in self.graph.neighbors(node_id):
            edge_data = self.graph[node_id][neighbor]
            neighbor_data = self.node_data.get(neighbor)
            
            connections.append({
                "target_node_id": neighbor,
                "target_title": neighbor_data.title if neighbor_data else neighbor,
                "weight": edge_data.get('weight', 0.0),
                "similarity_type": edge_data.get('similarity_type', 'unknown'),
                "user_boosted": edge_data.get('user_boosted', False)
            })
        
        # Sort by weight descending
        connections.sort(key=lambda x: x['weight'], reverse=True)
        return connections
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        if self.graph.number_of_nodes() == 0:
            return {"status": "empty", "message": "No graph data available"}
        
        # Basic stats
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_connected(self.graph),
        }
        
        # Node type distribution
        node_types = {}
        click_counts = []
        for node_id, node_attrs in self.graph.nodes(data=True):
            node_type = node_attrs.get('node_type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
            click_counts.append(node_attrs.get('click_count', 0))
        
        stats['node_types'] = node_types
        stats['total_clicks'] = sum(click_counts)
        stats['avg_clicks_per_node'] = np.mean(click_counts) if click_counts else 0
        
        # Edge weight statistics
        weights = [edge_attrs.get('weight', 0.0) for _, _, edge_attrs in self.graph.edges(data=True)]
        if weights:
            stats['avg_edge_weight'] = np.mean(weights)
            stats['max_edge_weight'] = np.max(weights)
            stats['min_edge_weight'] = np.min(weights)
        
        # Most connected nodes
        degree_centrality = nx.degree_centrality(self.graph)
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        stats['most_connected_nodes'] = []
        for node_id, centrality in top_nodes:
            node_data = self.node_data.get(node_id)
            stats['most_connected_nodes'].append({
                "node_id": node_id,
                "title": node_data.title if node_data else node_id,
                "centrality": centrality,
                "connections": self.graph.degree(node_id)
            })
        
        return stats
    
    def find_surprising_connections(self, limit: int = 5) -> List[Dict]:
        """
        Find surprising connections - high weight edges between seemingly different nodes
        
        Args:
            limit: Maximum number of surprising connections to return
            
        Returns:
            List of surprising connection information
        """
        surprising = []
        
        for source, target, edge_attrs in self.graph.edges(data=True):
            weight = edge_attrs.get('weight', 0.0)
            
            # Get node data
            source_node = self.node_data.get(source)
            target_node = self.node_data.get(target)
            
            if not source_node or not target_node:
                continue
            
            # Calculate "surprise" score based on:
            # 1. High similarity weight
            # 2. Different node types
            # 3. Few overlapping keywords
            
            surprise_score = weight
            
            # Boost if different node types
            if source_node.node_type != target_node.node_type:
                surprise_score *= 1.2
            
            # Reduce if many overlapping keywords
            source_keywords = set(source_node.keywords)
            target_keywords = set(target_node.keywords)
            overlap = len(source_keywords.intersection(target_keywords))
            if overlap > 2:
                surprise_score *= 0.8
            
            surprising.append({
                "source_id": source,
                "target_id": target,
                "source_title": source_node.title,
                "target_title": target_node.title,
                "weight": weight,
                "surprise_score": surprise_score,
                "source_type": source_node.node_type,
                "target_type": target_node.node_type,
                "overlapping_keywords": list(source_keywords.intersection(target_keywords))
            })
        
        # Sort by surprise score and return top results
        surprising.sort(key=lambda x: x['surprise_score'], reverse=True)
        return surprising[:limit]
