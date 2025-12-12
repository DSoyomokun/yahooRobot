"""
Centralized AI service manager.
Provides OpenAI clients to all modules.
Singleton pattern ensures single connection pool.
"""
import logging
from typing import Optional
from yahoo.config.ai_config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_CHAT_MODEL
)

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")


class AIService:
    """
    Singleton AI service for OpenAI.
    Provides centralized OpenAI client to all modules.
    """
    
    _instance = None
    _openai_client = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._init_openai()
            self._initialized = True
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI library not installed")
            return
        
        if OPENAI_API_KEY:
            try:
                self._openai_client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"OpenAI initialization failed: {e}")
        else:
            logger.warning("⚠️  OPENAI_API_KEY not set - AI features disabled")
    
    @property
    def openai(self) -> Optional[OpenAI]:
        """
        Get OpenAI client.
        
        Returns:
            OpenAI client instance or None if not available
        """
        return self._openai_client
    
    @property
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self._openai_client is not None
    
    def get_embedding_model(self) -> str:
        """Get embedding model name."""
        return OPENAI_EMBEDDING_MODEL
    
    def get_chat_model(self) -> str:
        """Get chat model name."""
        return OPENAI_CHAT_MODEL
