
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Interview(Base):
    """Interview session table"""
    __tablename__ = 'interviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    candidate_name = Column(String(200), nullable=False)
    candidate_email = Column(String(200), nullable=True)
    
    # Timestamps
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    
    # Scores
    overall_score = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), default='in_progress')  # 'in_progress', 'completed', 'abandoned'
    
    # JSON data
    target_skills = Column(JSON, nullable=True)
    skill_scores = Column(JSON, nullable=True)
    conversation_history = Column(JSON, nullable=True)
    final_report = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Response(Base):
    """Individual response table"""
    __tablename__ = 'responses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True, nullable=False)
    
    # Question info
    skill = Column(String(50), nullable=False)
    question_id = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=True)
    
    # Response
    response_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=True)
    
    # Scores
    rule_score = Column(Float, nullable=True)
    llm_score = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    
    # Timing
    response_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


# Database setup
DATABASE_URL = "sqlite:///./cyberhire.db"  # SQLite for simplicity
# For production, use: "postgresql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database initialized successfully!")


# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
    print(f"[DB] Database created at: {DATABASE_URL}")