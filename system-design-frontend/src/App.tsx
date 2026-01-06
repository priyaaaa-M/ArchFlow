import React, { useState, useCallback, useEffect } from 'react';
import {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
  type Node,
  type ReactFlowInstance,
  Position,
  useViewport,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { toPng } from 'html-to-image';
import { FaUser, FaServer, FaCompass, FaDatabase, FaTasks } from 'react-icons/fa';
import { MdMap } from 'react-icons/md';
import Sidebar from './components/Sidebar';
import IconNode from './nodes/IconNode';
import ShapeNode from './nodes/ShapeNode';
import EditableNode from './EditableNode';
import Header from './components/Header';
import ResizableSidebar from './components/ResizableSidebar';
import Canvas from './components/Canvas';
import './App.css';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

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
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Drawing states
  const [isDrawing, setIsDrawing] = useState(false);
  const [paths, setPaths] = useState<string[]>([]);
  const [currentPath, setCurrentPath] = useState("");

  // Theme state
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as 'light' | 'dark') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  const resetState = () => {
    setStatus("idle");
    setComponents([]);
    setNodes([]);
    setEdges([]);
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

  const exportAsImage = async () => {
    const element = document.querySelector('.react-flow') as HTMLElement;
    if (!element) return;

    try {
      const dataUrl = await toPng(element, {
        backgroundColor: theme === 'dark' ? '#121212' : '#ffffff',
        cacheBust: true,
      });

      const link = document.createElement('a');
      link.download = `architecture-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error("Export failed", err);
    }
  };

  const triggerGeneration = async (overrideType?: "HLD" | "LLD") => {
    if (!title.trim()) {
      setError("Please enter a system title.");
      return;
    }

    const currentType = overrideType || designType;
    setIsLoading(true);
    setError(null);
    setInfo(`Initializing ${currentType} generation...`);

    setComponents([]);
    setNodes([]);
    setEdges([]);

    console.log(`Attempting to hit backend at: ${BACKEND_URL}/generate`);
    try {
      const urls = urlsText.split('\n').map(u => u.trim()).filter(Boolean);
      const startRes = await fetch(`${BACKEND_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        mode: 'cors',
        body: JSON.stringify({ title, type: currentType, urls: urls.length ? urls : undefined }),
      });

      console.log("Backend response status:", startRes.status);
      if (!startRes.ok) {
        const errText = await startRes.text();
        console.error("Backend error response:", errText);
        throw new Error(`Failed to start job: ${startRes.status} ${errText}`);
      }
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
        setInfo(`${currentType} Diagram generated successfully.`);
        const rRes = await fetch(`${BACKEND_URL}/result/${jid}`);
        const rData = await rRes.json();

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
            return <FaServer />;
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
      } else {
        setError(`Job ended with status: ${finalStatus}`);
      }
    } catch (err: any) {
      console.error("Generation error:", err);
      setError(err.message || "Failed to connect to backend");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    triggerGeneration();
  };

  return (
    <div className="app-shell">
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        onExport={exportAsImage}
        onReset={resetState}
        backendUrl={BACKEND_URL}
      />

      <div className="main-layout">
        <ResizableSidebar>
          <div className="sidebar-section">
            <h2>Workflow Controls</h2>
            <form className="form" onSubmit={handleSubmit}>
              <label className="field">
                <span>System Title</span>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Uber backend"
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
                      onClick={() => {
                        setDesignType(t as "HLD" | "LLD");
                        if (title.trim()) triggerGeneration(t as "HLD" | "LLD");
                      }}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </label>

              <label className="field">
                <span>Reference URLs</span>
                <textarea
                  value={urlsText}
                  onChange={(e) => setUrlsText(e.target.value)}
                  placeholder="One per line"
                  rows={2}
                />
              </label>

              <div className="actions">
                <button disabled={isLoading} type="submit" className="primary" style={{ width: '100%' }}>
                  {isLoading ? "Generating..." : `Generate ${designType}`}
                </button>
                {status !== 'idle' && (
                  <div className={`status-pill status-${status} mt-2 text-center`}>
                    {status.toUpperCase()}
                  </div>
                )}
              </div>

              {error && <div className="callout error mt-2">{error}</div>}
              {info && <div className="callout info mt-2">{info}</div>}
            </form>
          </div>

          <div className="sidebar-section" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <h2>Detected Components</h2>
            <div className="component-grid" style={{ overflowY: 'auto' }}>
              {components.map((comp, i) => (
                <div key={i} className="component-card mb-2">
                  <div className="component-index">{i + 1}</div>
                  <div>
                    <p className="component-name">{comp.name}</p>
                    <p className="component-type">{comp.type}</p>
                  </div>
                </div>
              ))}
              {components.length === 0 && <p className="muted text-sm">No components yet.</p>}
            </div>
          </div>

          <Sidebar />
        </ResizableSidebar>

        <main className="canvas-area">
          <ReactFlowProvider>
            <Canvas
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onInit={setRfInstance}
              onDragOver={onDragOver}
              onDrop={onDrop}
              nodeTypes={nodeTypes}
              isDrawing={isDrawing}
              setIsDrawing={setIsDrawing}
              paths={paths}
              setPaths={setPaths}
              currentPath={currentPath}
              setCurrentPath={setCurrentPath}
              rfInstance={rfInstance}
              theme={theme}
              DrawingLayer={DrawingLayer}
            />
          </ReactFlowProvider>
        </main>
      </div>
    </div>
  );
}

export default App;
