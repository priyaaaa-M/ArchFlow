import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useReactFlow, NodeResizer } from 'reactflow';
import { SHAPES } from '../components/ShapesTab';

interface ShapeNodeProps {
    id: string;
    data: {
        label: string;
        shapeId: string;
        color: string;
    };
    isConnectable: boolean;
    selected?: boolean;
}

const ShapeNode: React.FC<ShapeNodeProps> = ({ id, data, isConnectable, selected }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [label, setLabel] = useState(data.label);
    const inputRef = useRef<HTMLInputElement>(null);
    const { setNodes, deleteElements } = useReactFlow();

    const shapeItem = SHAPES.find((shape) => shape.id === data.shapeId);

    useEffect(() => {
        setLabel(data.label);
    }, [data.label]);

    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
            inputRef.current.select();
        }
    }, [isEditing]);

    const onDoubleClick = () => {
        setIsEditing(true);
    };

    const onBlur = () => {
        setIsEditing(false);
        updateNodeLabel();
    };

    const onKeyDown = (evt: React.KeyboardEvent) => {
        if (evt.key === 'Enter') {
            setIsEditing(false);
            updateNodeLabel();
        }
    };

    const updateNodeLabel = () => {
        setNodes((nodes) =>
            nodes.map((node) => {
                if (node.id === id) {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            label: label,
                        },
                    };
                }
                return node;
            })
        );
    };

    const handleChange = (evt: React.ChangeEvent<HTMLInputElement>) => {
        setLabel(evt.target.value);
    };

    const handleDelete = () => {
        deleteElements({ nodes: [{ id }] });
    };

    return (
        <div className={`shape-node ${selected ? 'selected' : ''}`}>
            <NodeResizer
                isVisible={selected}
                minWidth={80}
                minHeight={40}
                maxWidth={300}
                maxHeight={200}
                handleStyle={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                }}
            />

            {/* Delete Button */}
            {selected && (
                <button
                    onClick={handleDelete}
                    className="node-delete-button"
                    title="Delete node"
                    style={{
                        position: 'absolute',
                        top: '-8px',
                        right: '-8px',
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        background: '#ef4444',
                        color: 'white',
                        border: '2px solid white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        padding: 0,
                        zIndex: 1000,
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    }}
                >
                    ❌
                </button>
            )}

            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="custom-handle"
            />
            <Handle
                type="target"
                position={Position.Left}
                isConnectable={isConnectable}
                className="custom-handle"
            />

            <div className="shape-node-content" onDoubleClick={onDoubleClick}>
                {shapeItem && (
                    <div className="shape-node-shape" style={{ color: data.color }}>
                        {shapeItem.renderShape(80)}
                    </div>
                )}
                {isEditing ? (
                    <input
                        ref={inputRef}
                        value={label}
                        onChange={handleChange}
                        onBlur={onBlur}
                        onKeyDown={onKeyDown}
                        className="shape-node-input"
                    />
                ) : (
                    <span className="shape-node-label">{label}</span>
                )}
            </div>

            <Handle
                type="source"
                position={Position.Bottom}
                isConnectable={isConnectable}
                className="custom-handle"
            />
            <Handle
                type="source"
                position={Position.Right}
                isConnectable={isConnectable}
                className="custom-handle"
            />
        </div>
    );
};

export default ShapeNode;
