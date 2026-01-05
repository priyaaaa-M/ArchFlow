import React, { useState } from 'react';
import IconsTab from './IconsTab';
import ShapesTab from './ShapesTab';
import './Sidebar.css';

type TabType = 'icons' | 'shapes';

const Sidebar: React.FC = () => {
    const [activeTab, setActiveTab] = useState<TabType>('icons');

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h3>Component Palette</h3>
                <p className="sidebar-description">Drag items onto the canvas</p>
            </div>

            <div className="sidebar-tabs">
                <button
                    className={`sidebar-tab ${activeTab === 'icons' ? 'active' : ''}`}
                    onClick={() => setActiveTab('icons')}
                >
                    Icons
                </button>
                <button
                    className={`sidebar-tab ${activeTab === 'shapes' ? 'active' : ''}`}
                    onClick={() => setActiveTab('shapes')}
                >
                    Shapes
                </button>
            </div>

            <div className="sidebar-content">
                {activeTab === 'icons' ? <IconsTab /> : <ShapesTab />}
            </div>
        </div>
    );
};

export default Sidebar;
