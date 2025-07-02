from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from loguru import logger

from .models import (
    AnalysisRequest, SearchRequest, AlertRequest,
    AnalysisResult, SearchResult, AlertAnalysisResult,
    DatabaseStats, VectorIndexStats, HealthCheck, ErrorResponse,
    FunctionInfo, ClassInfo, ImportInfo, MetricsInfo
)

from ..config.credential_manager import CredentialManager
from ..parsers.parser_factory import ParserFactory
from ..vectorization.embedding_manager import EmbeddingManager
from ..database.postgresql_database import PostgreSQLDatabase
from ..utils.logger import get_logger

# Initialize components
cred_manager = CredentialManager()
parser_factory = ParserFactory()
embedding_manager = None
database = None
logger_setup = get_logger()

# Initialize embedding manager and database
try:
    vector_config = cred_manager.get_vector_config()
    embedding_manager = EmbeddingManager(
        model_name='all-MiniLM-L6-v2',
        dimension=vector_config['dimension']
    )
    
    # Try to load existing index
    if vector_config['index_path']:
        embedding_manager.load_faiss_index(vector_config['index_path'])
        logger.info("Vector index initialization completed")
    
    # Initialize database
    db_config = cred_manager.get_db_credentials()
    database = PostgreSQLDatabase(db_config)
    if database.connect():
        logger.info("Database connected successfully")
    else:
        logger.warning("Database connection failed")
        database = None
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    database = None

router = APIRouter()

def map_host_path_to_container(path: str) -> str:
    """
    Map host paths to container paths for Docker environment.
    
    Args:
        path: Original path (potentially from host)
        
    Returns:
        Mapped container path
    """
    # Define path mappings (host_path -> container_path)
    path_mappings = {
        '/root/retrofit': '/app/host-repo',
        '/Users/harshit.bhardwaj/Documents/RZP-Online': '/app/host-repo',
        # Add more mappings as needed
    }
    
    # Check if the path matches any known host paths
    for host_path, container_path in path_mappings.items():
        if path == host_path or path.startswith(host_path + '/'):
            mapped_path = path.replace(host_path, container_path)
            logger.info(f"Mapped path: {path} -> {mapped_path}")
            return mapped_path
    
    # If no mapping found, return original path
    return path

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            database_connected=database.is_connected() if database else False,
            vector_index_loaded=embedding_manager.index is not None if embedding_manager else False,
            supported_languages=parser_factory.get_supported_languages()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.post("/analyze", response_model=List[AnalysisResult])
async def analyze_code(request: AnalysisRequest):
    """Analyze code files or repository."""
    try:
        start_time = datetime.now()
        
        if request.file_path:
            # Analyze single file
            parser = parser_factory.get_parser_by_file_extension(request.file_path)
            if not parser:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            result = parser.parse_file(request.file_path)
            if not result:
                raise HTTPException(status_code=404, detail="File not found or could not be parsed")
            
            # Store in database if available
            if database and database.is_connected():
                database.store_analysis_result(result)
            
            # Create embeddings if requested
            if request.include_embeddings and embedding_manager:
                embeddings_data = embedding_manager.create_embeddings([result])
                if embeddings_data:
                    embedding_manager.build_faiss_index(embeddings_data, cred_manager.get_vector_config()['index_path'])
            
            # Convert to response model
            analysis_result = AnalysisResult(
                file_path=result['file_path'],
                language=result['language'],
                functions=[FunctionInfo(**func) for func in result.get('functions', [])],
                classes=[ClassInfo(**cls) for cls in result.get('classes', [])],
                imports=[ImportInfo(**imp) for imp in result.get('imports', [])],
                metrics=MetricsInfo(**result.get('metrics', {})),
                analysis_timestamp=start_time
            )
            
            return [analysis_result]
            
        elif request.repository_path:
            # Use provided repository path with mapping
            repo_path = map_host_path_to_container(request.repository_path)
        else:
            # Use configured default repository path
            repo_path = cred_manager.git_repo_path
            logger.info(f"Using configured repository path: {repo_path}")
            
        # Analyze repository
        results = []
        supported_languages = [request.language] if request.language else parser_factory.get_supported_languages()
        
        for language in supported_languages:
            parser = parser_factory.get_parser(language)
            if parser:
                repo_result = parser.parse_repository(repo_path)
                if repo_result and repo_result['files']:
                    results.extend(repo_result['files'])
        
        # Store in database if available
        if database and database.is_connected():
            for result in results:
                database.store_analysis_result(result)
        
        # Create embeddings if requested
        if request.include_embeddings and embedding_manager and results:
            embeddings_data = embedding_manager.create_embeddings(results)
            if embeddings_data:
                embedding_manager.build_faiss_index(embeddings_data, cred_manager.get_vector_config()['index_path'])
        
        # Convert to response models
        analysis_results = []
        for result in results:
            analysis_result = AnalysisResult(
                file_path=result['file_path'],
                language=result['language'],
                functions=[FunctionInfo(**func) for func in result.get('functions', [])],
                classes=[ClassInfo(**cls) for cls in result.get('classes', [])],
                imports=[ImportInfo(**imp) for imp in result.get('imports', [])],
                metrics=MetricsInfo(**result.get('metrics', {})),
                analysis_timestamp=start_time
            )
            analysis_results.append(analysis_result)
        
        return analysis_results
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/search", response_model=List[SearchResult])
async def search_code(request: SearchRequest):
    """Search for code using various methods."""
    try:
        if not embedding_manager or not embedding_manager.index:
            raise HTTPException(status_code=503, detail="Vector index not available")
        
        results = []
        
        if request.search_type == "semantic":
            # Semantic search
            search_results = embedding_manager.search_similar_code(request.query, request.top_k)
            results = search_results
            
        elif request.search_type == "function_name":
            # Function name search
            search_results = embedding_manager.search_by_function_name(request.query, request.top_k)
            results = search_results
            
        elif request.search_type == "complexity":
            # Complexity range search
            min_complexity = request.min_complexity or 0.0
            max_complexity = request.max_complexity or 100.0
            search_results = embedding_manager.search_by_complexity_range(min_complexity, max_complexity)
            results = search_results[:request.top_k]
            
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
        
        # Apply language filter if specified
        if request.language_filter:
            results = [r for r in results if r.get('language') == request.language_filter]
        
        # Convert to response models
        search_results = []
        for result in results:
            search_result = SearchResult(
                file_path=result['file_path'],
                language=result['language'],
                similarity_score=result.get('similarity_score'),
                rank=result.get('rank'),
                matched_function=FunctionInfo(**result['matched_function']) if result.get('matched_function') else None,
                complexity_score=result.get('complexity_score'),
                functions=[FunctionInfo(**func) for func in result.get('functions', [])],
                classes=[ClassInfo(**cls) for cls in result.get('classes', [])],
                imports=[ImportInfo(**imp) for imp in result.get('imports', [])],
                metrics=MetricsInfo(**result.get('metrics', {}))
            )
            search_results.append(search_result)
        
        return search_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/analyze-alert", response_model=AlertAnalysisResult)
