import pytest
from app import create_app, db as _db
from app.models import User, Task


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def sample_user(db):
    user = User(username="testuser", email="test@example.com")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_task(db, sample_user):
    task = Task(title="Sample text", user_id=sample_user.id, priority=2)
    db.session.add(task)
    db.session.commit()
    return task