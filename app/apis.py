from app.models import (QuestionMaster, QuizInstance, QuizMaster, QuizQuestions, UserMaster, UserResponses, UserSession)
from app import *
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from app.schemas import (QuestionMasterSchema, CreateQuizSchema, UserMasterSchema, AssignQuizSchema, UserResponseSchema, LoginSchema, APIResponseSchema, ViewQuizSchema, ViewResponseSchema)
from app.services import *
from flask import session

"""
[Sign Up API] : Its responsibility is to perform the signup activity for the user.
"""
#  Restful way of creating APIs through Flask Restful
class SignUpAPI(MethodResource, Resource):
    @doc(description="Sign Up API", tags=["RIO APIs"])
    @use_kwargs(UserMasterSchema, location=('json'))
    @marshal_with(APIResponseSchema)
    def post(self, **kwargs):
        try:
            user = UserMaster(
                id=str(uuid.uuid4()),
                name=kwargs['name'],
                username=kwargs['username'],
                password=kwargs['password'],
                is_admin=kwargs['is_admin'],
            )
            db.session.add(user)
            db.session.commit()
            return APIResponseSchema().dump(dict(message=f"User {kwargs['username']} has created successfully")), 200
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while creating USER, error:{str(e)}")), 500
            

api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)

"""
[Login API] : Its responsibility is to perform the login activity for the user and 
create session id which will be used for all subsequent operations.
"""
class LoginAPI(MethodResource, Resource):
    @doc(descrition="Login API", tags=["RIO APIs"])
    @use_kwargs(LoginSchema, location=('json'))
    @marshal_with(APIResponseSchema)
    def post(self, **kwargs):
        try:
            user = UserMaster.query.filter_by(username=kwargs['username'], password=kwargs['password']).first()
            if user:
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
                return APIResponseSchema().dump(dict(message=f"User {kwargs['username']} has logged in successfully")), 200
            else:
                return APIResponseSchema().dump(dict(message=f"User {kwargs['username']} does not exist")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while logging USER, error:{str(e)}")), 500
        

api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)

"""
[Logout API] : Its responsibility is to perform the logout activity for the user.
"""
class LogoutAPI(MethodResource, Resource):
   @doc(description="Logout API", tags=["RIO APIs"])
   @marshal_with(APIResponseSchema)
   def get(self):
        try:
            if session.get('user_id') and session.get('session_id'):
                user = UserMaster.query.filter_by(id=session['user_id']).first()
                user.is_active = 0
                user_session = UserSession.query.filter_by(session_id=session['session_id']).first()
                user_session.is_active = 0
                db.session.commit()
            session.clear()
            return APIResponseSchema().dump(dict(message="User has logged out successfully")), 200
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while logging out USER, error:{str(e)}")), 500
            

api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)

"""
[Add Question API] : Its responsibility is to add question to the question bank.
Admin has only the rights to perform this activity.
"""
class AddQuestionAPI(MethodResource, Resource):
    @doc(description="Add Question API", tags=["Questions"])
    @use_kwargs(QuestionMasterSchema, location=('json'))
    @marshal_with(APIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
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
                return APIResponseSchema().dump(dict(message=f"Question {kwargs['question']} has created successfully")), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Admin can add the questions")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while creating QUESTION, error:{str(e)}")), 500


api.add_resource(AddQuestionAPI, '/add.question')
docs.register(AddQuestionAPI)

"""
[List Questions API] : Its responsibility is to list all questions present activly in the question bank.
Here only Admin can access all the questions.
"""
class ListQuestionAPI(MethodResource, Resource):
    @doc(description="List Question API", tags=["Questions"])
    # @use_kwargs(QuizQuestionsSchema, location=('json'))
    # @marshal_with(APIResponseSchema)
    def post(self):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
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
                return ViewResponseSchema().dump(dict(response=question_list)), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Admin can access all the questions")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while listing questions, error:{str(e)}")), 500


api.add_resource(ListQuestionAPI, '/list.questions')
docs.register(ListQuestionAPI)

"""
[Create Quiz API] : Its responsibility is to create quiz and only admin can create quiz using this API.
"""
class CreateQuizAPI(MethodResource, Resource):
    @doc(description="Create Quiz API", tags=["Quiz"])
    @use_kwargs(CreateQuizSchema, location=('json'))
    @marshal_with(APIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
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
                return APIResponseSchema().dump(dict(message=f"Quiz {kwargs['name']} has created successfully")), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Admin can create the quiz")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while creating quiz, error:{str(e)}")), 500


api.add_resource(CreateQuizAPI, '/create.quiz')
docs.register(CreateQuizAPI)

