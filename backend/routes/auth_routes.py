# routes/auth_routes.py

from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        return jsonify({"msg" : "username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "username already exists"}), 400

    user = User(username=username, email=email, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "user created", "user_id":user.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "bad username or password"}), 401

    additional_claims = {"role": user.role}

    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims, expires_delta=timedelta(hours=8))
    return jsonify({"access_token": access_token, "role": user.role, "user_id": user.id}), 200
