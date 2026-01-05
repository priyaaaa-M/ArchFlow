from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

# Add Graphviz to PATH on Windows
if os.name == 'nt':  # Windows
    graphviz_path = r"C:\Program Files\Graphviz\bin"
    if Path(graphviz_path).exists() and graphviz_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] += f";{graphviz_path}"
        logger.info(f"Added Graphviz to PATH: {graphviz_path}")

# Import diagrams library components
from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import Users, Client
from diagrams.onprem.network import Nginx, Internet
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL, MongoDB, Cassandra
from diagrams.onprem.inmemory import Redis, Memcached
from diagrams.onprem.queue import Kafka, RabbitMQ
from diagrams.onprem.analytics import Spark
from diagrams.aws.storage import S3
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.compute import Lambda, ECS
from diagrams.aws.network import ELB, CloudFront, APIGateway
from diagrams.elastic.elasticsearch import Elasticsearch
from diagrams.gcp.compute import GKE
from diagrams.azure.compute import AKS


def get_icon_for_component(component_type: str, component_name: str):
    """
    Smart icon selection based on component type and name
    """
    name_lower = component_name.lower()
    
    # Client components
    if component_type == "client":
        if any(word in name_lower for word in ["user", "customer", "mobile", "web"]):
            return Users
        return Client
    
    # Gateway components  
    elif component_type == "gateway":
        if any(word in name_lower for word in ["api", "gateway"]):
            return APIGateway
        if any(word in name_lower for word in ["load", "balancer", "nginx"]):
            return ELB
        if any(word in name_lower for word in ["cdn", "cloudfront"]):
            return CloudFront
        return Nginx
    
    # Service components
    elif component_type in ["service", "core_service"]:
        if any(word in name_lower for word in ["lambda", "function"]):
            return Lambda
        if any(word in name_lower for word in ["container", "ecs"]):
            return ECS
        return Server
    
    # Database components
    elif component_type == "database":
        if any(word in name_lower for word in ["postgres", "postgresql"]):
            return PostgreSQL
        if any(word in name_lower for word in ["mongo", "mongodb"]):
            return MongoDB
        if any(word in name_lower for word in ["cassandra", "scylla"]):
            return Cassandra
        if any(word in name_lower for word in ["rds", "aurora"]):
            return RDS
        if any(word in name_lower for word in ["dynamo", "dynamodb"]):
            return Dynamodb
        if any(word in name_lower for word in ["bigquery"]):
            return PostgreSQL  # Use PostgreSQL as fallback for BigQuery
        return PostgreSQL  # Default database icon
    
    # Cache components
    elif component_type == "cache":
        if any(word in name_lower for word in ["redis"]):
            return Redis
        if any(word in name_lower for word in ["memcache"]):
            return Memcached
        return Redis  # Default cache icon
    
    # Queue/Streaming components
    elif component_type in ["queue", "streaming"]:
        if any(word in name_lower for word in ["kafka"]):
            return Kafka
        if any(word in name_lower for word in ["rabbit", "rabbitmq"]):
            return RabbitMQ
        return Kafka  # Default queue icon
    
    # Infrastructure components
    elif component_type == "infra":
        if any(word in name_lower for word in ["kubernetes", "k8s", "gke"]):
            return GKE
        if any(word in name_lower for word in ["aks"]):
            return AKS
        if any(word in name_lower for word in ["spark", "analytics"]):
            return Spark
        if any(word in name_lower for word in ["storage", "s3"]):
            return S3
        return Server  # Default infra icon
    
    # External services
    elif component_type == "external_service":
        if any(word in name_lower for word in ["s3", "storage"]):
            return S3
        if any(word in name_lower for word in ["elasticsearch", "elastic"]):
            return Elasticsearch
        return Internet  # Default external service icon
    
    # Edge components
    elif component_type == "edge":
        return CloudFront
    
    # Default fallback
    return Server


