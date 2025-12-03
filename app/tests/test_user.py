
def test_create_user(client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "strongpassword"
    }

    response = client.post("/api/v1/user/create", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
