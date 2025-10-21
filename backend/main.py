from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routes import auth_routes, assistant_routes, admin_routes, slack_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing database...")
    init_db()
    print("Database initialized!")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Amida AI Personal Assistant",
    description="Agentic AI Personal Assistant for Amida Organization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(assistant_routes.router)
app.include_router(admin_routes.router)
app.include_router(slack_bot.router)


@app.get("/")
async def root():
    return {
        "message": "Amida AI Personal Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
