from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from .db import query_one, execute

auth = Blueprint('auth', __name__, template_folder='../templates', url_prefix='')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # if already logged in, send to home
        if session.get('user_id'):
            return redirect(url_for('index'))
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username and password required')
        return redirect(url_for('auth.login'))

    user = query_one('SELECT user_id, username, password_hash FROM users WHERE username = %s', (username,))
    if not user:
        flash('Invalid credentials')
        return redirect(url_for('auth.login'))

    pw_hash = user.get('password_hash')
    if not pw_hash:
        flash('Invalid credentials')
        return redirect(url_for('auth.login'))

    if not check_password_hash(pw_hash, password):
        flash('Invalid credentials')
        return redirect(url_for('auth.login'))

    # login success
    session.clear()
    session['user_id'] = user['user_id']
    session['username'] = user['username']
    # keep session persistent for the browser session
    session.permanent = True
    return redirect(url_for('index'))


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        # if already logged in, send to home
        if session.get('user_id'):
            return redirect(url_for('index'))
        return render_template('signup.html')

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    nickname = request.form.get('nickname') or None

    if not username or not email or not password:
        flash('username, email and password are required')
        return redirect(url_for('auth.signup'))

    # check existing username/email
    existing = query_one('SELECT user_id FROM users WHERE username = %s OR email_address = %s', (username, email))
    if existing:
        flash('Username or email already in use')
        return redirect(url_for('auth.signup'))

    pw_hash = generate_password_hash(password)
    # Insert user using a single statement that computes the next user_id
    inserted = execute(
        """
        INSERT INTO users (user_id, username, email_address, nickname, password_hash)
        SELECT COALESCE(MAX(user_id), 0) + 1, %s, %s, %s, %s
        FROM users
        RETURNING user_id, username
        """,
        (username, email, nickname, pw_hash),
        returning=True
    )

    if not inserted:
        flash('Failed to create user')
        return redirect(url_for('auth.signup'))

    # auto-login after signup
    session.clear()
    session['user_id'] = inserted['user_id']
    session['username'] = inserted['username']
    session.permanent = True
    return redirect(url_for('index'))
