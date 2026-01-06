import React, { useState } from 'react';
import IconsTab from './IconsTab';
import ShapesTab from './ShapesTab';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';
import './Sidebar.css';

type TabType = 'icons' | 'shapes';

interface SidebarProps {
    isCollapsed?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed }) => {
    const [activeTab, setActiveTab] = useState<TabType>('icons');
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className={`sidebar ${isCollapsed ? 'collapsed' : ''} ${isExpanded ? 'expanded' : 'compact'}`}>
            {!isCollapsed && (
                <div className="sidebar-header-accordion" onClick={() => setIsExpanded(!isExpanded)}>
                    <div className="header-main">
                        <h3>Palette</h3>
                        <div className="expand-toggle">
                            <span>{isExpanded ? 'See less' : 'See more'}</span>
                            {isExpanded ? <FaChevronUp size={12} /> : <FaChevronDown size={12} />}
                        </div>
                    </div>
                    {!isExpanded && <p className="sidebar-description">Drag to canvas</p>}
                </div>
            )}

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
                {activeTab === 'icons' ? (
                    <IconsTab isExpanded={isExpanded} />
                ) : (
                    <ShapesTab isExpanded={isExpanded} />
                )}
            </div>
        </div>
    );
};

export default Sidebar;
