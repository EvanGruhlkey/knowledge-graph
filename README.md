# Adaptive Personal Knowledge Graph MVP

An intelligent system that builds semantic knowledge graphs from your personal data (markdown notes and saved links) and adapts based on your interactions.

## Features

- 📝 **Data Ingestion**: Process markdown notes, PDF documents, and JSON/CSV link collections
- 🕸️ **Semantic Graph**: Build weighted connections using sentence embeddings
-  **Adaptive Learning**: Graph weights adapt based on user interactions
-  **FastAPI Backend**: RESTful API with automatic documentation
-  **Analytics**: Graph statistics and surprising connection discovery

## Quick Start

### 1. Install Dependencies

```bash
# Windows (recommended)
py -m pip install -r requirements.txt

# Or if pip is in PATH
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Easy way
py start_server.py

# Or directly with uvicorn
py -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### 3. Test with Sample Data

```bash
py test_api.py
```

This will ingest the sample markdown notes and links, build the graph, and demonstrate the API functionality.

## API Endpoints

### POST `/ingest`
Upload and process data sources to build/update the knowledge graph.

**Parameters:**
- `markdown_files`: List of markdown files (optional)
- `pdf_files`: List of PDF document files (optional)
- `links_file`: JSON or CSV file with saved links (optional)

**Response:**
```json
{
  "status": "success",
  "items_processed": 8,
  "nodes_created": 8,
  "edges_created": 12,
  "message": "Data successfully ingested and graph updated"
}
```

### GET `/graph`
Retrieve the complete knowledge graph with nodes and weighted edges.

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "total_nodes": 8,
  "total_edges": 12,
  "last_updated": "2025-09-25T..."
}
```

### POST `/feedback`
Record user interactions to adapt graph weights.

**Request:**
```json
{
  "node_id": "md_note1_ai_research.md_abcd1234",
  "interaction_type": "click",
  "duration": 15.5
}
```

### GET `/stats`
Get comprehensive graph statistics and analytics.

## Data Formats

### Markdown Notes
Standard markdown files with:
- Title extraction from first heading (`# Title`)
- Keyword extraction from content
- Full-text semantic analysis

### PDF Documents
PDF files with automatic text extraction:
- Supports both text-based and scanned PDFs
- Title extraction from document content
- Full-text indexing and keyword extraction
- Handles multi-page documents

### Links JSON Format
```json
[
  {
    "title": "Article Title",
    "url": "https://example.com",
    "description": "Brief description",
    "tags": ["tag1", "tag2"],
    "notes": "Personal notes about this link"
  }
]
```

### Links CSV Format
```csv
title,url,description,tags,notes
"Article Title","https://example.com","Brief description","tag1,tag2","Personal notes"
```

## Architecture

### Core Components

1. **`main.py`**: FastAPI application with endpoints
2. **`src/ingestion.py`**: Data processing and extraction
3. **`src/graph_builder.py`**: Graph construction and semantic analysis
4. **`src/models.py`**: Pydantic models for API schemas

### Graph Construction Process

1. **Text Processing**: Extract titles, keywords, and content from sources
2. **Embedding Generation**: Create semantic embeddings using `sentence-transformers`
3. **Similarity Calculation**: Compute cosine similarity between all node pairs
4. **Edge Creation**: Connect nodes with similarity above threshold (default: 0.3)
5. **Adaptive Updates**: Boost edge weights based on user interactions

### Adaptive Learning

The system learns from user behavior:
- **Click Tracking**: Records which nodes users interact with most
- **Weight Boosting**: Increases edge weights for frequently accessed nodes
- **Surprise Detection**: Identifies unexpected high-similarity connections

## Configuration

Key parameters in `src/graph_builder.py`:
- `similarity_threshold`: Minimum similarity to create edges (default: 0.3)
- `embedding_model`: Sentence transformer model (default: "all-MiniLM-L6-v2")
- `boost_factor`: Weight increase multiplier for user feedback (default: 1.1)

## Sample Data

The `test_data/` directory contains:
- **Markdown Notes**: AI research, productivity tips, web development
- **Links JSON**: Curated collection of relevant articles and tools

## Frontend (React + Cytoscape.js)

### Quick Start Frontend
```bash
# Start the React frontend (separate terminal)
cd frontend
npm run dev
# OR use the batch file
start_frontend.bat
```

The frontend will be available at `http://localhost:3000`

### Features
- 🎨 **Interactive Graph Visualization**: Cytoscape.js powered graph with smooth animations
- 🖱️ **Click to Explore**: Click any node to see details and connections
-  **Real-time Analytics**: Live stats and connection strength indicators  
- 🎯 **Adaptive Learning**: Visual feedback when edges get boosted by user interactions
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🎨 **Modern UI**: Beautiful gradients, glassmorphism effects, and smooth transitions

### Graph Visualization
- **Nodes**: Different shapes and colors for notes vs links
- **Edges**: Width and opacity based on similarity strength
- **User Boosted Connections**: Orange highlighting for learned preferences
- **Interactive Controls**: Fit, center, and re-layout buttons
- **Legend**: Visual guide to understand the graph elements

### Sidebar Features
- **Node Details**: Full content, keywords, and metadata
- **Connections Tab**: All related nodes with similarity scores
- **Statistics**: Graph overview and most connected nodes
- **Click Tracking**: Visual indicators for user engagement

## Complete System Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│  React Frontend │◄──────────────►│ FastAPI Backend │
│  (Port 3000)    │                 │  (Port 8000)    │
│                 │                 │                 │
│ • Cytoscape.js  │                 │ • NetworkX      │
│ • Interactive   │                 │ • Embeddings    │
│ • Real-time     │                 │ • Adaptive      │
└─────────────────┘                 └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Knowledge Graph │
                                    │                 │
                                    │ • Semantic      │
                                    │ • Weighted      │
                                    │ • Adaptive      │
                                    └─────────────────┘
```

## Running Both Services

### Option 1: Separate Terminals
```bash
# Terminal 1: Backend
py start_server.py

# Terminal 2: Frontend  
cd frontend && npm run dev
```

### Option 2: Batch Files (Windows)
```bash
# Start backend
start.bat

# Start frontend (in another terminal)
start_frontend.bat
```

## Next Steps

This complete system provides the foundation for:
- **Advanced Analytics**: Clustering, community detection, trend analysis  
- **Multi-modal Data**: Support for PDFs, images, audio transcripts
- **Collaborative Features**: Shared graphs and social recommendations
- **Export Options**: GraphML, GEXF, and other graph formats
- **Mobile App**: React Native version for mobile knowledge management

## Development

### Running Tests
```bash
python test_api.py
```

### Development Server
```bash
uvicorn main:app --reload --log-level debug
```

### Dependencies
- **FastAPI**: Modern Python web framework
- **NetworkX**: Graph manipulation and analysis
- **sentence-transformers**: Semantic embeddings
- **scikit-learn**: Similarity calculations
- **pydantic**: Data validation and serialization

## License

MIT License - feel free to extend and adapt for your needs!
