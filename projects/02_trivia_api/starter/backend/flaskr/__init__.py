import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

  '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
  '''

  @app.route('/categories')
  def categories():
    categories = Category.query.all()
    cats = [category.format() for category in categories]
    return jsonify({
      'success': True,
      'categories': cats
    })

  '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    # Pagination
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    # Fetch questions
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    # Fetch categories
    categories = Category.query.all()
    categories_names = []
    for category in categories:
      categories_names.append(category.type)
    current_category = request.args.get('current_category', 0, type=int)
    # Show question based on categories
    if current_category > 6:
      current_category = 0
    if current_category != 0:
      questions = Question.query.filter_by(category=(current_category)).all()
    formatted_questions = [question.format() for question in questions]
    questions_in_page = formatted_questions[start:end]
    if page == 0 or questions_in_page == 0:
        abort(404)
    data = {
        'success': True,
        'questions': questions_in_page,
        'total_questions': len(formatted_questions),
        'current_category': current_category,
        'categories': categories_names
    }
    return jsonify(data)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'message': 'deleted question {}'.format(question.id)
      })
    except:
      abort(404)

  '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def post_new_question():
    body = request.get_json()
    if not ("question" in body and "answer" in body and "category" in body and "difficulty" in body):
      abort(422)
    req_question = body.get("question")
    req_answer = body.get("answer")
    req_category = body.get("category")
    req_difficulty = body.get("difficulty")
    try:
      if req_category == 1:
        question = Question(question=req_question, answer=req_answer, category=int(req_category), difficulty=req_difficulty)  
      else:
        question = Question(question=req_question, answer=req_answer, category=(int(req_category)+1), difficulty=req_difficulty)
      question.insert()
      body['success'] = True
      return jsonify(body)
    except:
      abort(422)

  '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    search_term = request.get_json()['searchTerm']
    questions = Question.query.filter(Question.question.contains(search_term)).all()
    print(questions)
    return jsonify({
      "success": True,
      "questions": [question.format() for question in questions]
    })

  '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
  '''

  # This functionality is implemented in the /questions?current_category get route.

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/play', methods=['POST'])
  def quiz_game():
    body = request.get_json()
    req_category = body.get('category')
    req_previous_questions = body.get('previous_questions')

    try:
      if req_category['id'] == 0:
        questions = Question.query.filter(Question.id.notin_(req_previous_questions)).all()
        print(0)
      elif not req_category['id'] == 0:
        questions = Question.query.filter(Question.category == str(req_category['id']))\
        .filter(Question.id.notin_(req_previous_questions)).all()
        print(1)
      print(questions)
      print(req_category)
      question = questions[random.randrange(0, (len(questions)-1))]
      return jsonify({
        "success": True,
        "question": {
          "id": question.id,
          "question": question.question,
          "answer": question.answer,
          "category": question.category,
          "difficulty": question.difficulty
        }
      })
    except:
      abort(422)

  '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
  '''
  
  @app.errorhandler(404)
  def page_not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Page not found"
        }), 404

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad request"
        }), 400
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable entity"
    }), 422

  return app

    