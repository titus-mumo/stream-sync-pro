from flask import Blueprint, render_template, request, url_for, flash, redirect, session
from flask_login import login_user, login_required, logout_user
from models import db, User
from forms.form import LoginForm, SignUpForm
from sqlalchemy.exc import IntegrityError

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def landing_page():
    return render_template('landing-page.html')

@main.route('/login.html', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            subject  = form.subject.data
            password = form.password.data
            user = User.query.filter((User.username == subject) | (User.email == subject)).first()
            if user:
                if user.check_password(password):
                    login_user(user, remember=True)
                    session['username'] = user.username  
                    flash("Login successful")
                    return redirect( url_for('main.home'))
                else:
                    flash("Invalid credentials")
            else:
                flash("Invalid username or email")

        else:
            flash('Invalid form')
    return render_template('login.html', form = form)

@main.route('/signup.html', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            
            new_user = User(username = username, email = email)
            new_user.set_password(password)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully")
                return redirect( url_for('main.login'))
            except IntegrityError:
                db.session.rollback()
                flash("Username or email already exists")
        else:
            flash("Invalid form")
    return render_template('signup.html', form = form)


@main.route('/home.html')
@login_required
def home():
    return render_template('home.html')


@main.route('/logout.html', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    flash("Logout successful!")
    return redirect(url_for('main.login'))