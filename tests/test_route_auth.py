from unittest.mock import MagicMock

import pytest

from src.database.models import User
from src.conf import messages


@pytest.fixture()
def refresh_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/hw11/auth/signup", json=user)

    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/hw11/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["refresh_token"]


@pytest.fixture()
def access_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/hw11/auth/signup", json=user)

    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/hw11/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/hw11/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["email"] == user.get("email")


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/hw11/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload["detail"] == "Account already exists"


def test_login_user_not_confirmed_email(client, user):
    response = client.post("/hw11/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == messages.EMAIL_NOT_CONFIRMED


def test_login_user(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/hw11/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"


def test_login_user_with_wrong_password(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/hw11/auth/login", data={"username": user.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Invalid password"


def test_login_user_with_wrong_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/hw11/auth/login", data={"username": "example@test.com", "password": user.get("password")})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Invalid email"


def test_refresh_token(client, user, refresh_token):
    response = client.get(
        "/hw11/auth/refresh_token",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data


def test_request_email(client, user, access_token):
    response = client.post("/hw11/auth/request_email", json={"email": user.get("email")})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload == {"message": "Your email is already confirmed"}


def test_confirm_email(client, user, access_token):
    response = client.post("/hw11/auth/request_email", json={"email": user.get("email")})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload == {"message": "Your email is already confirmed"}