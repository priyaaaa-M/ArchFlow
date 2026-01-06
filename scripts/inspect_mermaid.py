import mermaid
print(dir(mermaid))
try:
    from mermaid.graph import Graph
    print(dir(Graph))
except ImportError:
    print("No mermaid.graph.Graph")
