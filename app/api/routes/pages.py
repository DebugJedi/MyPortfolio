from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Setup Jinja2 templates
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent.parent.parent / "templates")
)

# ==========================================
# MAIN PAGES
# ==========================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage - renders pages/home.html which extends base.html"""
    return templates.TemplateResponse(
        "pages/home.html",  # ← Changed from index.html
        {"request": request}
    )

@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio(request: Request):
    """Portfolio page"""
    return templates.TemplateResponse(
        "pages/portfolio.html",
        {"request": request}
    )

# ==========================================
# PROJECT PAGES
# ==========================================

@router.get("/cancer-prediction", response_class=HTMLResponse)
async def cancer_prediction(request: Request):
    """Cancer Prediction project"""
    return templates.TemplateResponse(
        "pages/project-details/cancer-prediction.html",
        {"request": request}
    )

@router.get("/cold-email-intro", response_class=HTMLResponse)
async def cold_email(request: Request):
    """Cold Email project"""
    return templates.TemplateResponse(
        "pages/project-details/cold-email_intro.html",
        {"request": request}
    )

@router.get("/cold-email", response_class=HTMLResponse)
async def cold_email(request: Request):
    """Cold Email project"""
    return templates.TemplateResponse(
        "pages/project-details/cold-email.html",
        {"request": request}
    )

@router.get("/hand-gesture-detection", response_class=HTMLResponse)
async def hand_gesture_detection(request: Request):
    """Hand Gesture Detection project"""
    return templates.TemplateResponse(
        "pages/project-details/hand-gesture-detection.html",
        {"request": request}
    )

@router.get("/graphrag-chatbot", response_class=HTMLResponse)
async def graphrag_chatbot(request: Request):
    """GraphRAG ChatBot project"""
    return templates.TemplateResponse(
        "pages/project-details/graphrag-chatbot.html",
        {"request": request}
    )