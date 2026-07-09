# goals.py — goal input (direct + calculated), edit/update

# two ways a user can set their goals:
# 1. direct — they enter calories + macros themselves
# 2. calculated — they enter age, height, weight, and a fitness goal
#                  and we run the Mifflin-St Jeor equation to get their targets

# goals are saved to the db tied to the user, upserted if they already exist
# all routes require a valid JWT

# endpoints:
#   POST /api/goals/direct      → save targets directly
#   POST /api/goals/calculated  → calculate targets from body stats, then save
#   PUT  /api/goals             → update the active goal

from flask import Blueprint, request, jsonify
from app import db
from models import Goal, ProfileInput
from auth import login_required

goals_bp = Blueprint('goals', __name__, url_prefix='/api/goals')


# activity multipliers for Mifflin-St Jeor
activity_multipliers = {
    'sedentary':   1.2,
    'light':       1.375,
    'moderate':    1.55,
    'active':      1.725,
    'very_active': 1.9,
}

# how many calories to add/subtract based on what they want
goal_offsets = {
    'cut':      -300,
    'maintain':    0,
    'bulk':      300,
}


def run_mifflin(age, height_cm, weight_lbs, sex, activity='moderate', goal='maintain'):
    kg = weight_lbs * 0.453592  # lbs to kg
    if sex == 'male':
        bmr = (10 * kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * kg) + (6.25 * height_cm) - (5 * age) - 161

    tdee = bmr * activity_multipliers.get(activity, 1.55)
    cals = tdee + goal_offsets.get(goal, 0)

    # rough macro split: 30% protein, 40% carbs, 30% fat
    protein = round((cals * 0.30) / 4, 1)
    carbs = round((cals * 0.40) / 4, 1)
    fat = round((cals * 0.30) / 9, 1)

    return round(cals, 1), protein, carbs, fat


def save_goal(user_id, cals, protein, carbs, fat, source):
    # update if they already have one, otherwise make a new row
    existing = Goal.query.filter_by(user_id=user_id).first()
    if existing:
        existing.calories = cals
        existing.protein_g = protein
        existing.carbs_g = carbs
        existing.fat_g = fat
        existing.source = source
        g = existing
    else:
        g = Goal(user_id=user_id, calories=cals,
                 protein_g=protein, carbs_g=carbs,
                 fat_g=fat, source=source)
        db.session.add(g)
    db.session.commit()
    return g


@goals_bp.route('/direct', methods=['POST'])
@login_required
def set_direct(user_id=None):
    body = request.get_json()
    cals = body.get('calories')
    protein = body.get('protein_g')
    carbs = body.get('carbs_g')
    fat = body.get('fat_g')

    if not all([cals, protein, carbs, fat]):
        return jsonify({'error': 'calories, protein_g, carbs_g, fat_g are all required'}), 400

    g = save_goal(user_id, cals, protein, carbs, fat, source='direct')

    return jsonify({
        'message': 'goals saved',
        'goals': {
            'calories': g.calories,
            'protein_g': g.protein_g,
            'carbs_g': g.carbs_g,
            'fat_g': g.fat_g,
        }
    }), 201


@goals_bp.route('/calculated', methods=['POST'])
@login_required
def set_calculated(user_id=None):
    body = request.get_json()
    age = body.get('age')
    height = body.get('height')
    weight = body.get('weight')  # lbs
    sex = body.get('sex', 'male')
    activity = body.get('activity', 'moderate')
    goal = body.get('fitness_goal', 'maintain')

    if not all([age, height, weight]):
        return jsonify({'error': 'age, height, and weight are required'}), 400

    cals, protein, carbs, fat = run_mifflin(age, height, weight, sex, activity, goal)

    # save their raw stats too
    p = ProfileInput.query.filter_by(user_id=user_id).first()
    if p:
        p.age = age
        p.height = height
        p.weight = weight
        p.fitness_goal = goal
    else:
        p = ProfileInput(user_id=user_id, age=age, height=height, weight=weight, fitness_goal=goal)
        db.session.add(p)

    g = save_goal(user_id, cals, protein, carbs, fat, source='calculated')

    return jsonify({
        'message': 'goals calculated and saved',
        'goals': {
            'calories': g.calories,
            'protein_g': g.protein_g,
            'carbs_g': g.carbs_g,
            'fat_g': g.fat_g,
        }
    }), 201


@goals_bp.route('', methods=['PUT'])
@login_required
def edit_goal(user_id=None):
    body = request.get_json()

    g = Goal.query.filter_by(user_id=user_id).first()
    if not g:
        return jsonify({'error': 'no goal found, set one first with /direct or /calculated'}), 404

    # only touch fields they actually sent
    if 'calories' in body:
        g.calories = body['calories']
    if 'protein_g' in body:
        g.protein_g = body['protein_g']
    if 'carbs_g' in body:
        g.carbs_g = body['carbs_g']
    if 'fat_g' in body:
        g.fat_g = body['fat_g']

    db.session.commit()

    return jsonify({
        'message': 'goals updated',
        'goals': {
            'calories': g.calories,
            'protein_g': g.protein_g,
            'carbs_g': g.carbs_g,
            'fat_g': g.fat_g,
        }
    }), 200
