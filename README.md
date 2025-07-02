# AI Code Analysis Microservice

A modular AI-driven code analysis microservice that analyzes code from Git repositories using Tree-sitter, generates Abstract Syntax Trees (AST), extracts key features, and provides vector-based semantic search capabilities.

## Features

### 🔍 **Code Analysis**
- **Multi-language Support**: Python, Go, Java with extensible parser architecture
- **AST Generation**: Deep code understanding using Tree-sitter
- **Feature Extraction**: Functions, classes, methods, imports, complexity metrics
- **Complexity Analysis**: Cyclomatic complexity calculation

### 🧠 **AI-Powered Search**
- **Vector Embeddings**: Code representation using sentence transformers
- **Semantic Search**: FAISS-based similarity search
- **Multiple Search Types**: Semantic, function name, complexity-based search

### 🗄️ **Data Management**
- **Database Integration**: PostgreSQL with optional MongoDB support
- **Historical Data**: Store analysis results and alert history
- **Optimized Queries**: Indexed database for fast retrieval

### 🔧 **Modular Architecture**
- **Parser Factory**: Extensible language parser system
- **Credential Management**: Secure environment-based configuration
- **Comprehensive Logging**: Multi-level logging with rotation
- **REST API**: FastAPI-based RESTful interface

### 🐳 **Deployment Ready**
- **Docker Support**: Containerized deployment
- **Docker Compose**: Multi-service orchestration
- **Health Checks**: Kubernetes-ready health endpoints

## Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- PostgreSQL (optional, for production)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-code-analysis-microservice
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Docker Deployment (Recommended)

```bash
# Build and start services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GIT_REPO_PATH=/path/to/your/repo
export DB_HOST=localhost
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_NAME=code_analysis

# Run the application
python app.py
```

## API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Health Check
```bash
GET /health
```

### Code Analysis
```bash
POST /analyze
Content-Type: application/json

{
  "file_path": "/path/to/file.py",
  "include_metrics": true,
  "include_embeddings": true
}
```

### Repository Analysis
```bash
POST /analyze
Content-Type: application/json

{
  "repository_path": "/path/to/repository",
  "language": "python",
  "include_metrics": true,
  "include_embeddings": true
}
```

### Semantic Search
```bash
POST /search
Content-Type: application/json

{
  "query": "database connection function",
  "search_type": "semantic",
  "top_k": 5,
  "language_filter": "python"
}
```

### Function Name Search
```bash
POST /search
Content-Type: application/json

{
  "query": "connect",
  "search_type": "function_name",
  "top_k": 10
}
```

### Alert Analysis
```bash
POST /analyze-alert
Content-Type: application/json

{
  "alert_type": "error",
  "alert_message": "Database connection failed",
  "file_path": "/path/to/file.py",
  "line_number": 42,
  "severity": "high"
}
```

### Statistics
```bash
GET /stats/database
GET /stats/vector-index
GET /languages
```

## Architecture

### Core Components

```
src/
├── config/
│   └── credential_manager.py    # Environment-based configuration
├── parsers/
│   ├── base_parser.py          # Abstract parser interface
│   ├── python_parser.py        # Python-specific parser
│   ├── go_parser.py           # Go-specific parser
│   ├── java_parser.py         # Java-specific parser
│   └── parser_factory.py      # Parser management
├── vectorization/
│   └── embedding_manager.py    # Vector embeddings and search
├── database/
│   ├── base_database.py       # Database interface
│   └── postgresql_database.py # PostgreSQL implementation
├── api/
│   ├── models.py              # Pydantic models
│   └── routes.py              # FastAPI routes
└── utils/
    └── logger.py              # Logging configuration
```

### Data Flow

1. **Code Input**: File or repository path
2. **Parsing**: Language-specific AST generation
3. **Feature Extraction**: Functions, classes, imports, metrics
4. **Vectorization**: Text embedding generation
5. **Storage**: Database persistence
6. **Search**: Vector-based similarity search
7. **API Response**: Structured JSON output

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GIT_REPO_PATH` | Local repository path | `/app/repo` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_USER` | Database user | `user` |
| `DB_PASSWORD` | Database password | `password` |
| `DB_NAME` | Database name | `code_analysis` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `5000` |
| `VECTOR_DIMENSION` | Embedding dimension | `384` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Database Schema

#### analysis_results
- `id`: Primary key
- `file_path`: Unique file path
- `language`: Programming language
- `functions`: JSONB function data
- `classes`: JSONB class data
- `imports`: JSONB import data
- `metrics`: JSONB metrics data
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

#### alert_data
- `id`: Primary key
- `alert_type`: Alert type
- `alert_message`: Alert message
- `file_path`: Related file path
- `line_number`: Related line number
- `severity`: Alert severity
- `analysis_result`: JSONB analysis data
- `created_at`: Creation timestamp

## Development

### Adding New Language Support

1. Create new parser in `src/parsers/`
2. Extend `BaseParser` class
3. Implement required methods
4. Register in `ParserFactory`

### Example Parser Structure

```python
from .base_parser import BaseParser

class NewLanguageParser(BaseParser):
    def __init__(self):
        super().__init__("new_language")
    
    def _setup_language(self):
        # Setup tree-sitter language
        pass
    
    def parse_file(self, file_path: str):
        # Parse file and extract features
        pass
    
    def extract_functions(self, tree):
        # Extract function definitions
        pass
    
    def extract_classes(self, tree):
        # Extract class definitions
        pass
    
    def extract_imports(self, tree):
        # Extract import statements
        pass
    
    def _get_default_file_patterns(self):
        return ['*.ext']
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_parsers.py::test_python_parser
```

## Monitoring and Logging

### Log Files
- Application logs: `/app/logs/app.log`
- Error logs: `/app/logs/error.log`
- Rotated logs: Compressed after 10MB

### Health Endpoints
- `/health`: Service health check
- `/ready`: Readiness probe
- `/api/v1/stats/*`: Component statistics

### Metrics
- Request processing time
- Database operation duration
- Vector search performance
- Error rates and types

## Production Deployment

### Docker Compose (Recommended)

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With custom configuration
docker-compose -f docker-compose.prod.yml up -d \
  -e DB_PASSWORD=secure_password \
  -e API_DEBUG=False
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-code-analysis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-code-analysis
  template:
    metadata:
      labels:
        app: ai-code-analysis
    spec:
      containers:
      - name: app
        image: ai-code-analysis:latest
        ports:
        - containerPort: 5000
        env:
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: host
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
```

## Troubleshooting

### Common Issues

1. **Tree-sitter Language Not Found**
   ```bash
   # Rebuild language library
   python -c "from tree_sitter import Language; Language.build_library('build/my-languages.so', ['vendor/tree-sitter-python'])"
   ```

2. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose ps db
   
   # View database logs
   docker-compose logs db
   ```

3. **Vector Index Not Loading**
   ```bash
   # Check index file exists
   ls -la /app/data/
   
   # Rebuild index
   curl -X POST http://localhost:5000/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"repository_path": "/app/repo", "include_embeddings": true}'
   ```

### Performance Optimization

1. **Database Indexing**
   - Ensure all query columns are indexed
   - Use JSONB indexes for complex queries

2. **Vector Search**
   - Use appropriate FAISS index type
   - Consider GPU acceleration for large datasets

3. **Caching**
   - Implement Redis for frequent queries
   - Cache parsed ASTs for repeated analysis

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue
- Check documentation
- Review troubleshooting guide 