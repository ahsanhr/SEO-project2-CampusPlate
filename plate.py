# plate.py — generate-plate endpoint + knapsack matching algorithm

# picks a combination of real dining hall items that fits the user's calorie and macro budget for the meal

# algorithm (knapsack-style):
#   score each item by how closely its macro ratios match the user's target
#   protein is weighted 2x more than carbs/fat since hitting protein matters most
#   generate multiple different combinations (each anchored on a different high-protein item)
#   so Gemini can pick the best tasting one from the list

# log the result to the recommendations table after generating

# endpoint:
#   POST /api/v1/generate-plate
#   body: { meal_type, max_items, num_combos }
#   returns: { combinations: [[...], [...], ...], targets: {...} }
#   requires valid JWT

import datetime
from flask import Blueprint, request, jsonify
from app import db
from models import Goal, FoodItem, Recommendation
from auth import login_required

plate_bp = Blueprint('plate', __name__, url_prefix='/api/v1')

NUM_COMBOS = 4  
# what fraction of the daily goal each meal gets
MEAL_SPLIT = {
    'breakfast': 0.25,
    'lunch':     0.35,
    'dinner':    0.40,
}


def get_meal_budget(goal, meal_type): # figures out how many cals/macros this meal should be
    split = MEAL_SPLIT.get(meal_type, 0.33)
    return {
        'calories': goal.calories * split,
        'protein_g': goal.protein_g * split,
        'carbs_g': goal.carbs_g * split,
        'fat_g': goal.fat_g * split,
    }


def calc_score(item, targets): # how well does this item fit the macro targets
    if not targets['calories']:
        return 0

    cal = item.calories or 0
    ratio = cal / targets['calories']

    # protein weighted 2x
    p_diff = abs((item.protein_g or 0) - targets['protein_g'] * ratio) * 2
    c_diff = abs((item.carbs_g or 0) - targets['carbs_g'] * ratio)
    f_diff = abs((item.fat_g or 0) - targets['fat_g'] * ratio)

    return 1 / (1 + p_diff + c_diff + f_diff)


def make_plate(anchor, remaining, targets, max_items): # build one meal starting from the anchor item
    cal_budget = targets['calories'] * 1.10  # stay within 110% of this meal's calorie budget
    picked = [anchor]
    total_cal = anchor.calories or 0

    ranked = sorted(remaining, key=lambda i: calc_score(i, targets), reverse=True)

    for item in ranked:
        if len(picked) >= max_items:
            break
        if item.calories and total_cal + item.calories <= cal_budget:
            picked.append(item)
            total_cal += item.calories

    return picked


def get_meals(items, targets, max_items, num_combos): # get multiple meal options each starting from a different high protein food
    by_protein = sorted(items, key=lambda i: i.protein_g or 0, reverse=True)
    anchors = by_protein[:num_combos]

    combos = []
    for anchor in anchors:
        rest = [i for i in items if i.id != anchor.id]
        combo = make_plate(anchor, rest, targets, max_items)
        combos.append(combo)

    return combos


def format_meal(combo): # turn the list of food objects into json
    foods = []
    for i in combo:
        foods.append({
            'id': i.id,
            'name': i.name,
            'serving_size': i.serving_size or '1 serving',
            'calories': i.calories,
            'protein': i.protein_g,
            'carbs': i.carbs_g,
            'fat': i.fat_g
        })
    return {
        'foods': foods,
        'totals': {
            'calories': round(sum(i.calories or 0 for i in combo), 1),
            'protein': round(sum(i.protein_g or 0 for i in combo), 1),
            'carbs': round(sum(i.carbs_g or 0 for i in combo), 1),
            'fat': round(sum(i.fat_g or 0 for i in combo), 1),
        }
    }


@plate_bp.route('/generate-plate', methods=['POST'])
@login_required
def generate_plate(user_id):
    body = request.get_json()
    meal_type = body.get('meal_type', 'lunch')
    max_items = body.get('max_items', 6)
    num_combos = body.get('num_combos', NUM_COMBOS)
    
    goal = Goal.query.filter_by(user_id=user_id).first()
    if not goal:
        return jsonify({'error': 'set your goals first'}), 400

    today = datetime.date.today()
    # items = FoodItem.query.filter_by(date=today, time_of_day=meal_type).all()
    items = FoodItem.query.filter_by(time_of_day=meal_type).all()
    if not items:
        return jsonify({'error': f'no menu items found for {meal_type} today'}), 404

    targets = get_meal_budget(goal, meal_type)
    combos = get_meals(items, targets, max_items, num_combos)

    first = combos[0]
    rec = Recommendation(
        user_id=user_id,
        date=today,
        meal_type=meal_type,
        item_ids=[i.id for i in first],
        total_calories=round(sum(i.calories or 0 for i in first), 1)
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({
        'meals': [format_meal(c) for c in combos],
        'meal_targets': {
            'calories': round(targets['calories'], 1),
            'protein':  round(targets['protein_g'], 1),
            'carbs':    round(targets['carbs_g'], 1),
            'fat':      round(targets['fat_g'], 1),
        },
        'daily_targets': {
            'calories': goal.calories,
            'protein':  goal.protein_g,
            'carbs':    goal.carbs_g,
            'fat':      goal.fat_g
        }
    }), 200
