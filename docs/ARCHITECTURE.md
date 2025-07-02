# AI Code Analysis Microservice - Architecture & Flow Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Component Interactions](#component-interactions)
5. [API Flow](#api-flow)
6. [Database Schema](#database-schema)
7. [Vector Search Pipeline](#vector-search-pipeline)
8. [Monitoring & Logging](#monitoring--logging)
9. [Deployment Architecture](#deployment-architecture)

## System Overview

The AI Code Analysis Microservice is a modular, event-driven system designed for intelligent code analysis and semantic search. It combines traditional AST parsing with modern AI-powered vector embeddings to provide comprehensive code insights.

### Key Features
- **Multi-language Support**: Python, Go, Java with extensible parser architecture
- **AI-Powered Search**: Semantic code search using sentence transformers
- **Vector Database**: FAISS-based similarity search for code patterns
- **Modular Design**: Clean separation of concerns with factory patterns
- **Comprehensive Logging**: Multi-level logging with request tracking
- **Docker Ready**: Production-ready containerization

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        CLIENT[HTTP Client]
        N8N[n8n Workflow]
    end
    
    subgraph "API Gateway"
        FASTAPI[FastAPI Application]
        MIDDLEWARE[Request Middleware]
        ROUTES[API Routes]
    end
    
    subgraph "Core Services"
        PARSER_FACTORY[Parser Factory]
        EMBEDDING_MGR[Embedding Manager]
        CRED_MGR[Credential Manager]
        LOGGER[Logger Setup]
    end
    
    subgraph "Language Parsers"
        PYTHON_PARSER[Python Parser]
        GO_PARSER[Go Parser]
        JAVA_PARSER[Java Parser]
        TREE_SITTER[Tree-sitter]
    end
    
    subgraph "AI & Vector"
        SENTENCE_TRANSFORMERS[Sentence Transformers]
        FAISS[FAISS Vector Index]
        VECTOR_DB[(Vector Database)]
    end
    
    subgraph "Data Storage"
        POSTGRES[(PostgreSQL)]
        ALERT_TABLE[Alert Data]
        ANALYSIS_TABLE[Analysis Results]
    end
    
    subgraph "Monitoring"
        HEALTH_CHECK[Health Check]
        STATS[Statistics]
        LOGS[Log Files]
    end
    
    CLIENT --> FASTAPI
    N8N --> FASTAPI
    FASTAPI --> MIDDLEWARE
    MIDDLEWARE --> ROUTES
    ROUTES --> PARSER_FACTORY
    ROUTES --> EMBEDDING_MGR
    ROUTES --> CRED_MGR
    ROUTES --> LOGGER
    
    PARSER_FACTORY --> PYTHON_PARSER
    PARSER_FACTORY --> GO_PARSER
    PARSER_FACTORY --> JAVA_PARSER
    PYTHON_PARSER --> TREE_SITTER
    GO_PARSER --> TREE_SITTER
    JAVA_PARSER --> TREE_SITTER
    
    EMBEDDING_MGR --> SENTENCE_TRANSFORMERS
    EMBEDDING_MGR --> FAISS
    FAISS --> VECTOR_DB
    
    ROUTES --> POSTGRES
    POSTGRES --> ALERT_TABLE
    POSTGRES --> ANALYSIS_TABLE
    
    ROUTES --> HEALTH_CHECK
    ROUTES --> STATS
    LOGGER --> LOGS
```

## Data Flow Diagrams

### 1. Code Analysis Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant ParserFactory
    participant TreeSitter
    participant Database
    participant EmbeddingManager
    participant FAISS
    
    Client->>FastAPI: POST /api/v1/analyze
    Note over Client,FastAPI: {file_path: "/path/to/file.py", include_embeddings: true}
    
    FastAPI->>ParserFactory: get_parser_by_file_extension()
    ParserFactory->>FastAPI: PythonParser instance
    
    FastAPI->>TreeSitter: parse_file(file_path)
    TreeSitter->>FastAPI: AST with functions, classes, imports, metrics
    
    FastAPI->>Database: store_analysis_result(result)
    Database->>FastAPI: Success confirmation
    
    alt include_embeddings is true
        FastAPI->>EmbeddingManager: create_embeddings([result])
        EmbeddingManager->>FAISS: build_faiss_index(embeddings_data)
        FAISS->>EmbeddingManager: Index updated
        EmbeddingManager->>FastAPI: Embeddings created
    end
    
    FastAPI->>Client: AnalysisResult with structured data
```

### 2. Semantic Search Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant EmbeddingManager
    participant FAISS
    participant Database
    
    Client->>FastAPI: POST /api/v1/search
    Note over Client,FastAPI: {query: "database connection", search_type: "semantic", top_k: 5}
    
    FastAPI->>EmbeddingManager: search_similar_code(query, top_k)
    EmbeddingManager->>FAISS: search(query_embedding, top_k)
    FAISS->>EmbeddingManager: (scores, indices)
    
    EmbeddingManager->>Database: get_analysis_results(indices)
    Database->>EmbeddingManager: Code data with metadata
    
    EmbeddingManager->>FastAPI: Search results with similarity scores
    FastAPI->>Client: List[SearchResult] with ranked results
```

### 3. Alert Analysis Flow

```mermaid
sequenceDiagram
    participant N8N
    participant FastAPI
    participant Database
    participant EmbeddingManager
    participant FAISS
    
    N8N->>FastAPI: POST /api/v1/analyze-alert
    Note over N8N,FastAPI: {alert_type: "error", alert_message: "DB connection failed", severity: "high"}
    
    FastAPI->>Database: store_alert_data(alert_data)
    Database->>FastAPI: Alert stored with ID
    
    FastAPI->>EmbeddingManager: search_similar_code(alert_query, 5)
    EmbeddingManager->>FAISS: search(alert_embedding, 5)
    FAISS->>EmbeddingManager: Related code indices
    
    EmbeddingManager->>Database: get_analysis_results(indices)
    Database->>EmbeddingManager: Related code data
    
    FastAPI->>N8N: AlertAnalysisResult with insights and suggestions
```

## Component Interactions

### Parser Factory Pattern

```mermaid
classDiagram
    class ParserFactory {
        -_parsers: Dict[str, BaseParser]
        -_supported_languages: Dict[str, Type]
        +get_parser(language: str): BaseParser
        +get_parser_by_file_extension(path: str): BaseParser
        +get_supported_languages(): List[str]
    }
    
    class BaseParser {
        <<abstract>>
        +language: str
        +parse_file(file_path: str): Dict
        +parse_repository(repo_path: str): Dict
        +extract_functions(tree): List[Dict]
        +extract_classes(tree): List[Dict]
        +extract_imports(tree): List[Dict]
        +calculate_metrics(tree): Dict
    }
    
    class PythonParser {
        +language: str = "python"
        +_setup_language()
        +parse_file(file_path: str): Dict
        +extract_functions(tree): List[Dict]
        +extract_classes(tree): List[Dict]
        +extract_imports(tree): List[Dict]
    }
    
    class GoParser {
        +language: str = "go"
        +_setup_language()
        +parse_file(file_path: str): Dict
        +extract_functions(tree): List[Dict]
        +extract_classes(tree): List[Dict]
        +extract_imports(tree): List[Dict]
    }
    
    class JavaParser {
        +language: str = "java"
        +_setup_language()
        +parse_file(file_path: str): Dict
        +extract_functions(tree): List[Dict]
        +extract_classes(tree): List[Dict]
        +extract_imports(tree): List[Dict]
    }
    
    ParserFactory --> BaseParser
    BaseParser <|-- PythonParser
    BaseParser <|-- GoParser
    BaseParser <|-- JavaParser
```

### Database Abstraction Layer

```mermaid
classDiagram
    class BaseDatabase {
        <<abstract>>
        +config: Dict
        +connected: bool
        +connect(): bool
        +disconnect()
        +store_analysis_result(data): bool
        +get_analysis_result(file_path): Dict
        +store_alert_data(data): bool
        +get_alert_history(limit): List[Dict]
        +search_analysis_results(query): List[Dict]
        +get_database_stats(): Dict
    }
    
    class PostgreSQLDatabase {
        +connection: psycopg2.Connection
        +connect(): bool
        +disconnect()
        +store_analysis_result(data): bool
        +get_analysis_result(file_path): Dict
        +store_alert_data(data): bool
        +get_alert_history(limit): List[Dict]
        +search_analysis_results(query): List[Dict]
        +get_database_stats(): Dict
        -_create_tables()
        -_create_indexes()
    }
    
    BaseDatabase <|-- PostgreSQLDatabase
```

## API Flow

### Request Processing Pipeline

```mermaid
graph LR
    subgraph "Request Processing"
        A[HTTP Request] --> B[FastAPI Router]
        B --> C[Request Middleware]
        C --> D[Logging Middleware]
        D --> E[API Endpoint]
        E --> F[Business Logic]
        F --> G[Response Middleware]
        G --> H[HTTP Response]
    end
    
    subgraph "Middleware Stack"
        I[Process Time Header]
        J[Request Logging]
        K[Error Handling]
        L[CORS Headers]
    end
    
    C --> I
    C --> J
    C --> K
    C --> L
```

### API Endpoints Flow

```mermaid
graph TD
    subgraph "API Endpoints"
        A[POST /analyze] --> B[Code Analysis]
        C[POST /search] --> D[Vector Search]
        E[POST /analyze-alert] --> F[Alert Analysis]
        G[GET /health] --> H[Health Check]
        I[GET /stats/*] --> J[Statistics]
        K[GET /languages] --> L[Supported Languages]
    end
    
    subgraph "Core Operations"
        B --> M[Parser Factory]
        B --> N[Tree-sitter Parsing]
        B --> O[Database Storage]
        B --> P[Vector Embedding]
        
        D --> Q[Embedding Manager]
        D --> R[FAISS Search]
        D --> S[Result Ranking]
        
        F --> T[Alert Storage]
        F --> U[Related Code Search]
        F --> V[Insight Generation]
    end
    
    subgraph "Response Models"
        W[AnalysisResult]
        X[SearchResult]
        Y[AlertAnalysisResult]
        Z[HealthCheck]
    end
    
    B --> W
    D --> X
    F --> Y
    H --> Z
```

## Database Schema

### Analysis Results Table

```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) UNIQUE NOT NULL,
    language VARCHAR(50) NOT NULL,
    functions JSONB,
    classes JSONB,
    imports JSONB,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_analysis_file_path ON analysis_results(file_path);
CREATE INDEX idx_analysis_language ON analysis_results(language);
CREATE INDEX idx_analysis_created_at ON analysis_results(created_at);
CREATE INDEX idx_analysis_functions ON analysis_results USING GIN(functions);
CREATE INDEX idx_analysis_classes ON analysis_results USING GIN(classes);
```

### Alert Data Table

```sql
CREATE TABLE alert_data (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100) NOT NULL,
    alert_message TEXT NOT NULL,
    file_path VARCHAR(500),
    line_number INTEGER,
    severity VARCHAR(20),
    analysis_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for alert queries
CREATE INDEX idx_alert_type ON alert_data(alert_type);
CREATE INDEX idx_alert_severity ON alert_data(severity);
CREATE INDEX idx_alert_created_at ON alert_data(created_at);
CREATE INDEX idx_alert_file_path ON alert_data(file_path);
```

## Vector Search Pipeline

### Embedding Generation Process

```mermaid
graph TD
    A[Code Data] --> B[Text Representation]
    B --> C[Sentence Transformers]
    C --> D[384-Dimensional Vector]
    D --> E[FAISS Index]
    E --> F[Vector Database]
    
    subgraph "Text Representation"
        G[Function Definitions]
        H[Class Definitions]
        I[Import Statements]
        J[Code Comments]
        K[File Structure]
    end
    
    B --> G
    B --> H
    B --> I
    B --> J
    B --> K
```

### Search Types

```mermaid
graph LR
    subgraph "Search Types"
        A[Semantic Search] --> B[Query Embedding]
        C[Function Name Search] --> D[Text Matching]
        E[Complexity Search] --> F[Range Filtering]
    end
    
    subgraph "Processing"
        B --> G[Vector Similarity]
        D --> H[Exact/Partial Match]
        F --> I[Complexity Filter]
    end
    
    subgraph "Results"
        G --> J[Ranked by Similarity]
        H --> K[Filtered by Name]
        I --> L[Filtered by Complexity]
    end
```

## Monitoring & Logging

### Logging Architecture

```mermaid
graph TD
    subgraph "Log Sources"
        A[API Requests]
        B[Parser Operations]
        C[Database Operations]
        D[Vector Operations]
        E[Error Events]
    end
    
    subgraph "Logger Setup"
        F[Console Logger]
        G[File Logger]
        H[Error Logger]
        I[Request Logger]
    end
    
    subgraph "Log Storage"
        J[app.log - Main Logs]
        K[error.log - Error Logs]
        L[Compressed Archives]
    end
    
    A --> F
    A --> G
    A --> I
    B --> F
    B --> G
    C --> F
    C --> G
    D --> F
    D --> G
    E --> H
    E --> K
    
    G --> J
    H --> K
    J --> L
    K --> L
```

### Health Check Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Database
    participant EmbeddingManager
    participant ParserFactory
    
    Client->>FastAPI: GET /api/v1/health
    
    FastAPI->>Database: is_connected()
    Database->>FastAPI: Connection status
    
    FastAPI->>EmbeddingManager: index is not None
    EmbeddingManager->>FastAPI: Index status
    
    FastAPI->>ParserFactory: get_supported_languages()
    ParserFactory->>FastAPI: Language list
    
    FastAPI->>Client: HealthCheck response
    Note over FastAPI,Client: {status: "healthy", database_connected: true, vector_index_loaded: true, supported_languages: ["python", "go", "java"]}
```

## Deployment Architecture

### Docker Compose Setup

```mermaid
graph TB
    subgraph "Docker Compose Services"
        A[app:5000] --> B[PostgreSQL:5432]
        A --> C[Volume: logs]
        A --> D[Volume: data]
        A --> E[Volume: repo]
    end
    
    subgraph "External Access"
        F[HTTP Client] --> A
        G[n8n Workflow] --> A
    end
    
    subgraph "Persistent Storage"
        H[postgres_data] --> B
        I[logs] --> C
        J[faiss_index] --> D
        K[git_repos] --> E
    end
```

### Production Deployment

```mermaid
graph TD
    subgraph "Load Balancer"
        A[NGINX/HAProxy]
    end
    
    subgraph "Application Layer"
        B[AI Code Analysis App 1]
        C[AI Code Analysis App 2]
        D[AI Code Analysis App N]
    end
    
    subgraph "Database Layer"
        E[PostgreSQL Primary]
        F[PostgreSQL Replica]
    end
    
    subgraph "Storage Layer"
        G[Shared Volume - Logs]
        H[Shared Volume - Data]
        I[Shared Volume - Repos]
    end
    
    subgraph "Monitoring"
        J[Prometheus]
        K[Grafana]
        L[Log Aggregator]
    end
    
    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> F
    B --> G
    C --> G
    D --> G
    B --> H
    C --> H
    D --> H
    B --> I
    C --> I
    D --> I
    B --> J
    C --> J
    D --> J
    J --> K
    B --> L
    C --> L
    D --> L
```

## Performance Considerations

### Caching Strategy

```mermaid
graph LR
    subgraph "Parser Caching"
        A[Parser Factory] --> B[Parser Cache]
        B --> C[Python Parser]
        B --> D[Go Parser]
        B --> E[Java Parser]
    end
    
    subgraph "Vector Caching"
        F[Embedding Manager] --> G[FAISS Index]
        G --> H[In-Memory Vectors]
    end
    
    subgraph "Database Caching"
        I[PostgreSQL] --> J[Query Cache]
        J --> K[Connection Pool]
    end
```

### Scalability Patterns

1. **Horizontal Scaling**: Multiple app instances behind load balancer
2. **Database Scaling**: Read replicas for search operations
3. **Vector Index Scaling**: Sharded FAISS indices for large datasets
4. **Caching**: Redis for frequently accessed data
5. **Async Processing**: Background tasks for heavy operations

## Security Considerations

### Authentication & Authorization

```mermaid
graph TD
    A[API Request] --> B[Authentication Middleware]
    B --> C{Valid Token?}
    C -->|Yes| D[Authorization Check]
    C -->|No| E[401 Unauthorized]
    D --> F{Has Permission?}
    F -->|Yes| G[Process Request]
    F -->|No| H[403 Forbidden]
```

### Data Protection

1. **Environment Variables**: Sensitive data in environment variables
2. **Database Encryption**: Encrypted connections and data at rest
3. **Input Validation**: Pydantic models for request validation
4. **Rate Limiting**: API rate limiting to prevent abuse
5. **Audit Logging**: Comprehensive audit trails

This architecture provides a robust, scalable, and maintainable foundation for AI-powered code analysis with clear separation of concerns and comprehensive monitoring capabilities. 

# Git repository configuration
GIT_REPO_PATH=/app/repo

# Database configuration
DB_TYPE=postgresql
DB_HOST=db
DB_PORT=5432
DB_USER=code_analysis_user
DB_PASSWORD=code_analysis_password
DB_NAME=code_analysis_db

# MongoDB configuration (if using MongoDB instead)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=code_analysis

# API configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# Vector database configuration
VECTOR_DIMENSION=384
FAISS_INDEX_PATH=/app/data/faiss_index

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# External API keys (for future AI features)
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here

# Security (for production)
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com 