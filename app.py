from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
import uuid

from src.api.routes import router
from src.config.credential_manager import CredentialManager
from src.utils.logger import get_logger

# Initialize components
cred_manager = CredentialManager()
logger_setup = get_logger()

# Create FastAPI app
app = FastAPI(
    title="AI Code Analysis Microservice",
    description="A modular AI-driven code analysis microservice with vector search capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request
    logger_setup.log_api_request(
        method=request.method,
        path=str(request.url.path),
        status_code=200,  # Will be updated after response
        duration=0.0  # Will be updated after response
    )
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log response
        logger_setup.log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger_setup.log_error(e, f"Request {request_id}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            }
        )

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "AI Code Analysis Microservice",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration."""
    try:
        # Check if essential components are available
        api_config = cred_manager.get_api_config()
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "credential_manager": "ready",
                "api_config": "ready"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    api_config = cred_manager.get_api_config()
    
    uvicorn.run(
        "app:app",
        host=api_config['host'],
        port=api_config['port'],
        reload=api_config['debug'],
        log_level="info"
    ) 