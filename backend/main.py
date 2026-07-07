from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import rules, evaluate, audit, seed_routes

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Configurable Business Rules Engine",
    description="API for managing and evaluating lending rules",
    version="1.0.0",
)

# Enable CORS for React frontend (running on different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rules.router)
app.include_router(evaluate.router)
app.include_router(audit.router)
app.include_router(seed_routes.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Configurable Business Rules Engine API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
