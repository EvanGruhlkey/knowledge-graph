import React, { useState, useEffect } from 'react'
import KnowledgeGraph from './components/KnowledgeGraph'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { graphService } from './services/api'
import './styles/App.css'

function App() {
  const [graphData, setGraphData] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)

  // Load initial graph data
  useEffect(() => {
    loadGraphData()
    loadStats()
  }, [])

  const loadGraphData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await graphService.getGraph()
      setGraphData(data)
    } catch (err) {
      setError('Failed to load graph data. Make sure the backend server is running.')
      console.error('Error loading graph:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await graphService.getStats()
      setStats(statsData)
    } catch (err) {
      console.error('Error loading stats:', err)
    }
  }

  const handleNodeClick = async (nodeData) => {
    setSelectedNode(nodeData)
    
    // Send feedback to backend for adaptive learning
    try {
      await graphService.recordFeedback({
        node_id: nodeData.id,
        interaction_type: 'click',
        duration: null
      })
      
      // Reload graph data to get updated weights
      await loadGraphData()
      await loadStats()
    } catch (err) {
      console.error('Error recording feedback:', err)
    }
  }

  const handleRefresh = () => {
    loadGraphData()
    loadStats()
  }

  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your knowledge graph...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <div className="error-container">
          <h2>⚠️ Connection Error</h2>
          <p>{error}</p>
          <button onClick={handleRefresh} className="retry-button">
            Retry Connection
          </button>
          <div className="error-help">
            <p>Make sure the backend server is running:</p>
            <code>py start_server.py</code>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Header 
        stats={stats} 
        onRefresh={handleRefresh}
        graphData={graphData}
      />
      
      <div className="app-content">
        <div className="graph-container">
          <KnowledgeGraph 
            graphData={graphData}
            onNodeClick={handleNodeClick}
            selectedNode={selectedNode}
          />
        </div>
        
        <Sidebar 
          selectedNode={selectedNode}
          onClose={() => setSelectedNode(null)}
          graphData={graphData}
          stats={stats}
        />
      </div>
    </div>
  )
}

export default App
