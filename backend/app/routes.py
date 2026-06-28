from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from . import db
from .models import Task, User
from .workers import worker, Job

tasks_bp = Blueprint("tasks", __name__)
users_bp = Blueprint("users", __name__)

# ------------ User Routes ------------

@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "Username and Email are required,"}), 400
    
    user = User(username=data["username"], email=data["email"])
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or Email already exist."}), 409
    
    return jsonify(user.to_dict()), 201

@users_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

# ------------ Task Routes ------------

@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status")
    query = Task.query

    if status:
        query = query.filter_by(status=status)
    tasks = query.order_by(Task.priority.desc()).all()

    return jsonify([t.to_dict() for t in tasks])

@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Title is required."}), 400
    if not data.get("user_id"):
        return jsonify({"error": "User ID is required."}), 400
    
    user = db.session.get(User, data["user_id"])
    if not user:
        return jsonify({"error": f"No user found with id {data['user_id']}"}), 404
    
    task = Task(
        title=data["title"],
        description=data.get("description", ""),
        user_id=data["user_id"],
        priority=data.get("priority", 1),
    )
    db.session.add(task)
    db.session.commit()

    worker.enqueue(Job("notify", {
        "email": user.email,
        "message": f"New task created: {task.title}",
    }))
    
    return jsonify(task.to_dict()), 201

@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    task.priority = data.get("priority", task.priority)

    db.session.commit()
    return jsonify(task.to_dict())

@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted.", "id": task_id}), 200