import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useReactFlow, NodeResizer } from 'reactflow';
import { ICONS } from '../components/IconsTab';

interface IconNodeProps {
    id: string;
    data: {
        label: string;
        iconId: string;
        gradient: string;
    };
    isConnectable: boolean;
    selected?: boolean;
}

const IconNode: React.FC<IconNodeProps> = ({ id, data, isConnectable, selected }) => {
    const [isEditing, setIsEditing] = useState(false);
    const theme = document.documentElement.getAttribute('data-theme');
    const [label, setLabel] = useState(data.label);
    const inputRef = useRef<HTMLInputElement>(null);
    const { setNodes, deleteElements } = useReactFlow();

    const iconItem = ICONS.find((icon) => icon.id === data.iconId);

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
        <div className={`icon-node ${selected ? 'selected' : ''}`} style={{ background: theme === 'dark' ? 'rgba(255,255,255,0.05)' : data.gradient, border: theme === 'dark' ? '1px solid var(--border-color)' : 'none' }}>
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

            <div className="icon-node-content" onDoubleClick={onDoubleClick}>
                {iconItem && <div className="icon-node-icon">{iconItem.icon}</div>}
                {isEditing ? (
                    <input
                        ref={inputRef}
                        value={label}
                        onChange={handleChange}
                        onBlur={onBlur}
                        onKeyDown={onKeyDown}
                        className="icon-node-input"
                    />
                ) : (
                    <span className="icon-node-label">{label}</span>
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

export default IconNode;
