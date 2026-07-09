# things to test:
#   - POST /api/auth/signup with valid data creates a user and returns a token
#   - POST /api/auth/signup with a duplicate email returns 409
#   - POST /api/auth/signup with missing fields returns 400
#   - POST /api/auth/login with correct credentials returns a token
#   - POST /api/auth/login with wrong password returns 401
#   - a protected route with no token returns 401
#   - a protected route with an expired token returns 401
#   - a protected route with a valid token returns 200

import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_signup(client):
    res = client.post('/api/auth/signup', json={
        'username': 'kamsi',
        'email': 'kamsi@test.com',
        'password': 'password123'
    })
    assert res.status_code == 201
    assert 'token' in res.get_json()

def test_signup_duplicate(client):
    client.post('/api/auth/signup', json={
        'username': 'kamsi',
        'email': 'kamsi@test.com',
        'password': 'password123'
    })
    res = client.post('/api/auth/signup', json={
        'username': 'kamsi',
        'email': 'kamsi@test.com',
        'password': 'password123'
    })
    assert res.status_code == 409

def test_login(client):
    client.post('/api/auth/signup', json={
        'username': 'kamsi',
        'email': 'kamsi@test.com',
        'password': 'password123'
    })
    res = client.post('/api/auth/login', json={
        'email': 'kamsi@test.com',
        'password': 'password123'
    })
    assert res.status_code == 200
    assert 'token' in res.get_json()

def test_login_wrong_password(client):
    client.post('/api/auth/signup', json={
        'username': 'kamsi',
        'email': 'kamsi@test.com',
        'password': 'password123'
    })
    res = client.post('/api/auth/login', json={
        'email': 'kamsi@test.com',
        'password': 'wrongpassword'
    })
    assert res.status_code == 401
