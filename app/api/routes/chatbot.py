"""
GraphRAG Chatbot API Routes
Handles PDF upload, processing, and querying
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from app.database.models import ChatSession, ChatQuery
from app.database.connection import get_db
from app.config import settings
import uuid
import time
import hashlib
from datetime import datetime

router = APIRouter()

chat_sessions = {}

@router.post("/upload")
async def upload_pdf(request: Request, file: UploadFile=File(...)):
    """
    Upload and process PDF for chatbot

    Returns session__id for subsequent queries
    """

    try:

        if not file.filename.endswith(".pdf"):
            raise HTTPException(400, detail="Only PDF files aer accepted at the moment.")
        
        content = await file.read()
        file_size_mb = len(content) /(1024*1024)

        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(400, detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB")
        
        session_id = str(uuid.uuid4())

        # TODO: Process PDF with your GraphRAG system
        # from app.core.graphrag import GraphRAG
        # graph_rag = GraphRAG()
        # documents = process_pdf(content)
        # graph_rag.build_knowledge_graph(documents)
        # chat_sessions[session_id] = {'graph_rag': graph_rag, 'filename': file.filename}
        
        # For now, just store filename

        chat_sessions[session_id] = {
            'filename' : file.filename,
            'uploaded_at': datetime.now(datetime.timezone.utc)
        }
        ip = request.client.host
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()

        with get_db() as db:
            session = ChatSession(
                session_id = session_id,
                pdf_filename = file.filename,
                file_size_bytes=len(content),
                ip_hash=ip_hash,
                user_agent=request.header.get('user-agent', '')[:500]
            )
            db.add(session)

        return {
            "status":"success",
            "session_id": session_id,
            "filename": file.filename,
            "message": "PDF uploaded and processed successfully!"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Error processing PDF: {str(e)}")
    
@router.post('/qeury')
async def query_pdf(payload: dict=Body(...)):
    """
    Query the uploaded PDF
    Request body:
    {
        "session_id": "uuid",
        "query: "user question"
    }
    """

    try:
        query = payload.get("query")
        session_id = payload.get("session_id")

        if not query:
            raise HTTPException(400, detail="Query is required!")
        if not session_id:
            raise HTTPException(400, detail="Session ID is required!")
        
        if session_id not in chat_sessions:
            raise HTTPException(404, detail="Session not found. Please upload a PDF first.")
        
        start_time = time.time()

        # TODO: Query your GraphRAG system
        # graph_rag = chat_sessions[session_id]['graph_rag']
        # response_text = graph_rag.query(query)

        # Placehoder
        response_text = (
            f"This is a placehoder response for your query: '{query}'."
            f"Integrate your GraphRAG system here to get actual answers form the PDF: "
            f"{chat_sessions[session_id]['filename']}"
        )

        response_time_ms = (time.time() - start_time)*1000

        with get_db() as db:
            chat_query = ChatQuery(
                session_id = session_id,
                query=query,
                response=response_text,
                response_time_ms=response_time_ms,
                error=False
            )
            db.add(chat_query)

            db_session = db.query(ChatSession).filter_by(session_id=session_id).first()
            if db_session:
                db_session.update_stats(response_time_ms)

        return {
            "status": "success",
            "response": response_text,
            "response_time_ms": round(response_time_ms,2),
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Log error to database
        try:
            with get_db() as db:
                chat_query = ChatQuery(
                    session_id=session_id,
                    query=query,
                    response="",
                    response_time_ms=0,
                    error=True,
                    error_message=str(e)
                )
                db.add(chat_query)
        except:
            pass

        raise HTTPException(500, detail=f"Error processing query: {str(e)}")
    

@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Get chat history for a session"""

    try:
        with get_db() as db:
            # Get session info

            session = db.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                raise HTTPException(404, detail="Session not found")
            
            queries = db.query(ChatQuery)\
                .filter_by(session_id=session_id)\
                .order_by(ChatQuery.timestamp.asc())\
                .all()
            
            return {
                "session": session.to_dict(),
                "queries": [q.to_dict() for q in queries]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    
@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session and its history"""
    try:
        if session_id in chat_sessions:
            del chat_sessions[session_id]

        with get_db() as db:
            db.query(ChatQuery).filter_by(session_id=session_id).delete()

            db.query(ChatSession).filter_by(session_id=session_id).delete()

            db.query(ChatSession).filter_by(session_id=session_id).delete()

        return {"status": "success", "message": "Session deleted"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))
        