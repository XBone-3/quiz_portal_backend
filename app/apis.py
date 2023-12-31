from app.models import UserSession
from app import *
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from app.schemas import (QuestionMasterSchema, CreateQuizSchema, UserMasterSchema, AssignQuizSchema, UserResponseSchema, LoginSchema, UnifiedAPIResponseSchema, ViewQuizSchema, UnifiedViewResponseSchema)
from app.services import session, add_user, add_session, add_question, list_questions, add_quiz, assign_quiz, view_quiz, list_assigned_quizzes, list_quizzes, attempt_quiz, all_quiz_result


def _view_generator(status, _response, *messages):
    """
    Generate the response based on the status and response data.

    Args:
        status (int): The status of the response.
        _response (int or list): The response data.
        *messages (str): The optional messages to include in the response.

    Returns:
        tuple: A tuple containing the serialized response data and the HTTP status code.

    Raises:
        Exception: If the status is not 1.

    Note:
        - If the status is 1:
            - If the response is an integer:
                - If the response is 1, the message at index 0 will be included in the response.
                - If the response is not 1, the message at index 1 will be included in the response.
            - If the response is a list, the response will be serialized using UnifiedViewResponseSchema.
        - If the status is not 1, an exception will be raised with the given status.

    """
    if status == 1:
        if type(_response) == type(1):
            if _response == 1:
                return UnifiedAPIResponseSchema().dump(dict(message=messages[0])), 200
            else:
                return UnifiedAPIResponseSchema().dump(dict(message=messages[1])), 404
        elif type(_response) == type([]):
            return UnifiedViewResponseSchema().dump(dict(response=_response)), 200
        else:
            return UnifiedAPIResponseSchema().dump(dict(message=messages[0])), 200
    else:
        raise Exception(status)


"""
[Sign Up API] : Its responsibility is to perform the signup activity for the user.
"""
#  Restful way of creating APIs through Flask Restful
class SignUpAPI(MethodResource, Resource):
    @doc(description="Sign Up API", tags=["RIO APIs"])
    @use_kwargs(UserMasterSchema, location=('json'))
    @marshal_with(UnifiedAPIResponseSchema)
    def post(self, **kwargs):
        try:
            status, _response = add_user(**kwargs)
            message_success=f"User {kwargs['username']} is created successfully"
            return _view_generator(status, _response, message_success)
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while creating USER, error:{str(e)}")), 500
            

api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)

"""
[Login API] : Its responsibility is to perform the login activity for the user and 
create session id which will be used for all subsequent operations.
"""
class LoginAPI(MethodResource, Resource):
    @doc(descrition="Login API", tags=["RIO APIs"])
    @use_kwargs(LoginSchema, location=('json'))
    @marshal_with(UnifiedAPIResponseSchema)
    def post(self, **kwargs):
        try:
            user = UserMaster.query.filter_by(username=kwargs['username'], password=kwargs['password']).first()
            if user:
                status, _response = add_session(user=user)
                message=f"User {kwargs['username']} is logged in successfully"
                return _view_generator(status, _response, message)
            else:
                return UnifiedAPIResponseSchema().dump(dict(message=f"User {kwargs['username']} does not exist")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while logging USER, error:{str(e)}")), 500
        

api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)

"""
[Logout API] : Its responsibility is to perform the logout activity for the user.
"""
class LogoutAPI(MethodResource, Resource):
   @doc(description="Logout API", tags=["RIO APIs"])
   @marshal_with(UnifiedAPIResponseSchema)
   def post(self):
        try:
            if session.get('user_id') and session.get('session_id'):
                user = UserMaster.query.filter_by(id=session['user_id']).first()
                user.is_active = 0
                user_session = UserSession.query.filter_by(session_id=session['session_id']).first()
                user_session.is_active = 0
                db.session.commit()
            session.clear()
            return UnifiedAPIResponseSchema().dump(dict(message="User has logged out successfully")), 200
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while logging out USER, error:{str(e)}")), 500
            

api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)

