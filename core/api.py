from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.users_controller import router as users_router
from api.matching_controller import router as matching_router

tags_metadata = [
    {"name": "users", "description": "Create, read, update users"},
    {"name": "matching", "description": "Driver/Rider matching endpoints"},
]

app = FastAPI(
    title="Carpooling API",
    description="Endpoints for users and matching.",
    version="0.1.0",
    docs_url="/swagger",         # Swagger UI
    redoc_url="/redoc",          # ReDoc
    openapi_url="/openapi.json", # OpenAPI JSON
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "docExpansion": "list",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(matching_router)

# Explicit servers to avoid Swagger UI host issues on Windows
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
        servers=[
            {"url": "http://localhost:8000"},
            {"url": "http://127.0.0.1:8000"},
        ],
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi