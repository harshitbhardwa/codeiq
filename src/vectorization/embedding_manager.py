import numpy as np
import faiss
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from loguru import logger
import time

class EmbeddingManager:
    """
    Manages code embedding and vector search functionality.
    Uses sentence transformers for embedding and FAISS for efficient similarity search.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', dimension: int = 384):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: Name of the sentence transformer model to use
            dimension: Dimension of the embedding vectors
        """
        self.model_name = model_name
        self.dimension = dimension
        self.model = None
        self.index = None
        self.code_metadata = []
        self.index_path = None
        
        self._load_model()
        logger.info(f"EmbeddingManager initialized with model: {model_name}")
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded sentence transformer model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            raise
    
    def create_embeddings(self, code_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create embeddings for code snippets.
        
        Args:
            code_data: List of dictionaries containing code information
            
        Returns:
            List of dictionaries with embeddings added
        """
        if not code_data:
            return []
        
        start_time = time.time()
        embeddings_data = []
        
        for item in code_data:
            try:
                # Create text representation for embedding
                text_for_embedding = self._create_text_representation(item)
                
                # Generate embedding
                embedding = self.model.encode([text_for_embedding])[0]
                
                # Add embedding to item
                item_with_embedding = item.copy()
                item_with_embedding['embedding'] = embedding.tolist()
                item_with_embedding['text_for_embedding'] = text_for_embedding
                
                embeddings_data.append(item_with_embedding)
                
            except Exception as e:
                logger.error(f"Error creating embedding for item: {str(e)}")
                continue
        
        duration = time.time() - start_time
        logger.info(f"Created {len(embeddings_data)} embeddings in {duration:.3f}s")
        
        return embeddings_data
    
    def _create_text_representation(self, code_item: Dict[str, Any]) -> str:
        """
        Create a text representation of code for embedding.
        
        Args:
            code_item: Dictionary containing code information
            
        Returns:
            Text representation suitable for embedding
        """
        parts = []
        
        # Add file path and language
        parts.append(f"File: {code_item.get('file_path', 'unknown')}")
        parts.append(f"Language: {code_item.get('language', 'unknown')}")
        
        # Add function/method information
        if 'functions' in code_item:
            for func in code_item['functions']:
                func_text = f"Function: {func.get('name', 'unknown')}"
                if func.get('parameters'):
                    params = ', '.join(func['parameters'])
                    func_text += f" Parameters: {params}"
                if func.get('body_text'):
                    func_text += f" Body: {func['body_text'][:200]}..."  # Truncate for embedding
                parts.append(func_text)
        
        # Add class information
        if 'classes' in code_item:
            for cls in code_item['classes']:
                class_text = f"Class: {cls.get('name', 'unknown')}"
                if cls.get('methods'):
                    methods = ', '.join([m.get('name', 'unknown') for m in cls['methods']])
                    class_text += f" Methods: {methods}"
                if cls.get('body_text'):
                    class_text += f" Body: {cls['body_text'][:200]}..."
                parts.append(class_text)
        
        # Add import information
        if 'imports' in code_item:
            imports = [imp.get('text', '') for imp in code_item['imports']]
            if imports:
                parts.append(f"Imports: {' '.join(imports)}")
        
        # Add metrics
        if 'metrics' in code_item:
            metrics = code_item['metrics']
            metrics_text = f"Metrics: Lines={metrics.get('total_lines', 0)}, "
            metrics_text += f"Complexity={metrics.get('average_complexity', 0):.2f}"
            parts.append(metrics_text)
        
        return ' '.join(parts)
    
    def build_faiss_index(self, embeddings_data: List[Dict[str, Any]], index_path: Optional[str] = None):
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings_data: List of dictionaries containing embeddings
            index_path: Path to save the index
        """
        if not embeddings_data:
            logger.warning("No embeddings data provided for index building")
            return
        
        start_time = time.time()
        
        # Extract embeddings and metadata
        embeddings = np.array([item['embedding'] for item in embeddings_data], dtype=np.float32)
        self.code_metadata = [item for item in embeddings_data]
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.index.add(embeddings)
        
        # Save index and metadata
        if index_path:
            self.index_path = Path(index_path)
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            metadata_path = self.index_path.with_suffix('.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.code_metadata, f)
        
        duration = time.time() - start_time
        logger.info(f"Built FAISS index with {len(embeddings_data)} vectors in {duration:.3f}s")
    
    def create_empty_index(self):
        """Create an empty FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.code_metadata = []
        logger.info("Created empty FAISS index")
    
    def load_faiss_index(self, index_path: str):
        """
        Load existing FAISS index or create empty one if it doesn't exist.
        
        Args:
            index_path: Path to the FAISS index file
        """
        try:
            self.index_path = Path(index_path)
            
            # Check if index file exists
            if not self.index_path.exists():
                logger.info(f"FAISS index file not found at {index_path}, creating empty index")
                self.create_empty_index()
                return
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            metadata_path = self.index_path.with_suffix('.pkl')
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.code_metadata = pickle.load(f)
            else:
                logger.warning(f"Metadata file not found at {metadata_path}, using empty metadata")
                self.code_metadata = []
            
            logger.info(f"Loaded FAISS index from {index_path} with {len(self.code_metadata)} vectors")
            
        except Exception as e:
            logger.error(f"Error loading FAISS index from {index_path}: {str(e)}")
            logger.info("Creating empty index as fallback")
            self.create_empty_index()
    
    def search_similar_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar code based on a text query.
        
        Args:
            query: Text query to search for
            top_k: Number of top results to return
            
        Returns:
            List of similar code items with similarity scores
        """
        if not self.index or not self.code_metadata:
            logger.warning("No FAISS index available for search")
            return []
        
        try:
            # Create embedding for query
            query_embedding = self.model.encode([query])[0].reshape(1, -1).astype(np.float32)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.code_metadata)))
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.code_metadata):
                    result = self.code_metadata[idx].copy()
                    result['similarity_score'] = float(score)
                    result['rank'] = i + 1
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar code items for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar code: {str(e)}")
            return []
    
    def search_by_function_name(self, function_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for code by function name.
        
        Args:
            function_name: Name of the function to search for
            top_k: Number of top results to return
            
        Returns:
            List of matching code items
        """
        results = []
        
        for item in self.code_metadata:
            if 'functions' in item:
                for func in item['functions']:
                    if function_name.lower() in func.get('name', '').lower():
                        result = item.copy()
                        result['matched_function'] = func
                        results.append(result)
                        if len(results) >= top_k:
                            break
                if len(results) >= top_k:
                    break
        
        logger.info(f"Found {len(results)} items with function name: {function_name}")
        return results[:top_k]
    
    def search_by_complexity_range(self, min_complexity: float, max_complexity: float) -> List[Dict[str, Any]]:
        """
        Search for code within a complexity range.
        
        Args:
            min_complexity: Minimum complexity threshold
            max_complexity: Maximum complexity threshold
            
        Returns:
            List of code items within the complexity range
        """
        results = []
        
        for item in self.code_metadata:
            if 'metrics' in item:
                avg_complexity = item['metrics'].get('average_complexity', 0)
                if min_complexity <= avg_complexity <= max_complexity:
                    result = item.copy()
                    result['complexity_score'] = avg_complexity
                    results.append(result)
        
        # Sort by complexity
        results.sort(key=lambda x: x['complexity_score'], reverse=True)
        
        logger.info(f"Found {len(results)} items with complexity between {min_complexity} and {max_complexity}")
        return results
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index."""
        if not self.index:
            return {'error': 'No index available'}
        
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.index.d,
            'index_type': type(self.index).__name__,
            'metadata_count': len(self.code_metadata)
        }
    
    def clear_index(self):
        """Clear the current index and metadata."""
        self.index = None
        self.code_metadata = []
        logger.info("Cleared FAISS index and metadata") 