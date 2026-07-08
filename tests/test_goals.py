# test_goals.py — tests for goal setting endpoints
#
# things to test:
#   - POST /api/goals/direct saves goals and returns them
#   - POST /api/goals/direct with missing fields returns 400
#   - POST /api/goals/calculated runs the formula and saves goals
#   - POST /api/goals/calculated with missing fields returns 400
#   - PUT /api/goals updates existing goals
#   - PUT /api/goals when no goal exists returns 404
#   - all routes return 401 without a token

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


def signup_and_token(client):
    res = client.post('/api/auth/signup', json={
        'username': 'kamsi', 'email': 'k@test.com', 'password': 'pass123'
    })
    data = res.get_json()
    return data['token']


def test_set_direct(client):
    token = signup_and_token(client)
    res = client.post('/api/goals/direct',
        json={'calories': 2000, 'protein_g': 150, 'carbs_g': 200, 'fat_g': 67},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data['goals']['calories'] == 2000
    assert data['goals']['protein_g'] == 150


def test_set_direct_missing_fields(client):
    token = signup_and_token(client)
    res = client.post('/api/goals/direct',
        json={'calories': 2000},  # missing protein, carbs, fat
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 400


def test_set_calculated(client):
    token = signup_and_token(client)
    res = client.post('/api/goals/calculated',
        json={'age': 21, 'height': 175, 'weight': 160, 'sex': 'male',
              'activity': 'moderate', 'fitness_goal': 'maintain'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 201
    data = res.get_json()
    assert 'goals' in data
    assert data['goals']['calories'] > 0
    assert data['goals']['protein_g'] > 0


def test_set_calculated_missing_fields(client):
    token = signup_and_token(client)
    res = client.post('/api/goals/calculated',
        json={'age': 21},  # missing height and weight
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 400


def test_update_goal(client):
    token = signup_and_token(client)
    # set a goal first
    client.post('/api/goals/direct',
        json={'calories': 2000, 'protein_g': 150, 'carbs_g': 200, 'fat_g': 67},
        headers={'Authorization': f'Bearer {token}'}
    )
    # now update just calories
    res = client.put('/api/goals',
        json={'calories': 2200},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200
    assert res.get_json()['goals']['calories'] == 2200
    assert res.get_json()['goals']['protein_g'] == 150  # unchanged


def test_update_goal_not_found(client):
    token = signup_and_token(client)
    res = client.put('/api/goals',
        json={'calories': 2200},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 404


def test_no_token(client):
    res = client.post('/api/goals/direct',
        json={'calories': 2000, 'protein_g': 150, 'carbs_g': 200, 'fat_g': 67}
    )
    assert res.status_code == 401
