import React from 'react';
import { Sun, Moon, FileImage, RotateCcw } from 'lucide-react';
import './Header.css';

interface HeaderProps {
    theme: 'light' | 'dark';
    toggleTheme: () => void;
    onExport: () => void;
    onReset: () => void;
    backendUrl: string;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme, onExport, onReset, backendUrl }) => {
    return (
        <header className="app-header">
            <div className="header-left">
                <div className="logo-section">
                    <span className="eyebrow">Team Quirkless Code</span>
                    <h1>ArchFlow</h1>
                </div>
            </div>

            <div className="header-center">
                <span className="backend-badge">
                    <span className="pulse"></span>
                    API: {backendUrl}
                </span>
            </div>

            <div className="header-right">
                <button className="header-btn secondary" onClick={onReset} title="Reset Canvas">
                    <RotateCcw size={18} />
                    <span>Reset</span>
                </button>
                <button className="header-btn theme-toggle" onClick={toggleTheme} title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
                    {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
                </button>
                <button className="header-btn primary" onClick={onExport} title="Export as PNG">
                    <FileImage size={18} />
                    <span>Export</span>
                </button>
            </div>
        </header>
    );
};

export default Header;
