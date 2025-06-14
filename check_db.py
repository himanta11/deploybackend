from database import SessionLocal
from models import Question
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    db = SessionLocal()
    try:
        # Count total questions
        total_questions = db.query(Question).count()
        logger.info(f"Total questions in database: {total_questions}")
        
        # Get a sample question
        sample_question = db.query(Question).first()
        if sample_question:
            logger.info(f"Sample question: {sample_question.question_text}")
        else:
            logger.info("No questions found in database")
            
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database() 