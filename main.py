from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import close_db, init_db
from routers import auth, expenses


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB and initialize Beanie ODM on startup.
    await init_db()
    yield
    await close_db()


app = FastAPI(title="ExpenseTracker API", lifespan=lifespan)

# Setup CORS origins from config + sensible local defaults
origins = [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]
defaults = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5050",
    "http://127.0.0.1:5050",
]
for d in defaults:
    if d not in origins:
        origins.append(d)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure unhandled exceptions return application/json with CORS headers instead of text/plain."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/")
def health() -> dict:
    return {"status": "ok"}

