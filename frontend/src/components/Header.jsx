import React from 'react'
import { RefreshCw, Brain, Network, TrendingUp } from 'lucide-react'

const Header = ({ stats, onRefresh, graphData }) => {
  return (
    <header className="app-header">
      <div className="header-left">
        <div className="logo">
          <Brain className="logo-icon" />
          <h1>Adaptive Knowledge Graph</h1>
        </div>
        
        {stats && (
          <div className="stats-summary">
            <div className="stat-item">
              <Network size={16} />
              <span>{stats.total_nodes} nodes</span>
            </div>
            <div className="stat-item">
              <TrendingUp size={16} />
              <span>{stats.total_edges} connections</span>
            </div>
            {stats.total_clicks > 0 && (
              <div className="stat-item">
                <span>👆 {stats.total_clicks} interactions</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="header-right">
        <button 
          onClick={onRefresh}
          className="refresh-button"
          title="Refresh graph data"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
    </header>
  )
}

export default Header
