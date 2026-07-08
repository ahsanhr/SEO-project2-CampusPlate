# menu.py — fetches today's uf dining menu and saves it to the db

# uses the dineoncampus api (apiv4.dineoncampus.com)
# needs cloudscraper because plain requests gets blocked by cloudflare
#
# flow:
#   1. hit /sites/todays_menu to get all 19 uf locations
#   2. for each location, get its meal periods (breakfast / lunch / dinner)
#   3. for each period, fetch the full menu with macros
#   4. write every item to food_items table

import cloudscraper
from datetime import date
from flask import Blueprint, jsonify

from app import db
from models import FoodItem
from menu_parser import extract_nutrients

menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')

BASE_URL = 'https://apiv4.dineoncampus.com'
UF_SITE_ID = '62312845a9f13a1011b4dd3a'

# map period names to the 3 time slots we use in the db
PERIOD_MAP = {
    'breakfast': 'breakfast',
    'brunch':    'lunch',
    'lunch':     'lunch',
    'dinner':    'dinner',
    'late night': 'dinner',
}


# --- private helpers ---

def _scraper():
    return cloudscraper.create_scraper()


def _fetch_periods(scraper, loc_id, date_str):
    # returns a list of { id, name } for the given location + date
    r = scraper.get(
        f'{BASE_URL}/locations/{loc_id}/periods/',
        params={'date': date_str},
        timeout=15,
    )
    if r.status_code != 200:
        return []
    return r.json().get('periods', [])


def _fetch_menu_items(scraper, loc_id, period_id, date_str, loc_name, period_name):
    # returns a list of dicts ready to be turned into FoodItem rows
    r = scraper.get(
        f'{BASE_URL}/locations/{loc_id}/menu',
        params={'date': date_str, 'period': period_id},
        timeout=20,
    )
    if r.status_code != 200:
        return []

    time_of_day = PERIOD_MAP.get(period_name.lower(), period_name.lower())
    items = []

    for category in r.json().get('period', {}).get('categories', []):
        station = category.get('name', '')
        for raw_item in category.get('items', []):
            name = raw_item.get('name', '').strip()
            if not name:
                continue
            nutrients = extract_nutrients(raw_item)
            items.append({
                'name':        name,
                'location':    loc_name,
                'time_of_day': time_of_day,
                'station':     station,
                **nutrients,
            })

    return items


# --- public function called by the route or by other parts of the app ---

def fetch_and_store_menu():
    # returns (number of rows inserted, error string or None)
    today = date.today()

    # skip if we already loaded today's menu
    if FoodItem.query.filter_by(date=today).first():
        return 0, 'already_loaded'

    scraper = _scraper()
    date_str = today.isoformat()

    # step 1: get all locations for uf
    r = scraper.get(
        f'{BASE_URL}/sites/todays_menu',
        params={'siteId': UF_SITE_ID},
        timeout=20,
    )
    if r.status_code != 200:
        return 0, f'api_error_{r.status_code}'

    locations = r.json().get('locations', [])
    inserted = 0

    for location in locations:
        loc_id = location['id']
        loc_name = location.get('name', '')

        # step 2: get meal periods for this location
        periods = _fetch_periods(scraper, loc_id, date_str)

        for period in periods:
            # step 3: get full menu with macros for this period
            items = _fetch_menu_items(
                scraper, loc_id, period['id'], date_str, loc_name, period['name']
            )

            # step 4: write to db
            for item in items:
                db.session.add(FoodItem(date=today, **item))
                inserted += 1

    db.session.commit()
    return inserted, None


# --- routes ---

@menu_bp.route('/today')
def today_menu():
    today = date.today()
    items = FoodItem.query.filter_by(date=today).all()

    # auto-fetch if the table is empty for today
    if not items:
        count, err = fetch_and_store_menu()
        if err and err != 'already_loaded':
            return jsonify({'error': err}), 502
        items = FoodItem.query.filter_by(date=today).all()

    return jsonify([{
        'id':          i.id,
        'name':        i.name,
        'location':    i.location,
        'time_of_day': i.time_of_day,
        'station':     i.station,
        'calories':    i.calories,
        'protein_g':   i.protein_g,
        'carbs_g':     i.carbs_g,
        'fat_g':       i.fat_g,
    } for i in items])


@menu_bp.route('/refresh', methods=['POST'])
def refresh_menu():
    # wipe today's rows and re-fetch fresh data from the api
    today = date.today()
    FoodItem.query.filter_by(date=today).delete()
    db.session.commit()

    count, err = fetch_and_store_menu()
    if err:
        return jsonify({'error': err}), 502
    return jsonify({'inserted': count})
