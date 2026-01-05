from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
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
import imageio
import base64
import io
import requests
from PIL import Image
import numpy as np


# ============================================================================
# BYTEBYTEGO-STYLE VISUAL CONSTANTS
# ============================================================================

class CommunicationPattern:
    """ByteByteGo-style communication patterns"""
    SYNC_REQUEST = "solid"      # HTTP/gRPC calls
    ASYNC_EVENT = "dashed"      # Message queues, pub/sub
    DATA_FLOW = "bold"          # Bulk data transfer
    READ_OPERATION = "dotted"   # Read-only queries
    
class EdgeColors:
    """ByteByteGo-style color coding"""
    READ = "#3b82f6"      # Blue - read operations
    WRITE = "#ef4444"     # Red - write operations
    ASYNC = "#8b5cf6"     # Purple - async/events
    SYNC = "#10b981"      # Green - sync calls
    DATA = "#f59e0b"      # Orange - data flow
    DEFAULT = "#6b7280"   # Gray - default


def validate_structure(structure: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate the input structure for common issues
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    components = structure.get("components", [])
    relationships = structure.get("relationships", [])
    
    if not components:
        errors.append("No components found in structure")
        return False, errors
    
    # Check for duplicate component IDs
    component_ids = [c.get("id", "") for c in components]
    duplicates = [id for id in component_ids if component_ids.count(id) > 1]
    if duplicates:
        errors.append(f"Duplicate component IDs found: {set(duplicates)}")
    
    # Validate component fields
    valid_types = {
        "client", "gateway", "service", "core_service", "database", 
        "cache", "queue", "streaming", "external_service", "edge", "infra"
    }
    
    for idx, component in enumerate(components):
        if not component.get("id"):
            errors.append(f"Component at index {idx} missing 'id' field")
        if not component.get("name"):
            errors.append(f"Component at index {idx} missing 'name' field")
        if not component.get("type"):
            errors.append(f"Component at index {idx} missing 'type' field")
        elif component.get("type") not in valid_types:
            errors.append(f"Component '{component.get('id')}' has invalid type: {component.get('type')}")
    
    # Validate relationships reference existing components
    component_id_set = set(component_ids)
    for idx, rel in enumerate(relationships):
        source = rel.get("source")
        target = rel.get("target")
        
        if not source:
            errors.append(f"Relationship at index {idx} missing 'source' field")
        elif source not in component_id_set:
            errors.append(f"Relationship references non-existent source: {source}")
            
        if not target:
            errors.append(f"Relationship at index {idx} missing 'target' field")
        elif target not in component_id_set:
            errors.append(f"Relationship references non-existent target: {target}")
        
        if source == target:
            errors.append(f"Self-referencing relationship found: {source}")
    
    # Warn about orphaned components
    connected_components = set()
    for rel in relationships:
        connected_components.add(rel.get("source"))
        connected_components.add(rel.get("target"))
    
    orphaned = component_id_set - connected_components
    if orphaned:
        logger.warning(f"Orphaned components (no relationships): {orphaned}")
    
    return len(errors) == 0, errors


def get_icon_for_component(component_type: str, component_name: str):
    """
    Enhanced icon selection with better pattern matching
    """
    name_lower = component_name.lower()
    type_lower = component_type.lower()
    
    # Client components
    if type_lower == "client":
        if any(word in name_lower for word in ["user", "customer", "mobile", "web", "browser"]):
            return Users
        return Client
    
    # Gateway components  
    elif type_lower == "gateway":
        if any(word in name_lower for word in ["api", "gateway", "apigw"]):
            return APIGateway
        if any(word in name_lower for word in ["load", "balancer", "nginx", "elb", "alb"]):
            return ELB
        if any(word in name_lower for word in ["cdn", "cloudfront", "edge"]):
            return CloudFront
        return Nginx
    
    # Service components - distinguish core from regular
    elif type_lower in ["service", "core_service"]:
        if any(word in name_lower for word in ["lambda", "function", "serverless"]):
            return Lambda
        if any(word in name_lower for word in ["container", "ecs", "docker"]):
            return ECS
        if any(word in name_lower for word in ["kubernetes", "k8s"]):
            return GKE
        return Server
    
    # Database components - enhanced matching
    elif type_lower == "database":
        if any(word in name_lower for word in ["postgres", "postgresql", "pg"]):
            return PostgreSQL
        if any(word in name_lower for word in ["mongo", "mongodb"]):
            return MongoDB
        if any(word in name_lower for word in ["cassandra", "scylla"]):
            return Cassandra
        if any(word in name_lower for word in ["rds", "aurora", "relational"]):
            return RDS
        if any(word in name_lower for word in ["dynamo", "dynamodb"]):
            return Dynamodb
        if any(word in name_lower for word in ["bigquery", "warehouse"]):
            return PostgreSQL
        if any(word in name_lower for word in ["sql", "relational"]):
            return PostgreSQL
        if any(word in name_lower for word in ["nosql", "document"]):
            return MongoDB
        return PostgreSQL
    
    # Cache components
    elif type_lower == "cache":
        if any(word in name_lower for word in ["redis", "elasticache"]):
            return Redis
        if any(word in name_lower for word in ["memcache", "memcached"]):
            return Memcached
        return Redis
    
    # Queue/Streaming components
    elif type_lower in ["queue", "streaming"]:
        if any(word in name_lower for word in ["kafka", "stream"]):
            return Kafka
        if any(word in name_lower for word in ["rabbit", "rabbitmq", "amqp"]):
            return RabbitMQ
        if any(word in name_lower for word in ["sqs", "queue"]):
            return RabbitMQ
        return Kafka
    
    # Infrastructure components
    elif type_lower == "infra":
        if any(word in name_lower for word in ["kubernetes", "k8s", "gke"]):
            return GKE
        if any(word in name_lower for word in ["aks", "azure"]):
            return AKS
        if any(word in name_lower for word in ["spark", "analytics", "hadoop"]):
            return Spark
        if any(word in name_lower for word in ["storage", "s3", "blob"]):
            return S3
        return Server
    
    # External services
    elif type_lower == "external_service":
        if any(word in name_lower for word in ["s3", "storage", "blob"]):
            return S3
        if any(word in name_lower for word in ["elasticsearch", "elastic", "search"]):
            return Elasticsearch
        if any(word in name_lower for word in ["cdn", "cloudfront"]):
            return CloudFront
        return Internet
    
    # Edge components
    elif type_lower == "edge":
        return CloudFront
    
    # Default fallback
    logger.warning(f"Using default Server icon for unknown type: {component_type}")
    return Server


def categorize_relationship_bytebytego_style(label: str) -> Dict[str, Any]:
    """
    ByteByteGo-style relationship categorization with visual attributes
    
    Returns dict with: {style, color, pattern}
    """
    label_lower = label.lower() if label else ""
    
    # Async operations (message queues, events, pub/sub)
    if any(word in label_lower for word in [
        "publish", "emit", "send", "queue", "event", "message", 
        "notify", "subscribe", "kafka", "rabbitmq", "async"
    ]):
        return {
            "style": CommunicationPattern.ASYNC_EVENT,
            "color": EdgeColors.ASYNC,
            "pattern": "async"
        }
    
    # Read operations
    elif any(word in label_lower for word in [
        "read", "query", "fetch", "get", "retrieve", "select", "search"
    ]):
        return {
            "style": CommunicationPattern.READ_OPERATION,
            "color": EdgeColors.READ,
            "pattern": "read"
        }
    
    # Write operations
    elif any(word in label_lower for word in [
        "write", "store", "save", "update", "insert", "delete", "persist"
    ]):
        return {
            "style": CommunicationPattern.SYNC_REQUEST,
            "color": EdgeColors.WRITE,
            "pattern": "write"
        }
    
    # Data flow (ETL, streaming, replication)
    elif any(word in label_lower for word in [
        "stream", "replicate", "sync", "backup", "transfer", "etl", "flow"
    ]):
        return {
            "style": CommunicationPattern.DATA_FLOW,
            "color": EdgeColors.DATA,
            "pattern": "data"
        }
    
    # Sync calls (HTTP, gRPC, API calls)
    elif any(word in label_lower for word in [
        "call", "request", "invoke", "http", "grpc", "api", "rpc"
    ]):
        return {
            "style": CommunicationPattern.SYNC_REQUEST,
            "color": EdgeColors.SYNC,
            "pattern": "sync"
        }
    
    # Default - assume synchronous
    else:
        return {
            "style": CommunicationPattern.SYNC_REQUEST,
            "color": EdgeColors.DEFAULT,
            "pattern": "default"
        }


def get_component_tier(component_type: str) -> int:
    """
    Assign tier numbers for logical grouping (lower = closer to user)
    ByteByteGo style: Client -> Gateway -> Services -> Data
    """
    tier_map = {
        "client": 1,
        "edge": 2,
        "gateway": 3,
        "service": 4,
        "core_service": 4,
        "cache": 5,
        "queue": 5,
        "streaming": 5,
        "database": 6,
        "infra": 7,
        "external_service": 8
    }
    return tier_map.get(component_type.lower(), 5)


def group_components_into_clusters(
    components: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    ByteByteGo-style clustering: Clear separation of concerns
    """
    # Build dependency graph for context
    depends_on = {}
    for rel in relationships:
        source = rel.get("source")
        target = rel.get("target")
        if source not in depends_on:
            depends_on[source] = set()
        depends_on[source].add(target)
    
    # ByteByteGo-style layer names
    clusters = {
        "Client Layer": [],
        "Edge & Gateway": [],
        "Application Services": [],
        "Data & Messaging": [],
        "Infrastructure": [],
        "External Services": []
    }
    
    for component in components:
        comp_type = component.get("type", "").lower()
        comp_id = component.get("id", "")
        
        if comp_type == "client":
            clusters["Client Layer"].append(component)
            
        elif comp_type in ["edge", "gateway"]:
            clusters["Edge & Gateway"].append(component)
            
        elif comp_type in ["service", "core_service"]:
            clusters["Application Services"].append(component)
            
        elif comp_type in ["database", "cache", "queue", "streaming"]:
            clusters["Data & Messaging"].append(component)
            
        elif comp_type == "infra":
            clusters["Infrastructure"].append(component)
            
        elif comp_type == "external_service":
            clusters["External Services"].append(component)
            
        else:
            logger.warning(f"Unknown type '{comp_type}' for {comp_id}, defaulting to Application Services")
            clusters["Application Services"].append(component)
    
    # Remove empty clusters and sort components
    result = {}
    for cluster_name, cluster_components in clusters.items():
        if cluster_components:
            sorted_components = sorted(
                cluster_components,
                key=lambda c: (get_component_tier(c.get("type", "")), c.get("name", ""))
            )
            result[cluster_name] = sorted_components
    
    return result


def generate_diagram_with_diagrams(structure: Dict[str, Any], job_id: str) -> Dict[str, str]:
    """
    Generate ByteByteGo-style diagram with proper visual conventions
    """
    try:
        # Validate structure
        is_valid, errors = validate_structure(structure)
        if not is_valid:
            logger.error(f"Structure validation failed: {errors}")
            return ""
        
        components = structure.get("components", [])
        relationships = structure.get("relationships", [])
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filename = f"{job_id}_system_design"
        png_path = output_dir / f"{filename}.png"
        
        logger.info(f"Generating ByteByteGo-style diagram: {len(components)} components, {len(relationships)} relationships")
        
        # Group components ByteByteGo style
        clusters = group_components_into_clusters(components, relationships)
        
        # Create diagram with ByteByteGo-inspired styling
        with Diagram(
            "System Architecture",
            show=False,
            direction="TB",  # Top to Bottom - ByteByteGo standard
            filename=str(output_dir / filename),
            outformat="png",
            graph_attr={
                "fontsize": "16",
                "fontname": "Arial",
                "bgcolor": "white",
                "pad": "1.0",
                "splines": "ortho",  # Orthogonal lines for clarity
                "nodesep": "1.5",    # More spacing between nodes
                "ranksep": "2.0",    # Clear layer separation
                "compound": "true"   # Better cluster handling
            },
            node_attr={
                "fontsize": "13",
                "fontname": "Arial"
            },
            edge_attr={
                "fontsize": "11",
                "fontname": "Arial"
            }
        ):
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
                        
                        icon_class = get_icon_for_component(comp_type, comp_name)
                        instance = icon_class(comp_name)
                        component_instances[comp_id] = instance
            
            # Create relationships with ByteByteGo-style visual conventions
            for relationship in relationships:
                source_id = relationship.get("source", "")
                target_id = relationship.get("target", "")
                label = relationship.get("label", "")
                
                source_instance = component_instances.get(source_id)
                target_instance = component_instances.get(target_id)
                
                if source_instance and target_instance:
                    # Get ByteByteGo-style attributes
                    rel_attrs = categorize_relationship_bytebytego_style(label)
                    
                    edge_params = {}
                    
                    # Add label if present
                    if label:
                        edge_params["label"] = label
                    
                    # Apply ByteByteGo visual conventions
                    edge_params["color"] = rel_attrs["color"]
                    
                    # Line style based on communication pattern
                    if rel_attrs["style"] == CommunicationPattern.ASYNC_EVENT:
                        edge_params["style"] = "dashed"
                    elif rel_attrs["style"] == CommunicationPattern.DATA_FLOW:
                        edge_params["style"] = "bold"
                    elif rel_attrs["style"] == CommunicationPattern.READ_OPERATION:
                        edge_params["style"] = "dotted"
                    # else: solid (default)
                    
                    # Create the edge
                    source_instance >> Edge(**edge_params) >> target_instance
                else:
                    logger.warning(f"Missing instances for: {source_id} -> {target_id}")
        
        logger.info(f"ByteByteGo-style diagram generated: {png_path}")
        
        # Print legend info
        logger.info("=" * 60)
        logger.info("VISUAL CONVENTIONS APPLIED (ByteByteGo Style)")
        logger.info("=" * 60)
        logger.info("Line Styles:")
        logger.info("  • Solid lines    → Synchronous/HTTP calls")
        logger.info("  • Dashed lines   → Asynchronous/Events")
        logger.info("  • Dotted lines   → Read operations")
        logger.info("  • Bold lines     → Data flow/Streaming")
        logger.info("")
        logger.info("Colors:")
        logger.info("  • Blue (Read)    → Query/Fetch operations")
        logger.info("  • Red (Write)    → Store/Update operations")
        logger.info("  • Purple (Async) → Events/Messages")
        logger.info("  • Green (Sync)   → API/RPC calls")
        logger.info("  • Orange (Data)  → Data transfer/ETL")
        logger.info("=" * 60)
        
        # Generate Animated GIF
        gif_path = generate_animated_gif(structure, job_id)
        
        return {"png": str(png_path), "gif": str(gif_path)}
        
    except Exception as e:
        logger.error(f"Error generating diagram: {e}", exc_info=True)
        return {"png": "", "gif": ""}


def generate_animated_gif(structure: Dict[str, Any], job_id: str) -> str:
    """
    Generate an animated GIF highlighting components sequentially using Mermaid.
    Ensures all frames have identical dimensions by resizing to match the first frame.
    """
    try:
        components = structure.get("components", [])
        if not components:
            return ""

        output_dir = Path("output")
        gif_filename = f"{job_id}_animated.gif"
        gif_path = output_dir / gif_filename
        
        frames = []
        
        # Base Mermaid syntax
        base_mermaid = to_mermaid(structure)
        
        def fetch_mermaid_image(mermaid_code):
            graphbytes = mermaid_code.encode("utf8")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            url =  "https://mermaid.ink/img/" + base64_string
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Use PIL to load the image so we can check/resize dimensions
                    return Image.open(io.BytesIO(response.content))
            except Exception as e:
                logger.warning(f"Failed to fetch frame from Mermaid: {e}")
            return None

        # --- 1. Initial Frame ---
        base_img = fetch_mermaid_image(base_mermaid)
        if base_img is not None:
            # Convert to RGB to ensure consistency
            base_img = base_img.convert("RGB")
            target_size = base_img.size  # (width, height)
            frames.append(np.array(base_img))
            # Add a couple initial frames for pause
            for _ in range(2): frames.append(np.array(base_img))
        else:
            logger.error("Failed to fetch initial Mermaid image for GIF")
            return ""
        
        # --- 2. Highlight Each Component ---
        for i, comp in enumerate(components):
            comp_id = comp.get("id", "")
            if not comp_id: continue
            
            highlight_style = (
                f"\n  style {comp_id} fill:#FFF700,stroke:#FF0000,stroke-width:4px,stroke-dasharray: 5 5"
            )
            frame_script = base_mermaid + highlight_style
            
            frame_img = fetch_mermaid_image(frame_script)
            if frame_img is not None:
                # Resize to match base_img dimensions
                if frame_img.size != target_size:
                    frame_img = frame_img.resize(target_size, Image.Resampling.LANCZOS)
                
                frame_img = frame_img.convert("RGB")
                frames.append(np.array(frame_img))

        # --- 3. Save as GIF ---
        if frames:
            # Duration per frame: 800ms
            imageio.mimsave(gif_path, frames, duration=800, loop=0)
            logger.info(f"Animated GIF generated: {gif_path}")
            return str(gif_path)
        
        return ""

    except Exception as e:
        logger.error(f"Error generating animated GIF: {e}", exc_info=True)
        return ""


def to_mermaid(structure: Dict[str, Any]) -> str:
    """
    Enhanced Mermaid generation with ByteByteGo-style conventions
    """
    is_valid, errors = validate_structure(structure)
    if not is_valid:
        logger.error(f"Structure validation failed: {errors}")
        return f"%%Error: {', '.join(errors)}"
    
    components = structure.get("components", [])
    relationships = structure.get("relationships", [])
    
    mermaid_lines = ["graph TD"]
    
    # Add components with different shapes
    for component in components:
        comp_id = component.get("id", "")
        comp_name = component.get("name", "Unknown")
        comp_type = component.get("type", "service")
        
        # ByteByteGo-style: Different shapes for different types
        if comp_type == "client":
            mermaid_lines.append(f'  {comp_id}(("{comp_name}"))')
        elif comp_type == "database":
            mermaid_lines.append(f'  {comp_id}[("{comp_name}")]')
        elif comp_type in ["cache", "queue"]:
            mermaid_lines.append(f'  {comp_id}["{comp_name}"]')
        else:
            mermaid_lines.append(f'  {comp_id}["{comp_name}"]')
    
    # Add relationships with visual styling
    for relationship in relationships:
        source = relationship.get("source", "")
        target = relationship.get("target", "")
        label = relationship.get("label", "")
        
        rel_attrs = categorize_relationship_bytebytego_style(label)
        
        # Use different arrow styles in Mermaid
        if rel_attrs["pattern"] == "async":
            arrow = "-.->|"  # Dashed for async
        elif rel_attrs["pattern"] == "data":
            arrow = "==>|"   # Thick for data flow
        else:
            arrow = "-->|"   # Solid for sync
        
        if label:
            mermaid_lines.append(f'  {source} {arrow}{label}| {target}')
        else:
            mermaid_lines.append(f'  {source} {arrow[:-1]}> {target}')
    
    return "\n".join(mermaid_lines)