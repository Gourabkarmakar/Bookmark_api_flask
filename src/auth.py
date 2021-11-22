from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK
import validators
from src.database import User
from src.database import db
from flasgger import swag_from
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity


auth = Blueprint('auth', __name__, url_prefix="/api/v1/auth")


@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()
    if user:
        is_correct_password = check_password_hash(user.password, password)

        if is_correct_password:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                "refresh": refresh,
                "access": access,
                "email": user.email,
                "username": user.username
            }), HTTP_200_OK

    return jsonify({
        "error": "wrong credential"
    }), HTTP_200_OK


@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if len(password) < 6:
        return jsonify({
            "error": "password is too short"
        }), HTTP_400_BAD_REQUEST

    if len(username) < 4:
        return jsonify({
            "error": "username is too short"
        }), HTTP_400_BAD_REQUEST

    if not username.isalnum() or ' ' in username:
        return jsonify({
            "error": "username should be alphanumaric"
        }), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({
            "error": "Email id is not valid"
        }), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({
            "error": "email is already taken"
        }), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            "error": "username is already taken"
        }), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password=password)
    user = User(
        username=username,
        password=pwd_hash,
        email=email
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "user created",
        "user": {
            "username": username,
            "email": email,
            "password": password

        }
    }), HTTP_201_CREATED


@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "username": user.username,
        "email": user.email
    }), HTTP_200_OK


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({
        'access': access
    }), HTTP_200_OK
