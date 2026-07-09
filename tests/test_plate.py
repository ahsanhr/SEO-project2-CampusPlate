# test_plate.py — tests for the plate generation + knapsack algorithm

# things to test:
#   - generate-plate returns items that don't exceed the user's calorie target
#   - the number of returned items never exceeds max_items
#   - if there are no menu items for today, returns a clear error
#   - if the user hasn't set goals yet, returns a clear error before running the algorithm
#   - the knapsack result is logged to the recommendations table
#   - calling generate-plate without a JWT returns 401

import pytest
import datetime
import json
from unittest.mock import patch, MagicMock
from app import app, db
from models import Goal, FoodItem

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
    return data['token'], data['user_id']


def seed_goal(user_id):
    goal = Goal(user_id=user_id, calories=2000, protein_g=150, carbs_g=200, fat_g=67)
    db.session.add(goal)
    db.session.commit()


DUMMY_MENU = [
    # breakfast
    {'time_of_day': 'breakfast', 'name': 'Scrambled Eggs',     'serving_size': '2 eggs',   'calories': 180, 'protein_g': 14, 'carbs_g': 2,  'fat_g': 12},
    {'time_of_day': 'breakfast', 'name': 'Oatmeal',            'serving_size': '1 cup',    'calories': 160, 'protein_g': 6,  'carbs_g': 28, 'fat_g': 3},
    {'time_of_day': 'breakfast', 'name': 'Greek Yogurt',       'serving_size': '6 oz',     'calories': 120, 'protein_g': 17, 'carbs_g': 8,  'fat_g': 0},
    {'time_of_day': 'breakfast', 'name': 'Bacon',              'serving_size': '2 strips', 'calories': 90,  'protein_g': 6,  'carbs_g': 0,  'fat_g': 7},
    {'time_of_day': 'breakfast', 'name': 'Whole Wheat Toast',  'serving_size': '2 slices', 'calories': 140, 'protein_g': 5,  'carbs_g': 26, 'fat_g': 2},
    {'time_of_day': 'breakfast', 'name': 'Orange Juice',       'serving_size': '8 oz',     'calories': 110, 'protein_g': 2,  'carbs_g': 26, 'fat_g': 0},
    {'time_of_day': 'breakfast', 'name': 'Banana',             'serving_size': '1 medium', 'calories': 105, 'protein_g': 1,  'carbs_g': 27, 'fat_g': 0},

    # lunch
    {'time_of_day': 'lunch', 'name': 'Grilled Chicken',        'serving_size': '4 oz',     'calories': 350, 'protein_g': 45, 'carbs_g': 10, 'fat_g': 8},
    {'time_of_day': 'lunch', 'name': 'Brown Rice',             'serving_size': '1 cup',    'calories': 250, 'protein_g': 5,  'carbs_g': 52, 'fat_g': 2},
    {'time_of_day': 'lunch', 'name': 'Caesar Salad',           'serving_size': '1 bowl',   'calories': 180, 'protein_g': 6,  'carbs_g': 12, 'fat_g': 14},
    {'time_of_day': 'lunch', 'name': 'Mac and Cheese',         'serving_size': '1 cup',    'calories': 480, 'protein_g': 18, 'carbs_g': 60, 'fat_g': 20},
    {'time_of_day': 'lunch', 'name': 'Black Beans',            'serving_size': '1/2 cup',  'calories': 200, 'protein_g': 12, 'carbs_g': 36, 'fat_g': 1},
    {'time_of_day': 'lunch', 'name': 'Steamed Broccoli',       'serving_size': '1 cup',    'calories': 80,  'protein_g': 5,  'carbs_g': 14, 'fat_g': 1},
    {'time_of_day': 'lunch', 'name': 'Turkey Meatballs',       'serving_size': '3 pcs',    'calories': 300, 'protein_g': 35, 'carbs_g': 8,  'fat_g': 12},
    {'time_of_day': 'lunch', 'name': 'Pasta Marinara',         'serving_size': '1 cup',    'calories': 420, 'protein_g': 14, 'carbs_g': 72, 'fat_g': 8},

    # dinner
    {'time_of_day': 'dinner', 'name': 'Salmon Fillet',         'serving_size': '5 oz',     'calories': 350, 'protein_g': 40, 'carbs_g': 0,  'fat_g': 18},
    {'time_of_day': 'dinner', 'name': 'Mashed Potatoes',       'serving_size': '1 cup',    'calories': 220, 'protein_g': 4,  'carbs_g': 38, 'fat_g': 8},
    {'time_of_day': 'dinner', 'name': 'Roasted Vegetables',    'serving_size': '1 cup',    'calories': 100, 'protein_g': 3,  'carbs_g': 18, 'fat_g': 3},
    {'time_of_day': 'dinner', 'name': 'Beef Stir Fry',         'serving_size': '1 cup',    'calories': 420, 'protein_g': 38, 'carbs_g': 22, 'fat_g': 18},
    {'time_of_day': 'dinner', 'name': 'Steamed White Rice',    'serving_size': '1 cup',    'calories': 200, 'protein_g': 4,  'carbs_g': 44, 'fat_g': 0},
    {'time_of_day': 'dinner', 'name': 'Garden Salad',          'serving_size': '1 bowl',   'calories': 80,  'protein_g': 2,  'carbs_g': 10, 'fat_g': 4},
    {'time_of_day': 'dinner', 'name': 'Chicken Breast',        'serving_size': '5 oz',     'calories': 280, 'protein_g': 52, 'carbs_g': 0,  'fat_g': 6},
]

