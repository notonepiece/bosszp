import functools

from flask import Blueprint, request, render_template, redirect, session, url_for, g

user_bp = Blueprint('user', __name__)
from db import db
from app import app
from models.user import User

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        account = request.form.get('account')
        password = request.form.get('password')
        with app.app_context():
            user = User.query.filter_by(account=account, password=password).first()
        if user:
            session['account'] = user.account
            return redirect('/index/')
        else:
            return render_template('login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == 'POST':
        account = request.form.get("account")
        password = request.form.get("password")
        passwordVerify = request.form.get("passwordVerify")
        agree = request.form.get("agree")
        if account is not None and password is not None and password == passwordVerify and agree is not None:
            with app.app_context():
                user = User(account=account, password=password)
                db.session.add(user)
                db.session.commit()
            return redirect('/user/login')
        else:
            return render_template('register.html')

@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))
        return view(**kwargs)
    return wrapped_view

@user_bp.before_app_request
def load_logged_in_user():
    account = session.get('account')
    if account is None:
        g.user = None
    else:
        g.user = User.query.filter_by(account=account).first()

