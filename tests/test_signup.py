from rest_framework.test import APIClient

def test_signup_happy_path(db):
    c = APIClient()
    r = c.post("/api/users/signup", {
        "first_name": "T", "last_name": "User",
        "email": "t+1@example.com", "password": "Pass1243!"
    }, format="json")
    assert r.status_code == 201
    assert "id" in r.data and r.data["email"] == "t+1@example.com"

def test_signup_duplicate_email(db):
    c = APIClient()
    c.post("/api/users/signup", {
        "first_name": "T", "last_name": "User",
        "email": "dupe@example.com", "password": "Pass1243!"
    }, format="json")
    r = c.post("/api/users/signup", {
        "first_name": "T", "last_name": "User",
        "email": "dupe@example.com", "password": "Pass1243!"
    }, format="json")
    assert r.status_code == 400
    assert "errors" in r.data and "email" in r.data["errors"]
