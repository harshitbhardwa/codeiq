import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

from .base_database import BaseDatabase

class PostgreSQLDatabase(BaseDatabase):
    """
    PostgreSQL database implementation for storing code analysis results and alert data.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize PostgreSQL database connection."""
        super().__init__(config)
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Connect to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Create tables if they don't exist
            self._create_tables()
            
            self.connected = True
            logger.info("Connected to PostgreSQL database")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from PostgreSQL database."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connected = False
            logger.info("Disconnected from PostgreSQL database")
        except Exception as e:
            logger.error(f"Error disconnecting from PostgreSQL: {str(e)}")
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            # Analysis results table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id SERIAL PRIMARY KEY,
                    file_path VARCHAR(500) UNIQUE NOT NULL,
                    language VARCHAR(50) NOT NULL,
                    functions JSONB,
                    classes JSONB,
                    imports JSONB,
                    metrics JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alert data table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_data (
                    id SERIAL PRIMARY KEY,
                    alert_type VARCHAR(100) NOT NULL,
                    alert_message TEXT,
                    file_path VARCHAR(500),
                    line_number INTEGER,
                    severity VARCHAR(20),
                    analysis_result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_results_file_path 
                ON analysis_results(file_path)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_results_language 
                ON analysis_results(language)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alert_data_created_at 
                ON alert_data(created_at)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alert_data_alert_type 
                ON alert_data(alert_type)
            """)
            
            self.connection.commit()
            logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            self.connection.rollback()
            raise
    
    def store_analysis_result(self, analysis_data: Dict[str, Any]) -> bool:
        """Store code analysis results."""
        if not self.connected:
            logger.error("Database not connected")
            return False
        
        try:
            self.cursor.execute("""
                INSERT INTO analysis_results 
                (file_path, language, functions, classes, imports, metrics)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (file_path) 
                DO UPDATE SET 
                    language = EXCLUDED.language,
                    functions = EXCLUDED.functions,
                    classes = EXCLUDED.classes,
                    imports = EXCLUDED.imports,
                    metrics = EXCLUDED.metrics,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                analysis_data.get('file_path'),
                analysis_data.get('language'),
                json.dumps(analysis_data.get('functions', [])),
                json.dumps(analysis_data.get('classes', [])),
                json.dumps(analysis_data.get('imports', [])),
                json.dumps(analysis_data.get('metrics', {}))
            ))
            
            self.connection.commit()
            logger.info(f"Stored analysis result for {analysis_data.get('file_path')}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analysis result: {str(e)}")
            self.connection.rollback()
            return False
    
    def get_analysis_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve code analysis results for a file."""
        if not self.connected:
            logger.error("Database not connected")
            return None
        
        try:
            self.cursor.execute("""
                SELECT * FROM analysis_results WHERE file_path = %s
            """, (file_path,))
            
            result = self.cursor.fetchone()
            if result:
                # Convert to dictionary and parse JSON fields
                data = dict(result)
                data['functions'] = json.loads(data['functions']) if data['functions'] else []
                data['classes'] = json.loads(data['classes']) if data['classes'] else []
                data['imports'] = json.loads(data['imports']) if data['imports'] else []
                data['metrics'] = json.loads(data['metrics']) if data['metrics'] else {}
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving analysis result: {str(e)}")
            return None
    
    def store_alert_data(self, alert_data: Dict[str, Any]) -> bool:
        """Store alert data."""
        if not self.connected:
            logger.error("Database not connected")
            return False
        
        try:
            self.cursor.execute("""
                INSERT INTO alert_data 
                (alert_type, alert_message, file_path, line_number, severity, analysis_result)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                alert_data.get('alert_type'),
                alert_data.get('alert_message'),
                alert_data.get('file_path'),
                alert_data.get('line_number'),
                alert_data.get('severity', 'medium'),
                json.dumps(alert_data.get('analysis_result', {}))
            ))
            
            self.connection.commit()
            logger.info(f"Stored alert data: {alert_data.get('alert_type')}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing alert data: {str(e)}")
            self.connection.rollback()
            return False
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve alert history."""
        if not self.connected:
            logger.error("Database not connected")
            return []
        
        try:
            self.cursor.execute("""
                SELECT * FROM alert_data 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            results = []
            for row in self.cursor.fetchall():
                data = dict(row)
                data['analysis_result'] = json.loads(data['analysis_result']) if data['analysis_result'] else {}
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving alert history: {str(e)}")
            return []
    
    def search_analysis_results(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search analysis results based on criteria."""
        if not self.connected:
            logger.error("Database not connected")
            return []
        
        try:
            # Build dynamic query
            sql = "SELECT * FROM analysis_results WHERE 1=1"
            params = []
            
            if 'language' in query:
                sql += " AND language = %s"
                params.append(query['language'])
            
            if 'file_path_pattern' in query:
                sql += " AND file_path ILIKE %s"
                params.append(f"%{query['file_path_pattern']}%")
            
            if 'min_complexity' in query:
                sql += " AND (metrics->>'average_complexity')::float >= %s"
                params.append(query['min_complexity'])
            
            if 'max_complexity' in query:
                sql += " AND (metrics->>'average_complexity')::float <= %s"
                params.append(query['max_complexity'])
            
            sql += " ORDER BY created_at DESC"
            
            if 'limit' in query:
                sql += " LIMIT %s"
                params.append(query['limit'])
            
            self.cursor.execute(sql, params)
            
            results = []
            for row in self.cursor.fetchall():
                data = dict(row)
                data['functions'] = json.loads(data['functions']) if data['functions'] else []
                data['classes'] = json.loads(data['classes']) if data['classes'] else []
                data['imports'] = json.loads(data['imports']) if data['imports'] else []
                data['metrics'] = json.loads(data['metrics']) if data['metrics'] else {}
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching analysis results: {str(e)}")
            return []
    
    def update_analysis_result(self, file_path: str, update_data: Dict[str, Any]) -> bool:
        """Update existing analysis results."""
        if not self.connected:
            logger.error("Database not connected")
            return False
        
        try:
            # Build dynamic update query
            update_fields = []
            params = []
            
            for field, value in update_data.items():
                if field in ['functions', 'classes', 'imports', 'metrics']:
                    update_fields.append(f"{field} = %s")
                    params.append(json.dumps(value))
                elif field in ['language']:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(file_path)
            
            sql = f"""
                UPDATE analysis_results 
                SET {', '.join(update_fields)}
                WHERE file_path = %s
            """
            
            self.cursor.execute(sql, params)
            self.connection.commit()
            
            logger.info(f"Updated analysis result for {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating analysis result: {str(e)}")
            self.connection.rollback()
            return False
    
    def delete_analysis_result(self, file_path: str) -> bool:
        """Delete analysis results for a file."""
        if not self.connected:
            logger.error("Database not connected")
            return False
        
        try:
            self.cursor.execute("""
                DELETE FROM analysis_results WHERE file_path = %s
            """, (file_path,))
            
            self.connection.commit()
            logger.info(f"Deleted analysis result for {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analysis result: {str(e)}")
            self.connection.rollback()
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.connected:
            return {'error': 'Database not connected'}
        
        try:
            stats = {}
            
            # Count analysis results
            self.cursor.execute("SELECT COUNT(*) as count FROM analysis_results")
            stats['total_analysis_results'] = self.cursor.fetchone()['count']
            
            # Count alerts
            self.cursor.execute("SELECT COUNT(*) as count FROM alert_data")
            stats['total_alerts'] = self.cursor.fetchone()['count']
            
            # Language distribution
            self.cursor.execute("""
                SELECT language, COUNT(*) as count 
                FROM analysis_results 
                GROUP BY language
            """)
            stats['language_distribution'] = dict(self.cursor.fetchall())
            
            # Recent activity
            self.cursor.execute("""
                SELECT COUNT(*) as count 
                FROM analysis_results 
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
            """)
            stats['recent_analysis_results'] = self.cursor.fetchone()['count']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {'error': str(e)} 