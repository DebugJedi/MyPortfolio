from fastapi import FastAPI, Form, Request, Body, UploadFile, File,HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import requests  # Ensure this line is included
from langchain_community.document_loaders import PyPDFLoader
from src.graphrag import GraphRAG
import tempfile
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from src.generator import emailGenerator
import os 
from dotenv import load_dotenv
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware



app = FastAPI()
# app.add_middleware(HTTPSRedirectMiddleware)
load_dotenv()

WEBHOOK_URL = os.getenv("_WEBHOOK_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["https://priyankrao.co"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# Mount static files for serving assets (CSS, JS, etc.)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

# Set up templates for HTML rendering
templates = Jinja2Templates(directory="templates")



async def get_graph_rag():
    graph_rag = getattr(app.state, "graphrag", None)
    if not graph_rag:
        raise HTTPException(status_code=400, detail="GraphRAG not initialized. Please upload a PDF first.")
    return graph_rag


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main intro page."""
    
    return templates.TemplateResponse("intro.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("aboutme.html", {"request": request})


@app.get("/portfolio", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("portfolio.html", {"request": request})

@app.get("/chatbot", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.get("/CancerPrediction-Intro", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("cancerprediction.html", {"request": request})

@app.get("/ColdEmail-Intro", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("coldemail-intro.html", {"request": request})

@app.get("/ObjDetection-Intro", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("obj-detection-intro.html", {"request": request})

@app.get("/ChatBot-Intro", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("chatbot-intro.html", {"request": request})


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...) ):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file received.")
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="invalid file type. Only PDF accepted.")
        print(f"File received: {file.filename}, Content Type: {file.content_type}")
        app.state.graphrag = None
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.file.read())
            tmp_file_path = tmp_file.name
        try:
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()[:20]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")
        graph_rag = GraphRAG()
        try:
            graph_rag.process_documents(documents)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF not uploaded.: {e}")
        app.state.graphrag = graph_rag

        print("graphrag instances set: ", app.state.graphrag)
        return JSONResponse({"Message": "File processed successfully", "file_name": file.filename})
    except HTTPException as e:
        print(f"HTTPException: {str(e)}")
        raise e
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occured: {str(e)}")
    
@app.post("/query")
async def query(body: dict= Body(...),
                graph_rag: GraphRAG = Depends(get_graph_rag)):
    
    user_query = body.get("query")
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
        # user_query = data.get("query")

    output = graph_rag.query(user_query)
    
    response_text = getattr(output, "content", getattr(output, "text", str(output)))

    return JSONResponse({"response": response_text})

@app.get("/coldemail", response_class=HTMLResponse)
async def get_aboutme(request: Request):
    return templates.TemplateResponse("coldEmail.html", {"request": request})

@app.post("/generate_email")
async def generateEmail(resume: UploadFile = File(...), job_url: str =Form(...)):
    try: 
        print("Received job_url:", job_url)  # Debugging
        print("Received file name:", resume.filename)  # Debugging
        funct = emailGenerator(job_url=job_url, document=resume)
        generated_email = funct.run()
        print("Generated email:", generated_email)  # Log the response
        return JSONResponse({"email": generated_email})
    except AttributeError:
        print("AttributeError: Invalid file or missing data")
        raise HTTPException(status_code=400, detail="Please upload a file.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occured: {str(e)}")


@app.post("/post/message")
async def post_message(payload: dict = Body(...)):
    """Endpoint to handle form submissions."""
    print("Received payload: ", payload)  # Debugging: Log received data

    # os.getenv("_WEBHOOK_URL")
    # Optional: Forward the data to Pabbly Connect URL for Google Sheets integration
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload
        )
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return {"status": "success", "message": "Data forwarded successfully"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)