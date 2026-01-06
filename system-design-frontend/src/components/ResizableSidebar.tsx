import React, { useState, useCallback, useEffect, useRef } from 'react';
import './ResizableSidebar.css';

interface ResizableSidebarProps {
    children: React.ReactNode;
    minWidth?: number;
    maxWidth?: number;
    defaultWidth?: number;
}

const ResizableSidebar: React.FC<ResizableSidebarProps> = ({
    children,
    minWidth = 200,
    maxWidth = 500,
    defaultWidth = 300
}) => {
    const [width, setWidth] = useState(() => {
        const saved = localStorage.getItem('sidebarWidth');
        return saved ? parseInt(saved, 10) : defaultWidth;
    });
    const [isResizing, setIsResizing] = useState(false);
    const sidebarRef = useRef<HTMLDivElement>(null);

    const startResizing = useCallback((e: React.MouseEvent) => {
        e.preventDefault();
        setIsResizing(true);
    }, []);

    const stopResizing = useCallback(() => {
        setIsResizing(false);
    }, []);

    const resize = useCallback(
        (e: MouseEvent) => {
            if (isResizing) {
                let newWidth = e.clientX;
                if (newWidth < 150) {
                    newWidth = 80; // Collapsed state
                } else if (newWidth < minWidth) {
                    newWidth = minWidth;
                } else if (newWidth > maxWidth) {
                    newWidth = maxWidth;
                }
                setWidth(newWidth);
            }
        },
        [isResizing, minWidth, maxWidth]
    );

    useEffect(() => {
        window.addEventListener('mousemove', resize);
        window.addEventListener('mouseup', stopResizing);
        return () => {
            window.removeEventListener('mousemove', resize);
            window.removeEventListener('mouseup', stopResizing);
        };
    }, [resize, stopResizing]);

    useEffect(() => {
        localStorage.setItem('sidebarWidth', width.toString());
    }, [width]);

    const isCollapsed = width <= 100;

    return (
        <div
            ref={sidebarRef}
            className={`resizable-sidebar ${isResizing ? 'resizing' : ''} ${isCollapsed ? 'collapsed' : ''}`}
            style={{ width: `${width}px` }}
        >
            <div className="sidebar-container">
                {React.Children.map(children, child => {
                    if (React.isValidElement(child)) {
                        return React.cloneElement(child as React.ReactElement<any>, { isCollapsed });
                    }
                    return child;
                })}
            </div>
            <div className="resize-handle" onMouseDown={startResizing} />
        </div>
    );
};

export default ResizableSidebar;
