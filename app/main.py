from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db
from .service import ask_question
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Q&A System")

class QuestionRequest(BaseModel):
    question: str
    summary: bool = True

class AnswerResponse(BaseModel):
    answer: str

@app.post("/ask")
def ask_endpoint(request: QuestionRequest, db: Session = Depends(get_db)):
    """
    Endpoint to ask a question about the data.
    """
    logger.info(f"Received question: {request.question}, summary: {request.summary}")
    try:
        answer = ask_question(db, request.question, summary=request.summary)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
