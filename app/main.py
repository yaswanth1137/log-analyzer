from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.log_parser import analyze_log_payload

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(f"{settings.API_V1_STR}/analyze")
async def analyze_workflow_run(payload: dict = Body(...)):
    raw_log = payload.get("log_text")
    if not raw_log:
        raise HTTPException(status_code=400, detail="Missing required field: 'log_text'")
        
    # Pipe input logs directly through the NLP matrix analyzer
    evaluation_report = analyze_log_payload(raw_log)
    return evaluation_report