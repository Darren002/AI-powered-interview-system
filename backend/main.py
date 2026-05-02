# backend/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import json
import os
from datetime import datetime

from chatbot_engine import ConversationalInterviewBot
from database import get_db, init_db, Interview, Response

# Path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# In-memory session storage
active_sessions = {}

# ==========================================
# Lifespan Events (Modern FastAPI)
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    init_db()
    print("[OK] CyberHire AI API started successfully!")
    print("[DOCS] API Documentation: http://localhost:8000/docs")
    yield
    # Shutdown
    print("[BYE] API shutting down...")

# ==========================================
# Initialize FastAPI
# ==========================================

app = FastAPI(
    title="CyberHire AI API",
    description="Next-generation AI interview system for cybersecurity recruitment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Pydantic Models
# ==========================================

class StartInterviewRequest(BaseModel):
    candidate_name: str
    candidate_email: Optional[str] = None

class ResponseSubmission(BaseModel):
    session_id: str
    response_text: str

# ==========================================
# API Endpoints
# ==========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CyberHire AI API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "start_interview": "POST /api/interview/start",
            "submit_response": "POST /api/interview/respond",
            "get_report": "GET /api/interview/{session_id}/report"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions)
    }

@app.post("/api/interview/start")
async def start_interview(request: StartInterviewRequest, db: Session = Depends(get_db)):
    """Start a new interview session"""
    try:
        # Check for duplicate email (if provided)
        if request.candidate_email:
            existing = db.query(Interview).filter(
                Interview.candidate_email == request.candidate_email.lower(),
                Interview.status == 'completed'
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="This email has already completed an interview. Each email can only be used once."
                )
        
        bot = ConversationalInterviewBot(
            candidate_name=request.candidate_name
        )
        
        intro = bot.start_interview()
        active_sessions[bot.session_id] = bot
        
        db_interview = Interview(
            session_id=bot.session_id,
            candidate_name=request.candidate_name,
            candidate_email=request.candidate_email,
            target_skills=bot.target_skills,
            status='in_progress'
        )
        db.add(db_interview)
        db.commit()
        
        return {
            "success": True,
            "session_id": bot.session_id,
            "message": intro,
            "candidate_name": request.candidate_name
        }
    
    except Exception as e:
        import traceback
        print(f"ERROR in start_interview: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/respond")
async def submit_response(submission: ResponseSubmission, db: Session = Depends(get_db)):
    """Submit candidate response"""
    try:
        bot = active_sessions.get(submission.session_id)
        
        if not bot:
            raise HTTPException(status_code=404, detail="Session not found")
        
        result = bot.process_response(submission.response_text)
        
        db_interview = db.query(Interview).filter(
            Interview.session_id == submission.session_id
        ).first()
        
        if db_interview:
            db_interview.conversation_history = bot.conversation_history
            db_interview.skill_scores = bot.skill_scores
            db_interview.status = bot.state.value
            db_interview.updated_at = datetime.now()
            
            if result['type'] == 'completion':
                db_interview.end_time = datetime.now()
                db_interview.status = 'completed'
                db_interview.final_report = result['final_report']
                db_interview.overall_score = result['final_report']['overall_performance']['average_score']
                
                # Send completion email
                try:
                    from email_service import send_completion_email
                    if db_interview.candidate_email:
                        score = result['final_report']['overall_performance']['average_score']
                        percentage = result['final_report']['overall_performance']['percentage']
                        send_completion_email(
                            db_interview.candidate_email,
                            db_interview.candidate_name,
                            score,
                            percentage
                        )
                except Exception as email_err:
                    print(f"Failed to send completion email: {email_err}")
            
            db.commit()
        
        return {
            "success": True,
            "result": result,
            "session_id": submission.session_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/{session_id}/report")
async def get_interview_report(session_id: str, db: Session = Depends(get_db)):
    """Get final interview report"""
    try:
        bot = active_sessions.get(session_id)
        
        if bot and bot.state.value == "completed":
            report = bot._generate_final_report()
            return {"success": True, "report": report}
        
        db_interview = db.query(Interview).filter(
            Interview.session_id == session_id
        ).first()
        
        if not db_interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        if db_interview.status != 'completed':
            raise HTTPException(status_code=400, detail="Interview not completed")
        
        report = db_interview.final_report or {}
        # Add candidate_email to report if not present
        if 'candidate_email' not in report:
            report['candidate_email'] = db_interview.candidate_email
        
        return {"success": True, "report": report}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/{session_id}/status")
async def get_interview_status(session_id: str):
    """Get interview status"""
    try:
        bot = active_sessions.get(session_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "session_info": bot.get_session_info()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/questions")
async def get_all_questions():
    """Get all questions"""
    try:
        questions_path = os.path.join(BASE_DIR, 'data', 'final 16.json')
        with open(questions_path, 'r') as f:
            questions = json.load(f)
        
        return {
            "success": True,
            "questions": questions,
            "total_questions": sum(len(q) for q in questions.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dataset-stats")
async def get_dataset_statistics():
    """Get dataset statistics"""
    try:
        dataset_path = os.path.join(BASE_DIR, 'data', 'enhanced_cybersecurity_dataset.json')
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        stats = {
            "total_responses": len(dataset),
            "by_skill": {},
            "by_quality": {},
            "avg_word_count": sum(len(d['response'].split()) for d in dataset) / len(dataset)
        }
        
        for item in dataset:
            skill = item['skill']
            quality = item['quality_level']
            stats['by_skill'][skill] = stats['by_skill'].get(skill, 0) + 1
            stats['by_quality'][quality] = stats['by_quality'].get(quality, 0) + 1
        
        return {"success": True, "statistics": stats}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interviews/recent")
async def get_recent_interviews(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent interviews"""
    try:
        interviews = db.query(Interview).order_by(
            Interview.created_at.desc()
        ).limit(limit).all()
        
        return {
            "success": True,
            "interviews": [
                {
                    "session_id": i.session_id,
                    "candidate_name": i.candidate_name,
                    "status": i.status,
                    "overall_score": i.overall_score,
                    "created_at": i.created_at.isoformat(),
                    "target_skills": i.target_skills
                }
                for i in interviews
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Health Check (for Render deployment)
# ==========================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==========================================
# Run Server
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)