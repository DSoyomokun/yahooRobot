"""
Grading module for evaluating test answers.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class Grader:
    """Grades test papers against an answer key."""
    
    def __init__(self, answer_key_path: Optional[str] = None):
        """
        Initialize grader.
        
        Args:
            answer_key_path: Path to answer key JSON file
        """
        # Look for answer_key.json in project root or robot_scanner directory
        if answer_key_path is None:
            project_root = Path(__file__).parent.parent
            scanner_dir = Path(__file__).parent
            if (project_root / 'answer_key.json').exists():
                answer_key_path = str(project_root / 'answer_key.json')
            elif (scanner_dir / 'answer_key.json').exists():
                answer_key_path = str(scanner_dir / 'answer_key.json')
            else:
                answer_key_path = 'answer_key.json'
        self.answer_key_path = answer_key_path
        self.answer_key = {}
        self.num_questions = 0
        self.load_answer_key()
    
    def load_answer_key(self):
        """Load answer key from file."""
        try:
            key_path = Path(self.answer_key_path)
            if not key_path.exists():
                logger.warning(f"Answer key not found at {self.answer_key_path}")
                return
            
            with open(key_path, 'r') as f:
                data = json.load(f)
            
            self.answer_key = data.get('answers', {})
            self.num_questions = data.get('num_questions', len(self.answer_key))
            
            logger.info(f"Answer key loaded: {self.num_questions} questions")
        except Exception as e:
            logger.error(f"Error loading answer key: {e}")
    
    def grade(self, student_answers: Dict[str, Optional[str]]) -> Dict:
        """
        Auto grading pipeline.
        Grades student answers against the answer key.
        
        Args:
            student_answers: Dictionary in format {"1": "B", "2": "D", ...}
            
        Returns:
            Dictionary with grading results including score
        """
        correct = 0
        incorrect = 0
        unanswered = 0
        details = {}
        
        for q_num in range(1, self.num_questions + 1):
            q_str = str(q_num)
            correct_answer = self.answer_key.get(q_str)
            student_answer = student_answers.get(q_str)
            
            if student_answer is None:
                unanswered += 1
                details[q_str] = {
                    'correct': False,
                    'student_answer': None,
                    'correct_answer': correct_answer
                }
            elif student_answer.upper() == correct_answer.upper():
                correct += 1
                details[q_str] = {
                    'correct': True,
                    'student_answer': student_answer,
                    'correct_answer': correct_answer
                }
            else:
                incorrect += 1
                details[q_str] = {
                    'correct': False,
                    'student_answer': student_answer,
                    'correct_answer': correct_answer
                }
        
        score = float(correct)
        percentage = (correct / self.num_questions * 100) if self.num_questions > 0 else 0.0
        
        result = {
            'total_questions': self.num_questions,
            'correct': correct,
            'incorrect': incorrect,
            'unanswered': unanswered,
            'score': score,
            'percentage': percentage,
            'details': details
        }
        
        logger.info(f"Grading complete: {correct}/{self.num_questions} correct ({percentage:.1f}%)")
        return result

