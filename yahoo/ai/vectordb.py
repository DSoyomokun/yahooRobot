"""
Vector database manager supporting local storage with OpenAI embeddings.
Provides unified interface for vector operations.
Uses OpenAI text-embedding-3-small for cost-effective, lightweight embeddings.
"""
import logging
import json
import pickle
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from yahoo.config.ai_config import (
    VECTOR_DB_TYPE,
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    CHROMA_PERSIST_DIR,
    WEAVIATE_URL,
    WEAVIATE_API_KEY
)

logger = logging.getLogger(__name__)


class VectorDB:
    """
    Unified vector database interface.
    Uses OpenAI embeddings with local storage (lightweight, cost-effective).
    """
    
    def __init__(self):
        self.db_type = VECTOR_DB_TYPE.lower()
        self.client = None
        self.index = None
        self._initialized = False
        self._vectors = {}  # Local storage: {id: {'embedding': np.array, 'metadata': dict}}
        self._storage_path = None
        self._init()
    
    def _init(self):
        """Initialize vector database based on type."""
        if self.db_type == "none":
            logger.info("Vector DB disabled (VECTOR_DB_TYPE=none)")
            return
        
        if self.db_type == "local" or self.db_type == "openai":
            self._init_local()
        elif self.db_type == "pinecone":
            self._init_pinecone()
        elif self.db_type == "chroma":
            self._init_chroma()
        elif self.db_type == "weaviate":
            self._init_weaviate()
        else:
            # Default to local if unknown
            logger.info(f"Unknown vector DB type: {self.db_type}, defaulting to local")
            self.db_type = "local"
            self._init_local()
    
    def _init_local(self):
        """Initialize local vector storage with OpenAI embeddings."""
        try:
            # Set storage path
            storage_dir = Path(__file__).parent.parent / "data" / "vectordb"
            storage_dir.mkdir(parents=True, exist_ok=True)
            self._storage_path = storage_dir / "vectors.pkl"
            
            # Load existing vectors if available
            if self._storage_path.exists():
                try:
                    with open(self._storage_path, 'rb') as f:
                        self._vectors = pickle.load(f)
                    logger.info(f"✅ Loaded {len(self._vectors)} vectors from local storage")
                except Exception as e:
                    logger.warning(f"Could not load existing vectors: {e}")
                    self._vectors = {}
            else:
                self._vectors = {}
            
            self._initialized = True
            logger.info("✅ Local vector DB initialized (using OpenAI embeddings)")
            
        except Exception as e:
            logger.error(f"Local vector DB initialization failed: {e}")
    
    def _save_vectors(self):
        """Save vectors to disk."""
        if self._storage_path:
            try:
                with open(self._storage_path, 'wb') as f:
                    pickle.dump(self._vectors, f)
            except Exception as e:
                logger.warning(f"Could not save vectors: {e}")
    
    def _init_pinecone(self):
        """Initialize Pinecone."""
        if not PINECONE_API_KEY:
            logger.warning("⚠️  PINECONE_API_KEY not set - Pinecone disabled")
            return
        
        try:
            import pinecone
            from pinecone import Pinecone
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=PINECONE_API_KEY)
            
            # Get or create index
            try:
                self.index = pc.Index(PINECONE_INDEX_NAME)
                logger.info(f"✅ Pinecone connected to index: {PINECONE_INDEX_NAME}")
            except Exception as e:
                logger.warning(f"Pinecone index '{PINECONE_INDEX_NAME}' not found: {e}")
                logger.info("💡 Create the index in Pinecone dashboard or use create_index()")
            
            self.client = pc
            self._initialized = True
            
        except ImportError:
            logger.error("pinecone-client not installed. Install with: pip install pinecone-client")
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
    
    def _init_chroma(self):
        """Initialize ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"✅ ChromaDB initialized: {CHROMA_PERSIST_DIR}")
            self._initialized = True
            
        except ImportError:
            logger.error("chromadb not installed. Install with: pip install chromadb")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
    
    def _init_weaviate(self):
        """Initialize Weaviate."""
        try:
            import weaviate
            
            auth_config = None
            if WEAVIATE_API_KEY:
                auth_config = weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)
            
            self.client = weaviate.Client(
                url=WEAVIATE_URL,
                auth_client_secret=auth_config
            )
            logger.info(f"✅ Weaviate initialized: {WEAVIATE_URL}")
            self._initialized = True
            
        except ImportError:
            logger.error("weaviate-client not installed. Install with: pip install weaviate-client")
        except Exception as e:
            logger.error(f"Weaviate initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if vector DB is available."""
        if self.db_type == "local" or self.db_type == "openai":
            return self._initialized
        return self._initialized and self.client is not None
    
    def query(self, 
              embedding: np.ndarray, 
              top_k: int = 3,
              namespace: Optional[str] = None,
              filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Query vector database for similar vectors.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            namespace: Namespace/collection name (for Pinecone)
            filter: Metadata filter (optional)
            
        Returns:
            List of results with 'id', 'score', 'metadata' keys
        """
        if not self.is_available():
            logger.warning("Vector DB not available")
            return []
        
        try:
            if self.db_type == "local" or self.db_type == "openai":
                return self._query_local(embedding, top_k, filter)
            elif self.db_type == "pinecone":
                return self._query_pinecone(embedding, top_k, namespace, filter)
            elif self.db_type == "chroma":
                return self._query_chroma(embedding, top_k, filter)
            elif self.db_type == "weaviate":
                return self._query_weaviate(embedding, top_k, filter)
        except Exception as e:
            logger.error(f"Vector DB query failed: {e}")
            return []
    
    def _query_local(self, embedding: np.ndarray, top_k: int, filter: Optional[Dict]) -> List[Dict]:
        """Query local vector storage using cosine similarity."""
        if not self._vectors:
            return []
        
        # Convert embedding to numpy array if needed
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)
        embedding = embedding.reshape(1, -1)
        
        # Calculate similarities
        similarities = []
        for vec_id, vec_data in self._vectors.items():
            # Apply filter if provided
            if filter:
                metadata = vec_data.get('metadata', {})
                if not all(metadata.get(k) == v for k, v in filter.items()):
                    continue
            
            vec_embedding = vec_data['embedding']
            if not isinstance(vec_embedding, np.ndarray):
                vec_embedding = np.array(vec_embedding)
            vec_embedding = vec_embedding.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(embedding, vec_embedding)[0][0]
            similarities.append({
                'id': vec_id,
                'score': float(similarity),
                'metadata': vec_data.get('metadata', {})
            })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:top_k]
    
    def _query_pinecone(self, embedding: np.ndarray, top_k: int, namespace: Optional[str], filter: Optional[Dict]) -> List[Dict]:
        """Query Pinecone."""
        if not self.index:
            return []
        
        query_response = self.index.query(
            vector=embedding.tolist(),
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
            filter=filter
        )
        
        results = []
        for match in query_response.get('matches', []):
            results.append({
                'id': match['id'],
                'score': match['score'],
                'metadata': match.get('metadata', {})
            })
        
        return results
    
    def _query_chroma(self, embedding: np.ndarray, top_k: int, filter: Optional[Dict]) -> List[Dict]:
        """Query ChromaDB."""
        # Get or create collection
        collection = self.client.get_or_create_collection(name="yahoo-robot")
        
        results = collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k,
            where=filter
        )
        
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'score': 1.0 - results['distances'][0][i] if 'distances' in results else 1.0,
                    'metadata': results['metadatas'][0][i] if 'metadatas' in results else {}
                })
        
        return formatted_results
    
    def _query_weaviate(self, embedding: np.ndarray, top_k: int, filter: Optional[Dict]) -> List[Dict]:
        """Query Weaviate."""
        # Placeholder - implement Weaviate query logic
        logger.warning("Weaviate query not yet implemented")
        return []
    
    def upsert(self, 
               vectors: List[Tuple[str, np.ndarray, Dict[str, Any]]],
               namespace: Optional[str] = None):
        """
        Insert/update vectors in database.
        
        Args:
            vectors: List of (id, embedding, metadata) tuples
            namespace: Namespace/collection name (for Pinecone)
        """
        if not self.is_available():
            logger.warning("Vector DB not available")
            return
        
        try:
            if self.db_type == "local" or self.db_type == "openai":
                self._upsert_local(vectors)
            elif self.db_type == "pinecone":
                self._upsert_pinecone(vectors, namespace)
            elif self.db_type == "chroma":
                self._upsert_chroma(vectors)
            elif self.db_type == "weaviate":
                self._upsert_weaviate(vectors)
        except Exception as e:
            logger.error(f"Vector DB upsert failed: {e}")
    
    def _upsert_local(self, vectors: List[Tuple[str, np.ndarray, Dict]]):
        """Upsert to local storage."""
        for vec_id, embedding, metadata in vectors:
            # Convert to numpy array if needed
            if not isinstance(embedding, np.ndarray):
                embedding = np.array(embedding)
            
            self._vectors[vec_id] = {
                'embedding': embedding,
                'metadata': metadata
            }
        
        # Save to disk
        self._save_vectors()
        logger.info(f"Upserted {len(vectors)} vectors to local storage")
    
    def _upsert_pinecone(self, vectors: List[Tuple[str, np.ndarray, Dict]], namespace: Optional[str]):
        """Upsert to Pinecone."""
        if not self.index:
            return
        
        # Format for Pinecone
        pinecone_vectors = []
        for vec_id, embedding, metadata in vectors:
            pinecone_vectors.append({
                'id': vec_id,
                'values': embedding.tolist(),
                'metadata': metadata
            })
        
        self.index.upsert(vectors=pinecone_vectors, namespace=namespace)
        logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
    
    def _upsert_chroma(self, vectors: List[Tuple[str, np.ndarray, Dict]]):
        """Upsert to ChromaDB."""
        collection = self.client.get_or_create_collection(name="yahoo-robot")
        
        ids = [v[0] for v in vectors]
        embeddings = [v[1].tolist() for v in vectors]
        metadatas = [v[2] for v in vectors]
        
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Upserted {len(vectors)} vectors to ChromaDB")
    
    def _upsert_weaviate(self, vectors: List[Tuple[str, np.ndarray, Dict]]):
        """Upsert to Weaviate."""
        logger.warning("Weaviate upsert not yet implemented")
