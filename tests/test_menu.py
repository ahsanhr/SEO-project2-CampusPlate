import pytest
from datetime import date
from unittest.mock import patch

# patch the startup fetch before app module executes so tests don't hit the real API
with patch('menu.fetch_and_store_menu', return_value=(0, 'already_loaded')):
    from app import app, db
from models import FoodItem




@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()


def _wipe_today():
    """Remove any existing FoodItem rows for today so tests start clean."""
    FoodItem.query.filter_by(date=date.today()).delete()
    db.session.commit()


def _seed(n=2):
    _wipe_today()
    for i in range(n):
        db.session.add(FoodItem(
            name=f'Item {i}', location='Test Hall', date=date.today(),
            time_of_day='lunch', station='Grill', serving_size=None,
            calories=float(100 * (i + 1)), protein_g=10.0,
            carbs_g=5.0, fat_g=3.0,
        ))
    db.session.commit()


def test_today_returns_seeded_items(client):
    with app.app_context():
        _seed()
    res = client.get('/api/menu/today')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    assert data[0]['location'] == 'Test Hall'
    assert set(data[0].keys()) == {
        'id', 'name', 'location', 'time_of_day', 'station',
        'calories', 'protein_g', 'carbs_g', 'fat_g',
    }


def test_today_empty_when_no_data(client):
    with app.app_context():
        _wipe_today()
    res = client.get('/api/menu/today')
    assert res.status_code == 200
    assert res.get_json() == []


def test_refresh_wipes_and_reinserts(client):
    with app.app_context():
        _seed()
    with patch('menu.fetch_and_store_menu', return_value=(5, None)) as mock_fetch:
        res = client.post('/api/menu/refresh')
    assert res.status_code == 200
    assert res.get_json()['inserted'] == 5
    mock_fetch.assert_called_once()
    with app.app_context():
        count = FoodItem.query.filter_by(date=date.today()).count()
    assert count == 0  # mock didn't actually insert rows


def test_refresh_get_not_allowed(client):
    res = client.get('/api/menu/refresh')
    assert res.status_code == 405
