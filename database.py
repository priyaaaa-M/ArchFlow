#!/usr/bin/env python3
"""
SQLite database management for job storage
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger

class JobDatabase:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Jobs table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        type TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'queued',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        error TEXT NULL,
                        result_json TEXT NULL,
                        urls_json TEXT NULL,
                        raw_files_json TEXT NULL
                    )
                ''')
                
                # Components table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS components (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        component_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE
                    )
                ''')
                
                # Relationships table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        source_component_id TEXT NOT NULL,
                        target_component_id TEXT NOT NULL,
                        label TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE
                    )
                ''')
                
                # Create indexes for faster queries
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_components_job_id ON components(job_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_components_type ON components(type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_job_id ON relationships(job_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_component_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_component_id)')
                
                conn.commit()
                logger.info(f"Database initialized at: {Path(self.db_path).absolute()}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_job(self, job_id: str, title: str, job_type: str, topic: str) -> bool:
        """Create a new job record"""
        try:
            now = datetime.utcnow().isoformat() + "Z"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO jobs (job_id, title, type, topic, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'queued', ?, ?)
                ''', (job_id, title, job_type, topic, now, now))
                conn.commit()
                
            logger.info(f"Created job record: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create job {job_id}: {e}")
            return False
    
    def update_job_status(self, job_id: str, status: str, error: str = None) -> bool:
        """Update job status"""
        try:
            now = datetime.utcnow().isoformat() + "Z"
            
            with sqlite3.connect(self.db_path) as conn:
                if error:
                    conn.execute('''
                        UPDATE jobs SET status = ?, error = ?, updated_at = ?
                        WHERE job_id = ?
                    ''', (status, error, now, job_id))
                else:
                    conn.execute('''
                        UPDATE jobs SET status = ?, updated_at = ?
                        WHERE job_id = ?
                    ''', (status, now, job_id))
                conn.commit()
                
            logger.info(f"Updated job {job_id} status to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False
    
    def save_job_result(self, job_id: str, result: Dict[str, Any]) -> bool:
        """Save job result to database"""
        try:
            now = datetime.utcnow().isoformat() + "Z"
            
            # Extract and serialize components
            result_json = json.dumps(result)
            urls_json = json.dumps(result.get('urls', []))
            raw_files_json = json.dumps(result.get('raw_files', []))
            
            with sqlite3.connect(self.db_path) as conn:
                # Update job status and result
                conn.execute('''
                    UPDATE jobs SET 
                        status = 'completed',
                        result_json = ?,
                        urls_json = ?,
                        raw_files_json = ?,
                        updated_at = ?
                    WHERE job_id = ?
                ''', (result_json, urls_json, raw_files_json, now, job_id))
                
                # Store components separately
                components_data = result.get('components', {})
                components = components_data.get('components', [])
                
                for component in components:
                    conn.execute('''
                        INSERT INTO components (job_id, component_id, name, type, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        job_id,
                        component.get('id', ''),
                        component.get('name', ''),
                        component.get('type', ''),
                        now
                    ))
                
                # Store relationships separately
                relationships = components_data.get('relationships', [])
                
                for relationship in relationships:
                    conn.execute('''
                        INSERT INTO relationships (job_id, source_component_id, target_component_id, label, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        job_id,
                        relationship.get('source', ''),
                        relationship.get('target', ''),
                        relationship.get('label', ''),
                        now
                    ))
                
                conn.commit()
                
            logger.info(f"Saved result for job: {job_id} ({len(components)} components, {len(relationships)} relationships)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save result for job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
                row = cursor.fetchone()
                
                if row:
                    job = dict(row)
                    
                    # Parse JSON fields
                    if job['result_json']:
                        job['result'] = json.loads(job['result_json'])
                    if job['urls_json']:
                        job['urls'] = json.loads(job['urls_json'])
                    if job['raw_files_json']:
                        job['raw_files'] = json.loads(job['raw_files_json'])
                    
                    # Clean up JSON fields from response
                    for key in ['result_json', 'urls_json', 'raw_files_json']:
                        job.pop(key, None)
                    
                    return job
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def get_all_jobs(self, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """Get all jobs with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if status:
                    cursor = conn.execute('''
                        SELECT job_id, title, type, topic, status, created_at, updated_at, error
                        FROM jobs WHERE status = ?
                        ORDER BY created_at DESC LIMIT ?
                    ''', (status, limit))
                else:
                    cursor = conn.execute('''
                        SELECT job_id, title, type, topic, status, created_at, updated_at, error
                        FROM jobs
                        ORDER BY created_at DESC LIMIT ?
                    ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    def get_job_stats(self) -> Dict[str, Any]:
        """Get job statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                        SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued
                    FROM jobs
                ''')
                
                row = cursor.fetchone()
                return {
                    'total': row[0],
                    'completed': row[1],
                    'failed': row[2], 
                    'running': row[3],
                    'queued': row[4]
                }
                
        except Exception as e:
            logger.error(f"Failed to get job stats: {e}")
            return {'total': 0, 'completed': 0, 'failed': 0, 'running': 0, 'queued': 0}
    
    def cleanup_old_jobs(self, days: int = 30) -> int:
        """Clean up jobs older than specified days"""
        try:
            cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days).isoformat() + "Z"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM jobs WHERE created_at < ?', (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()
                
            logger.info(f"Cleaned up {deleted_count} old jobs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            return 0
    
    def get_job_components(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all components for a specific job"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT component_id, name, type, created_at
                    FROM components 
                    WHERE job_id = ?
                    ORDER BY name
                ''', (job_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get components for job {job_id}: {e}")
            return []
    
    def get_job_relationships(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific job"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT source_component_id, target_component_id, label, created_at
                    FROM relationships 
                    WHERE job_id = ?
                    ORDER BY source_component_id, target_component_id
                ''', (job_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get relationships for job {job_id}: {e}")
            return []
    
    def get_components_by_type(self, component_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get components by type across all jobs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT c.job_id, c.component_id, c.name, c.type, c.created_at, j.title, j.topic
                    FROM components c
                    JOIN jobs j ON c.job_id = j.job_id
                    WHERE c.type = ? AND j.status = 'completed'
                    ORDER BY c.created_at DESC
                    LIMIT ?
                ''', (component_type, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get components by type {component_type}: {e}")
            return []
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about components across all jobs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Component type distribution
                cursor = conn.execute('''
                    SELECT type, COUNT(*) as count
                    FROM components c
                    JOIN jobs j ON c.job_id = j.job_id
                    WHERE j.status = 'completed'
                    GROUP BY type
                    ORDER BY count DESC
                ''')
                
                component_types = dict(cursor.fetchall())
                
                # Total components and relationships
                cursor = conn.execute('''
                    SELECT 
                        (SELECT COUNT(*) FROM components c JOIN jobs j ON c.job_id = j.job_id WHERE j.status = 'completed') as total_components,
                        (SELECT COUNT(*) FROM relationships r JOIN jobs j ON r.job_id = j.job_id WHERE j.status = 'completed') as total_relationships
                ''')
                
                totals = cursor.fetchone()
                
                return {
                    'total_components': totals[0] if totals else 0,
                    'total_relationships': totals[1] if totals else 0,
                    'component_types': component_types
                }
                
        except Exception as e:
            logger.error(f"Failed to get component stats: {e}")
            return {'total_components': 0, 'total_relationships': 0, 'component_types': {}}

# Global database instance
db = JobDatabase()