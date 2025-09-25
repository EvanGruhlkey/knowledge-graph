import React, { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'

const KnowledgeGraph = ({ graphData, onNodeClick, selectedNode }) => {
  const cyRef = useRef(null)
  const containerRef = useRef(null)
  const [cy, setCy] = useState(null)

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current || !graphData) return

    const cytoscapeInstance = cytoscape({
      container: containerRef.current,
      
      elements: [
        // Nodes
        ...graphData.nodes.map(node => ({
          data: {
            id: node.id,
            label: node.title,
            type: node.node_type,
            content: node.content,
            keywords: node.keywords,
            clickCount: node.click_count || 0,
            sourceFile: node.source_file
          }
        })),
        
        // Edges
        ...graphData.edges.map(edge => ({
          data: {
            id: `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            weight: edge.weight,
            similarityType: edge.similarity_type,
            userBoosted: edge.user_boosted || false
          }
        }))
      ],

      style: [
        // Node styles - Obsidian style
        {
          selector: 'node',
          style: {
            'background-color': (ele) => {
              const nodeType = ele.data('type')
              if (nodeType === 'note') return '#9c88ff'
              if (nodeType === 'pdf') return '#c084fc'
              return '#7c3aed' // links
            },
            'label': 'data(label)',
            'color': '#dcddde',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '11px',
            'font-weight': '500',
            'font-family': 'system-ui, -apple-system, sans-serif',
            'width': (ele) => {
              const clickCount = ele.data('clickCount') || 0
              return Math.max(40, 40 + clickCount * 6) // Obsidian-like smaller nodes
            },
            'height': (ele) => {
              const clickCount = ele.data('clickCount') || 0
              return Math.max(40, 40 + clickCount * 6) // Obsidian-like smaller nodes
            },
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            'border-width': 2,
            'border-color': (ele) => {
              const nodeType = ele.data('type')
              if (nodeType === 'note') return '#b197fc'
              if (nodeType === 'pdf') return '#ddd6fe'
              return '#a855f7' // links
            },
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': '0.2s',
            'text-outline-width': 1,
            'text-outline-color': '#1e1e1e',
            'text-outline-opacity': 0.8
          }
        },
        
        // Selected node style - Obsidian style
        {
          selector: 'node:selected',
          style: {
            'border-color': '#f093fb',
            'border-width': 3,
            'background-color': '#f093fb',
            'color': '#ffffff'
          }
        },
        
        // Hover effect for nodes
        {
          selector: 'node:active',
          style: {
            'overlay-color': '#000000',
            'overlay-opacity': 0.1
          }
        },

        // Edge styles - Obsidian style
        {
          selector: 'edge',
          style: {
            'width': (ele) => {
              const weight = ele.data('weight')
              return Math.max(1, weight * 4) // Thinner, more subtle edges like Obsidian
            },
            'line-color': (ele) => {
              const userBoosted = ele.data('userBoosted')
              const weight = ele.data('weight')
              if (userBoosted) return '#f093fb'
              // Obsidian-like purple edges with opacity based on strength
              const alpha = Math.max(0.3, weight * 0.8)
              return `rgba(156, 136, 255, ${alpha})`
            },
            'target-arrow-color': (ele) => {
              const userBoosted = ele.data('userBoosted')
              const weight = ele.data('weight')
              if (userBoosted) return '#f093fb'
              const alpha = Math.max(0.3, weight * 0.8)
              return `rgba(156, 136, 255, ${alpha})`
            },
            'target-arrow-shape': 'triangle',
            'target-arrow-size': 8,
            'curve-style': 'straight', // Obsidian uses straight lines
            'opacity': (ele) => {
              const weight = ele.data('weight')
              return Math.max(0.4, weight) // Subtle opacity
            },
            'transition-property': 'line-color, target-arrow-color, width, opacity',
            'transition-duration': '0.2s'
          }
        },

        // Highlighted edges (connected to selected node) - Obsidian style
        {
          selector: 'edge.highlighted',
          style: {
            'line-color': '#f093fb',
            'target-arrow-color': '#f093fb',
            'opacity': 0.9,
            'width': (ele) => {
              const weight = ele.data('weight')
              return Math.max(2, weight * 6)
            }
          }
        },

        // Node type specific styles
        {
          selector: 'node[type = "note"]',
          style: {
            'shape': 'round-rectangle'
          }
        },
        
        {
          selector: 'node[type = "link"]',
          style: {
            'shape': 'ellipse'
          }
        },
        
        {
          selector: 'node[type = "pdf"]',
          style: {
            'shape': 'rectangle',
            'background-color': '#c084fc'
          }
        }
      ],

      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
      },

      // Interaction settings
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false,
      selectionType: 'single',
      touchTapThreshold: 8,
      desktopTapThreshold: 4
    })

    setCy(cytoscapeInstance)
    cyRef.current = cytoscapeInstance

    // Add event listeners
    cytoscapeInstance.on('tap', 'node', (event) => {
      const node = event.target
      const nodeData = {
        id: node.data('id'),
        title: node.data('label'),
        content: node.data('content'),
        type: node.data('type'),
        keywords: node.data('keywords'),
        clickCount: node.data('clickCount'),
        sourceFile: node.data('sourceFile')
      }
      
      onNodeClick(nodeData)
    })

    // Cleanup
    return () => {
      if (cytoscapeInstance) {
        cytoscapeInstance.destroy()
      }
    }
  }, [graphData, onNodeClick])

  // Update selected node highlighting
  useEffect(() => {
    if (!cy || !selectedNode) return

    // Remove previous highlights
    cy.elements().removeClass('highlighted')
    
    // Highlight selected node and its connections
    const selectedCyNode = cy.getElementById(selectedNode.id)
    if (selectedCyNode.length > 0) {
      selectedCyNode.select()
      
      // Highlight connected edges
      const connectedEdges = selectedCyNode.connectedEdges()
      connectedEdges.addClass('highlighted')
      
      // Optionally highlight connected nodes
      const connectedNodes = connectedEdges.connectedNodes()
      connectedNodes.addClass('connected')
    }
  }, [cy, selectedNode])

  // Handle window resize
  useEffect(() => {
    if (!cy) return

    const handleResize = () => {
      cy.resize()
      cy.fit()
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [cy])

  if (!graphData) {
    return (
      <div className="graph-loading">
        <p>Loading graph...</p>
      </div>
    )
  }

  return (
    <div className="knowledge-graph-container">
      <div className="graph-controls">
        <button 
          onClick={() => cy && cy.fit()}
          className="control-button"
          title="Fit to view"
        >
          🔍 Fit
        </button>
        <button 
          onClick={() => cy && cy.center()}
          className="control-button"
          title="Center graph"
        >
          🎯 Center
        </button>
        <button 
          onClick={() => cy && cy.elements().layout({ name: 'cose', animate: true }).run()}
          className="control-button"
          title="Re-layout graph"
        >
          🔄 Layout
        </button>
      </div>
      
      <div 
        ref={containerRef}
        className="cytoscape-container"
        style={{ width: '100%', height: '100%' }}
      />
      
      <div className="graph-legend">
        <div className="legend-item">
          <div className="legend-node note"></div>
          <span>Notes</span>
        </div>
        <div className="legend-item">
          <div className="legend-node link"></div>
          <span>Links</span>
        </div>
        <div className="legend-item">
          <div className="legend-node pdf"></div>
          <span>PDFs</span>
        </div>
        <div className="legend-item">
          <div className="legend-edge normal"></div>
          <span>Similarity</span>
        </div>
        <div className="legend-item">
          <div className="legend-edge boosted"></div>
          <span>User Boosted</span>
        </div>
      </div>
    </div>
  )
}

export default KnowledgeGraph
