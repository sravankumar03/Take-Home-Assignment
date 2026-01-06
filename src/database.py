"""
Database utilities for SQLite operations.

Provides connection management and batch insert helpers.
"""

import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """SQLite database wrapper with batch insert support."""
    
    def __init__(self, db_path: str, schema_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            schema_path: Optional path to schema.sql for initialization
        """
        self.db_path = db_path
        self.schema_path = schema_path
        self.connection: Optional[sqlite3.Connection] = None
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """Create and return database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        return self.connection
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    def initialize_schema(self):
        """Create tables from schema.sql file."""
        if not self.schema_path:
            raise ValueError("No schema path provided")
        
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        conn = self.connect()
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema (may contain multiple statements)
        conn.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema initialized")
    
    def clear_database(self):
        """Remove existing database file and recreate."""
        self.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info(f"Removed existing database: {self.db_path}")
    
    def insert_one(self, table: str, data: Dict[str, Any]) -> None:
        """
        Insert a single row into a table.
        
        Args:
            table: Table name
            data: Dict of column names to values
        """
        conn = self.connect()
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        values = [data[col] for col in columns]
        
        conn.execute(sql, values)
        conn.commit()
    
    def insert_many(self, table: str, rows: List[Dict[str, Any]], batch_size: int = 1000) -> int:
        """
        Batch insert multiple rows into a table.
        
        Args:
            table: Table name
            rows: List of dicts with column names to values
            batch_size: Number of rows per batch
        
        Returns:
            Number of rows inserted
        """
        if not rows:
            return 0
        
        conn = self.connect()
        columns = list(rows[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        total_inserted = 0
        
        # Process in batches
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            values = [[row[col] for col in columns] for row in batch]
            conn.executemany(sql, values)
            total_inserted += len(batch)
        
        conn.commit()
        logger.info(f"Inserted {total_inserted} rows into {table}")
        return total_inserted
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL statement and return cursor."""
        conn = self.connect()
        return conn.execute(sql, params)
    
    def fetchall(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a query and fetch all results."""
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute a query and fetch one result."""
        cursor = self.execute(sql, params)
        return cursor.fetchone()
    
    def count(self, table: str) -> int:
        """Count rows in a table."""
        result = self.fetchone(f"SELECT COUNT(*) as count FROM {table}")
        return result['count'] if result else 0
    
    @contextmanager
    def transaction(self):
        """Context manager for transactions."""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """Get row counts for all tables."""
        tables = [
            'organizations', 'teams', 'users', 'team_memberships',
            'projects', 'sections', 'tasks', 'comments',
            'custom_field_definitions', 'custom_field_values',
            'tags', 'task_tags'
        ]
        
        stats = {}
        for table in tables:
            try:
                stats[table] = self.count(table)
            except sqlite3.OperationalError:
                stats[table] = 0
        
        return stats
    
    def validate_integrity(self) -> List[str]:
        """
        Run integrity checks and return list of issues.
        
        Checks:
        - Foreign key violations
        - Temporal consistency (created_at < completed_at)
        - Required relationships
        """
        issues = []
        
        # Foreign key check
        result = self.fetchone("PRAGMA foreign_key_check")
        if result:
            issues.append(f"Foreign key violation: {result}")
        
        # Temporal consistency: tasks
        bad_tasks = self.fetchall("""
            SELECT id FROM tasks 
            WHERE completed = 1 
            AND completed_at IS NOT NULL 
            AND completed_at < created_at
        """)
        if bad_tasks:
            issues.append(f"Found {len(bad_tasks)} tasks with completed_at < created_at")
        
        # Check for orphaned subtasks
        orphans = self.fetchall("""
            SELECT t.id FROM tasks t
            WHERE t.parent_task_id IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM tasks p WHERE p.id = t.parent_task_id)
        """)
        if orphans:
            issues.append(f"Found {len(orphans)} orphaned subtasks")
        
        return issues
