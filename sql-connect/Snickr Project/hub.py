import os
import re
from flask import Flask, flash, render_template, redirect, request, url_for, session
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


def workspace_slug(workspace_name):
    slug = re.sub(r'[^a-z0-9]+', '-', workspace_name.lower()).strip('-')
    return slug or 'workspace'


def channel_slug(channel_name):
    slug = re.sub(r'[^a-z0-9]+', '-', channel_name.lower()).strip('-')
    return slug or 'channel'


app.jinja_env.filters['channel_slug'] = channel_slug


@app.route('/')
def index():
    # Redirect to workspace selection for logged-in users or to login page otherwise
    if 'user_id' in session:
        return redirect(url_for('select_workspace'))
    return redirect(url_for('auth.login'))


@app.route('/select_workspace', methods=['GET', 'POST'])
@app.route('/select_workspaces', methods=['GET', 'POST'])
@login_required
def select_workspace():
    user_id = session.get('user_id')

    if request.method == 'POST':
        workspace_id = request.form.get('workspace_id')
        if not workspace_id:
            flash('Please select a workspace')
            return redirect(url_for('select_workspace'))

        try:
            from backend.workspaces import fetch_workspace_with_channels
            workspace = fetch_workspace_with_channels(user_id, workspace_id)
        except Exception:
            workspace = None

        if not workspace:
            flash('You do not have access to that workspace')
            return redirect(url_for('select_workspace'))

        session['workspace_id'] = workspace['workspace_id']
        return redirect(url_for(
            'workspace_hub',
            workspace_id=workspace['workspace_id'],
            slug=workspace_slug(workspace['wname'])
        ))

    try:
        from backend.workspaces import fetch_user_workspaces
        workspaces = fetch_user_workspaces(user_id)
    except Exception:
        workspaces = []

    return render_template('select_workspace.html', workspaces=workspaces)


@app.route('/home')
@login_required
def home():
    workspace_id = session.get('workspace_id')
    if not workspace_id:
        return redirect(url_for('select_workspace'))

    return redirect(url_for('workspace_hub', workspace_id=workspace_id, slug='workspace'))


@app.route('/workspace/<int:workspace_id>/<slug>')
@login_required
def workspace_hub(workspace_id, slug):
    user_id = session.get('user_id')

    try:
        from backend.workspaces import fetch_workspace_with_channels
        workspace = fetch_workspace_with_channels(user_id, workspace_id)
    except Exception:
        workspace = None

    if not workspace:
        session.pop('workspace_id', None)
        flash('Please choose a workspace')
        return redirect(url_for('select_workspace'))

    session['workspace_id'] = workspace['workspace_id']
    canonical_slug = workspace_slug(workspace['wname'])
    if slug != canonical_slug:
        return redirect(url_for(
            'workspace_hub',
            workspace_id=workspace['workspace_id'],
            slug=canonical_slug
        ))

    return render_template('workspace_hub.html', workspace=workspace, slug=canonical_slug)


@app.route('/workspace/<int:workspace_id>/<slug>/channels/create', methods=['GET', 'POST'])
@login_required
def create_channel(workspace_id, slug):
    user_id = session.get('user_id')

    try:
        from backend.workspaces import fetch_workspace_with_channels
        workspace = fetch_workspace_with_channels(user_id, workspace_id)
    except Exception:
        workspace = None

    if not workspace:
        session.pop('workspace_id', None)
        flash('Please choose a workspace')
        return redirect(url_for('select_workspace'))

    session['workspace_id'] = workspace['workspace_id']
    canonical_slug = workspace_slug(workspace['wname'])
    if slug != canonical_slug:
        return redirect(url_for(
            'create_channel',
            workspace_id=workspace['workspace_id'],
            slug=canonical_slug
        ))

    if request.method == 'GET':
        return render_template('channel_create.html', workspace=workspace, slug=canonical_slug)

    channel_name = request.form.get('channel-input', '').strip()
    channel_type = request.form.get('channel-type', '').strip()

    if not channel_name:
        flash('Channel name is required')
        return redirect(url_for('create_channel', workspace_id=workspace_id, slug=canonical_slug))

    if channel_type not in ('public', 'private'):
        flash('Channel type must be public or private')
        return redirect(url_for('create_channel', workspace_id=workspace_id, slug=canonical_slug))

    try:
        from backend.workspaces import create_channel as create_channel_record
        create_channel_record(user_id, workspace_id, channel_name, channel_type)
    except Exception:
        flash('Could not create channel')
        return redirect(url_for('create_channel', workspace_id=workspace_id, slug=canonical_slug))

    flash('Channel created')
    return redirect(url_for('workspace_hub', workspace_id=workspace_id, slug=canonical_slug))