"""
[Assign Quiz API] : Its responsibility is to assign quiz to the user. Only Admin can perform this API call.
"""
class AssignQuizAPI(MethodResource, Resource):
    @doc(description="Assign Quiz API", tags=["Quiz"])
    @use_kwargs(AssignQuizSchema, location=('json'))
    @marshal_with(APIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
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
                        return APIResponseSchema().dump(dict(message="Quiz does not exist")), 404
                db.session.commit()
                return APIResponseSchema().dump(dict(message="Quiz has been assigned respectively to the Users")), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Admin can assign the quiz")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while assigning quiz, error:{str(e)}")), 500


api.add_resource(AssignQuizAPI, '/assign.quiz')
docs.register(AssignQuizAPI)

"""
[View Quiz API] : Its responsibility is to view the quiz details.
Only Admin and the assigned users to this quiz can access the quiz details.
"""
class ViewQuizAPI(MethodResource, Resource):
    @doc(description="View Quiz API", tags=["Quiz"])
    @use_kwargs(ViewQuizSchema, location=('json'))
    def post(self, **kwargs):
        try:
            if session.get('user_id'):
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
                    return ViewResponseSchema().dump(dict(response=quiz_questions_list)), 200
                else:
                    return APIResponseSchema().dump(dict(message="Quiz does not exist or you are not assigned to this quiz")), 404
            else:
                return APIResponseSchema().dump(dict(message="Login to view the quiz details")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while viewing quiz, error:{str(e)}")), 500


api.add_resource(ViewQuizAPI, '/view.quiz')
docs.register(ViewQuizAPI)

"""
[View Assigned Quiz API] : Its responsibility is to list all the assigned quizzes 
                            with there submittion status and achieved scores.
"""
class ViewAssignedQuizAPI(MethodResource, Resource):
    @doc(description="View Assigned Quiz API", tags=["Quiz"])
    # @marshal_with(APIResponseSchema)
    def post(self):
        try:
            if session.get('user_id'):
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
                return ViewResponseSchema().dump(dict(response=quiz_instance_list)), 200
            else:
                return APIResponseSchema().dump(dict(message="Login to view the assigned quizzes")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while viewing assigned quizzes, error:{str(e)}")), 500


api.add_resource(ViewAssignedQuizAPI, '/assigned.quizzes')
docs.register(ViewAssignedQuizAPI)


"""
[View All Quiz API] : Its responsibility is to list all the created quizzes. Admin can only list all quizzes.
"""
class ViewAllQuizAPI(MethodResource, Resource):
    @doc(description="View All Quiz API", tags=["Quiz"])
    # @marshal_with(APIResponseSchema)
    def post(self):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
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
                return ViewResponseSchema().dump(dict(response=quiz_list)), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Admin can view the quiz")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while viewing quiz, error:{str(e)}")), 500


api.add_resource(ViewAllQuizAPI, '/all.quizzes')
docs.register(ViewAllQuizAPI)

"""
[Attempt Quiz API] : Its responsibility is to perform quiz attempt activity by 
                        the user and the score will be shown as a result of the submitted attempt.
"""
class AttemptQuizAPI(MethodResource, Resource):
    @doc(description="Attempt Quiz API", tags=["Quiz"])
    @use_kwargs(UserResponseSchema, location=("json"))
    @marshal_with(APIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id'):
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
                else:
                    return APIResponseSchema().dump(dict(message="Quiz is not assigned to you or does not exist")), 404
                db.session.commit()
                return APIResponseSchema().dump(dict(message=f"Quiz {quiz.quiz_name} score achieved: {quiz_instance.score_achieved}")), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Users can attempt the quiz")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while attempting quiz, error:{str(e)}")), 500


api.add_resource(AttemptQuizAPI, '/attempt.quiz')
docs.register(AttemptQuizAPI)

"""
[Quiz Results API] : Its responsibility is to provide the quiz results in which the users 
                        having the scores sorted in descending order are displayed, 
                        also the ones who have not attempted are also shown.
                        Admin has only acess to this functionality.
"""
class QuizResultAPI(MethodResource, Resource):
    @doc(description="Quiz Results API", tags=["Quiz"])
    def post(self):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                quiz_instances = QuizInstance.query.all()
                quiz_instance_list = list()
                for quiz_instance in quiz_instances:
                    quiz_instance = {
                        'id': quiz_instance.id,
                        'quiz_id': quiz_instance.quiz_id,
                        'user_id': quiz_instance.user_id,
                        'score_achieved': quiz_instance.score_achieved,
                        'is_submitted': quiz_instance.is_submitted,
                    }
                    quiz_instance_list.append(quiz_instance)
                return ViewResponseSchema().dump(dict(response=quiz_instance_list)), 200
            else:
                return APIResponseSchema().dump(dict(message="Only Admin can view the quiz")), 404
        except Exception as e:
            return APIResponseSchema().dump(dict(message=f"error while viewing quiz, error:{str(e)}")), 500


api.add_resource(QuizResultAPI, '/quiz.results')
docs.register(QuizResultAPI)


