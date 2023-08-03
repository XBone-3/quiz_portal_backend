from marshmallow import Schema, fields, base


"""
This module aims at providing the request and response format for the various api calls.
This also helpful for creating swagger docs for apis testing.
"""

class UserMasterSchema(Schema):
    name = fields.String(required=True, default='name')
    username = fields.String(required=True, default='username')
    password = fields.String(required=True, default='password')
    is_admin = fields.Integer(required=True, default=0)


class CreateQuizSchema(Schema):
    quiz_name = fields.String(required=True, default='quiz_name')
    question_ids = fields.List(fields.String()) 

class ViewQuizSchema(Schema):
    quiz_id = fields.String(required=True)

class QuestionMasterSchema(Schema):
    question = fields.String(required=True)
    choice1 = fields.String(required=True)
    choice2 = fields.String(required=True)
    choice3 = fields.String(required=True)
    choice4 = fields.String(required=True)
    answer = fields.Integer(required=True)
    marks = fields.Integer(required=True)
    remarks = fields.String(required=True)

class AssignQuizSchema(Schema):
    instance = fields.Dict(keys=fields.String(), values=fields.List(fields.String()))

class UserResponseSchema(Schema):
    quiz_id = fields.String(required=True)
    responses = fields.List(fields.Dict(keys=fields.String(), values=fields.String()))

class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

class APIResponseSchema(Schema):
    message = fields.String(default="default responce message")

class ViewResponseSchema(Schema):
    response = fields.List(fields.Dict(keys=fields.String(), values=fields.String()))