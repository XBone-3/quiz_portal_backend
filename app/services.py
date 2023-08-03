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

def exception_handler(func):
    def wrapper():
        try:
            data = func()
            return 1, data
        except Exception as e:
            return e
    return wrapper

@exception_handler
def add_user(**kwargs):
    user = UserMaster(
            id=str(uuid.uuid4()),
            name=kwargs['name'],
            username=kwargs['username'],
            password=kwargs['password'],
            is_admin=kwargs['is_admin'],
        )
    db.session.add(user)
    db.session.commit()
    return 1
    
@exception_handler    
def add_session(user):
    user_session = UserSession(
                    id = str(uuid.uuid4()),
                    user_id = user.id,
                    session_id = str(uuid.uuid4()),
                )
    session['session_id'] = user_session.session_id
    session['user_id'] = user.id
    session['is_admin'] = user.is_admin
    user.is_active = 1
    db.session.add(user_session)
    db.session.commit()
    return 1

@exception_handler
def add_question(**kwargs):
    question = QuestionMaster(
                    id=str(uuid.uuid4()),
                    question=kwargs['question'],
                    choice1=kwargs['choice1'],
                    choice2=kwargs['choice2'],
                    choice3=kwargs['choice3'],
                    choice4=kwargs['choice4'],
                    answer=kwargs['answer'],
                    marks=kwargs['marks'],
                    remarks=kwargs['remarks'],
                )
    db.session.add(question)
    db.session.commit()
    return 1

@exception_handler
def list_questions():
    questions = QuestionMaster.query.all()
    question_list = List()
    for question in questions:
        question = {
            'id': question.id,
            'question': question.question,
            'choice1': question.choice1,
            'choice2': question.choice2,
            'choice3': question.choice3,
            'choice4': question.choice4,
            'answer': question.answer,
        }
        question_list.append(question)
    return question_list

@exception_handler
def add_quiz(**kwargs):
    quiz = QuizMaster(
                    id=str(uuid.uuid4()),
                    quiz_name=kwargs['name'],   
                )
    for question_id in kwargs['question_ids']:
        quiz_question = QuizQuestions(
            id=str(uuid.uuid4()),
            quiz_id=quiz.id,
            question_id=question_id,
        )
        db.session.add(quiz_question)
    db.session.add(quiz)
    db.session.commit()
    return 1

@exception_handler
def assign_quiz(**kwargs):
    for quiz_id, user_ids in kwargs['instance'].items():
        quiz = QuizMaster.query.filter_by(id=quiz_id).first()
        if quiz:
            for user_id in user_ids:
                quiz_instance = QuizInstance(
                    id=str(uuid.uuid4()),
                    quiz_id=quiz.id,
                    user_id=user_id,
                )
                db.session.add(quiz_instance)
        else:
            db.session.rollback()
            return 0
    db.session.commit()
    return 1

@exception_handler
def view_quiz(**kwargs):
    quiz = QuizMaster.query.filter_by(id=kwargs['quiz_id']).first()
    quiz_question_ids = [quiz_question.question_id for quiz_question in QuizQuestions.query.filter_by(quiz_id=quiz.id).all()]
    quiz_questions = [QuestionMaster.query.filter_by(id=question_id).first() for question_id in quiz_question_ids]
    user_ids = [quiz_instance.user_id for quiz_instance in QuizInstance.query.filter_by(quiz_id=quiz.id).all()]
    print(user_ids)
    if (session['user_id'] in user_ids) or (session['is_admin'] == 1):
        quiz_questions_list = list()
        for question in quiz_questions:
            question = {
                'quiz_name': quiz.quiz_name,
                'question_id': question.id,
                'question': question.question,
                'choice1': question.choice1,
                'choice2': question.choice2,
                'choice3': question.choice3,
                'choice4': question.choice4,
                'marks': question.marks,
                'remarks': question.remarks
            }
            quiz_questions_list.append(question)
        return quiz_questions_list
    else:
        return 0
    
@exception_handler
def list_assigned_quizzes():
    quiz_instances = QuizInstance.query.filter_by(user_id=session['user_id']).all()
    quiz_instance_list = List()
    for quiz_instance in quiz_instances:
        quiz_instance = {
            'quiz_name': QuizMaster.query.filter_by(id=quiz_instance.quiz_id).first().quiz_name,
            'quiz_id': quiz_instance.quiz_id,
            'user_id': quiz_instance.user_id,
            'score_achieved': quiz_instance.score_achieved,
            'is_submitted': quiz_instance.is_submitted,
        }
        quiz_instance_list.append(quiz_instance)
    return quiz_instance_list

@exception_handler
def list_quizzes():
    quizzes = QuizMaster.query.all()
    quiz_list = list()
    for quiz in quizzes:
        quiz = {
            'id': quiz.id,
            'quiz_name': quiz.quiz_name,
            'is_active': quiz.is_active,
            'created_at': quiz.created_ts,
            'updated_at': quiz.updated_ts
        }
        quiz_list.append(quiz)
    return quiz_list

@exception_handler
def attempt_quiz(**kwargs):
    quiz = QuizMaster.query.filter_by(id=kwargs['quiz_id']).first()
    quiz_instance = QuizInstance.query.filter_by(quiz_id=quiz.id).first()
    if quiz_instance.user_id == session['user_id']:
        responses = kwargs['responses'][0]
        for question_id, choice in responses.items():
            quiz_question = QuestionMaster.query.filter_by(id=question_id).first()
            user_response = UserResponses(
                id=str(uuid.uuid4()),
                quiz_id=quiz.id,
                user_id=session['user_id'], 
                question_id=question_id,
                response=int(choice)
            )
            db.session.add(user_response)
            if int(quiz_question.answer) == int(choice):
                quiz_instance.score_achieved += quiz_question.marks
        quiz_instance.is_submitted = 1
        quiz_instance.is_active = 0
        quiz_instance.updated_ts = datetime.datetime.utcnow()
    else:
        return 0
    db.session.commit()
    return quiz_instance

@exception_handler
def all_quiz_result():
    quiz_instances = QuizInstance.query.all()
    detailed_quiz_instance_list = list()
    for quiz_instance in quiz_instances:
        quiz_instance = {
            'id': quiz_instance.id,
            'quiz_id': quiz_instance.quiz_id,
            'user_id': quiz_instance.user_id,
            'score_achieved': quiz_instance.score_achieved,
            'is_submitted': quiz_instance.is_submitted,
        }
        detailed_quiz_instance_list.append(quiz_instance)
    return detailed_quiz_instance_list

        