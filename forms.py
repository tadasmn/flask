from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField
import app

def group_query():
    return app.Group.query

def get_pk(obj):
    return str(obj)

class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Login')
    
class RegisterForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])
    patvirtintas_slaptazodis = PasswordField("Repeat password", [EqualTo('password', 'Passwords do not match')])
    submit = SubmitField("Register")

    def validate_name(self, name):
        user = app.User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('User already in use')
        
    def validate_email(self, email):
        user = app.User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use')
        
class GroupForm(FlaskForm):
    number = IntegerField('Number', [DataRequired()])
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Add')
    
class BillForm(FlaskForm):
    description = StringField('Description', [DataRequired()])
    amount = IntegerField('Amount', [DataRequired()])
    group = QuerySelectField(query_factory=group_query, allow_blank=True, get_label="name", get_pk=get_pk)
    submit = SubmitField('Add')