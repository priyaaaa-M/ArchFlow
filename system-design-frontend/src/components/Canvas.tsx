import React, { useRef, useEffect, useCallback } from 'react';
import ReactFlow, {
    Controls,
    MiniMap,
    Panel,
    useViewport,
    type ReactFlowInstance,
    type Node,
    type Edge,
    type Connection,
} from 'reactflow';
import { Pencil, Trash2 } from 'lucide-react';

interface CanvasProps {
    nodes: Node[];
    edges: Edge[];
    onNodesChange: any;
    onEdgesChange: any;
    onConnect: (params: Connection) => void;
    onInit: (instance: ReactFlowInstance) => void;
    onDragOver: (event: React.DragEvent) => void;
    onDrop: (event: React.DragEvent) => void;
    nodeTypes: any;
    isDrawing: boolean;
    setIsDrawing: (val: boolean) => void;
    paths: string[];
    setPaths: React.Dispatch<React.SetStateAction<string[]>>;
    currentPath: string;
    setCurrentPath: React.Dispatch<React.SetStateAction<string>>;
    rfInstance: ReactFlowInstance | null;
    theme: 'light' | 'dark';
    DrawingLayer: React.FC<{ paths: string[], currentPath: string }>;
}

const GridOverlay = ({ theme }: { theme: 'light' | 'dark' }) => {
    const { x, y, zoom } = useViewport();
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const drawGrid = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number, offsetX: number, offsetY: number, scale: number) => {
        ctx.clearRect(0, 0, width, height);

        const gridSize = 40 * scale;
        const gridColor = theme === 'dark' ? '#333333' : '#e0e0e0';

        ctx.beginPath();
        ctx.strokeStyle = gridColor;
        ctx.lineWidth = 1;

        // Calculate starting positions based on offset and scale
        const startX = offsetX % gridSize;
        const startY = offsetY % gridSize;

        // Vertical lines
        for (let xPos = startX; xPos < width; xPos += gridSize) {
            ctx.moveTo(xPos, 0);
            ctx.lineTo(xPos, height);
        }

        // Horizontal lines
        for (let yPos = startY; yPos < height; yPos += gridSize) {
            ctx.moveTo(0, yPos);
            ctx.lineTo(width, yPos);
        }

        ctx.stroke();
    }, [theme]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const resizeObserver = new ResizeObserver((entries) => {
            for (const entry of entries) {
                const { width, height } = entry.contentRect;
                canvas.width = width;
                canvas.height = height;
                drawGrid(ctx, width, height, x, y, zoom);
            }
        });

        resizeObserver.observe(canvas.parentElement!);

        drawGrid(ctx, canvas.width, canvas.height, x, y, zoom);

        return () => resizeObserver.disconnect();
    }, [x, y, zoom, drawGrid]);

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                pointerEvents: 'none',
                zIndex: -1,
            }}
        />
    );
};

const Canvas: React.FC<CanvasProps> = ({
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onInit,
    onDragOver,
    onDrop,
    nodeTypes,
    isDrawing,
    setIsDrawing,
    paths,
    setPaths,
    currentPath,
    setCurrentPath,
    rfInstance,
    theme,
    DrawingLayer,
}) => {
    return (
        <div
            className="canvas-section"
            style={{ width: '100%', height: '100%', position: 'relative' }}
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
        >
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onInit={onInit}
                onDragOver={onDragOver}
                onDrop={onDrop}
                nodeTypes={nodeTypes}
                panOnDrag={!isDrawing}
                panOnScroll={!isDrawing}
                zoomOnScroll={!isDrawing}
                fitView
            >
                <GridOverlay theme={theme} />
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
                        style={{
                            background: isDrawing ? 'var(--accent-color)' : 'var(--bg-secondary)',
                            color: isDrawing ? 'white' : 'var(--text-primary)',
                            border: '1px solid var(--border-color)',
                            padding: '8px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                        title={isDrawing ? "Stop Drawing" : "Start Drawing"}
                    >
                        <Pencil size={18} />
                    </button>
                    {paths.length > 0 && (
                        <button
                            className="panel-button"
                            onClick={(e) => {
                                e.stopPropagation();
                                setPaths([]);
                                setCurrentPath("");
                            }}
                            style={{
                                background: 'var(--bg-secondary)',
                                color: '#ef4444',
                                border: '1px solid var(--border-color)',
                                padding: '8px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                            title="Clear Drawings"
                        >
                            <Trash2 size={18} />
                        </button>
                    )}
                </Panel>
            </ReactFlow>
        </div>
    );
};

export default Canvas;
