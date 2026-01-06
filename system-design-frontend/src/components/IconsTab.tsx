import React from 'react';
import {
    FaServer,
    FaDatabase,
    FaCloud,
    FaUserAlt,
    FaNetworkWired,
    FaShieldAlt,
    FaCogs,
    FaMemory,
    FaHdd,
    FaLayerGroup,
} from 'react-icons/fa';
import {
    MdStorage,
    MdApi,
    MdQueue,
    MdSecurity,
    MdDns,
    MdMonitor,
    MdCloudQueue,
} from 'react-icons/md';
import {
    SiKubernetes,
    SiRabbitmq,
    SiRedis,
    SiElasticsearch,
    SiNginx,
} from 'react-icons/si';
import { BiGitBranch } from 'react-icons/bi';
import { AiOutlineContainer } from 'react-icons/ai';

interface IconItem {
    id: string;
    label: string;
    icon: React.ReactNode;
    gradient: string;
}

const ICONS: IconItem[] = [
    {
        id: 'server',
        label: 'Server',
        icon: <FaServer size={24} />,
        gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    },
    {
        id: 'database',
        label: 'Database',
        icon: <FaDatabase size={32} />,
        gradient: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
    },
    {
        id: 'api',
        label: 'API',
        icon: <MdApi size={32} />,
        gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
    },
    {
        id: 'queue',
        label: 'Queue',
        icon: <MdQueue size={32} />,
        gradient: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
    },
    {
        id: 'cache',
        label: 'Cache',
        icon: <SiRedis size={32} />,
        gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
    {
        id: 'microservice',
        label: 'Microservice',
        icon: <FaCogs size={32} />,
        gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
    },
    {
        id: 'user',
        label: 'User',
        icon: <FaUserAlt size={32} />,
        gradient: 'linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)',
    },
    {
        id: 'loadbalancer',
        label: 'Load Balancer',
        icon: <FaNetworkWired size={32} />,
        gradient: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
    },
    {
        id: 'cloud',
        label: 'Cloud',
        icon: <FaCloud size={32} />,
        gradient: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
    },
    {
        id: 'storage',
        label: 'Storage',
        icon: <MdStorage size={32} />,
        gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
        id: 'cdn',
        label: 'CDN',
        icon: <MdCloudQueue size={32} />,
        gradient: 'linear-gradient(135deg, #84cc16 0%, #65a30d 100%)',
    },
    {
        id: 'auth',
        label: 'Authentication',
        icon: <MdSecurity size={32} />,
        gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    },
    {
        id: 'gateway',
        label: 'Gateway',
        icon: <SiNginx size={32} />,
        gradient: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    },
    {
        id: 'worker',
        label: 'Worker',
        icon: <FaMemory size={32} />,
        gradient: 'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)',
    },
    {
        id: 'monitor',
        label: 'Monitor',
        icon: <MdMonitor size={32} />,
        gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
    },
    {
        id: 'network',
        label: 'Network',
        icon: <BiGitBranch size={32} />,
        gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
    },
    {
        id: 'firewall',
        label: 'Firewall',
        icon: <FaShieldAlt size={32} />,
        gradient: 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)',
    },
    {
        id: 'container',
        label: 'Container',
        icon: <AiOutlineContainer size={32} />,
        gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    },
    {
        id: 'kubernetes',
        label: 'Kubernetes',
        icon: <SiKubernetes size={32} />,
        gradient: 'linear-gradient(135deg, #326ce5 0%, #1e40af 100%)',
    },
    {
        id: 'messagebroker',
        label: 'Message Broker',
        icon: <SiRabbitmq size={32} />,
        gradient: 'linear-gradient(135deg, #ff6600 0%, #ea580c 100%)',
    },
    {
        id: 'search',
        label: 'Search Engine',
        icon: <SiElasticsearch size={32} />,
        gradient: 'linear-gradient(135deg, #005571 0%, #0891b2 100%)',
    },
    {
        id: 'diskstore',
        label: 'Disk Storage',
        icon: <FaHdd size={32} />,
        gradient: 'linear-gradient(135deg, #78716c 0%, #57534e 100%)',
    },
    {
        id: 'layer',
        label: 'Layer Service',
        icon: <FaLayerGroup size={32} />,
        gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
        id: 'dns',
        label: 'DNS',
        icon: <MdDns size={32} />,
        gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    },
];

interface IconsTabProps {
    isExpanded?: boolean;
}

const IconsTab: React.FC<IconsTabProps> = ({ isExpanded }) => {
    const onDragStart = (event: React.DragEvent, iconItem: IconItem) => {
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData(
            'application/reactflow',
            JSON.stringify({
                nodeType: 'iconNode',
                iconId: iconItem.id,
                label: iconItem.label,
                gradient: iconItem.gradient,
            })
        );
    };

    const displayedIcons = isExpanded ? ICONS : ICONS.slice(0, 6);

    return (
        <div className="icons-tab">
            <div className={`icon-grid ${!isExpanded ? 'compact' : ''}`}>
                {displayedIcons.map((iconItem) => (
                    <div
                        key={iconItem.id}
                        className={`icon-item ${!isExpanded ? 'compact' : ''}`}
                        draggable
                        onDragStart={(e) => onDragStart(e, iconItem)}
                        style={{ background: iconItem.gradient }}
                        title={iconItem.label}
                    >
                        <div className="icon-wrapper">{iconItem.icon}</div>
                        <span className="icon-label">{iconItem.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default IconsTab;
export { ICONS };
