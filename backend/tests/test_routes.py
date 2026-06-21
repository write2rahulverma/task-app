import json

def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")

def put_json(client, url, data):
    return client.put(url, data=json.dumps(data), content_type="application/json")

class TestUserRoutes:
    def test_create_user_success(self, client, db):
        res = post_json(client, "api/users", {"username": "alice", "email": "alice@x.com"})
        assert res.status_code == 201
        assert res.json["username"] == "alice"

    def test_create_user_missing_fields(self, client, db):
        res = post_json(client, "/api/users", {"username": "bob"})
        assert res.status_code == 400
        assert "error" in res.json

    def test_create_duplicate_user(self, client, db, sample_user):
        res = post_json(client, "/api/users", {
            "username": "testuser", "email": "another@example.com"
        })
        assert res.status_code == 409

class TestTaskRoutes:
    def test_get_tasks_returns_list(self, client, db):
        res = client.get("api/tasks")
        assert res.status_code == 200
        assert isinstance(res.json, list)

    def test_create_task_success(self, client, db, sample_user):
        res = post_json(client, "/api/tasks", {
            "title": "Write integration tests",
            "user_id": sample_user.id,
            "priority": 3,
        })
        assert res.status_code == 201
        assert res.json["title"] == "Write integration tests"
        assert res.json["status"] == "pending"

    def test_create_task_without_description(self, client, db, sample_user):
        res = post_json(client, "/api/tasks", {
            "title": "No description here",
            "user_id": sample_user.id,
        })
        assert res.status_code == 201
        assert res.json["description"] == ""

    def test_create_task_missing_title(self, client, db, sample_user):
        res = post_json(client, "/api/tasks", {"user_id": sample_user.id})
        assert res.status_code == 400

    def test_create_task_missing_user_id(self, client, db):
        res = post_json(client, "/api/tasks", {"title": "Orphan task"})
        assert res.status_code == 400

    def test_create_task_invalid_user_id(self, client, db):
        res = post_json(client, "/api/tasks", {"title": "Ghost task", "user_id": 99999})
        assert res.status_code == 404

    def test_update_task_status(self, client, db, sample_task):
        res = put_json(client, f"/api/tasks/{sample_task.id}", {"status": "done"})
        assert res.status_code == 200
        assert res.json["status"] == "done"

    def test_delete_task(self, client, db, sample_task):
        res = client.delete(f"/api/tasks/{sample_task.id}")
        assert res.status_code == 200

        get_res = client.get(f"/api/tasks/{sample_task.id}")
        assert get_res.status_code == 404

    def test_filter_tasks_by_status(self, client, db, sample_user):
        post_json(client, "/api/tasks", {"title": "Pending one", "user_id": sample_user.id, "priority": 1})
        res = client.get("/api/tasks?status=pending")
        assert res.status_code == 200
        assert all(t["status"] == "pending" for t in res.json)