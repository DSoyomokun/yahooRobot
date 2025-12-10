"""
Storage module for saving test results to database.
Supports multiple database backends: SQLite, PostgreSQL, MySQL, MongoDB, JSON.
"""
import logging
import json
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Storage:
    """Handles storage of test results to various databases."""
    
    def __init__(self, db_type: str = "sqlite", **kwargs):
        """
        Initialize storage.
        
        Args:
            db_type: Database type - "sqlite", "postgresql", "mysql", "mongodb", "json"
            **kwargs: Database-specific connection parameters
        """
        self.db_type = db_type.lower()
        self.client = None
        self.name_matcher = None
        self._initialize(**kwargs)
        
        # Initialize name matcher
        try:
            from .name_matcher import NameMatcher
            self.name_matcher = NameMatcher()
        except ImportError:
            logger.warning("NameMatcher not available, name matching disabled")
    
    def _initialize(self, **kwargs):
        """Initialize database client based on type."""
        try:
            if self.db_type == "sqlite":
                self._init_sqlite(**kwargs)
            elif self.db_type == "postgresql":
                self._init_postgresql(**kwargs)
            elif self.db_type == "mysql":
                self._init_mysql(**kwargs)
            elif self.db_type == "mongodb":
                self._init_mongodb(**kwargs)
            elif self.db_type == "supabase":
                self._init_supabase(**kwargs)
            elif self.db_type == "json":
                self._init_json(**kwargs)
            else:
                logger.warning(f"Unknown database type: {self.db_type}, using SQLite")
                self._init_sqlite(**kwargs)
            
            logger.info(f"{self.db_type.upper()} database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize {self.db_type} database: {e}")
            # Fallback to JSON file storage
            logger.info("Falling back to JSON file storage")
            self.db_type = "json"
            self._init_json(**kwargs)
    
    def _init_sqlite(self, db_path: Optional[str] = None, **kwargs):
        """Initialize SQLite database."""
        try:
            import sqlite3
            from pathlib import Path
            
            if db_path is None:
                db_path = str(Path(__file__).parent / "test_results.db")
            
            self.client = sqlite3.connect(db_path, check_same_thread=False)
            self.client.row_factory = sqlite3.Row
            
            # Create class table if it doesn't exist
            cursor = self.client.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS class (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    last_name TEXT,
                    first_name TEXT,
                    role TEXT,
                    UNIQUE(full_name)
                )
            """)
            
            # Create test_results table with student_id and needs_review
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    student_name TEXT NOT NULL,
                    answers TEXT NOT NULL,
                    score REAL NOT NULL,
                    total_questions INTEGER NOT NULL,
                    correct INTEGER NOT NULL,
                    incorrect INTEGER NOT NULL,
                    unanswered INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    grading_details TEXT,
                    scanned_at TEXT NOT NULL,
                    needs_review BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES class(id)
                )
            """)
            self.client.commit()
            logger.info(f"SQLite database initialized at: {db_path}")
        except ImportError:
            raise ImportError("sqlite3 is built-in to Python, but import failed")
    
    def _init_postgresql(self, host: str = "localhost", port: int = 5432, 
                        database: str = "test_scanner", user: str = "postgres", 
                        password: str = "", **kwargs):
        """Initialize PostgreSQL database."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.client = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                **kwargs
            )
            self.client.autocommit = True
            
            # Create class table
            cursor = self.client.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS class (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    last_name VARCHAR(255),
                    first_name VARCHAR(255),
                    role VARCHAR(50),
                    UNIQUE(full_name)
                )
            """)
            
            # Create test_results table with student_id and needs_review
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER,
                    student_name VARCHAR(255) NOT NULL,
                    answers JSONB NOT NULL,
                    score REAL NOT NULL,
                    total_questions INTEGER NOT NULL,
                    correct INTEGER NOT NULL,
                    incorrect INTEGER NOT NULL,
                    unanswered INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    grading_details JSONB,
                    scanned_at TIMESTAMP NOT NULL,
                    needs_review BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES class(id)
                )
            """)
            logger.info(f"PostgreSQL database initialized: {database}@{host}")
        except ImportError:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
    
    def _init_mysql(self, host: str = "localhost", port: int = 3306,
                   database: str = "test_scanner", user: str = "root",
                   password: str = "", **kwargs):
        """Initialize MySQL database."""
        try:
            import mysql.connector
            
            self.client = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                **kwargs
            )
            
            # Create class table
            cursor = self.client.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS class (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    last_name VARCHAR(255),
                    first_name VARCHAR(255),
                    role VARCHAR(50),
                    UNIQUE(full_name)
                )
            """)
            
            # Create test_results table with student_id and needs_review
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    student_name VARCHAR(255) NOT NULL,
                    answers JSON NOT NULL,
                    score DECIMAL(10,2) NOT NULL,
                    total_questions INT NOT NULL,
                    correct INT NOT NULL,
                    incorrect INT NOT NULL,
                    unanswered INT NOT NULL,
                    percentage DECIMAL(5,2) NOT NULL,
                    grading_details JSON,
                    scanned_at DATETIME NOT NULL,
                    needs_review BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES class(id)
                )
            """)
            self.client.commit()
            logger.info(f"MySQL database initialized: {database}@{host}")
        except ImportError:
            raise ImportError("mysql-connector-python not installed. Install with: pip install mysql-connector-python")
    
    def _init_mongodb(self, connection_string: str = "mongodb://localhost:27017/",
                     database: str = "test_scanner", collection: str = "test_results", **kwargs):
        """Initialize MongoDB database."""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(connection_string, **kwargs)
            self.client = client[database]
            self.collection_name = collection
            logger.info(f"MongoDB database initialized: {database}.{collection}")
        except ImportError:
            raise ImportError("pymongo not installed. Install with: pip install pymongo")
    
    def _init_supabase(self, url: Optional[str] = None, key: Optional[str] = None, 
                       table: str = "test_results", **kwargs):
        """Initialize Supabase database."""
        try:
            from supabase import create_client, Client
            
            if url is None or key is None:
                # Try to get from environment or config
                import os
                url = url or os.getenv('SUPABASE_URL')
                key = key or os.getenv('SUPABASE_KEY')
                
                if not url or not key:
                    raise ValueError("Supabase URL and key must be provided")
            
            self.client: Client = create_client(url, key)
            self.supabase_table = table
            logger.info(f"Supabase database initialized: {table}")
        except ImportError:
            raise ImportError("supabase not installed. Install with: pip install supabase")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            raise
    
    def _init_json(self, json_path: Optional[str] = None, **kwargs):
        """Initialize JSON file storage."""
        if json_path is None:
            json_path = str(Path(__file__).parent / "test_results.json")
        
        self.json_path = Path(json_path)
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.json_path.exists():
            with open(self.json_path, 'w') as f:
                json.dump([], f)
        
        logger.info(f"JSON file storage initialized at: {json_path}")
    
    def save_result(self, result: Dict) -> bool:
        """
        Save test result to database with automatic name matching.
        
        Args:
            result: Dictionary with test result data in format:
                   {
                       'student_name': str,
                       'answers': {"1": "B", "2": "D", ...},
                       'score': float
                   }
            
        Returns:
            True if saved successfully, False otherwise
        """
        if self.client is None and self.db_type != "json":
            logger.warning("Database client not initialized, cannot save result")
            return False
        
        try:
            # Stage 3: Matching - Match OCR name to database
            student_id = None
            needs_review = False
            ocr_name = result.get('student_name', 'Unknown')
            
            if self.name_matcher and ocr_name and ocr_name != 'Unknown':
                student_id = self.name_matcher.match_student_name(ocr_name, self)
                
                if student_id is None:
                    needs_review = True
                    # Get suggestions for manual review
                    suggestions = self.name_matcher.get_suggestions(ocr_name, self, limit=3)
                    if suggestions:
                        logger.warning(f"No match found for '{ocr_name}'. Suggestions: {', '.join([s[1] for s in suggestions])}")
                    else:
                        logger.warning(f"No match found for '{ocr_name}'")
            
            data = {
                'student_id': student_id,
                'student_name': ocr_name,
                'answers': result.get('answers', {}),
                'score': result.get('score', 0.0),
                'total_questions': result.get('total_questions', 0),
                'correct': result.get('correct', 0),
                'incorrect': result.get('incorrect', 0),
                'unanswered': result.get('unanswered', 0),
                'percentage': result.get('percentage', 0.0),
                'grading_details': result.get('details', {}),
                'scanned_at': result.get('scanned_at', datetime.now().isoformat()),
                'needs_review': needs_review
            }
            
            if self.db_type == "sqlite":
                return self._save_sqlite(data)
            elif self.db_type == "postgresql":
                return self._save_postgresql(data)
            elif self.db_type == "mysql":
                return self._save_mysql(data)
            elif self.db_type == "mongodb":
                return self._save_mongodb(data)
            elif self.db_type == "supabase":
                return self._save_supabase(data)
            elif self.db_type == "json":
                return self._save_json(data)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error saving result to {self.db_type}: {e}")
            return False
    
    def _save_sqlite(self, data: Dict) -> bool:
        """Save to SQLite."""
        cursor = self.client.cursor()
        cursor.execute("""
            INSERT INTO test_results 
            (student_id, student_name, answers, score, total_questions, correct, incorrect, 
             unanswered, percentage, grading_details, scanned_at, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('student_id'),
            data['student_name'],
            json.dumps(data['answers']),
            data['score'],
            data['total_questions'],
            data['correct'],
            data['incorrect'],
            data['unanswered'],
            data['percentage'],
            json.dumps(data['grading_details']),
            data['scanned_at'],
            data.get('needs_review', False)
        ))
        self.client.commit()
        status = "MATCHED" if data.get('student_id') else "NEEDS REVIEW"
        logger.info(f"Result saved to SQLite: {data['student_name']} - Score: {data['score']} - {status}")
        return True
    
    def _save_postgresql(self, data: Dict) -> bool:
        """Save to PostgreSQL."""
        cursor = self.client.cursor()
        cursor.execute("""
            INSERT INTO test_results 
            (student_id, student_name, answers, score, total_questions, correct, incorrect, 
             unanswered, percentage, grading_details, scanned_at, needs_review)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('student_id'),
            data['student_name'],
            json.dumps(data['answers']),
            data['score'],
            data['total_questions'],
            data['correct'],
            data['incorrect'],
            data['unanswered'],
            data['percentage'],
            json.dumps(data['grading_details']),
            data['scanned_at'],
            data.get('needs_review', False)
        ))
        status = "MATCHED" if data.get('student_id') else "NEEDS REVIEW"
        logger.info(f"Result saved to PostgreSQL: {data['student_name']} - Score: {data['score']} - {status}")
        return True
    
    def _save_mysql(self, data: Dict) -> bool:
        """Save to MySQL."""
        cursor = self.client.cursor()
        cursor.execute("""
            INSERT INTO test_results 
            (student_id, student_name, answers, score, total_questions, correct, incorrect, 
             unanswered, percentage, grading_details, scanned_at, needs_review)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('student_id'),
            data['student_name'],
            json.dumps(data['answers']),
            data['score'],
            data['total_questions'],
            data['correct'],
            data['incorrect'],
            data['unanswered'],
            data['percentage'],
            json.dumps(data['grading_details']),
            data['scanned_at'],
            data.get('needs_review', False)
        ))
        self.client.commit()
        status = "MATCHED" if data.get('student_id') else "NEEDS REVIEW"
        logger.info(f"Result saved to MySQL: {data['student_name']} - Score: {data['score']} - {status}")
        return True
    
    def _save_mongodb(self, data: Dict) -> bool:
        """Save to MongoDB."""
        collection = self.client[self.collection_name]
        data['created_at'] = datetime.now()
        collection.insert_one(data)
        logger.info(f"Result saved to MongoDB: {data['student_name']} - Score: {data['score']}")
        return True
    
    def _save_supabase(self, data: Dict) -> bool:
        """Save to Supabase database."""
        try:
            # Prepare data for Supabase (convert datetime to string)
            supabase_data = {
                'student_name': data['student_name'],
                'answers': json.dumps(data['answers']),
                'score': data['score'],
                'total_questions': data['total_questions'],
                'correct': data['correct'],
                'incorrect': data['incorrect'],
                'unanswered': data['unanswered'],
                'percentage': data['percentage'],
                'grading_details': json.dumps(data.get('grading_details', {})),
                'scanned_at': data['scanned_at']
            }
            
            response = self.client.table(self.supabase_table).insert(supabase_data).execute()
            logger.info(f"Result saved to Supabase: {data['student_name']} - Score: {data['score']}")
            return True
        except Exception as e:
            logger.error(f"Error saving to Supabase: {e}")
            return False
    
    def store_to_db(self, result: Dict) -> bool:
        """
        Store result to database (alias for save_result with Supabase focus).
        This method is specifically for Supabase integration.
        
        Args:
            result: Dictionary with test result data
            
        Returns:
            True if saved successfully, False otherwise
        """
        return self.save_result(result)
    
    def _save_json(self, data: Dict) -> bool:
        """Save to JSON file."""
        # Load existing data
        if self.json_path.exists():
            with open(self.json_path, 'r') as f:
                results = json.load(f)
        else:
            results = []
        
        # Add new result
        data['id'] = len(results) + 1
        data['created_at'] = datetime.now().isoformat()
        results.append(data)
        
        # Save back
        with open(self.json_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Result saved to JSON: {data['student_name']} - Score: {data['score']}")
        return True
    
    def get_results(self, limit: int = 100) -> list:
        """
        Retrieve test results from database.
        
        Args:
            limit: Maximum number of results to retrieve
            
        Returns:
            List of test results
        """
        if self.client is None and self.db_type != "json":
            logger.warning("Database client not initialized")
            return []
        
        try:
            if self.db_type == "sqlite":
                return self._get_sqlite(limit)
            elif self.db_type == "postgresql":
                return self._get_postgresql(limit)
            elif self.db_type == "mysql":
                return self._get_mysql(limit)
            elif self.db_type == "mongodb":
                return self._get_mongodb(limit)
            elif self.db_type == "supabase":
                return self._get_supabase(limit)
            elif self.db_type == "json":
                return self._get_json(limit)
            else:
                return []
        except Exception as e:
            logger.error(f"Error retrieving results: {e}")
            return []
    
    def _get_sqlite(self, limit: int) -> list:
        """Get results from SQLite."""
        cursor = self.client.cursor()
        cursor.execute("""
            SELECT * FROM test_results 
            ORDER BY scanned_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def _get_postgresql(self, limit: int) -> list:
        """Get results from PostgreSQL."""
        cursor = self.client.cursor()
        cursor.execute("""
            SELECT * FROM test_results 
            ORDER BY scanned_at DESC 
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    
    def _get_mysql(self, limit: int) -> list:
        """Get results from MySQL."""
        cursor = self.client.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM test_results 
            ORDER BY scanned_at DESC 
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    
    def _get_mongodb(self, limit: int) -> list:
        """Get results from MongoDB."""
        collection = self.client[self.collection_name]
        results = collection.find().sort('scanned_at', -1).limit(limit)
        return list(results)
    
    def _get_supabase(self, limit: int) -> list:
        """Get results from Supabase."""
        try:
            response = self.client.table(self.supabase_table)\
                .select("*")\
                .order('scanned_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error retrieving from Supabase: {e}")
            return []
    
    def _get_json(self, limit: int) -> list:
        """Get results from JSON file."""
        if not self.json_path.exists():
            return []
        
        with open(self.json_path, 'r') as f:
            results = json.load(f)
        
        return results[-limit:] if len(results) > limit else results
