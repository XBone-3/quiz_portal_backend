from sqlalchemy.orm.session import sessionmaker
from app.models import QuestionMaster, QuizInstance, QuizMaster, QuizQuestions, UserMaster, UserResponses, UserSession
from app import db
import uuid
from flask import session
import datetime
from typing import List

"""
[Services Module] Implement various helper functions here as a part of api
                    implementation using MVC Template
"""

def add_users():
    try:
        users = [
            {
                'id': str(uuid.uuid4()),
                'name': 'admin',
                'username': 'admin',
                'password': 'admin',
                'is_admin': 1
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'user',
                'username': 'user',
                'password': 'user',
                'is_admin': 0
            }
        ]
        for user in users:
            user_entry = UserMaster(
                user['id'],
                user['name'],
                user['username'],
                user['password'],
                user['is_admin']
            )
            db.session.add(user_entry)
        db.session.commit()

    except Exception as e:
        print(f'{e} setup file')

def add_quizzes():
    try:
        questions = QuestionMaster.query.all()
        question_ids = [question.id for question in questions]
        quizzes = [
            {
                'id': str(uuid.uuid4()),
                'quiz_name': 'Quiz 1',
                'question_ids': question_ids[:5]
            },
            {
                'id': str(uuid.uuid4()),
                'quiz_name': 'Quiz 2',
                'question_ids': question_ids[5:]
            }
        ]
        for quiz in quizzes:
            quiz_entry = QuizMaster(
                id=quiz['id'],
                quiz_name=quiz['quiz_name']
            )
            db.session.add(quiz_entry)
            # db.session.commit()
            for question_id in quiz['question_ids']:
                quiz_question = QuizQuestions(
                    id=str(uuid.uuid4()),
                    quiz_id=quiz_entry.id,
                    question_id=question_id
                )
                db.session.add(quiz_question)
                # db.session.commit()
        user = UserMaster.query.filter_by(name="user").first()
        for i in range(2):
            quiz_instance = QuizInstance(
                id=str(uuid.uuid4()),
                quiz_id=quizzes[i]['id'],
                user_id=user.id
            )
            db.session.add(quiz_instance)
        db.session.commit()
    except Exception as e:
        print(f'{e} setup file')

        