async def analyze_alert(request: AlertRequest):
    """Analyze an alert and provide relevant code insights."""
    try:
        alert_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Store alert in database if available
        if database and database.is_connected():
            alert_data = {
                'alert_type': request.alert_type,
                'alert_message': request.alert_message,
                'file_path': request.file_path,
                'line_number': request.line_number,
                'severity': request.severity,
                'analysis_result': {}
            }
            database.store_alert_data(alert_data)
        
        # Search for related code
        related_code = []
        if embedding_manager and embedding_manager.index:
            # Search for code related to the alert
            search_query = f"{request.alert_type} {request.alert_message}"
            search_results = embedding_manager.search_similar_code(search_query, 5)
            
            # Convert to response models
            for result in search_results:
                search_result = SearchResult(
                    file_path=result['file_path'],
                    language=result['language'],
                    similarity_score=result.get('similarity_score'),
                    rank=result.get('rank'),
                    functions=[FunctionInfo(**func) for func in result.get('functions', [])],
                    classes=[ClassInfo(**cls) for cls in result.get('classes', [])],
                    imports=[ImportInfo(**imp) for imp in result.get('imports', [])],
                    metrics=MetricsInfo(**result.get('metrics', {}))
                )
                related_code.append(search_result)
        
        # Generate suggested fixes (placeholder for future AI integration)
        suggested_fixes = [
            "Review the code for potential issues",
            "Check for proper error handling",
            "Verify input validation",
            "Consider refactoring complex functions"
        ]
        
        return AlertAnalysisResult(
            alert_id=alert_id,
            alert_type=request.alert_type,
            alert_message=request.alert_message,
            severity=request.severity,
            file_path=request.file_path,
            line_number=request.line_number,
            related_code=related_code,
            suggested_fixes=suggested_fixes,
            analysis_timestamp=start_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Alert analysis failed: {str(e)}")

@router.get("/stats/database", response_model=DatabaseStats)
async def get_database_stats():
    """Get database statistics."""
    try:
        if not database or not database.is_connected():
            raise HTTPException(status_code=503, detail="Database not connected")
        
        stats = database.get_database_stats()
        if 'error' in stats:
            raise HTTPException(status_code=500, detail=stats['error'])
        
        return DatabaseStats(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

@router.get("/stats/vector-index", response_model=VectorIndexStats)
async def get_vector_index_stats():
    """Get vector index statistics."""
    try:
        if not embedding_manager:
            raise HTTPException(status_code=503, detail="Vector index not available")
        
        stats = embedding_manager.get_index_stats()
        if 'error' in stats:
            raise HTTPException(status_code=500, detail=stats['error'])
        
        return VectorIndexStats(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vector index stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get vector index stats: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages."""
    try:
        return {
            "supported_languages": parser_factory.get_supported_languages(),
            "parser_info": parser_factory.get_parser_info()
        }
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported languages: {str(e)}") 