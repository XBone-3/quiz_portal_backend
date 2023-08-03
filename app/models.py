from enum import unique
from marshmallow.schema import Schema
from sqlalchemy.orm import session
from app import application
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

"""
[DataBase Access Details]
Below is the configuration mentioned by which the application can make connection with MySQL database
"""
username = 'call_me_x'
password = 'fool'
database_name = 'quiz_app'
application.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{username}:{password}@localhost/{database_name}"
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CONSTANTS = {
      "QuizM_FK": 'quiz_master.id',
      "UserM_FK": 'user_master.id',
      "QuestionM_FK": 'question_master.id',
}

db = SQLAlchemy(application)

class BaseModel(db.Model):
        __abstract__ = True
        id = db.Column(db.String(100), primary_key=True)
        is_active = db.Column(db.Integer, default=1)
        created_ts = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
        updated_ts = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

class UserMaster(BaseModel):
        __tablename__ = 'user_master'

        name = db.Column(db.String(200), nullable=False)
        username = db.Column(db.String(200), nullable=False, unique=True)
        password = db.Column(db.String(200), nullable=False)
        is_admin = db.Column(db.Integer, default=0)

        def __init__(self, id, name, username, password, is_admin):
            self.id = id
            self.name = name
            self.username = username
            self.password = password
            self.is_admin = is_admin
            
class UserSession(BaseModel):
        __tablename__ = 'user_session'
        
        user_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['UserM_FK']), nullable=False)
        session_id = db.Column(db.String(200))
        
        def __init__(self, id, user_id, session_id):
            self.id = id
            self.user_id = user_id
            self.session_id = session_id
        
class QuestionMaster(BaseModel):
        
        __tablename__ = 'question_master'
        
        question = db.Column(db.String(200), nullable=False)
        choice1 = db.Column(db.String(200), nullable=False)
        choice2 = db.Column(db.String(200), nullable=False)
        choice3 = db.Column(db.String(200), nullable=False)
        choice4 = db.Column(db.String(200), nullable=False)
        answer = db.Column(db.Integer, nullable=False)
        marks = db.Column(db.Integer, nullable=False)
        remarks = db.Column(db.String(200))
        
        def __init__(self, id, question, choice1, 
                     choice2, choice3, choice4, answer, marks, remarks):
            self.id = id
            self.question = question
            self.choice1 = choice1
            self.choice2 = choice2
            self.choice3 = choice3
            self.choice4 = choice4
            self.answer = answer
            self.marks = marks
            self.remarks = remarks
            
class QuizMaster(BaseModel):
    
        __tablename__ = 'quiz_master'
        
        quiz_name = db.Column(db.String(200), nullable=False)
        
        def __init__(self, id, quiz_name):
            self.id = id
            self.quiz_name = quiz_name
            
class QuizQuestions(BaseModel):
        
        __tablename__ = 'quiz_questions'
        __table_args__ = (
                db.UniqueConstraint('quiz_id', 'question_id', name='unique_quiz_question'),
        )
        
        quiz_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['QuizM_FK']), nullable=False)
        question_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['QuestionM_FK']), nullable=False)
        
        def __init__(self, id, quiz_id, question_id):
            self.id = id
            self.quiz_id = quiz_id
            self.question_id = question_id
     
class QuizInstance(BaseModel):
        __tablename__ = 'quiz_instance'
        __table_args__ = (
                db.UniqueConstraint('quiz_id', 'user_id', name='unique_quiz_user'),
        )
        
        quiz_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['QuizM_FK']), nullable=False)
        user_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['UserM_FK']), nullable=False)
        score_achieved = db.Column(db.Integer, default=0)
        is_submitted = db.Column(db.Integer, default=0)
        
        def __init__(self, id, quiz_id, user_id):
            self.id = id
            self.quiz_id = quiz_id
            self.user_id = user_id
            
class UserResponses(BaseModel):
        __tablename__ = 'user_responses'
        __table_args__ = (
                db.UniqueConstraint('quiz_id', 'user_id', 'question_id', name='unique_quiz_user_question'),
        )
        
        quiz_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['QuizM_FK']), nullable=False)
        user_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['UserM_FK']), nullable=False)
        question_id = db.Column(db.String(200), db.ForeignKey(CONSTANTS['QuestionM_FK']), nullable=False)
        response = db.Column(db.Integer, nullable=False)

        def __init__(self, id, quiz_id, user_id, question_id, response):
            self.id = id
            self.quiz_id = quiz_id
            self.user_id = user_id
            self.question_id = question_id
            self.response = response
        
with application.app_context():   
        db.drop_all()
        db.create_all()
        db.session.commit()