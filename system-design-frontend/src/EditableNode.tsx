import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useReactFlow } from 'reactflow';

interface EditableNodeProps {
    id: string;
    data: {
        label: string;
        icon?: React.ReactNode;
    };
    isConnectable: boolean;
    selected?: boolean;
}

const EditableNode: React.FC<EditableNodeProps> = ({ id, data, isConnectable, selected }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [label, setLabel] = useState(data.label);
    const inputRef = useRef<HTMLInputElement>(null);
    const { setNodes, deleteElements } = useReactFlow();

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
        <div className={`editable-node ${selected ? 'selected' : ''}`}>
            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="handle-target"
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
                        border: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        fontSize: '10px',
                        zIndex: 1000,
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                    }}
                >
                    ✕
                </button>
            )}

            <div className="node-content" onDoubleClick={onDoubleClick}>
                {data.icon && <span className="node-icon">{data.icon}</span>}
                {isEditing ? (
                    <input
                        ref={inputRef}
                        value={label}
                        onChange={handleChange}
                        onBlur={onBlur}
                        onKeyDown={onKeyDown}
                        className="node-input"
                    />
                ) : (
                    <span className="node-label">{label}</span>
                )}
            </div>

            <Handle
                type="source"
                position={Position.Bottom}
                isConnectable={isConnectable}
                className="handle-source"
            />
        </div>
    );
};

export default EditableNode;
