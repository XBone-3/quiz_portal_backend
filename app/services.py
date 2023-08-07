from sqlalchemy.orm.session import sessionmaker
from app.models import (QuestionMaster, QuizInstance, QuizMaster, QuizQuestions, UserMaster, UserResponses, UserSession)
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
    def wrapper(**kwargs):
        """
        A function that serves as a wrapper function.

        Args:
            **kwargs: Keyword arguments that will be passed to the wrapped function.

        Returns:
            tuple: A tuple containing an integer status code and the result of the wrapped function if successful.
            Exception: An exception object if an error occurs during the execution of the wrapped function.
        """
        try:
            data = func(**kwargs)
            return 1, data
        except Exception as dbe:
            return dbe
    return wrapper

@exception_handler
def add_user(**kwargs):
    """
    Adds a new user to the database.

    Parameters:
        **kwargs (dict): A dictionary containing the user information.
            - name (str): The name of the user.
            - username (str): The username of the user.
            - password (str): The password of the user.
            - is_admin (bool): Indicates whether the user is an admin or not.

    Returns:
        int: The result of the operation. Returns 1 if the user was successfully added to the database.

    Raises:
        DatabaseError: If there was an error adding the user to the database.
    """
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
def add_session(**kwargs):
    """
    Adds a session for the given user.

    Args:
        **kwargs (dict): Keyword arguments containing the user information.
            - user (UserMaster): The user to add the session for.

    Returns:
        int: Returns 1 on success.

    Raises:
        Exception: If there is an error while adding the session.

    Notes:
        - This function adds a session for the user.
        - The user information is passed as keyword arguments.
        - The session ID and user ID are stored in the session object.
        - The user's `is_active` flag is set to 1.
        - The changes are committed to the database.
    """
    user = kwargs['user']
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
    """
    Adds a question to the database.

    Parameters:
        **kwargs (dict): Keyword arguments containing the question details.
            - question (str): The question text.
            - choice1 (str): The first choice for the question.
            - choice2 (str): The second choice for the question.
            - choice3 (str): The third choice for the question.
            - choice4 (str): The fourth choice for the question.
            - answer (str): The correct answer for the question.
            - marks (int): The marks assigned to the question.
            - remarks (str): Any remarks for the question.

    Returns:
        int: The result of adding the question to the database. Returns 1 on success.
    """
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
    """
    Retrieve a list of questions from the QuestionMaster table.

    Returns:
        List: A list of dictionaries containing the question details. Each dictionary
        contains the following keys: 'id', 'question', 'choice1', 'choice2',
        'choice3', 'choice4', 'answer'.
    """
    questions = QuestionMaster.query.all()
    question_list = list()
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
    """
    Adds a quiz to the database.

    Args:
        **kwargs: A dictionary containing the following keys:
            - name (str): The name of the quiz.
            - question_ids (List[str]): A list of question ids associated with the quiz.

    Returns:
        int: The status code indicating the success of the operation. Returns 1 if the quiz was successfully added to the database.
    """
    quiz = QuizMaster(
                    id=str(uuid.uuid4()),
                    quiz_name=kwargs['quiz_name'],   
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
    """
    Assigns a quiz to one or more users.

    Args:
        **kwargs (dict): A dictionary containing the quiz ID as the key and a list of user IDs as the value.

    Returns:
        int: Returns 1 if the quiz is successfully assigned to all users, otherwise returns 0.
    """
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
    """
    View a quiz and retrieve the list of questions for the quiz.

    Parameters:
        **kwargs (dict): Arbitrary keyword arguments. The 'quiz_id' key is required.

    Returns:
        list: A list of dictionaries representing the quiz questions. Each dictionary contains the following keys:
            - 'quiz_name' (str): The name of the quiz.
            - 'question_id' (int): The ID of the question.
            - 'question' (str): The text of the question.
            - 'choice1' (str): The first choice for the question.
            - 'choice2' (str): The second choice for the question.
            - 'choice3' (str): The third choice for the question.
            - 'choice4' (str): The fourth choice for the question.
            - 'marks' (int): The marks assigned to the question.
            - 'remarks' (str): Remarks or additional information about the question.

        int: 0 if the user is not authorized to view the quiz.
    """
    quiz = QuizMaster.query.filter_by(id=kwargs['quiz_id']).first()
    quiz_question_ids = [quiz_question.question_id for quiz_question in QuizQuestions.query.filter_by(quiz_id=quiz.id).all()]
    quiz_questions = [QuestionMaster.query.filter_by(id=question_id).first() for question_id in quiz_question_ids]
    user_ids = [quiz_instance.user_id for quiz_instance in QuizInstance.query.filter_by(quiz_id=quiz.id).all()]
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
    """
    Retrieves a list of assigned quizzes for the current user.

    Returns:
        List: A list of dictionaries containing information about each assigned quiz.
            Each dictionary has the following keys:
            - 'quiz_name' (str): The name of the assigned quiz.
            - 'quiz_id' (int): The ID of the assigned quiz.
            - 'user_id' (int): The ID of the user the quiz is assigned to.
            - 'score_achieved' (float): The score achieved by the user for the quiz.
            - 'is_submitted' (bool): Indicates whether the quiz has been submitted by the user.
    """
    quiz_instances = QuizInstance.query.filter_by(user_id=session['user_id']).all()
    quiz_instance_list = list()
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
    """
    Function that lists all the quizzes.
    
    Returns:
        list: A list of dictionaries containing the details of each quiz. Each dictionary has the following keys:
            - id (int): The unique identifier of the quiz.
            - quiz_name (str): The name of the quiz.
            - is_active (bool): Indicates whether the quiz is active or not.
            - created_at (datetime): The timestamp when the quiz was created.
            - updated_at (datetime): The timestamp when the quiz was last updated.
    """
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
    """
    Attempt a quiz and save the user's responses.

    Args:
        **kwargs (dict): Keyword arguments containing the quiz ID and user's responses.

    Returns:
        QuizInstance: The updated QuizInstance object.

        Int: 0 if the user is not authorized to attempt the quiz.
    """
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
    """
    Retrieves all quiz results from the database.

    Returns:
        list: A list of dictionaries containing detailed information about each quiz instance.
              Each dictionary contains the following keys:
              - id (int): The ID of the quiz instance.
              - quiz_id (int): The ID of the quiz associated with the instance.
              - user_id (int): The ID of the user who took the quiz.
              - score_achieved (int): The score achieved by the user in the quiz.
              - is_submitted (bool): Indicates whether the quiz was submitted by the user.
    """
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

        