"""
Centralized AI/LLM and Vector DB configuration.
Used by scanner, webui, and other modules that need AI capabilities.

Configuration is loaded from environment variables for security.
Set these in your .env file or environment:
- OPENAI_API_KEY
- PINECONE_API_KEY
- PINECONE_ENVIRONMENT
- etc.
"""
import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================
# OpenAI Configuration
# ============================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# ============================================================
# Vector DB Configuration
# ============================================================
# Default to "local" for lightweight OpenAI embeddings storage
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "local").lower()  # local, pinecone, chroma, weaviate, none

# Pinecone Configuration (optional, not used with "local" mode)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "yahoo-robot")

# ChromaDB Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(Path(__file__).parent.parent.parent / "data" / "chroma"))

# Weaviate Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# ============================================================
# Validation
# ============================================================
def validate_config():
    """Validate AI configuration and log warnings."""
    if not OPENAI_API_KEY:
        logger.warning("⚠️  OPENAI_API_KEY not set - AI features will be disabled")
    
    if VECTOR_DB_TYPE == "local" or VECTOR_DB_TYPE == "openai":
        logger.info("✅ Using local vector storage with OpenAI embeddings (lightweight, cost-effective)")
    
    if VECTOR_DB_TYPE == "pinecone":
        if not PINECONE_API_KEY:
            logger.warning("⚠️  PINECONE_API_KEY not set - Vector DB will be disabled")
    
    if VECTOR_DB_TYPE == "weaviate" and not WEAVIATE_API_KEY:
        logger.warning("⚠️  WEAVIATE_API_KEY not set - Vector DB may not work")

# Validate on import
validate_config()
