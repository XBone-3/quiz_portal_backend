from flask import Flask
from apispec import APISpec
from flask_restful import Api
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

"""
Initialiasing application instance with Flask Framework and applying secret key to the application
"""
application = Flask(__name__)
application.secret_key = 'quiz-portal-12345'

"""
Thsi will configure the swagger docs for the application
"""
api = Api(application)  # Flask restful wraps Flask app around it.

application.config.update({
    'APISPEC_SPEC': APISpec(
        title='Quiz Portal',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(application)

from app.models import *

def add_user():
    try:
        users = [
            {
                'id': str(i),
                'name': 'admin' if i == 10000 else 'user' + str(i),
                'username': 'admin' if i == 10000 else 'user' + str(i),
                'password': 'admin' if i == 10000 else 'user' + str(i),
                'is_admin': 1 if i == 10000 else 0
            } for i in range(10000, 11001)
        ]
        for user in users:
            user_entry = UserMaster(
                id=user['id'],
                name=user['name'],
                username=user['username'],
                password=user['password'],
                is_admin=user['is_admin']
            )
            db.session.add(user_entry)
        db.session.commit()
    except Exception as e:
        print(f'{e}')

with application.app_context():
    add_user()
