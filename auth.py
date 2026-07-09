import os
import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify
from app import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

secret = os.getenv('JWT_SECRET', 'dev-jwt-secret')


def make_token(uid): # makes the jwt toekn for the user
    payload = {
        'sub': uid,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def login_required(f): 
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return jsonify({'error': 'missing token'}), 401

        token = header.split(' ', 1)[1]

        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token expired, please log in again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'invalid token'}), 401

        kwargs['user_id'] = payload['sub']
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route('/signup', methods=['POST'])
def signup(): # creates new accout and returns token
    body = request.get_json()
    username = body.get('username', '').strip()
    email = body.get('email', '').strip().lower()
    password = body.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'username, email, and password are all required'}), 400

    taken = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()
    if taken:
        return jsonify({'error': 'username or email already taken'}), 409

    new_user = User(
        username=username,
        email=email,
        password=password
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'token': make_token(new_user.id), 'user_id': new_user.id}), 201


@auth_bp.route('/login', methods=['POST'])
def login(): # checks credentails and returns token if correct
    body = request.get_json()
    email = body.get('email', '').strip().lower()
    password = body.get('password', '')

    match = User.query.filter_by(email=email).first()

    if not match or match.password != password:
        return jsonify({'error': 'invalid email or password'}), 401

    return jsonify({'token': make_token(match.id), 'user_id': match.id}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }), 200