"""
[Add Question API] : Its responsibility is to add question to the question bank.
Admin has only the rights to perform this activity.
"""
class AddQuestionAPI(MethodResource, Resource):
    @doc(description="""
         [Add Question API] : Its responsibility is to add question to the question bank.
         Admin has only the rights to perform this activity.
         """, tags=["Questions"])
    @use_kwargs(QuestionMasterSchema, location=('json'))
    @marshal_with(UnifiedAPIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                status, _response = add_question(**kwargs)
                message=f"Question {kwargs['question']} has created successfully"
                return _view_generator(status, _response, message)
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Admin can add the questions")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while creating QUESTION, error:{str(e)}")), 500


api.add_resource(AddQuestionAPI, '/add.question')
docs.register(AddQuestionAPI)

"""
[List Questions API] : Its responsibility is to list all questions present activly in the question bank.
Here only Admin can access all the questions.
"""
class ListQuestionAPI(MethodResource, Resource):
    @doc(description="""
         [List Questions API] : Its responsibility is to list all questions present activly in the question bank.
         only Admin can access all the questions.
         """, tags=["Questions"])
    def post(self):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                status, _response = list_questions() # return list of questions
                return _view_generator(status, _response, "Questions are listed successfully")
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Admin can access all the questions")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while listing questions, error:{str(e)}")), 500


api.add_resource(ListQuestionAPI, '/list.questions')
docs.register(ListQuestionAPI)

"""
[Create Quiz API] : Its responsibility is to create quiz and only admin can create quiz using this API.
"""
class CreateQuizAPI(MethodResource, Resource):
    @doc(description="""
         [Create Quiz API] : Its responsibility is to create quiz and only admin can create quiz using this API.
         [Input Format] :   {
                                "question_ids": [
                                    "id1", "id2", "id3"...
                                ],
                                "quiz_name": "name of the quiz"
                            }
         """, tags=["Quiz"])
    @use_kwargs(CreateQuizSchema, location=('json'))
    @marshal_with(UnifiedAPIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                status, _response = add_quiz(**kwargs)
                message = f"Quiz {kwargs['quiz_name']} has created successfully"
                return _view_generator(status, _response, message)
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Admin can create the quiz")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while creating quiz, error:{str(e)}")), 500


api.add_resource(CreateQuizAPI, '/create.quiz')
docs.register(CreateQuizAPI)

"""
[Assign Quiz API] : Its responsibility is to assign quiz to the user. Only Admin can perform this API call.
"""
class AssignQuizAPI(MethodResource, Resource):
    @doc(description="""
         [Assign Quiz API] : Its responsibility is to assign quiz to the user. Only Admin can perform this API call.
         assign quiz to different users at a time.
         [Input Format] :   {
                                "quiz_id": "id of the quiz",
                                "user_ids": [
                                    "id1", "id2", "id3"...
                                ]
                            }
         """, tags=["Quiz"])
    @use_kwargs(AssignQuizSchema, location=('json'))
    @marshal_with(UnifiedAPIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                status, _response = assign_quiz(**kwargs)
                message_success="Quiz has been assigned respectively to the Users"
                message_not_exist="Quiz does not exist Please check the quiz id"
                return _view_generator(status, _response, message_success, message_not_exist)
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Admin can assign the quiz")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while assigning quiz, error:{str(e)}")), 500


api.add_resource(AssignQuizAPI, '/assign.quiz')
docs.register(AssignQuizAPI)

"""
[View Quiz API] : Its responsibility is to view the quiz details.
Only Admin and the assigned users to this quiz can access the quiz details.
"""
class ViewQuizAPI(MethodResource, Resource):
    @doc(description="""
         [View Quiz API] : Its responsibility is to view the quiz details.
         Only Admin and the assigned users to this quiz can access the quiz details.
         """, tags=["Quiz"])
    @use_kwargs(ViewQuizSchema, location=('json'))
    def post(self, **kwargs):
        try:
            if session.get('user_id'):
                status, _response = view_quiz(**kwargs) #  returns list of questions for the quiz
                message_success = "Quiz has been viewed successfully"
                message_not_exist="Quiz does not exist or you are not assigned to this quiz"
                return _view_generator(status, _response, message_success, message_not_exist)
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Login to view the quiz details")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while viewing quiz, error:{str(e)}")), 500