def seed_menu():
    today = datetime.date.today()
    for item in DUMMY_MENU:
        db.session.add(FoodItem(date=today, **item))
    db.session.commit()


def test_generate_plate(client):
    token, user_id = signup_and_token(client)
    with app.app_context():
        seed_goal(user_id)
        seed_menu()

    res = client.post('/api/v1/generate-plate',
        json={'meal_type': 'lunch', 'max_items': 4, 'num_combos': 6},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200
    data = res.get_json()
    print(json.dumps(data, indent=2))

    # response shape
    assert 'meals' in data
    assert 'meal_targets' in data
    assert 'daily_targets' in data
    assert len(data['meals']) == 6

    for meal in data['meals']:
        assert meal['totals']['calories'] <= data['meal_targets']['calories'] * 1.10

    meal = data['meals'][0]
    assert 'foods' in meal
    assert 'totals' in meal
    assert len(meal['foods']) <= 4

    food = meal['foods'][0]
    assert 'serving_size' in food
    assert 'protein' in food
    assert 'calories' in food


def test_no_goal(client):
    token, user_id = signup_and_token(client)
    with app.app_context():
        seed_menu()

    res = client.post('/api/v1/generate-plate',
        json={'meal_type': 'lunch'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 400


def test_no_menu(client):
    token, user_id = signup_and_token(client)
    with app.app_context():
        seed_goal(user_id)

    res = client.post('/api/v1/generate-plate',
        json={'meal_type': 'lunch'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 404


def test_no_token(client):
    res = client.post('/api/v1/generate-plate', json={'meal_type': 'lunch'})
    assert res.status_code == 401


# --- gemini tests (real api calls) ---

def test_gemini_serving_tips_attached(client):
    # real gemini call — serving_tip and gemini_pick should come back
    token, user_id = signup_and_token(client)
    with app.app_context():
        seed_goal(user_id)
        seed_menu()

    with patch('plate._gemini_cache', {}):  # clear cache so we actually hit the api
        res = client.post('/api/v1/generate-plate',
            json={'meal_type': 'lunch', 'max_items': 3, 'num_combos': 4},
            headers={'Authorization': f'Bearer {token}'}
        )

    assert res.status_code == 200
    data = res.get_json()
    print(json.dumps(data.get('gemini_pick'), indent=2))

    assert data['gemini_pick'] is not None
    assert 'pick' in data['gemini_pick']
    assert 'reason' in data['gemini_pick']
    assert isinstance(data['gemini_pick']['pick'], int)

    # each food should have a serving_tip
    for food in data['meals'][0]['foods']:
        assert 'serving_tip' in food
        assert food['serving_tip'] is not None


def test_gemini_failure_still_returns_meals(client):
    # if gemini throws for any reason, meals still come back fine
    token, user_id = signup_and_token(client)
    with app.app_context():
        seed_goal(user_id)
        seed_menu()

    with patch('plate._gemini_cache', {}):
        with patch('plate.gemini') as mock_client:
            mock_client.models.generate_content.side_effect = Exception('api error')

            res = client.post('/api/v1/generate-plate',
                json={'meal_type': 'lunch', 'max_items': 3, 'num_combos': 4},
                headers={'Authorization': f'Bearer {token}'}
            )

    assert res.status_code == 200
    data = res.get_json()
    assert 'meals' in data
    assert len(data['meals']) == 4
    assert data['gemini_pick'] is None


def test_gemini_cached_on_second_call(client):
    # second request same day should use cache, not call gemini again
    token, user_id = signup_and_token(client)
    with app.app_context():
        seed_goal(user_id)
        seed_menu()

    with patch('plate._gemini_cache', {}):
        with patch('plate.gemini') as mock_client:
            mock_res = MagicMock()
            mock_res.text = json.dumps({
                "serving_tips": {"Option 1": ["tip"], "Option 2": ["tip"], "Option 3": ["tip"], "Option 4": ["tip"]},
                "recommendation": {"pick": 1, "reason": "best option"}
            })
            mock_client.models.generate_content.return_value = mock_res

            client.post('/api/v1/generate-plate',
                json={'meal_type': 'lunch', 'num_combos': 4},
                headers={'Authorization': f'Bearer {token}'}
            )
            client.post('/api/v1/generate-plate',
                json={'meal_type': 'lunch', 'num_combos': 4},
                headers={'Authorization': f'Bearer {token}'}
            )

            assert mock_client.models.generate_content.call_count == 1

