from flask import Blueprint, render_template, request, jsonify, session, current_app
from models import mysql, User, Match, Leaderboard, Conversation, Message, Notification, UserBadge
import re
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# ============================================================
# HELPERS
# ============================================================

def login_required_json():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return None


# ============================================================
# AI SPORTS ASSISTANT
# ============================================================

@chat_bp.route('/ai-assistant')
def ai_assistant_page():
    redirect_resp = login_required_json()
    if redirect_resp:
        return redirect_resp
    user = User.get_by_id(session['user_id'])
    return render_template('ai_assistant.html', user=user)


@chat_bp.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    """Chat with AI Sports Assistant - Demo Mode (Offline).
    Keeps last 10 messages as context.
    Uses built-in knowledge base instead of external APIs.
    """
    resp = login_required_json()
    if resp:
        return resp

    data = request.get_json() or {}
    user_message = (data.get('message') or '').strip()
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Get conversation history from session (last 10 messages)
    history = session.get('ai_chat_history', [])
    history.append({'role': 'user', 'content': user_message})
    history = history[-10:]

    try:
        # Import demo AI processor
        from routes.demo_ai import process_message, get_suggested_questions
        
        # Process message with demo AI
        ai_text = process_message(user_message, conversation_history=history)
        
        # Store assistant response in history
        history.append({'role': 'assistant', 'content': ai_text})
        session['ai_chat_history'] = history[-10:]

        # Get suggested questions for UI
        suggestions = get_suggested_questions()

        return jsonify({
            'success': True,
            'reply': ai_text,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f'AI chat error: {e}')
        # Never expose internal errors to user
        return jsonify({
            'success': True,
            'reply': "I don't have information about that topic yet. Try asking about sports rules, matches, tournaments, rankings, venues, or platform features.",
            'suggestions': [
                "Rules of Cricket",
                "Explain Badminton Scoring",
                "How to Create a Match",
                "Improve My Ranking",
                "Nearby Sports Venues"
            ],
            'timestamp': datetime.now().isoformat()
        })




# ============================================================
# PRIVATE CHAT SYSTEM
# ============================================================

@chat_bp.route('/conversations')
def conversations_page():
    user = User.get_by_id(session['user_id'])
    return render_template('conversations.html', user=user)


@chat_bp.route('/api/conversations')
def api_get_conversations():
    resp = login_required_json()
    if resp:
        return resp
    user_id = session['user_id']
    convos = Conversation.get_user_conversations(user_id)
    result = []
    for c in convos:
        result.append({
            'id': c['id'],
            'other_user_id': c['other_user_id'],
            'other_user_name': c['other_user_name'],
            'updated_at': c['updated_at'].isoformat() if hasattr(c['updated_at'], 'isoformat') else str(c['updated_at']),
            'unread_count': c['unread_count']
        })
    return jsonify({'success': True, 'conversations': result})


@chat_bp.route('/api/conversation/<int:conversation_id>/messages')
def api_get_messages(conversation_id):
    resp = login_required_json()
    if resp:
        return resp
    messages = Message.get_conversation_messages(conversation_id)
    msg_list = []
    for m in messages:
        msg_list.append({
            'id': m['id'],
            'sender_id': m['sender_id'],
            'sender_name': m['sender_name'],
            'message_text': m['message_text'],
            'created_at': m['created_at'].isoformat() if hasattr(m['created_at'], 'isoformat') else str(m['created_at']),
            'is_read': bool(m['is_read'])
        })
    return jsonify({'success': True, 'messages': msg_list})


@chat_bp.route('/api/conversation/start', methods=['POST'])
def api_start_conversation():
    resp = login_required_json()
    if resp:
        return resp
    data = request.get_json() or {}
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        return jsonify({'error': 'other_user_id is required'}), 400
    convo = Conversation.get_or_create(session['user_id'], other_user_id)
    return jsonify({'success': True, 'conversation_id': convo['id']})


@chat_bp.route('/api/message/send', methods=['POST'])
def api_send_message():
    resp = login_required_json()
    if resp:
        return resp
    data = request.get_json() or {}
    conversation_id = data.get('conversation_id')
    match_id = data.get('match_id')  # optional for group chat
    text = (data.get('message_text') or '').strip()
    if not text or (not conversation_id and not match_id):
        return jsonify({'error': 'message_text and (conversation_id or match_id) are required'}), 400

    sender_id = session['user_id']
    msg = Message.send(
        conversation_id=conversation_id,
        match_id=match_id,
        sender_id=sender_id,
        message_text=text
    )

    # Create notification for the other party
    if conversation_id:
        convo = Conversation.get_by_id(conversation_id)
        if convo:
            other_id = convo['user2_id'] if convo['user1_id'] == sender_id else convo['user1_id']
            sender = User.get_by_id(sender_id)
            Notification.create(
                user_id=other_id,
                type='new_private_message',
                title='New Message',
                message=f'{sender["name"]}: {text[:80]}',
                related_user_id=sender_id,
                related_conversation_id=conversation_id
            )
    elif match_id:
        match = Match.get_by_id(match_id)
        if match:
            sender = User.get_by_id(sender_id)
            # Notify match participants except sender
            cur = mysql.connection.cursor()
            cur.execute("SELECT user_id FROM match_participants WHERE match_id = %s AND user_id != %s", (match_id, sender_id))
            participants = [r['user_id'] for r in cur.fetchall()]
            cur.close()
            for pid in participants:
                Notification.create(
                    user_id=pid,
                    type='new_group_message',
                    title=f'New message in {match["sport_name"]}',
                    message=f'{sender["name"]}: {text[:80]}',
                    related_match_id=match_id
                )

    return jsonify({'success': True, 'message': msg})


@chat_bp.route('/api/match/<int:match_id>/participants')
def api_get_match_participants(match_id):
    resp = login_required_json()
    if resp:
        return resp
    match = Match.get_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT mp.user_id, u.name, u.email
        FROM match_participants mp
        JOIN users u ON mp.user_id = u.id
        WHERE mp.match_id = %s
        ORDER BY mp.joined_at ASC
    """, (match_id,))
    participants = cur.fetchall()
    cur.close()
    
    result = []
    for p in participants:
        result.append({
            'id': p['user_id'],
            'name': p['name'],
            'email': p['email']
        })
    
    return jsonify({
        'success': True,
        'participants': result,
        'creator_id': match['creator_id']
    })


@chat_bp.route('/api/match/<int:match_id>/messages')
def api_get_match_messages(match_id):
    resp = login_required_json()
    if resp:
        return resp
    messages = Message.get_match_messages(match_id)
    msg_list = []
    for m in messages:
        msg_list.append({
            'id': m['id'],
            'sender_id': m['sender_id'],
            'sender_name': m['sender_name'],
            'message_text': m['message_text'],
            'created_at': m['created_at'].isoformat() if hasattr(m['created_at'], 'isoformat') else str(m['created_at']),
            'is_read': bool(m['is_read'])
        })
    return jsonify({'success': True, 'messages': msg_list})


# ============================================================
# MATCH GROUP CHAT PAGE
# ============================================================

@chat_bp.route('/match/<int:match_id>/chat')
def match_chat_page(match_id):
    match = Match.get_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    user = User.get_by_id(session['user_id'])
    return render_template('match_chat.html', match=match, user=user)


# ============================================================
# NOTIFICATIONS
# ============================================================

@chat_bp.route('/api/notifications')
def api_get_notifications():
    resp = login_required_json()
    if resp:
        return resp
    user_id = session['user_id']
    notifs = Notification.get_user_notifications(user_id)
    unread = Notification.get_unread_count(user_id)
    data = []
    for n in notifs:
        data.append({
            'id': n['id'],
            'type': n['type'],
            'title': n['title'],
            'message': n['message'],
            'related_user_id': n.get('related_user_id'),
            'related_match_id': n.get('related_match_id'),
            'related_conversation_id': n.get('related_conversation_id'),
            'related_badge_id': n.get('related_badge_id'),
            'related_tournament_id': n.get('related_tournament_id'),
            'related_ai_report_id': n.get('related_ai_report_id'),
            'is_read': bool(n['is_read']),
            'created_at': n['created_at'].isoformat() if hasattr(n['created_at'], 'isoformat') else str(n['created_at'])
        })
    return jsonify({'success': True, 'notifications': data, 'unread_count': unread})


@chat_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def api_mark_notification_read(notification_id):
    resp = login_required_json()
    if resp:
        return resp
    Notification.mark_as_read(notification_id, session['user_id'])
    return jsonify({'success': True})


@chat_bp.route('/api/notifications/read-all', methods=['POST'])
def api_mark_all_notifications_read():
    resp = login_required_json()
    if resp:
        return resp
    Notification.mark_all_as_read(session['user_id'])
    return jsonify({'success': True})


# ============================================================
# LEADERBOARD IMPROVEMENTS (API enhancements)
# ============================================================

@chat_bp.route('/api/leaderboard/enhanced')
def api_enhanced_leaderboard():
    """Enhanced leaderboard with sport filter."""
    sport = request.args.get('sport')
    ranking = request.args.get('ranking')  # e.g., 'top', 'all'
    experience = request.args.get('experience')  # 'rookie', 'veteran', etc.

    leaderboard = Leaderboard.get_dynamic_leaderboard()
    badges_map = {}

    for entry in leaderboard:
        uid = entry['user_id']
        badges = UserBadge.get_user_badges(uid)
        badges_map[uid] = [b['badge_code'] for b in badges]

    # Filters
    filtered = []
    for entry in leaderboard:
        if sport:
            # Need to check user's sport preference or match history
            # Stub: include all (real implementation needs user_sports table)
            pass
        if experience == 'rookie' and entry['matches_played'] >= 20:
            continue
        if experience == 'veteran' and entry['matches_played'] < 20:
            continue
        filtered.append(entry)

    if ranking == 'top':
        filtered = filtered[:10]

    return jsonify({
        'success': True,
        'leaderboard': filtered,
        'badges': badges_map
    })


@chat_bp.route('/api/user/<int:user_id>/badges')
def api_user_badges(user_id):
    badges = UserBadge.get_user_badges(user_id)
    data = []
    for b in badges:
        data.append({
            'badge_code': b['badge_code'],
            'badge_name': b['badge_name'],
            'description': b['description'],
            'icon': b['icon'],
            'awarded_at': b['awarded_at'].isoformat() if hasattr(b['awarded_at'], 'isoformat') else str(b['awarded_at'])
        })
    return jsonify({'success': True, 'badges': data})


@chat_bp.route('/api/users/search')
def api_search_users():
    """Search users by name for starting conversations."""
    resp = login_required_json()
    if resp:
        return resp
    
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'success': True, 'users': []})
    
    cur = mysql.connection.cursor()
    search_pattern = f'%{query}%'
    cur.execute("""
        SELECT id, name, email FROM users
        WHERE name LIKE %s OR email LIKE %s
        LIMIT 20
    """, (search_pattern, search_pattern))
    users = cur.fetchall()
    cur.close()
    
    result = []
    for u in users:
        result.append({
            'id': u['id'],
            'name': u['name'],
            'email': u['email']
        })
    
    return jsonify({'success': True, 'users': result})