api.add_resource(ViewQuizAPI, '/view.quiz')
docs.register(ViewQuizAPI)

"""
[View Assigned Quiz API] : Its responsibility is to list all the assigned quizzes 
                            with there submittion status and achieved scores.
"""
class ViewAssignedQuizAPI(MethodResource, Resource):
    @doc(description="""
         [View Assigned Quiz API] : Its responsibility is to list all the assigned quizzes with their submittion status and achieved scores.
         Takes no parameters.
         """, tags=["Quiz"])
    def post(self):
        try:
            if session.get('user_id'):
                status, _response = list_assigned_quizzes() #  returns list of quiz_instances assigned to user
                return _view_generator(status, _response, "Assigned quizzes are listed successfully")
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Login to view the assigned quizzes")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while viewing assigned quizzes, error:{str(e)}")), 500


api.add_resource(ViewAssignedQuizAPI, '/assigned.quizzes')
docs.register(ViewAssignedQuizAPI)


"""
[View All Quiz API] : Its responsibility is to list all the created quizzes. Admin can only list all quizzes.
"""
class ViewAllQuizAPI(MethodResource, Resource):
    @doc(description="""
         [View All Quiz API] : Its responsibility is to list all the created quizzes.
         Admin can only list all quizzes.
         """, tags=["Quiz"])
    # @marshal_with(UnifiedAPIResponseSchema)
    def post(self):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                status, _response = list_quizzes() # return list of quizzes
                return _view_generator(status, _response, "Quizzes are listed successfully")
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Admin can view the quiz")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while viewing quiz, error:{str(e)}")), 500


api.add_resource(ViewAllQuizAPI, '/all.quizzes')
docs.register(ViewAllQuizAPI)

"""
[Attempt Quiz API] : Its responsibility is to perform quiz attempt activity by 
                        the user and the score will be shown as a result of the submitted attempt.
"""
class AttemptQuizAPI(MethodResource, Resource):
    @doc(description="""
         [Attempt Quiz API] : Its responsibility is to perform quiz attempt activity by the user and the score will be shown as a result of the submitted attempt.
         [Input Format] :   {
                                "quiz_id": "id of attempting quiz",
                                "responses": [
                                    {
                                        "question_id": "choice number",
                                        "question_id": "choice number",
                                        "question_id": "choice number",
                                        ...
                                    }
                                ]
                            }
         """, tags=["Quiz"])
    @use_kwargs(UserResponseSchema, location=("json"))
    @marshal_with(UnifiedAPIResponseSchema)
    def post(self, **kwargs):
        try:
            if session.get('user_id'):
                status, _response = attempt_quiz(**kwargs) # return attempted quiz score
                message_success=f"score achieved: {_response.score_achieved if _response != 0 else 0}"
                message_not_exist="Quiz is not assigned to you or does not exist"
                return _view_generator(status, _response, message_success, message_not_exist)
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Users can attempt the quiz")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while attempting quiz, error:{str(e)}")), 500


api.add_resource(AttemptQuizAPI, '/attempt.quiz')
docs.register(AttemptQuizAPI)

"""
[Quiz Results API] : Its responsibility is to provide the quiz results in which the users 
                        having the scores sorted in descending order are displayed, 
                        also the ones who have not attempted are also shown.
                        Admin has only acess to this functionality.
"""
class QuizResultAPI(MethodResource, Resource):
    @doc(description="""
         [Quiz Results API] : Its responsibility is to provide the quiz results in which the users having the scores sorted in descending order are displayed.
         Also the ones who have not attempted are also shown.
         Admin has only acess to this functionality.
         """, tags=["Quiz"])
    def post(self):
        try:
            if session.get('user_id') and (session['is_admin'] == 1):
                status, _response = all_quiz_result() #  returns list of all quizzes with details
                return _view_generator(status, _response, "Quiz results are listed successfully")
            else:
                return UnifiedAPIResponseSchema().dump(dict(message="Only Admin can view all quiz status")), 404
        except Exception as e:
            return UnifiedAPIResponseSchema().dump(dict(message=f"error while viewing quiz status, error:{str(e)}")), 500


api.add_resource(QuizResultAPI, '/quiz.results')
docs.register(QuizResultAPI)


