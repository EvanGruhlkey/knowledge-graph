import React, { useState } from 'react'
import { X, FileText, Link, Tag, MousePointer, TrendingUp, Star } from 'lucide-react'

const Sidebar = ({ selectedNode, onClose, graphData, stats }) => {
  const [activeTab, setActiveTab] = useState('details')

  if (!selectedNode) {
    return (
      <div className="sidebar sidebar-collapsed">
        <div className="sidebar-placeholder">
          <div className="placeholder-content">
            <MousePointer size={48} className="placeholder-icon" />
            <h3>Explore Your Knowledge</h3>
            <p>Click on any node to see details and connections</p>
            
            {stats && (
              <div className="sidebar-stats">
                <h4>Graph Overview</h4>
                <div className="stat-grid">
                  <div className="stat-card">
                    <div className="stat-number">{stats.total_nodes}</div>
                    <div className="stat-label">Knowledge Nodes</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-number">{stats.total_edges}</div>
                    <div className="stat-label">Connections</div>
                  </div>
                  {stats.density && (
                    <div className="stat-card">
                      <div className="stat-number">{(stats.density * 100).toFixed(1)}%</div>
                      <div className="stat-label">Density</div>
                    </div>
                  )}
                </div>

                {stats.most_connected_nodes && stats.most_connected_nodes.length > 0 && (
                  <div className="top-nodes">
                    <h4>🌟 Knowledge Hubs</h4>
                    {stats.most_connected_nodes.slice(0, 3).map((node, index) => (
                      <div key={node.node_id} className="top-node-item">
                        <span className="rank">#{index + 1}</span>
                        <span className="node-title">{node.title}</span>
                        <span className="connection-count">{node.connections} connections</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Get connections for the selected node
  const getNodeConnections = () => {
    if (!graphData) return []
    
    return graphData.edges
      .filter(edge => edge.source === selectedNode.id || edge.target === selectedNode.id)
      .map(edge => {
        const connectedNodeId = edge.source === selectedNode.id ? edge.target : edge.source
        const connectedNode = graphData.nodes.find(node => node.id === connectedNodeId)
        
        return {
          node: connectedNode,
          edge: edge,
          weight: edge.weight
        }
      })
      .sort((a, b) => b.weight - a.weight) // Sort by similarity strength
  }

  const connections = getNodeConnections()

  return (
    <div className="sidebar sidebar-expanded">
      <div className="sidebar-header">
        <div className="node-type-indicator">
          {selectedNode.type === 'note' ? <FileText size={20} /> : 
           selectedNode.type === 'pdf' ? <FileText size={20} /> : 
           <Link size={20} />}
          <span className="node-type">{selectedNode.type}</span>
        </div>
        <button onClick={onClose} className="close-button">
          <X size={20} />
        </button>
      </div>

      <div className="sidebar-content">
        <div className="node-title">
          <h2>{selectedNode.title}</h2>
          {selectedNode.clickCount > 0 && (
            <div className="click-indicator">
              <MousePointer size={14} />
              <span>{selectedNode.clickCount} clicks</span>
            </div>
          )}
        </div>

        <div className="sidebar-tabs">
          <button 
            className={`tab ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            Details
          </button>
          <button 
            className={`tab ${activeTab === 'connections' ? 'active' : ''}`}
            onClick={() => setActiveTab('connections')}
          >
            Connections ({connections.length})
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'details' && (
            <div className="details-tab">
              {selectedNode.keywords && selectedNode.keywords.length > 0 && (
                <div className="keywords-section">
                  <h4><Tag size={16} /> Keywords</h4>
                  <div className="keywords-list">
                    {selectedNode.keywords.map((keyword, index) => (
                      <span key={index} className="keyword-tag">{keyword}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="content-section">
                <h4>Content</h4>
                <div className="content-text">
                  {selectedNode.content && selectedNode.content.length > 500 
                    ? `${selectedNode.content.substring(0, 500)}...`
                    : selectedNode.content
                  }
                </div>
              </div>

              {selectedNode.sourceFile && (
                <div className="metadata-section">
                  <h4>Source</h4>
                  <div className="source-info">
                    <FileText size={14} />
                    <span>{selectedNode.sourceFile}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'connections' && (
            <div className="connections-tab">
              {connections.length === 0 ? (
                <div className="no-connections">
                  <p>No connections found for this node.</p>
                </div>
              ) : (
                <div className="connections-list">
                  {connections.map((connection, index) => (
                    <div key={connection.node.id} className="connection-item">
                      <div className="connection-header">
                        <div className="connection-node">
                          {connection.node.node_type === 'note' ? <FileText size={16} /> : 
                           connection.node.node_type === 'pdf' ? <FileText size={16} /> :
                           <Link size={16} />}
                          <span className="connection-title">{connection.node.title}</span>
                        </div>
                        <div className="connection-strength">
                          <div 
                            className="strength-bar"
                            style={{ 
                              width: `${connection.weight * 100}%`,
                              backgroundColor: connection.edge.user_boosted ? '#F59E0B' : '#059669'
                            }}
                          ></div>
                          <span className="strength-value">{(connection.weight * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                      
                      {connection.edge.user_boosted && (
                        <div className="boosted-indicator">
                          <TrendingUp size={12} />
                          <span>User boosted</span>
                        </div>
                      )}
                      
                      {connection.node.keywords && (
                        <div className="connection-keywords">
                          {connection.node.keywords.slice(0, 3).map((keyword, idx) => (
                            <span key={idx} className="mini-keyword">{keyword}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Sidebar
