import pytest
from app.models import User, Task

class TestUserModel:
    def test_user_creation(self, db, sample_user):
        assert sample_user.id is not None
        assert sample_user.username == "testuser"
        assert sample_user.email == "test@example.com"

    def test_user_to_dict(self, db, sample_user):
        result = sample_user.to_dict()
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "created_at" in result

    def test_duplicate_username_raises_error(self, db, sample_user):
        duplicate = User(username="testuser", email="different@example.com")
        db.session.add(duplicate)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

class TestTaskModel:
    def test_task_defaults(self, db, sample_user):
        task = Task(title="New task", user_id=sample_user.id)
        db.session.add(task)
        db.session.commit()
        assert task.status == "pending"
        assert task.priority == 1

    def test_task_belongs_to_user(self, db, sample_task, sample_user):
        assert sample_task.owner.username == sample_user.username

    def test_task_to_dict(self, db, sample_task):
        result = sample_task.to_dict()
        assert result["title"] == "Sample text"
        assert result["priority"] == 2