@app.route('/workspace/<int:workspace_id>/<slug>/channels/<int:channel_id>/<channel_slug_value>', methods=['GET', 'POST'])
@login_required
def channel_view(workspace_id, slug, channel_id, channel_slug_value):
    user_id = session.get('user_id')

    try:
        from backend.workspaces import fetch_channel_with_messages, fetch_workspace_with_channels
        workspace = fetch_workspace_with_channels(user_id, workspace_id)
        channel = fetch_channel_with_messages(user_id, workspace_id, channel_id)
    except Exception:
        workspace = None
        channel = None

    if not workspace:
        session.pop('workspace_id', None)
        flash('Please choose a workspace')
        return redirect(url_for('select_workspace'))

    session['workspace_id'] = workspace['workspace_id']
    canonical_workspace_slug = workspace_slug(workspace['wname'])
    if slug != canonical_workspace_slug:
        return redirect(url_for(
            'channel_view',
            workspace_id=workspace['workspace_id'],
            slug=canonical_workspace_slug,
            channel_id=channel_id,
            channel_slug_value=channel_slug_value
        ))

    if not channel:
        flash('You do not have access to that channel')
        return redirect(url_for(
            'workspace_hub',
            workspace_id=workspace['workspace_id'],
            slug=canonical_workspace_slug
        ))

    canonical_channel_slug = channel_slug(channel['cname'])
    if channel_slug_value != canonical_channel_slug:
        return redirect(url_for(
            'channel_view',
            workspace_id=workspace['workspace_id'],
            slug=canonical_workspace_slug,
            channel_id=channel['channel_id'],
            channel_slug_value=canonical_channel_slug
        ))

    if request.method == 'POST':
        message_text = request.form.get('message-text', '').strip()
        if not message_text:
            flash('Message cannot be empty')
            return redirect(url_for(
                'channel_view',
                workspace_id=workspace['workspace_id'],
                slug=canonical_workspace_slug,
                channel_id=channel['channel_id'],
                channel_slug_value=canonical_channel_slug
            ))

        try:
            from backend.workspaces import create_message
            create_message(user_id, workspace_id, channel_id, message_text)
        except Exception:
            flash('Could not send message')

        return redirect(url_for(
            'channel_view',
            workspace_id=workspace['workspace_id'],
            slug=canonical_workspace_slug,
            channel_id=channel['channel_id'],
            channel_slug_value=canonical_channel_slug
        ))

    return render_template(
        'channel.html',
        workspace=workspace,
        channel=channel,
        slug=canonical_workspace_slug,
        active_channel_id=channel['channel_id']
    )


@app.route('/createWorkspace', methods=['POST'])
@login_required
def create_workspace():
    user_id = session.get('user_id')
    workspace_name = request.form.get('workspace-input', '').strip()
    workspace_description = request.form.get('workspace-description', '').strip() or None

    if not workspace_name:
        flash('Workspace name is required')
        return redirect(url_for('select_workspace'))

    try:
        from backend.workspaces import create_workspace as create_workspace_record
        create_workspace_record(user_id, workspace_name, workspace_description)
    except Exception:
        flash('Could not create workspace')
        return redirect(url_for('select_workspace'))

    flash('Workspace created')
    return redirect(url_for('select_workspace'))


@app.route('/settings')
def settings():
    # simple settings page — you can move this into a blueprint later
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('settings.html')

if __name__ == '__main__':
    # Initialize DB pool lazily when app starts
    try:
        from backend.db import init_pool
        init_pool()
    except Exception:
        # If DB not configured in this environment, allow app to run for template testing
        pass
    app.run(debug=True)
