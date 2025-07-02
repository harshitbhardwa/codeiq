# AI Code Analysis Microservice - Flow Diagrams

## Quick Overview Diagrams

### 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "External Systems"
        CLIENT[HTTP Client]
        N8N[n8n Workflow]
    end
    
    subgraph "AI Code Analysis Microservice"
        API[FastAPI Application]
        PARSER[Parser Factory]
        AI[AI Embeddings]
        DB[(PostgreSQL)]
        VECTOR[(FAISS Vector DB)]
    end
    
    subgraph "Supported Languages"
        PY[Python]
        GO[Go]
        JAVA[Java]
    end
    
    CLIENT --> API
    N8N --> API
    API --> PARSER
    API --> AI
    API --> DB
    API --> VECTOR
    PARSER --> PY
    PARSER --> GO
    PARSER --> JAVA
```

### 2. Main Data Flow - Code Analysis

```mermaid
flowchart TD
    A[Code File/Repository] --> B[Parser Factory]
    B --> C[Language-Specific Parser]
    C --> D[AST Generation]
    D --> E[Feature Extraction]
    E --> F[Database Storage]
    E --> G[AI Embedding]
    G --> H[Vector Index]
    F --> I[Analysis Result]
    H --> I
    I --> J[API Response]
```

### 3. Search Flow

```mermaid
flowchart LR
    A[Search Query] --> B[Query Processing]
    B --> C{Search Type}
    C -->|Semantic| D[AI Embedding]
    C -->|Function Name| E[Text Search]
    C -->|Complexity| F[Range Filter]
    D --> G[Vector Search]
    E --> G
    F --> G
    G --> H[Result Ranking]
    H --> I[API Response]
```

### 4. Alert Analysis Flow

```mermaid
flowchart TD
    A[Alert from n8n] --> B[Alert Storage]
    B --> C[Related Code Search]
    C --> D[AI-Powered Analysis]
    D --> E[Insight Generation]
    E --> F[Suggested Fixes]
    F --> G[Response to n8n]
```

## Detailed Component Flows

### 5. Parser Factory Pattern

```mermaid
graph LR
    subgraph "Parser Factory"
        A[File Extension] --> B{Language Detection}
        B -->|.py| C[Python Parser]
        B -->|.go| D[Go Parser]
        B -->|.java| E[Java Parser]
    end
    
    subgraph "Tree-sitter Integration"
        C --> F[Python AST]
        D --> G[Go AST]
        E --> H[Java AST]
    end
    
    subgraph "Feature Extraction"
        F --> I[Functions, Classes, Imports]
        G --> I
        H --> I
    end
```

### 6. Vector Search Pipeline

```mermaid
graph TD
    subgraph "Input Processing"
        A[Code Data] --> B[Text Representation]
        B --> C[Function Definitions]
        B --> D[Class Definitions]
        B --> E[Import Statements]
    end
    
    subgraph "AI Processing"
        C --> F[Sentence Transformers]
        D --> F
        E --> F
        F --> G[384-D Vector]
    end
    
    subgraph "Storage & Search"
        G --> H[FAISS Index]
        H --> I[Similarity Search]
        I --> J[Ranked Results]
    end
```

### 7. Database Operations

```mermaid
graph LR
    subgraph "Analysis Results"
        A[Code Analysis] --> B[PostgreSQL]
        B --> C[JSONB Storage]
        C --> D[Indexed Queries]
    end
    
    subgraph "Alert Data"
        E[Alert Information] --> F[Alert Table]
        F --> G[Historical Data]
    end
    
    subgraph "Statistics"
        H[System Stats] --> I[Performance Metrics]
        I --> J[Health Monitoring]
    end
```

## API Endpoint Flows

### 8. Code Analysis Endpoint

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Parser
    participant DB
    participant AI
    
    Client->>API: POST /analyze
    API->>Parser: Parse Code
    Parser->>API: AST Data
    API->>DB: Store Results
    API->>AI: Create Embeddings
    AI->>API: Vector Data
    API->>Client: Analysis Result
```

### 9. Search Endpoint

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant AI
    participant VectorDB
    
    Client->>API: POST /search
    API->>AI: Process Query
    AI->>VectorDB: Search Vectors
    VectorDB->>AI: Similar Results
    AI->>API: Ranked Results
    API->>Client: Search Results
