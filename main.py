"""
Adaptive Personal Knowledge Graph MVP - FastAPI Backend

This application creates a semantic knowledge graph from personal data sources
(markdown notes and saved links) and adapts based on user interactions.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging

from src.ingestion import DataIngestion
from src.graph_builder import GraphBuilder
from src.models import GraphResponse, FeedbackRequest, IngestResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Adaptive Personal Knowledge Graph",
    description="An API for building and adapting personal knowledge graphs from notes and links",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
ingestion = DataIngestion()
graph_builder = GraphBuilder()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Adaptive Personal Knowledge Graph API is running"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_data(
    markdown_files: List[UploadFile] = File(None),
    pdf_files: List[UploadFile] = File(None),
    links_file: UploadFile = File(None)
):
    """
    Ingest personal data sources and build the knowledge graph.
    
    Args:
        markdown_files: List of markdown note files
        pdf_files: List of PDF document files
        links_file: JSON/CSV file containing saved links
    
    Returns:
        IngestResponse: Summary of ingested data and graph statistics
    """
    try:
        logger.info("Starting data ingestion...")
        
        # Process markdown files
        markdown_data = []
        if markdown_files:
            for file in markdown_files:
                content = await file.read()
                markdown_data.append({
                    "filename": file.filename,
                    "content": content.decode('utf-8')
                })
        
        # Process PDF files
        pdf_data = []
        if pdf_files:
            for file in pdf_files:
                content = await file.read()
                pdf_data.append({
                    "filename": file.filename,
                    "content": content  # Keep as bytes for PDF processing
                })
        
        # Process links file
        links_data = None
        if links_file:
            content = await links_file.read()
            if links_file.filename.endswith('.json'):
                links_data = json.loads(content.decode('utf-8'))
            elif links_file.filename.endswith('.csv'):
                # Handle CSV parsing in ingestion module
                links_data = content.decode('utf-8')
        
        # Extract and process data
        processed_data = ingestion.process_data(markdown_data, links_data, pdf_data)
        
        # Build/update the graph
        graph_stats = graph_builder.build_graph(processed_data)
        
        logger.info(f"Ingestion complete. Processed {len(processed_data)} items.")
        
        return IngestResponse(
            status="success",
            items_processed=len(processed_data),
            nodes_created=graph_stats["nodes"],
            edges_created=graph_stats["edges"],
            message="Data successfully ingested and graph updated"
        )
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.get("/graph", response_model=GraphResponse)
async def get_graph():
    """
    Retrieve the current knowledge graph with nodes and weighted edges.
    
    Returns:
        GraphResponse: Complete graph data including nodes, edges, and metadata
    """
    try:
        logger.info("Retrieving graph data...")
        graph_data = graph_builder.get_graph_data()
        
        if not graph_data["nodes"]:
            raise HTTPException(
                status_code=404, 
                detail="No graph data found. Please ingest data first."
            )
        
        return GraphResponse(**graph_data)
        
    except Exception as e:
        logger.error(f"Error retrieving graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve graph: {str(e)}")

@app.post("/feedback")
async def record_feedback(feedback: FeedbackRequest):
    """
    Record user interaction feedback to adapt the graph weights.
    
    Args:
        feedback: User interaction data (node clicks, time spent, etc.)
    
    Returns:
        dict: Confirmation of feedback processing
    """
    try:
        logger.info(f"Recording feedback for node: {feedback.node_id}")
        
        # Update graph weights based on user interaction
        graph_builder.update_weights_from_feedback(feedback)
        
        return {
            "status": "success",
            "message": f"Feedback recorded for node {feedback.node_id}",
            "updated_connections": graph_builder.get_node_connections(feedback.node_id)
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get current graph statistics and metadata"""
    try:
        return graph_builder.get_graph_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/clear")
async def clear_graph():
    """Clear all data from the knowledge graph"""
    try:
        logger.info("Clearing knowledge graph...")
        
        # Clear the graph
        graph_builder.graph.clear()
        graph_builder.embeddings_cache.clear()
        graph_builder.node_data.clear()
        
        # Clear ingestion data
        ingestion.processed_items = []
        
        logger.info("Knowledge graph cleared successfully")
        
        return {
            "status": "success",
            "message": "Knowledge graph cleared successfully",
            "nodes_removed": "all",
            "edges_removed": "all"
        }
        
    except Exception as e:
        logger.error(f"Error clearing graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear graph: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
