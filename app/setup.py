import csv
import uuid

from app.models import QuestionMaster
from app import db

"""
Helper function which will create questions based on the data in questions.csv file
"""
def add_questions():
    try:
        with open('questions.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question = row['Question']
                choices = [row[f'Choice{i}'] for i in range(1, 5)]
                answer = row['Answer']
                marks = row['Marks']
                remarks = row['Remarks']
                
                question_entry = QuestionMaster(
                    uuid.uuid4(),
                    question,
                    *choices,
                    answer,
                    marks,
                    remarks
                )
                
                db.session.add(question_entry)
                
            db.session.commit()
    except Exception as e:
        print(f'{e} setup file')
