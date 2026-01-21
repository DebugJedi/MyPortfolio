"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.config import settings
# from app.database.connection import init_db
# from app.api.routes import pages
from app.api.routes import pages, chatbot, email, contact, analytics
from app.api.middleware.analytics import AnalyticsMiddleware
from app.api.middleware.security import SecurityHeadersMiddleware

def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/api/docs" if settings.DEBUG else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom Middleware
    # app.add_middleware(AnalyticsMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Static Files
    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).parent.parent / "static"),
        name="static"
    )
    
    # # Routes
    app.include_router(pages.router, tags=["Pages"])
    app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["Chatbot"])
    app.include_router(email.router, prefix="/api/v1/email", tags=["Email"])
    app.include_router(contact.router, prefix="/api/v1/contact", tags=["Contact"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
    
    # @app.lifespan("startup")
    # async def startup():
    #     init_db()
    #     print(f"🚀 {settings.PROJECT_NAME} started!")
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=settings.DEBUG)
