import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()

    drinks = [drink.short() for drink in all_drinks]

    if len(drinks) == 0:
        abort(404)
        
    return jsonify({
        "success": True,
        "drinks": drinks
        })


@app.route('/drinks-detail')
@requires_auth('get:drink-detail')
def get_drinks_details():
    all_drinks = Drink.query.all()

    drinks = [drink.long() for drink in all_drinks]

    if len(drinks) == 0:
        abort(404)
        
    return jsonify({
        "success": True,
        "drinks": drinks
        })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        drink = [new_drink.long()]
        return jsonify({
            "success": True,
            "drinks": drink
        })

    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(id, payload):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.title = body['title']
        drink.recipe = body['recipe']

        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id, payload):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        }),200

    except Exception:
        abort(422)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404, 
        "message": "resource not found"
        }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, 
        "message": "bad request"
        }), 400

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 405, 
        "message": "method not allowed"
        }), 405
