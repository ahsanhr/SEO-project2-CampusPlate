from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
            validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('password')])
    calories = IntegerField('Daily Calorie Goal',
                validators=[DataRequired(), NumberRange(min=0, max=10000)])
    protein = IntegerField('Protein (g)',
            validators=[DataRequired(), NumberRange(min=0, max=500)])
    fats = IntegerField('Fat (g)', 
            validators=[DataRequired(), NumberRange(min=0, max=500)])
    carbs = IntegerField('Carbohydrates (g)',
            validators=[DataRequired(), NumberRange(min=0, max=500)])
    submit = SubmitField('Sign Up')
