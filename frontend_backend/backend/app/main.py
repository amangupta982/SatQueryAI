from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import images, grounding, change, multimodal
from app.core.exceptions import SatQueryError
from app.core.config import core_settings

app = FastAPI(
    title="SatQuery AI Backend",
    version="1.0.0",
    description="Backend API for SatQuery AI"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(SatQueryError)
async def satquery_exception_handler(request: Request, exc: SatQueryError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.message},
    )

# Routers
app.include_router(images.router, prefix="/api/v1")
app.include_router(grounding.router, prefix="/api/v1")
app.include_router(change.router, prefix="/api/v1")
app.include_router(multimodal.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to SatQuery AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
