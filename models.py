from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from passlib.context import CryptContext
import logging
import enum
from datetime import datetime

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ExamType(enum.Enum):
    NTPC = "NTPC"
    GROUP_D = "GROUP D"
    JE = "JE"
    SSC = "SSC"
    CGL = "CGL"

class ExamStage(enum.Enum):
    CBT1 = "CBT 1"
    CBT2 = "CBT 2"
    CBT3 = "CBT 3"
    PET = "PET"
    DV = "DV"
    TIER_1 = "Tier 1"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"
    TIER_4 = "Tier 4"

class Subject(enum.Enum):
    GENERAL_AWARENESS = "General Awareness"
    ARITHMETIC = "Arithmetic"
    GENERAL_INTELLIGENCE = "General Intelligence & Reasoning"
    BASIC_SCIENCE = "Basic Science & Engineering"
    TECHNICAL_ABILITIES = "Technical Abilities"
    REASONING = "Reasoning"
    LOGICAL_REASONING = "Logical Reasoning"
    GENERAL_SCIENCE = "General Science"
    MATHEMATICS = "Mathematics"
    SCIENCE = "Science"
    CURRENT_AFFAIRS = "Current Affairs"
    HISTORY = "History"
    GEOGRAPHY = "Geography"
    POLITY = "Polity"
    BIOLOGY = "Biology"
    CHEMISTRY = "Chemistry"
    INDIAN_CULTURE = "Indian Culture"
    ENVIRONMENT = "Environment"
    COMPUTER = "Computer"
    RAILWAY_AWARENESS = "Railway Awareness"
    INTERNATIONAL_AFFAIRS = "International Affairs"
    BANKING = "Banking"
    SCIENCE_AND_TECH = "Science and Tech"
    PHYSICS = "Physics"
    ENGLISH_GRAMMAR = "English Grammar"

class DifficultyLevel(enum.Enum):
    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def set_password(self, password: str):
        """Hash and set the user's password"""
        try:
            if not password:
                raise ValueError("Password cannot be empty")
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")
            self.hashed_password = pwd_context.hash(password)
            logger.info("Password hashed successfully")
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise ValueError(f"Error hashing password: {str(e)}")

    def verify_password(self, password: str) -> bool:
        """Verify the user's password"""
        try:
            if not password or not self.hashed_password:
                logger.warning("Password or hashed_password is empty")
                return False
            is_valid = pwd_context.verify(password, self.hashed_password)
            if not is_valid:
                logger.warning("Invalid password")
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    explanation = Column(Text)
    
    # Diagram/Image related fields
    has_diagram = Column(Boolean, default=False)
    diagram_description = Column(Text)  # Description of the diagram for accessibility
    
    # Metadata
    year = Column(Integer, nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)
    exam_stage = Column(Enum(ExamStage), nullable=False)
    subject = Column(Enum(Subject), nullable=False)
    topic = Column(String(100))  # Optional topic within subject
    
    # Additional metadata
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MODERATE)
    source = Column(String(255))  # Source of the question (e.g., "Previous Year Paper", "Practice Set")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tags = relationship("QuestionTag", back_populates="question")
    images = relationship("QuestionImage", back_populates="question")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    questions = relationship("QuestionTag", back_populates="tag")

class QuestionTag(Base):
    __tablename__ = "question_tags"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="tags")
    tag = relationship("Tag", back_populates="questions")

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to your user table
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    is_correct = Column(Integer, nullable=False)  # 1 for correct, 0 for incorrect
    time_taken = Column(Float)  # Time taken to answer in seconds
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("Question")

class QuestionStatistics(Base):
    __tablename__ = "question_statistics"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    average_time = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    question = relationship("Question")

class QuestionImage(Base):
    __tablename__ = "question_images"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    image_path = Column(String(255), nullable=False)  # Path to the stored image
    image_type = Column(String(50))  # Type of image (e.g., "diagram", "graph", "table")
    caption = Column(Text)  # Optional caption for the image
    display_order = Column(Integer, default=0)  # Order in which to display multiple images
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="images")
