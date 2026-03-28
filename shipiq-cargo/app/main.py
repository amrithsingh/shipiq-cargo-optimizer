"""Application entry point — creates the FastAPI app and mounts the router."""

import os

# FastAPI is the main application class (similar to Flask(__name__)).
from fastapi import FastAPI

# CORSMiddleware lets the browser call this API from a different origin
# (e.g. React dev server on port 5173 → FastAPI on port 8000).
from fastapi.middleware.cors import CORSMiddleware

# dotenv loads variables from a .env file into os.environ, useful for
# keeping secrets and config out of code.
from dotenv import load_dotenv

from app.router import router

load_dotenv()  # reads .env file if present

app = FastAPI(
    title=os.getenv("APP_TITLE", "ShipIQ Cargo Optimization Service"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Greedy cargo-to-tank allocation API for maritime logistics.",
)

# Allow all origins in development; restrict in production via env var.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# `include_router` registers all routes defined in router.py onto the app.
app.include_router(router)


@app.get("/")
def health():
    """Simple health-check endpoint."""
    return {"status": "healthy", "service": "shipiq-cargo"}
