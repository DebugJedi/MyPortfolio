"""Contact Form Routes"""
from fastapi import APIRouter, Request, Body, HTTPException
from fastapi.responses import JSONResponse
from app.database.models import ContactMessage
from app.database.connection import get_db
from app.config import settings
import hashlib
import requests
from datetime import datetime

router = APIRouter()

@router.post("/message")
async def submit_contact(request: Request, payload: dict = Body(...)):
    with get_db() as db:
        msg = ContactMessage(
            name=payload['name'],
            email=payload['email'],
            message=payload['message']
        )
        db.add(msg)
    return {"status": "success"}
