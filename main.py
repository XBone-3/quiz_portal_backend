from app import application
from app.apis import (SignUpAPI, LoginAPI, LogoutAPI, AddQuestionAPI, ListQuestionAPI, CreateQuizAPI, 
                      AssignQuizAPI, ViewQuizAPI, ViewAssignedQuizAPI, ViewAllQuizAPI, AttemptQuizAPI, QuizResultAPI)
from app.setup import add_questions
from app.services import add_users, add_quizzes

"""
[Driver Module] : It is responsible for stating the server for application for apis serving
"""
if __name__ == "__main__":
    with application.app_context():
        try:
            add_questions()
        except Exception as e:
            print(f'{e} main file')
        
        application.run(debug=False, port=8000)
    
    
    