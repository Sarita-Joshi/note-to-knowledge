import os
import pickle
from graph_parser import parse_fn, KG_TRIPLET_EXTRACT_TMPL
from graph_rag_store import GraphRAGStore
from graph_rag_extractor import GraphRAGExtractor
from llm_factory import llm, embed_model
from llama_index.core import PropertyGraphIndex
from process_documents import get_nodes
from graph_rag_query_engine import GraphRAGQueryEngine

class GraphRAGApp:
    def __init__(self, index_path="cached_graph_index.pkl", force_rebuild=False):
        self.index_path = index_path
        self.force_rebuild = force_rebuild
        self.index = self._load_or_build_index()
        self.query_engine = GraphRAGQueryEngine(
            graph_store=self.index.property_graph_store, llm=llm
        )

    def _load_or_build_index(self):
        if not self.force_rebuild and os.path.exists(self.index_path):
            print("🔁 Loading cached graph index...")
            with open(self.index_path, "rb") as f:
                return pickle.load(f)

        print("⚙️ Building graph index...")
        kg_extractor = GraphRAGExtractor(
            llm=llm,
            extract_prompt=KG_TRIPLET_EXTRACT_TMPL,
            max_paths_per_chunk=2,
            parse_fn=parse_fn,
        )
        index = PropertyGraphIndex(
            nodes=get_nodes(),
            property_graph_store=GraphRAGStore(),
            kg_extractors=[kg_extractor],
            show_progress=True,
        )

        with open(self.index_path, "wb") as f:
            pickle.dump(index, f)
        print("✅ Graph index cached at:", self.index_path)

        return index

    def query(self, question: str):
        """Query the graph using a natural language question."""
        return self.query_engine.query(question)

    def get_triplets(self):
        """Get all extracted triplets from the knowledge graph."""
        return self.index.property_graph_store.graph.get_triplets()

    def get_graph_store(self):
        """Access the underlying graph store."""
        return self.index.property_graph_store

    def clear_cache(self):
        """Delete the cached index file."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
            print("🗑️ Cached index removed.")
        else:
            print("⚠️ No cache file to remove.")
