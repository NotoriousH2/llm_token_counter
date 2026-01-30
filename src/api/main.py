"""
FastAPI application entry point for LLM Token Counter
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from api.config import SETTINGS
from api.routes import tokens, models, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print(f"Starting LLM Token Counter API on {SETTINGS.host}:{SETTINGS.port}")
    yield
    # Shutdown
    print("Shutting down LLM Token Counter API")


# Create FastAPI app
app = FastAPI(
    title="LLM Token Counter API",
    description="API for counting tokens across various LLM models",
    version="2.0.0",
    lifespan=lifespan,
    root_path="/tokenizer",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tokens.router)
app.include_router(models.router)
app.include_router(websocket.router)


# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


# Serve React frontend static files
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Handle 404 errors - serve index.html for SPA routing"""
    # If it's an API request, return JSON error
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "Not found"}
        )

    # For non-API requests, serve index.html (SPA routing)
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    return JSONResponse(
        status_code=404,
        content={"error": "Not found"}
    )


# Mount static files if frontend build exists
if FRONTEND_DIR.exists():
    # Serve static assets
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Serve index.html at root
    @app.get("/", include_in_schema=False)
    async def serve_root():
        """Serve React app"""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Frontend not built. Run 'npm run build' in frontend/"}


def main():
    """Run the server"""
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=SETTINGS.host,
        port=SETTINGS.port,
        reload=False,
        workers=2,
    )


if __name__ == "__main__":
    main()
