from flask import Blueprint, request, jsonify
from . import db
from .models import Task, User

tasks_bp = Blueprint("tasks", __name__)
users_bp = Blueprint("users", __name__)

# ------------ User Routes ------------

@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(username=data["username"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dist()), 201

@users_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dist() for u in users])

# ------------ Task Routes ------------

@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status")
    query = Task.query
    if status:
        query = query.filter_by(status=status)
    tasks = query.order_by(Task.priority.desc()).all()
    return jsonify([t.to_dist() for t in tasks])

@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required."}), 400
    
    task = Task(
        title=data["title"],
        description=data["description"],
        user_id=data["user_id"],
        priority=data.get("priority", 1),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dist()), 201

@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dist())

@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    task.priority = data.get("priority", task.priority)

    db.session.commit()
    return jsonify(task.to_dist())

@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted.", "id": task_id}), 200