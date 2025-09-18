from rest_framework.test import APIClient

def token(c, email):
    r = c.post("/api/users/token", {"username": email, "password": "Pass1243!"}, format="json")
    assert r.status_code == 200
    return r.data["access"]

def test_create_and_history(db):
    c = APIClient()

    # create user
    r = c.post("/api/users/signup", {
        "first_name":"U","last_name":"One","email":"u1@example.com","password":"Pass1243!"
    }, format="json")
    assert r.status_code in (200, 201)

    # auth
    tok = token(c, "u1@example.com")
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")

    # create conversation
    r = c.post("/api/chat/conversations", {"member_ids":[]}, format="json")
    assert r.status_code == 200 and "conversation_id" in r.data
    cid = r.data["conversation_id"]

    # fetch history
    r2 = c.get(f"/api/chat/conversations/{cid}/history?limit=5")
    assert r2.status_code == 200 and "messages" in r2.data
