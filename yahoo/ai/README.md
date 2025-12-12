# Centralized AI Services

This module provides centralized AI and Vector DB services for the entire Yahoo Robot system.

## Features

- **Centralized OpenAI Client**: Single shared client for all modules
- **Vector DB Support**: Pinecone, ChromaDB, and Weaviate
- **Environment-based Configuration**: Uses `.env` file for API keys
- **Singleton Pattern**: Ensures only one instance of each service

## Setup

1. **Install dependencies**:
   ```bash
   pip install openai python-dotenv pinecone-client
   ```

2. **Configure environment**:
   - Copy `.env.example` to `.env`
   - Add your API keys:
     ```bash
     OPENAI_API_KEY=sk-proj-...
     PINECONE_API_KEY=pcsk-...
     ```

3. **Use in your code**:
   ```python
   from yahoo.ai.service import AIService
   from yahoo.ai.vectordb import VectorDB
   
   # Get OpenAI client
   ai_service = AIService()
   openai_client = ai_service.openai
   
   # Get Vector DB
   vector_db = VectorDB()
   if vector_db.is_available():
       results = vector_db.query(embedding, top_k=3)
   ```

## Configuration

All configuration is done via environment variables in `.env`:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)
- `OPENAI_CHAT_MODEL`: Chat model (default: gpt-4o-mini)
- `VECTOR_DB_TYPE`: Vector DB type (pinecone, chroma, weaviate, none)
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `PINECONE_INDEX_NAME`: Pinecone index name

## Usage in Scanner

The scanner automatically uses these services:

```python
from yahoo.mission.scanner import ScanControl

# Automatically uses centralized AI services
scanner = ScanControl()
result = scanner.process_test(image="test.jpg")
```

No need to pass API keys - they're loaded from environment automatically!

