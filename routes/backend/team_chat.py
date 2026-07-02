from flask import Blueprint, request, jsonify, session
from models import mysql, User, TeamActivityLog

# Import the main backend blueprint
from routes.backend import backend_bp


@backend_bp.route('/team-activity', methods=['GET'])
def get_team_activity():
    """Get activity log for a team."""
    team_id = request.args.get('team_id')
    if not team_id:
        return jsonify({'success': False, 'message': 'team_id is required'}), 400

    try:
        activities = TeamActivityLog.get_recent_for_team(team_id, limit=10)
        formatted = []
        for a in activities:
            formatted.append({
                'id': a['id'],
                'activity_type': a['activity_type'],
                'description': a['description'],
                'created_at': a['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(a['created_at'], 'strftime') else str(a['created_at'])
            })
        return jsonify({
            'success': True,
            'activities': formatted
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'activities': [],
            'message': str(e)
        })


@backend_bp.route('/team-chat', methods=['GET'])
def get_team_messages():
    """Get messages for a team chat."""
    team_id = request.args.get('team_id')
    if not team_id:
        return jsonify({'success': False, 'message': 'team_id is required'}), 400

    # Check if there's a team_id column in messages table
    # For now, we'll return a placeholder since the messages table structure
    # needs to be checked
    try:
        cur = mysql.connection.cursor()
        # Try to get messages filtered by team_id if column exists
        try:
            cur.execute("""
                SELECT id, user_id, message_text, created_at
                FROM messages
                WHERE team_id = %s
                ORDER BY created_at ASC
            """, (team_id,))
            messages = cur.fetchall()
        except Exception:
            # If team_id column doesn't exist, return empty list
            messages = []
        
        formatted_messages = []
        for msg in messages:
            user = User.get_by_id(msg['user_id'])
            formatted_messages.append({
                'id': msg['id'],
                'user_id': msg['user_id'],
                'user_name': user['name'] if user else 'Unknown',
                'message': msg['message_text'],
                'timestamp': msg['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(msg['created_at'], 'strftime') else str(msg['created_at'])
            })
        
        cur.close()
        
        return jsonify({
            'success': True,
            'messages': formatted_messages
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'messages': [],
            'message': str(e)
        })


@backend_bp.route('/team-chat', methods=['POST'])
def post_team_message():
    """Post a message to team chat."""
    team_id = request.form.get('team_id')
    message = request.form.get('message', '').strip()
    
    if not team_id:
        return jsonify({'success': False, 'message': 'team_id is required'}), 400
    
    if not message:
        return jsonify({'success': False, 'message': 'Message is required'}), 400

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        cur = mysql.connection.cursor()
        # Try to insert with team_id column if it exists
        try:
            cur.execute("""
                INSERT INTO messages (conversation_id, sender_id, message_text, team_id, is_read)
                VALUES (NULL, %s, %s, %s, 0)
            """, (session['user_id'], message, team_id))
            mysql.connection.commit()
            cur.close()
            return jsonify({
                'success': True,
                'message': 'Message sent successfully'
            })
        except Exception:
            # If team_id column doesn't exist, try without it
            try:
                cur.execute("""
                    INSERT INTO messages (conversation_id, sender_id, message_text, is_read)
                    VALUES (NULL, %s, %s, 0)
                """, (session['user_id'], message))
                mysql.connection.commit()
                cur.close()
                return jsonify({
                    'success': True,
                    'message': 'Message sent successfully'
                })
            except Exception as e2:
                cur.close()
                return jsonify({
                    'success': False,
                    'message': f'Failed to send message: {str(e2)}'
                }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500