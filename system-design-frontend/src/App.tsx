import React, { useState, useCallback } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  type Connection,
  type Edge,
  type Node,
  type ReactFlowInstance,
  Position,
  useViewport,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { Download, Pencil, Trash2 } from 'lucide-react';
import { FaUser, FaServer, FaCompass, FaDatabase, FaTasks } from 'react-icons/fa';
import { MdMap } from 'react-icons/md';
import Sidebar from './components/Sidebar';
import IconNode from './nodes/IconNode';
import ShapeNode from './nodes/ShapeNode';
import EditableNode from './EditableNode';
import './App.css';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const nodeTypes = {
  editableNode: EditableNode,
  iconNode: IconNode,
  shapeNode: ShapeNode,
};

const DrawingLayer = ({ paths, currentPath }: { paths: string[], currentPath: string }) => {
  const { x, y, zoom } = useViewport();

  if (paths.length === 0 && !currentPath) return null;

  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 20,
      }}
    >
      <g transform={`translate(${x}, ${y}) scale(${zoom})`}>
        {paths.map((p, i) => (
          <path key={i} d={p} fill="none" stroke="#ef4444" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        ))}
        {currentPath && (
          <path d={currentPath} fill="none" stroke="#ef4444" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        )}
      </g>
    </svg>
  );
};

type JobStatus = "idle" | "queued" | "running" | "completed" | "failed" | "timeout";

interface ComponentItem {
  id: string;
  name: string;
  type: string;
}

const MAX_POLLS = 150;

