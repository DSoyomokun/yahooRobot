# mission/scanner/grader.py
"""
Grading subsystem for OMR test:
- Compares detected bubble answers to ANSWER_KEY
- Computes correctness, score, percentage
"""

from .config import ANSWER_KEY

def grade_test(detected_answers):
    """
    detected_answers: {1:"A", 2:"C", ..., 10:"B"}

    Returns:
    {
        "correct_per_q": {1:True/False/None, ...},
        "score": int (# correct),
        "percentage": float,
        "total_questions": int
    }
    """

    correct_per_q = {}
    correct_count = 0
    total_q = len(ANSWER_KEY)

    for q, correct_ans in ANSWER_KEY.items():

        student_ans = detected_answers.get(q)

        if student_ans is None:
            # unanswered or ambiguous
            correct_per_q[q] = None

        else:
            is_correct = (student_ans == correct_ans)
            correct_per_q[q] = is_correct
            if is_correct:
                correct_count += 1

    percentage = round((correct_count / total_q) * 100.0, 2)

    return {
        "correct_per_q": correct_per_q,
        "score": correct_count,
        "percentage": percentage,
        "total_questions": total_q
    }

