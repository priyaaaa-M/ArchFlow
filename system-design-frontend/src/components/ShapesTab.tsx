import React from 'react';

interface ShapeItem {
    id: string;
    label: string;
    renderShape: (size: number) => React.ReactNode;
    color: string;
}

const SHAPES: ShapeItem[] = [
    {
        id: 'circle',
        label: 'Circle',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="currentColor" />
            </svg>
        ),
        color: '#3b82f6',
    },
    {
        id: 'triangle',
        label: 'Triangle',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <polygon points="50,10 90,90 10,90" fill="currentColor" />
            </svg>
        ),
        color: '#8b5cf6',
    },
    {
        id: 'square',
        label: 'Square',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <rect x="10" y="10" width="80" height="80" fill="currentColor" />
            </svg>
        ),
        color: '#10b981',
    },
    {
        id: 'diamond',
        label: 'Diamond',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <polygon points="50,10 90,50 50,90 10,50" fill="currentColor" />
            </svg>
        ),
        color: '#f59e0b',
    },
    {
        id: 'hexagon',
        label: 'Hexagon',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <polygon points="50,5 90,27.5 90,72.5 50,95 10,72.5 10,27.5" fill="currentColor" />
            </svg>
        ),
        color: '#ec4899',
    },
    {
        id: 'line',
        label: 'Line',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <line x1="10" y1="50" x2="90" y2="50" stroke="currentColor" strokeWidth="6" />
            </svg>
        ),
        color: '#64748b',
    },
    {
        id: 'arrow',
        label: 'Arrow',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <line x1="10" y1="50" x2="75" y2="50" stroke="currentColor" strokeWidth="6" />
                <polygon points="75,35 90,50 75,65" fill="currentColor" />
            </svg>
        ),
        color: '#06b6d4',
    },
    {
        id: 'annotation',
        label: 'Annotation',
        renderShape: (size) => (
            <svg width={size} height={size} viewBox="0 0 100 100">
                <path d="M10,90 L30,90 L90,30 L70,10 L10,70 Z" fill="none" stroke="currentColor" strokeWidth="5" />
                <line x1="60" y1="20" x2="80" y2="40" stroke="currentColor" strokeWidth="5" />
                <rect x="10" y="80" width="20" height="10" fill="currentColor" />
            </svg>
        ),
        color: '#fbbf24',
    },
];

interface ShapesTabProps {
    isExpanded?: boolean;
}

const ShapesTab: React.FC<ShapesTabProps> = ({ isExpanded }) => {
    const onDragStart = (event: React.DragEvent, shapeItem: ShapeItem) => {
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData(
            'application/reactflow',
            JSON.stringify({
                nodeType: shapeItem.id === 'annotation' ? 'editableNode' : 'shapeNode',
                shapeId: shapeItem.id,
                label: shapeItem.id === 'annotation' ? 'Write here...' : shapeItem.label,
                color: shapeItem.color,
            })
        );
    };

    const displayedShapes = isExpanded ? SHAPES : SHAPES.slice(0, 4);

    return (
        <div className="shapes-tab">
            <div className={`shape-grid ${!isExpanded ? 'compact' : ''}`}>
                {displayedShapes.map((shapeItem) => (
                    <div
                        key={shapeItem.id}
                        className={`shape-item ${!isExpanded ? 'compact' : ''}`}
                        draggable
                        onDragStart={(e) => onDragStart(e, shapeItem)}
                        title={shapeItem.label}
                    >
                        <div className="shape-wrapper" style={{ color: shapeItem.color }}>
                            {shapeItem.renderShape(isExpanded ? 60 : 32)}
                        </div>
                        <span className="shape-label">{shapeItem.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ShapesTab;
export { SHAPES };
