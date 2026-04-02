from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(
    title="Orceu - Finance API (POC)",
    description="Backend Module for Orceu Financial ecosystem. (Multi-Tenant Schedules & Payments)",
    version="1.0.0",
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware global para acompanhar latência.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/", tags=["Health"])
async def health_check():
    """
    Simples endpoint garantindo orquestração Liveness do Servidor ASGI.
    """
    return {"status": "ok", "service": "orceu-finance-api"}

from app.presentation.routers import schedules, basics
app.include_router(basics.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
