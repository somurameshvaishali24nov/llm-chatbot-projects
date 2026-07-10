import os
import uuid
import faiss
import numpy as np
import pickle
from typing import List, Any, Optional
from sentence_transformers import SentenceTransformer
from src.embedding import EmbeddingPipeline

# Step 3
class FaissVectorStore:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", chunk_size = 1000, chunk_overlap = 200):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.embedding_model = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.metadata = []
        print(f"[INFO] Loaded embedding model: {embedding_model}")

    
    def build_from_documents(self, documents: List[Any]):
        print(f"[INFO] Building vector store from {len(documents)} raw documents...")
        emb_pipe = EmbeddingPipeline(model_name=self.embedding_model, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        
        chunks = emb_pipe.chunk_documents(documents=documents)
        embeddings = emb_pipe.embed_chunks(chunks=chunks)
        metadatas = [{"text": chunk.page_content} for chunk in chunks]
        
        self.add_embeddings(np.array(embeddings).astype("float32"), metadatas)
        self.save()
        print(f"[INFO] Vector store built and saved to {self.persist_dir}")


    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None):
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadatas:
            self.metadata.extend(metadatas)
        print(f"[INFO] Vector store built and saved to {self.persist_dir}")


    def save(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pk1")
        
        faiss.write_index(self.index, faiss_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[INFO] Loaded Faiss index and metadata from {self.persist_dir}")


    def load(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pk1")
        
        self.index = faiss.read_index(faiss_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[INFO] Loaded Faiss index and metadata from {self.persist_dir}")


    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        D, I = self.index.search(query_embedding, top_k)
        results = []

        for idx, dist in zip(I[0], D[0]):
            meta = self.metadata[idx] if idx < len(self.metadata) else None
            results.append({"index": idx, "distance": dist, "metadata": meta})
        return results
    

    def query(self, query_text: str, top_k: int = 5):
        print(f"[INFO] Querying vector store for: '{query_text}'")
        query_emb = self.model.encode([query_text]).astype("float32")
        return self.search(query_emb, top_k=top_k)


# Step 3b - Production-grade store for a bigger/business application
class QdrantVectorStore:
    """
    Vector store backed by Qdrant instead of a local FAISS file.

    Why this over FaissVectorStore for a bigger app:
      - Persists on a server (or Qdrant Cloud), not a pickle file on one disk
        -> multiple app instances/processes can share the same data.
      - Supports upserts/deletes of individual vectors (FAISS flat index does not).
      - Supports metadata filtering at query time (e.g. only search docs for tenant X).
      - Scales out (sharding/replication) without changing this code -
        you just point QDRANT_URL at a bigger cluster.

    Same public interface as FaissVectorStore (build_from_documents, load,
    save, query, add_embeddings, search) so app.py / search.py barely change.

    Config:
      - Local dev: run `docker compose up qdrant` and leave url/api_key unset
        (defaults to http://localhost:6333).
      - Production: set QDRANT_URL and QDRANT_API_KEY env vars (e.g. to a
        Qdrant Cloud cluster) - no code changes needed.
    """

    def __init__(
        self,
        collection_name: str = "rag_documents",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        distance: str = "Cosine",
    ):
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as qmodels

        self._qmodels = qmodels
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.distance = distance

        # Local docker Qdrant by default; swap to Qdrant Cloud via env vars
        # (or pass url/api_key directly) - no other code changes needed.
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")

        self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=30)
        self.model = SentenceTransformer(embedding_model)
        self._vector_size = self.model.get_sentence_embedding_dimension()

        self._ensure_collection()
        print(f"[INFO] Connected to Qdrant at {self.url}, collection='{self.collection_name}'")

    def _ensure_collection(self):
        """Create the collection on first run; reuse it if it already exists."""
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self._qmodels.VectorParams(
                    size=self._vector_size,
                    distance=self._qmodels.Distance[self.distance.upper()],
                ),
            )
            print(f"[INFO] Created Qdrant collection '{self.collection_name}' (dim={self._vector_size})")

    def count(self) -> int:
        return self.client.count(collection_name=self.collection_name, exact=True).count

    def build_from_documents(self, documents: List[Any]):
        print(f"[INFO] Building vector store from {len(documents)} raw documents...")
        emb_pipe = EmbeddingPipeline(
            model_name=self.embedding_model_name,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = emb_pipe.chunk_documents(documents=documents)
        embeddings = emb_pipe.embed_chunks(chunks=chunks)
        metadatas = [{"text": chunk.page_content, **chunk.metadata} for chunk in chunks]

        self.add_embeddings(np.array(embeddings).astype("float32"), metadatas)
        self.save()
        print(f"[INFO] Vector store built in Qdrant collection '{self.collection_name}'")

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None, batch_size: int = 256):
        """Upsert vectors in batches - safe to call repeatedly to add more data."""
        metadatas = metadatas or [{} for _ in range(len(embeddings))]
        points = [
            self._qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec.tolist(), payload=meta)
            for vec, meta in zip(embeddings, metadatas)
        ]
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch, wait=True)
        print(f"[INFO] Upserted {len(points)} vectors into '{self.collection_name}' (total now {self.count()})")

    def save(self):
        # No-op: Qdrant persists to its own storage (disk locally, managed in the cloud).
        # Kept for interface parity with FaissVectorStore.
        pass

    def load(self):
        # No-op: data already lives server-side; just confirm the collection exists.
        self._ensure_collection()
        print(f"[INFO] Qdrant collection '{self.collection_name}' ready ({self.count()} vectors)")

    def search(self, query_embedding: np.ndarray, top_k: int = 5, filters: Optional[dict] = None):
        query_filter = None
        if filters:
            query_filter = self._qmodels.Filter(
                must=[
                    self._qmodels.FieldCondition(key=k, match=self._qmodels.MatchValue(value=v))
                    for k, v in filters.items()
                ]
            )
        hits = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding[0].tolist(),
            limit=top_k,
            query_filter=query_filter,
        ).points
        return [{"index": h.id, "distance": h.score, "metadata": h.payload} for h in hits]

    def query(self, query_text: str, top_k: int = 5, filters: Optional[dict] = None):
        print(f"[INFO] Querying vector store for: '{query_text}'")
        query_emb = self.model.encode([query_text]).astype("float32")
        return self.search(query_emb, top_k=top_k, filters=filters)