// Dagre Layout
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 50 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 75,
        y: nodeWithPosition.y - 25,
      },
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
    };
  });

  return { nodes: layoutedNodes, edges };
};

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);

  const [title, setTitle] = useState("");
  const [designType, setDesignType] = useState<"HLD" | "LLD">("HLD");
  const [urlsText, setUrlsText] = useState("");

  const [status, setStatus] = useState<JobStatus>("idle");
  const [components, setComponents] = useState<ComponentItem[]>([]);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [gifUrl, setGifUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Drawing states
  const [isDrawing, setIsDrawing] = useState(false);
  const [paths, setPaths] = useState<string[]>([]);
  const [currentPath, setCurrentPath] = useState("");

  const resetState = () => {
    setStatus("idle");
    setComponents([]);
    setNodes([]);
    setEdges([]);
    setImageUrl(null);
    setGifUrl(null);
    setError(null);
    setInfo("");
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true, type: 'smoothstep' }, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      if (!rfInstance) return;

      const typeData = event.dataTransfer.getData('application/reactflow');
      if (!typeData) return;

      try {
        const data = JSON.parse(typeData);
        const position = rfInstance.screenToFlowPosition({
          x: event.clientX,
          y: event.clientY,
        });

        const newNode: Node = {
          id: `${data.nodeType}-${Date.now()}`,
          type: data.nodeType,
          position,
          data: { label: data.label, ...data },
        };

        setNodes((nds) => nds.concat(newNode));
      } catch (err) {
        console.error("Drop failed", err);
      }
    },
    [rfInstance, setNodes]
  );

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
    } catch (err) {
      console.error("Download failed", err);
      // Fallback to direct link if fetch fails
      window.open(url, '_blank');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Please enter a system title.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setInfo("Initializing generation...");

    // Clear previous results
    setImageUrl(null);
    setGifUrl(null);
    setComponents([]);
    setNodes([]);
    setEdges([]);

    try {
      const urls = urlsText.split('\n').map(u => u.trim()).filter(Boolean);
      const startRes = await fetch(`${BACKEND_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, type: designType, urls: urls.length ? urls : undefined }),
      });

      if (!startRes.ok) throw new Error("Failed to start job");
      const startData = await startRes.json();
      const jid = startData.job_id;
      setStatus("queued");

      let finalStatus: JobStatus = "queued";
      for (let i = 0; i < MAX_POLLS; i++) {
        const sRes = await fetch(`${BACKEND_URL}/status/${jid}`);
        const sData = await sRes.json();
        finalStatus = sData.status;
        setStatus(finalStatus);
        if (finalStatus === "completed" || finalStatus === "failed") break;
        await new Promise(r => setTimeout(r, 2000));
      }

      if (finalStatus === "completed") {
        setInfo("Job completed! Fetching results...");
        const rRes = await fetch(`${BACKEND_URL}/result/${jid}`);
        const rData = await rRes.json();

        if (rData.png_url) setImageUrl(rData.png_url.startsWith('http') ? rData.png_url : `${BACKEND_URL}${rData.png_url}`);
        if (rData.gif_url) setGifUrl(rData.gif_url.startsWith('http') ? rData.gif_url : `${BACKEND_URL}${rData.gif_url}`);

        if (rData.components) {
          setComponents(rData.components.components || []);

          const getIcon = (name: string, type: string) => {
            const lowName = name.toLowerCase();
            const lowType = type.toLowerCase();
            if (lowName.includes('client') || lowName.includes('user') || lowType.includes('user')) return <FaUser />;
            if (lowName.includes('map') || lowType.includes('map')) return <MdMap />;
            if (lowName.includes('gps') || lowType.includes('gps')) return <FaCompass />;
            if (lowName.includes('master') || lowType.includes('master') || lowName.includes('server')) return <FaServer />;
            if (lowName.includes('db') || lowName.includes('database') || lowType.includes('database')) return <FaDatabase />;
            if (lowName.includes('queue') || lowName.includes('lobby') || lowType.includes('queue')) return <FaTasks />;
            return <FaServer />; // Default
          };

          const initialNodes = (rData.components.components || []).map((c: any) => ({
            id: c.id,
            type: 'editableNode',
            data: {
              label: c.name,
              type: c.type,
              icon: getIcon(c.name, c.type)
            },
            position: { x: 0, y: 0 }
          }));
          const initialEdges = (rData.components.relationships || []).map((rel: any, i: number) => ({
            id: `e${i}`,
            source: rel.source,
            target: rel.target,
            label: rel.label,
            animated: true,
            type: 'smoothstep'
          }));

          const { nodes: lNodes, edges: lEdges } = getLayoutedElements(initialNodes, initialEdges);
          setNodes(lNodes);
          setEdges(lEdges);
        }
        setInfo("Diagram generated successfully.");
      } else {
        setError(`Job ended with status: ${finalStatus}`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Team Quirkless Code</p>
          <h1>System Design Generator</h1>
          <p className="sub">Submit a topic, wait for generation, view the diagram, and see detected components.</p>
        </div>
        <div className="hero-actions">
          <span className="badge">Backend: {BACKEND_URL}</span>
          <button className="ghost" type="button" onClick={resetState}>Reset</button>
        </div>
      </header>

      <div className="top-button-row">
        <section className="panel button-panel">
          <div className="flex justify-between items-center mb-4">
            <h2>Generate a Diagram</h2>
          </div>
          <form className="form" onSubmit={handleSubmit}>
            <label className="field">
              <span>System Title</span>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Uber backend system"
              />
            </label>

            <label className="field">
              <span>Design Type</span>
              <div className="segmented">
                {["HLD", "LLD"].map((t) => (
                  <button
                    key={t}
                    type="button"
                    className={designType === t ? "segmented-item active" : "segmented-item"}
                    onClick={() => setDesignType(t as "HLD" | "LLD")}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </label>

            <label className="field">
              <span>Reference URLs (optional)</span>
              <textarea
                value={urlsText}
                onChange={(e) => setUrlsText(e.target.value)}
                placeholder="Paste URLs here (one per line)"
                rows={3}
              />
            </label>

            <div className="actions flex items-center gap-4">
              <button disabled={isLoading} type="submit" className="primary">
                {isLoading ? "Generating..." : "Generate Design"}
              </button>
              {status !== 'idle' && (
                <div className={`status-pill status-${status} whitespace-nowrap`}>
                  Status: {status.toUpperCase()}
                </div>
              )}
            </div>

            {error && <div className="callout error mt-4">{error}</div>}
            {info && <div className="callout info mt-4">{info}</div>}
          </form>
        </section>

        <section className="panel button-panel">
          <h2>Components Detected</h2>
          {status === 'idle' ? (
            <p className="muted mt-4">Start generating to see components.</p>
          ) : (
            <div className="component-grid mt-4" style={{ maxHeight: '250px', overflowY: 'auto' }}>
              {components.map((comp, i) => (
                <div key={i} className="component-card mb-2">
                  <div className="component-index">{i + 1}</div>
                  <div>
                    <p className="component-name text-sm">{comp.name}</p>
                    <p className="component-type text-xs">{comp.type}</p>
                  </div>
                </div>
              ))}
              {components.length === 0 && status === 'completed' && <p className="muted">No components detected.</p>}
            </div>
          )}
        </section>
      </div>

      <div className="layout">
        <aside className="sidebar">
          <Sidebar />
        </aside>

        <div className="main-column">
          <main className="canvas-frame">
            <ReactFlowProvider>
              <div
                className="canvas-section"
                onMouseDown={(e) => {
                  if (!isDrawing || !rfInstance) return;
                  const pos = rfInstance.screenToFlowPosition({ x: e.clientX, y: e.clientY });
                  setCurrentPath(`M ${pos.x} ${pos.y}`);
                }}
                onMouseMove={(e) => {
                  if (!isDrawing || !currentPath || !rfInstance) return;
                  const pos = rfInstance.screenToFlowPosition({ x: e.clientX, y: e.clientY });
                  setCurrentPath((prev) => `${prev} L ${pos.x} ${pos.y}`);
                }}
                onMouseUp={() => {
                  if (currentPath) {
                    setPaths((prev) => [...prev, currentPath]);
                    setCurrentPath("");
                  }
                }}
                style={{ position: 'relative' }}
              >
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  onConnect={onConnect}
                  onInit={setRfInstance}
                  onDragOver={onDragOver}
                  onDrop={onDrop}
                  nodeTypes={nodeTypes}
                  panOnDrag={!isDrawing}
                  panOnScroll={!isDrawing}
                  zoomOnScroll={!isDrawing}
                  fitView
                >
                  <Background />
                  <Controls />
                  <MiniMap />
                  <DrawingLayer paths={paths} currentPath={currentPath} />

                  <Panel position="top-left" style={{ display: 'flex', gap: '8px' }}>
                    <button
                      className={`panel-button ${isDrawing ? 'active' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsDrawing(!isDrawing);
                      }}
                      title={isDrawing ? "Stop Drawing" : "Start Drawing"}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid #ccc',
                        background: isDrawing ? '#e0f2fe' : 'white',
                        cursor: 'pointer',
                        boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
                      }}
                    >
                      <Pencil size={16} />
                      {isDrawing ? "Stop Drawing" : "Draw"}
                    </button>

                    {paths.length > 0 && (
                      <button
                        className="panel-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setPaths([]);
                          setCurrentPath("");
                        }}
                        title="Clear Drawings"
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          padding: '0.5rem',
                          borderRadius: '4px',
                          border: '1px solid #ccc',
                          background: 'white',
                          cursor: 'pointer',
                          boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                          color: '#ef4444'
                        }}
                      >
                        <Trash2 size={16} />
                        Clear
                      </button>
                    )}
                  </Panel>
                </ReactFlow>
              </div>
            </ReactFlowProvider>
          </main>

          <section className="panel">
            <h2>Results & Export</h2>
            {(imageUrl || gifUrl) ? (
              <div className="image-display-section mt-4">
                {imageUrl && (
                  <div className="image-container mb-4">
                    <p className="font-bold text-sm mb-1">Static Diagram</p>
                    <img src={imageUrl} className="generated-image" alt="Generated" />
                    <button
                      onClick={() => handleDownload(imageUrl, "diagram.png")}
                      className="button secondary small mt-2 inline-flex items-center gap-2"
                    >
                      <Download size={16} />
                      Download PNG
                    </button>
                  </div>
                )}
                {gifUrl && (
                  <div className="image-container">
                    <p className="font-bold text-sm mb-1">Animated Tour</p>
                    <img src={gifUrl} className="generated-image" alt="Tour" />
                    <button
                      onClick={() => handleDownload(gifUrl, "tour.gif")}
                      className="button secondary small mt-2 inline-flex items-center gap-2"
                    >
                      <Download size={16} />
                      Download GIF
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p className="muted mt-4 text-center">Images will appear here after generation.</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
