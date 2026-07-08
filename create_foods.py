import datetime
from app import app, db
from models import FoodItem, Goal, User

with app.app_context():
    User.__table__.drop(db.engine)
    Goal.__table__.drop(db.engine)
    FoodItem.__table__.drop(db.engine)

    db.create_all()
    db.session.query(FoodItem).delete()
    
    today = datetime.date.today()
    
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
    
    today = datetime.date.today()
    for item in DUMMY_MENU:
        db.session.add(FoodItem(date=today, **item))

    db.session.query(User).delete()
    dummy_user = User(
        username="ojc", 
        email="rahul.ahsan10@gmail.com", 
        password="Password123",
        created_at=today,
        user_token="1"
    )
    db.session.add(dummy_user)

    db.session.query(Goal).delete()
    dummy_goal = Goal(
            user_id=dummy_user.id,
            calories=2000,
            protein_g=160,
            carbs_g=200,
            fat_g=60
        )
    db.session.add(dummy_goal)
    db.session.commit()
        