def group_components_into_clusters(components: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group components into logical clusters for better diagram organization
    """
    clusters = {
        "Client Layer": [],
        "Gateway Layer": [],
        "Service Layer": [],
        "Data Layer": [],
        "Infrastructure": [],
        "External Services": []
    }
    
    for component in components:
        comp_type = component.get("type", "")
        
        if comp_type == "client":
            clusters["Client Layer"].append(component)
        elif comp_type == "gateway":
            clusters["Gateway Layer"].append(component)
        elif comp_type in ["service", "core_service"]:
            clusters["Service Layer"].append(component)
        elif comp_type in ["database", "cache", "queue", "streaming"]:
            clusters["Data Layer"].append(component)
        elif comp_type == "infra":
            clusters["Infrastructure"].append(component)
        elif comp_type in ["external_service", "edge"]:
            clusters["External Services"].append(component)
        else:
            # Default to service layer
            clusters["Service Layer"].append(component)
    
    # Remove empty clusters
    return {k: v for k, v in clusters.items() if v}


def generate_diagram_with_diagrams(structure: Dict[str, Any], job_id: str) -> str:
    """
    Generate beautiful PNG diagram using diagrams library
    
    Args:
        structure: JSON with components and relationships
        job_id: Job identifier for filename
        
    Returns:
        Path to generated PNG file
    """
    try:
        components = structure.get("components", [])
        relationships = structure.get("relationships", [])
        
        if not components:
            logger.warning("No components found in structure")
            return ""
        
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        filename = f"{job_id}_system_design"
        png_path = output_dir / f"{filename}.png"
        
        logger.info(f"Generating diagram with {len(components)} components and {len(relationships)} relationships")
        
        # Group components into clusters
        clusters = group_components_into_clusters(components)
        
        # Create diagram
        with Diagram(
            "System Architecture",
            show=False,
            direction="TB",  # Top to Bottom
            filename=str(output_dir / filename),
            outformat="png",
            graph_attr={
                "fontsize": "16",
                "bgcolor": "white",
                "pad": "1.0",
                "splines": "curved"
            }
        ):
            # Store component instances for relationship mapping
            component_instances = {}
            
            # Create clusters and components
            for cluster_name, cluster_components in clusters.items():
                if not cluster_components:
                    continue
                    
                with Cluster(cluster_name):
                    for component in cluster_components:
                        comp_id = component.get("id", "")
                        comp_name = component.get("name", "Unknown")
                        comp_type = component.get("type", "service")
                        
                        # Get appropriate icon
                        icon_class = get_icon_for_component(comp_type, comp_name)
                        
                        # Create component instance
                        instance = icon_class(comp_name)
                        component_instances[comp_id] = instance
            
            # Create relationships
            for relationship in relationships:
                source_id = relationship.get("source", "")
                target_id = relationship.get("target", "")
                label = relationship.get("label", "")
                
                source_instance = component_instances.get(source_id)
                target_instance = component_instances.get(target_id)
                
                if source_instance and target_instance:
                    if label:
                        source_instance >> Edge(label=label) >> target_instance
                    else:
                        source_instance >> target_instance
                else:
                    logger.warning(f"Could not find instances for relationship: {source_id} -> {target_id}")
        
        logger.info(f"Diagram generated successfully: {png_path}")
        return str(png_path)
        
    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        return ""


def to_mermaid(structure: Dict[str, Any]) -> str:
    """
    Legacy function - now redirects to diagrams generation
    Keep for backward compatibility but log deprecation
    """
    logger.warning("to_mermaid() is deprecated. Use generate_diagram_with_diagrams() instead.")
    
    # For backward compatibility, return a simple mermaid representation
    components = structure.get("components", [])
    relationships = structure.get("relationships", [])
    
    mermaid_lines = ["flowchart TD"]
    
    # Add components
    for component in components:
        comp_id = component.get("id", "")
        comp_name = component.get("name", "Unknown")
        mermaid_lines.append(f'  {comp_id}["{comp_name}"]')
    
    # Add relationships
    for relationship in relationships:
        source = relationship.get("source", "")
        target = relationship.get("target", "")
        label = relationship.get("label", "")
        
        if label:
            mermaid_lines.append(f'  {source} -->|{label}| {target}')
        else:
            mermaid_lines.append(f'  {source} --> {target}')
    
    return "\n".join(mermaid_lines)