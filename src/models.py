"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class NodeData(BaseModel):
    """Represents a single node in the knowledge graph"""
    id: str = Field(..., description="Unique identifier for the node")
    title: str = Field(..., description="Display title of the node")
    content: str = Field(..., description="Full text content")
    node_type: str = Field(..., description="Type of node (note, link, etc.)")
    keywords: List[str] = Field(default=[], description="Extracted keywords")
    created_at: datetime = Field(default_factory=datetime.now)
    click_count: int = Field(default=0, description="Number of times user clicked this node")
    source_file: Optional[str] = Field(None, description="Original source file name")

class EdgeData(BaseModel):
    """Represents an edge (connection) between nodes"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    weight: float = Field(..., description="Connection strength (0.0 to 1.0)")
    similarity_type: str = Field(default="semantic", description="Type of similarity")
    created_at: datetime = Field(default_factory=datetime.now)
    user_boosted: bool = Field(default=False, description="Whether user interaction boosted this edge")

class GraphResponse(BaseModel):
    """Complete graph data response"""
    nodes: List[NodeData] = Field(..., description="All nodes in the graph")
    edges: List[EdgeData] = Field(..., description="All edges in the graph")
    total_nodes: int = Field(..., description="Total number of nodes")
    total_edges: int = Field(..., description="Total number of edges")
    last_updated: datetime = Field(default_factory=datetime.now)

class FeedbackRequest(BaseModel):
    """User feedback for adaptive learning"""
    node_id: str = Field(..., description="ID of the clicked/interacted node")
    interaction_type: str = Field(default="click", description="Type of interaction")
    duration: Optional[float] = Field(None, description="Time spent on node (seconds)")
    timestamp: datetime = Field(default_factory=datetime.now)

class IngestResponse(BaseModel):
    """Response from data ingestion endpoint"""
    status: str = Field(..., description="Success or error status")
    items_processed: int = Field(..., description="Number of items processed")
    nodes_created: int = Field(..., description="Number of nodes created")
    edges_created: int = Field(..., description="Number of edges created")
    message: str = Field(..., description="Human-readable status message")