```

### 10. Alert Analysis Endpoint

```mermaid
sequenceDiagram
    participant N8N
    participant API
    participant DB
    participant AI
    
    N8N->>API: POST /analyze-alert
    API->>DB: Store Alert
    API->>AI: Find Related Code
    AI->>API: Code Insights
    API->>N8N: Analysis + Suggestions
```

## Deployment Flows

### 11. Docker Deployment

```mermaid
graph TB
    subgraph "Docker Compose"
        A[App Container] --> B[PostgreSQL Container]
        A --> C[Volume: Logs]
        A --> D[Volume: Data]
    end
    
    subgraph "External Access"
        E[HTTP Client] --> A
        F[n8n] --> A
    end
```

### 12. Production Scaling

```mermaid
graph TD
    subgraph "Load Balancer"
        A[NGINX/HAProxy]
    end
    
    subgraph "Application Instances"
        B[App Instance 1]
        C[App Instance 2]
        D[App Instance N]
    end
    
    subgraph "Database Layer"
        E[Primary DB]
        F[Read Replica]
    end
    
    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> F
```

## Monitoring & Health Checks

### 13. Health Check Flow

```mermaid
flowchart TD
    A[Health Check Request] --> B[Database Connection]
    A --> C[Vector Index Status]
    A --> D[Parser Availability]
    B --> E{All Healthy?}
    C --> E
    D --> E
    E -->|Yes| F[200 OK]
    E -->|No| G[503 Service Unavailable]
```

### 14. Logging Flow

```mermaid
graph LR
    subgraph "Log Sources"
        A[API Requests]
        B[Parser Operations]
        C[Database Operations]
        D[Error Events]
    end
    
    subgraph "Log Processing"
        E[Console Output]
        F[File Storage]
        G[Error Logs]
        H[Compression]
    end
    
    A --> E
    A --> F
    B --> E
    B --> F
    C --> E
    C --> F
    D --> G
    F --> H
    G --> H
```

## Integration Flows

### 15. n8n Integration

```mermaid
graph TD
    subgraph "n8n Workflow"
        A[Alert Trigger] --> B[HTTP Request]
        B --> C[Process Response]
        C --> D[Next Action]
    end
    
    subgraph "AI Code Analysis"
        E[Alert Analysis] --> F[Code Search]
        F --> G[Insight Generation]
        G --> H[Response]
    end
    
    B --> E
    H --> C
```

### 16. Multi-Language Support

```mermaid
graph LR
    subgraph "Input Files"
        A[Python Files]
        B[Go Files]
        C[Java Files]
    end
    
    subgraph "Processing"
        D[Python Parser]
        E[Go Parser]
        F[Java Parser]
    end
    
    subgraph "Output"
        G[Unified JSON Format]
        H[Vector Embeddings]
        I[Database Storage]
    end
    
    A --> D
    B --> E
    C --> F
    D --> G
    E --> G
    F --> G
    G --> H
    G --> I
```

## Performance & Caching

### 17. Caching Strategy

```mermaid
graph TD
    subgraph "Parser Caching"
        A[Parser Factory] --> B[Parser Instances]
        B --> C[Reuse Parsers]
    end
    
    subgraph "Vector Caching"
        D[Embedding Manager] --> E[FAISS Index]
        E --> F[In-Memory Vectors]
    end
    
    subgraph "Database Caching"
        G[PostgreSQL] --> H[Connection Pool]
        H --> I[Query Cache]
    end
```

### 18. Scalability Patterns

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        A[Load Balancer] --> B[App Instance 1]
        A --> C[App Instance 2]
        A --> D[App Instance N]
    end
    
    subgraph "Database Scaling"
        E[Primary DB] --> F[Read Replica 1]
        E --> G[Read Replica 2]
    end
    
    subgraph "Vector Scaling"
        H[FAISS Index 1] --> I[Sharded Indices]
        I --> J[FAISS Index N]
    end
```

These diagrams provide a comprehensive visual understanding of the AI Code Analysis Microservice architecture and data flows, suitable for both technical and non-technical stakeholders. 