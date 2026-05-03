import os
from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret-change-me')

# register blueprints
from backend.auth import auth as auth_bp
app.register_blueprint(auth_bp)


def login_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapper


@app.route('/')
def index():
    # Redirect to home for logged-in users or to login page otherwise
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('auth.login'))


@app.route('/home')
@login_required
def home():
    # Simple landing page for authenticated users; expand later
    return render_template('workspace_hub.html')


if __name__ == '__main__':
    # Initialize DB pool lazily when app starts
    try:
        from backend.db import init_pool
        init_pool()
    except Exception:
        # If DB not configured in this environment, allow app to run for template testing
        pass
    app.run(debug=True)