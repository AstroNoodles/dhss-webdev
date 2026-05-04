from .db import get_conn, put_conn, query_all, query_one


def fetch_user_workspaces(user_id):
    """Return a list of workspaces the user is a member of."""
    sql = '''
    SELECT w.workspace_id, w.wname, w.work_desc, w.creator_id
    FROM workspaces w
    JOIN workspace_members wm ON w.workspace_id = wm.workspace_id
    WHERE wm.user_id = %s
    ORDER BY w.wname
    '''
    return query_all(sql, (user_id,))


def fetch_user_channels(user_id):
    """Return a list of channels the user is a member of across all workspaces."""
    sql = '''
    SELECT c.workspace_id, c.channel_id, c.cname, c.channel_type
    FROM channels c
    JOIN channel_members cm ON c.workspace_id = cm.workspace_id AND c.channel_id = cm.channel_id
    WHERE cm.user_id = %s
    ORDER BY c.workspace_id, c.cname
    '''
    return query_all(sql, (user_id,))


def fetch_workspaces_with_channels(user_id):
    """Return workspaces with a 'channels' list for each workspace the user belongs to."""
    workspaces = fetch_user_workspaces(user_id)
    channels = fetch_user_channels(user_id)

    # group channels by workspace_id
    channels_by_ws = {}
    for ch in channels:
        wsid = ch['workspace_id']
        channels_by_ws.setdefault(wsid, []).append(ch)

    for ws in workspaces:
        wsid = ws['workspace_id']
        ws['channels'] = channels_by_ws.get(wsid, [])

    return workspaces


def fetch_workspace_with_channels(user_id, workspace_id):
    """Return one workspace and its channels when the user belongs to it."""
    sql = '''
    SELECT w.workspace_id, w.wname, w.work_desc, w.creator_id
    FROM workspaces w
    JOIN workspace_members wm ON w.workspace_id = wm.workspace_id
    WHERE wm.user_id = %s AND w.workspace_id = %s
    '''
    workspace = query_one(sql, (user_id, workspace_id))
    if not workspace:
        return None

    channels_sql = '''
    SELECT c.workspace_id, c.channel_id, c.cname, c.channel_type
    FROM channels c
    JOIN channel_members cm ON c.workspace_id = cm.workspace_id AND c.channel_id = cm.channel_id
    WHERE cm.user_id = %s AND c.workspace_id = %s
    ORDER BY c.cname
    '''
    workspace['channels'] = query_all(channels_sql, (user_id, workspace_id))
    return workspace


def create_workspace(user_id, workspace_name, workspace_description=None):
    """Create a workspace and add the creator as an admin member."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO workspaces (workspace_id, wname, creator_id, work_desc)
            SELECT COALESCE(MAX(workspace_id), 0) + 1, %s, %s, %s
            FROM workspaces
            RETURNING workspace_id, wname, work_desc, creator_id
            ''',
            (workspace_name, user_id, workspace_description)
        )
        row = cur.fetchone()
        cols = [desc[0] for desc in cur.description]
        workspace = dict(zip(cols, row))

        cur.execute(
            '''
            INSERT INTO workspace_members (workspace_id, user_id, isadmin)
            VALUES (%s, %s, TRUE)
            ''',
            (workspace['workspace_id'], user_id)
        )
        conn.commit()
        cur.close()
        return workspace
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)


def create_channel(user_id, workspace_id, channel_name, channel_type):
    """Create a channel inside a workspace and add the creator as a member."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO channels (workspace_id, channel_id, cname, channel_type, creator_id)
            SELECT %s, COALESCE(MAX(channel_id), 0) + 1, %s, %s, %s
            FROM channels
            WHERE workspace_id = %s
            RETURNING workspace_id, channel_id, cname, channel_type, creator_id
            ''',
            (workspace_id, channel_name, channel_type, user_id, workspace_id)
        )
        row = cur.fetchone()
        cols = [desc[0] for desc in cur.description]
        channel = dict(zip(cols, row))

        cur.execute(
            '''
            INSERT INTO channel_members (workspace_id, channel_id, user_id)
            VALUES (%s, %s, %s)
            ''',
            (channel['workspace_id'], channel['channel_id'], user_id)
        )
        conn.commit()
        cur.close()
        return channel
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)


def fetch_channel_with_messages(user_id, workspace_id, channel_id):
    """Return a channel and its messages when the user is a channel member."""
    channel_sql = '''
    SELECT c.workspace_id, c.channel_id, c.cname, c.channel_type, c.creator_id
    FROM channels c
    JOIN channel_members cm
      ON c.workspace_id = cm.workspace_id
     AND c.channel_id = cm.channel_id
    WHERE cm.user_id = %s
      AND c.workspace_id = %s
      AND c.channel_id = %s
    '''
    channel = query_one(channel_sql, (user_id, workspace_id, channel_id))
    if not channel:
        return None

    messages_sql = '''
    SELECT m.message_id,
           m.sender_id,
           m.sent_at,
           m.text,
           u.username
    FROM messages m
    JOIN users u ON m.sender_id = u.user_id
    WHERE m.workspace_id = %s
      AND m.channel_id = %s
    ORDER BY m.sent_at ASC, m.message_id ASC
    '''
    channel['messages'] = query_all(messages_sql, (workspace_id, channel_id))
    return channel


def create_message(user_id, workspace_id, channel_id, message_text):
    """Create a message in a channel when the user is a channel member."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO messages (workspace_id, channel_id, message_id, sender_id, text)
            SELECT %s, %s, COALESCE(MAX(message_id), 0) + 1, %s, %s
            FROM messages
            WHERE workspace_id = %s AND channel_id = %s
            RETURNING workspace_id, channel_id, message_id, sender_id, sent_at, text
            ''',
            (workspace_id, channel_id, user_id, message_text, workspace_id, channel_id)
        )
        row = cur.fetchone()
        cols = [desc[0] for desc in cur.description]
        message = dict(zip(cols, row))
        conn.commit()
        cur.close()
        return message
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)
