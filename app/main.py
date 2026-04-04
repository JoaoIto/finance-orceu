from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

tags_metadata = [
    {
        "name": "Schedules",
        "description": "Operações do Core Financeiro (OData Nibo Compliance) - Contas a Pagar/Receber.",
    },
    {
        "name": "Basics",
        "description": "Recursos de Apoio (Contatos, Centros de Custo e Categorias).",
    },
    {
        "name": "Health",
        "description": "Monitoramento e liveness probe do micro-serviço.",
    },
]

app = FastAPI(
    title="Orceu ERP - Financial Módulo (Nibo API Pattern)",
    description=(
        "**Backend Module for Orceu Financial ecosystem**.\n\n"
        "Esta API imita as práticas listadas no Nibo API (OData Pagination: `$top`, `$skip`, `$orderBy`) "
        "para listagens avançadas mantendo a arquitetura própria de Clean Architecture/DDD Multi-tenant.\n\n"
        "**Autenticação Obrigatória:** `x-organization-id` no parâmetro do Header."
    ),
    version="1.0.0",
    contact={
        "name": "Orceu Finance repository",
        "url": "https://github.com/JoaoIto/finance-orceu",
    },
    openapi_tags=tags_metadata
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
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Captura todos os ValueErrors lançados pela camada de Domain (Regras de Negócio)
    e os converte em um erro 400 limpo no formato JSON.
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": "Business Logic Violation",
            "message": str(exc)
        },
    )

from app.presentation.routers import schedules, basics
app.include_router(basics.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
