
import os
import json
import logging
import numpy as np
import faiss
from typing import List, Dict, Optional
from pathlib import Path

# Only local imports
from core.local_model_engine import local_engine

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
INDEX_PATH = DATA_DIR / "faiss.index"
META_PATH = DATA_DIR / "faiss_meta.json"

class VectorStore:
    def __init__(self):
        self.dimension = 384 # Default for all-MiniLM-L6-v2
        self.index = None
        self.metadata = [] # List of dicts, parallel to index
        self._load_index()

    def _load_index(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load Index
        if INDEX_PATH.exists():
            try:
                self.index = faiss.read_index(str(INDEX_PATH))
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
                self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

        # Load Metadata
        if META_PATH.exists():
            try:
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                self.metadata = []
        else:
            self.metadata = []

    def save(self):
        try:
            if self.index:
                faiss.write_index(self.index, str(INDEX_PATH))
            with open(META_PATH, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def add(self, text: str, meta: Dict):
        """
        Embeds text and adds to index.
        meta should contain {'user_id': ..., 'ref_id': ..., 'role': ...}
        """
        if not text.strip():
            return
            
        try:
            # Embed
            embedding = local_engine.embed(text)
            if len(embedding) != self.dimension:
                logger.warning(f"Embedding dim mismatch: got {len(embedding)}, expected {self.dimension}")
                return

            vec = np.array([embedding], dtype='float32')
            
            # Add to Index
            self.index.add(vec)
            
            # Add Metadata
            self.metadata.append({
                "text": text[:500], # Store snippet for context
                **meta
            })
            
            # Auto-save on every write for v1.7 safety (could be optimized)
            self.save()
            
        except Exception as e:
            logger.error(f"Vector add error: {e}")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Returns top-k matching metadata items.
        """
        if not self.index or self.index.ntotal == 0:
            return []

        try:
            # Embed Query
            embedding = local_engine.embed(query)
            vec = np.array([embedding], dtype='float32')
            
            # Search
            distances, indices = self.index.search(vec, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx == -1 or idx >= len(self.metadata):
                    continue
                match = self.metadata[idx].copy()
                match["score"] = float(distances[0][i]) # L2 distance (lower is better)
                results.append(match)
            
            return results
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

vector_store = VectorStore()
