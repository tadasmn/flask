from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
import forms
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user
import os

db=SQLAlchemy()

def create_app():
    app = Flask(__name__)
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'duombaze1.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "groups"
login_manager.login_message_category = "info"

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Group(db.Model):
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column("Group ID", db.Integer)
    name = db.Column("name", db.String)
    bill = db.relationship("Bill")
    
class Bill(db.Model):
    __tablename__ = "bill"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column("Description", db.String)
    amount = db.Column("Amount", db.String)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group")   
        
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('groups'))
        else:
            flash('Login unsuccessfull. Check your email and password', 'danger')
    return render_template('index.html', form=form)

@app.route('/register', methods=['GET', 'POST'] )
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        password_code = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=password_code)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route("/groups", methods=["GET", "POST"])
def groups():
    all_groups = Group.query.all()
    form = forms.GroupForm()
    if form.validate_on_submit():
        new_group = Group(number=form.number.data, name=form.name.data)
        db.session.add(new_group)
        db.session.commit()
        return redirect(url_for('groups'))
    return render_template('groups.html', form=form, all_groups=all_groups)

@app.route("/<int:number>", methods=["GET", "POST"])
def bills(number):
    exact_bill = Bill.query.all()
    form = forms.BillForm()
    if form.validate_on_submit():
        new_bill = Bill(description = form.description.data, amount = form.amount.data, group_id = form.group.data.id)
        db.session.add(new_bill)
        db.session.commit()
        return redirect(request.url)
    return render_template('bills.html', number=number, form=form, exact_bill=exact_bill)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)