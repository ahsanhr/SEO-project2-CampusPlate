from app import db


class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(40), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


class Goal(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calories  = db.Column(db.Float)
    protein_g = db.Column(db.Float)
    carbs_g   = db.Column(db.Float)
    fat_g     = db.Column(db.Float)
    source    = db.Column(db.String(10))  


class ProfileInput(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age          = db.Column(db.Integer)
    height       = db.Column(db.Float)
    weight       = db.Column(db.Float)
    fitness_goal = db.Column(db.String(20))  


class FoodItem(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(200))
    date         = db.Column(db.Date)
    time_of_day  = db.Column(db.String(10))
    station      = db.Column(db.String(100))
    serving_size = db.Column(db.String(50))  # e.g. "1 cup", "4 oz", "1 serving"
    calories     = db.Column(db.Float)
    protein_g    = db.Column(db.Float)
    carbs_g      = db.Column(db.Float)
    fat_g        = db.Column(db.Float)


class Recommendation(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date           = db.Column(db.Date)
    meal_type      = db.Column(db.String(10))
    item_ids       = db.Column(db.JSON)
    total_calories = db.Column(db.Float)
