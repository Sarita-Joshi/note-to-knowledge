import os
import json
import datetime
import pickle
from llama_index_server.graph_parser import parse_fn, KG_TRIPLET_EXTRACT_TMPL
from llama_index_server.graph_rag_store import GraphRAGStore
from llama_index_server.graph_rag_extractor import GraphRAGExtractor
from llama_index_server.llm_factory import llm, embed_model
from llama_index.core import PropertyGraphIndex, StorageContext, load_index_from_storage
from llama_index_server.process_documents import get_nodes
from llama_index_server.graph_rag_query_engine import GraphRAGQueryEngine

class RagPipeline:
    """A pipeline for building and querying a knowledge graph using RAG techniques."""

    def __init__(self, graph_id:str, text:str=None, force_rebuild=False):
        self.graph_id = graph_id
        self.text = text
        self.base_dir = os.path.join("cached_graphs", self.graph_id)
        self.index_path = os.path.join(self.base_dir, ".index")
        self.graph_path = os.path.join(self.base_dir, "graph.json")
        self.file_log = os.path.join(self.base_dir, "file_log.josn")
        self.force_rebuild = force_rebuild
        self.graph = None

        os.makedirs(self.base_dir, exist_ok=True)
    
        self.index = self._load_or_build_index()
        self.chat_engine = self.index.as_chat_engine(chat_mode="react", llm=llm)
        

    def _load_or_build_index(self):

        
        if os.path.exists(self.index_path) and not self.force_rebuild:
            storage_context = StorageContext.from_defaults(persist_dir=self.index_path) 
            index = load_index_from_storage(storage_context)
            return index
        
        if not self.text:
            raise ValueError("No text provided to build the knowledge graph index.")

        print("Building graph index...")
        nodes = get_nodes(text=self.text)
        if not nodes:
            raise ValueError("No nodes found. Ensure documents are processed correctly.")
        
        kg_extractor = GraphRAGExtractor(
            llm=llm,
            extract_prompt=KG_TRIPLET_EXTRACT_TMPL,
            max_paths_per_chunk=10,
            parse_fn=parse_fn,
        )
        index = PropertyGraphIndex(
            nodes=nodes,
            property_graph_store=GraphRAGStore(),
            kg_extractors=[kg_extractor],
            show_progress=True,
            embed_model=embed_model,
            llm=llm, 
        )

        index.storage_context.persist(persist_dir=self.index_path)
        print("Graph index cached at:", self.index_path)
        return index
    
    def update_index(self, text: str):
        """Add new text to the knowledge graph and update the index."""
        nodes = get_nodes(text=text)
        if not nodes:
            raise ValueError("No nodes found in the provided text.")
        self.index.insert_nodes(nodes)

        print(f"Added {len(nodes)} nodes to the graph index.")
        # Log the update
        self.log_update(filename=self.graph_id, added_nodes=len(nodes), added_edges=0, notes="Added new text nodes.")
        self.export_graph_json()
    
    def build_chat_engine(self):
        """Build the chat engine for the knowledge graph."""
        self.index = self._load_or_build_index()
        self.chat_engine = self.index.as_chat_engine(chat_mode="react", llm=llm, system_prompt=""" 
ou are an assistant grounded in a knowledge graph.
If a question is unrelated to any entity or concept in the graph, add this warning at the beginning:
"This topic isn’t part of the current graph. Consider uploading more context. Here's a short answer from general knowledge"
Always provide short, direct answers. Do not say "Based on the graph" or refer to the source — just answer plainly.""")
        print("Chat engine built successfully.")

    def build_query_engine(self):
        """Build the query engine for the knowledge graph."""
        self.index = self._load_or_build_index()
        self.query_engine = GraphRAGQueryEngine(
            graph_store=self.index.property_graph_store, llm=llm
        )
        print("Query engine built successfully.")
    
    def export_graph_json(self):
        """Export graph nodes and edges to JSON files for visualization."""
        graph = self.index.property_graph_store.graph
        nodes = []
        edges = []
        node_ids = set()  # Track unique node IDs to avoid duplicates
        for node in list(graph.nodes.values()):
            try:
                nodes.append({
                    "id": node.name,
                    "type": node.label,
                    "description": node.properties.get("entity_description", "")
                })
                node_ids.add(node.name)
            except Exception as e:
                continue  # Skip nodes that cause errors
        for edge in graph.relations.values():
            if not edge.source_id in node_ids or not edge.target_id in node_ids:
                continue
            edges.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "relationship": edge.label or "related_to",
                "description": edge.properties.get("relationship_description", "")
            })

        self.graph = {
            "nodes": nodes,
            "edges": edges
        }

        with open(self.graph_path, "w") as f:
            json.dump(self.graph, f, indent=2)
        print(f"Graph exported to '{self.graph_path}")

    def query(self, question: str):
        """Query the graph using a natural language question."""
        response =  self.query_engine.query(question)
        return response.response if response else "No response from chat engine."
    
    def chat(self, question: str):
        """Query the graph using a natural language question."""
        response = self.chat_engine.chat(question)
        return response.response if response else "No response from chat engine."

    def get_triplets(self):
        """Get all extracted triplets from the knowledge graph."""
        return self.index.property_graph_store.graph.get_triplets()

    def get_graph_store(self):
        """Access the underlying graph store."""
        return self.index.property_graph_store
    
    def get_graph_json(self):
        """Get the graph in JSON format."""
        if not os.path.exists(self.graph_path):
            self.export_graph_json()
        
        with open(self.graph_path, "r") as f:
            return json.load(f)
        
    def get_file_log(self):
        """Get the log of files processed."""
        if not os.path.exists(self.file_log):
            return []

        with open(self.file_log, "r") as f:
            return json.load(f)

    def clear_cache(self):
        """Delete the cached index file."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
            print("Cached index removed.")
        else:
            print("No cache file to remove.")

    def log_update(self, filename: str, added_nodes: int, added_edges: int, notes: str = ""):
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "filename": filename,
            "notes": notes,
            "added_nodes": added_nodes,
            "added_edges": added_edges
        }

        log_path = os.path.join(self.base_dir, "logs.json")
        logs = []
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)
