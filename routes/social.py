from flask import Blueprint, render_template, request, jsonify, session
from models import mysql, User, Leaderboard, Notification, Follower
from datetime import datetime

social_bp = Blueprint('social', __name__)


def login_required_json():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return None


# ========================================
# USER PROFILE PAGES
# ========================================

@social_bp.route('/profile/<int:user_id>')
def profile_page(user_id):
    """View a user's profile."""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user stats
    try:
        stats = Leaderboard.get_dynamic_leaderboard()
        user_stat = next((s for s in stats if s['user_id'] == user_id), None)
    except Exception:
        user_stat = None
    
    # Get user badges
    badges = []
    try:
        from models import UserBadge
        badges = UserBadge.get_user_badges(user_id)
    except Exception:
        pass
    
    # Get followers/following counts
    followers_count = Follower.get_follower_count(user_id)
    following_count = Follower.get_following_count(user_id)
    
    # Check if current user is following this user
    is_following = False
    if 'user_id' in session and session['user_id'] != user_id:
        is_following = Follower.is_following(session['user_id'], user_id)
    
    return render_template(
        'profile.html',
        profile_user=user,
        user_stat=user_stat,
        badges=badges,
        followers_count=followers_count,
        following_count=following_count,
        is_following=is_following
    )


@social_bp.route('/followers')
def followers_page():
    """View current user's followers."""
    redirect_resp = login_required_json()
    if redirect_resp:
        return redirect_resp
    
    user_id = session['user_id']
    followers = Follower.get_followers(user_id, limit=50)
    following_count = Follower.get_following_count(user_id)
    followers_count = Follower.get_follower_count(user_id)
    
    return render_template(
        'followers.html',
        followers=followers,
        following_count=following_count,
        followers_count=followers_count,
        mode='followers'
    )


@social_bp.route('/following')
def following_page():
    """View current user's following list."""
    redirect_resp = login_required_json()
    if redirect_resp:
        return redirect_resp
    
    user_id = session['user_id']
    following = Follower.get_following(user_id, limit=50)
    following_count = Follower.get_following_count(user_id)
    followers_count = Follower.get_follower_count(user_id)
    
    return render_template(
        'followers.html',
        following=following,
        following_count=following_count,
        followers_count=followers_count,
        mode='following'
    )


@social_bp.route('/notifications')
def notifications_page():
    """View all notifications."""
    redirect_resp = login_required_json()
    if redirect_resp:
        return redirect_resp
    
    return render_template('notifications.html')


# ========================================
# AI MATCH REPORT PAGE
# ========================================

@social_bp.route('/match/<int:match_id>/report')
def ai_report_page(match_id):
    """View AI generated match report."""
    from models import Match
    match = Match.get_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT report_data, summary, mvp_user_id, key_statistics, strengths, improvements
        FROM ai_match_reports
        WHERE match_id = %s
        ORDER BY generated_at DESC
        LIMIT 1
    """, (match_id,))
    report = cur.fetchone()
    cur.close()
    
    if not report:
        return jsonify({'error': 'Report not generated yet'}), 404
    
    import json
    report_data = json.loads(report['report_data']) if isinstance(report['report_data'], str) else report['report_data']
    
    return render_template('ai_match_report.html', report=report_data)


# ========================================
# FOLLOW/UNFOLLOW APIs
# ========================================

@social_bp.route('/api/follow/<int:user_id>', methods=['POST'])
def api_follow(user_id):
    """Follow a user."""
    resp = login_required_json()
    if resp:
        return resp
    
    follower_id = session['user_id']
    if follower_id == user_id:
        return jsonify({'success': False, 'message': 'Cannot follow yourself'}), 400
    
    # Check if user exists
    target_user = User.get_by_id(user_id)
    if not target_user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    success = Follower.follow(follower_id, user_id)
    if success:
        # Log event to trigger notification
        from models.events import EventLog
        EventLog.log(
            'player_followed',
            user_id=follower_id,
            entity_type='user',
            entity_id=user_id,
            event_data={'follower_id': follower_id, 'following_id': user_id}
        )
        
        return jsonify({'success': True, 'message': f'Now following {target_user["name"]}'})
    else:
        return jsonify({'success': False, 'message': 'Already following or error occurred'}), 409


@social_bp.route('/api/unfollow/<int:user_id>', methods=['POST'])
def api_unfollow(user_id):
    """Unfollow a user."""
    resp = login_required_json()
    if resp:
        return resp
    
    follower_id = session['user_id']
    success = Follower.unfollow(follower_id, user_id)
    
    if success:
        target_user = User.get_by_id(user_id)
        message = f'Unfollowed {target_user["name"]}' if target_user else 'Unfollowed'
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': 'Not following this user or error occurred'}), 409


@social_bp.route('/api/follow/<int:user_id>/status')
def api_follow_status(user_id):
    """Check if current user is following another user."""
    if 'user_id' not in session:
        return jsonify({'is_following': False})
    
    follower_id = session['user_id']
    is_following = Follower.is_following(follower_id, user_id)
    return jsonify({'is_following': is_following})


# ========================================
# ENHANCED LEADERBOARD APIs
# ========================================

@social_bp.route('/leaderboard/seasonal')
def seasonal_leaderboard_page():
    """View seasonal leaderboard with tabs."""
    redirect_resp = login_required_json()
    if redirect_resp:
        return redirect_resp
    
    request_type = request.args.get('type', 'weekly')  # weekly, monthly, lifetime
    
    return render_template(
        'seasonal_leaderboard.html',
        request_type=request_type
    )


@social_bp.route('/api/leaderboard/seasonal')
def api_seasonal_leaderboard():
    """Get seasonal leaderboard data."""
    period_type = request.args.get('type', 'weekly')  # weekly, monthly, lifetime
    
    if period_type == 'lifetime':
        # Use existing dynamic leaderboard for lifetime
        leaderboard = Leaderboard.get_dynamic_leaderboard()
        result = []
        for idx, entry in enumerate(leaderboard, 1):
            result.append({
                'rank': idx,
                'user_id': entry['user_id'],
                'name': entry['name'],
                'points': entry['total_points'],
                'matches_played': entry['matches_played'],
                'wins': entry['wins'],
                'losses': entry['losses'],
                'draws': entry['draws'],
                'win_rate': round((entry['wins'] / entry['matches_played'] * 100) if entry['matches_played'] > 0 else 0, 2)
            })
        return jsonify({'success': True, 'leaderboard': result, 'type': 'lifetime'})
    else:
        # For weekly and monthly, return the seasonal leaderboard data
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                u.id as user_id,
                u.name,
                COALESCE(sl.points, 0) as points,
                COALESCE(sl.matches_played, 0) as matches_played,
                COALESCE(sl.wins, 0) as wins,
                COALESCE(sl.losses, 0) as losses,
                COALESCE(sl.draws, 0) as draws,
                COALESCE(sl.win_rate, 0.00) as win_rate,
                sl.rank_position as rank
            FROM users u
            LEFT JOIN seasonal_leaderboard sl ON u.id = sl.user_id 
                AND sl.period_type = %s 
                AND sl.is_current = TRUE
            ORDER BY sl.rank_position ASC
        """, (period_type,))
        leaderboard = cur.fetchall()
        cur.close()
        
        result = []
        rank = 1
        for entry in leaderboard:
            result.append({
                'rank': entry['rank'] or rank,
                'user_id': entry['user_id'],
                'name': entry['name'],
                'points': entry['points'],
                'matches_played': entry['matches_played'],
                'wins': entry['wins'],
                'losses': entry['losses'],
                'draws': entry['draws'],
                'win_rate': float(entry['win_rate'])
            })
            rank += 1
        
        return jsonify({'success': True, 'leaderboard': result, 'type': period_type})


# ========================================
# USER STATS APIs
# ========================================

@social_bp.route('/api/user/<int:user_id>/stats')
def api_user_stats(user_id):
    """Get detailed stats for a user."""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Get leaderboard stats
    stats = Leaderboard.get_dynamic_leaderboard()
    user_stat = next((s for s in stats if s['user_id'] == user_id), None)
    
    # Get badges
    badges = []
    try:
        from models import UserBadge
        badges = UserBadge.get_user_badges(user_id)
    except Exception:
        pass
    
    # Get followers/following counts
    followers_count = Follower.get_follower_count(user_id)
    following_count = Follower.get_following_count(user_id)
    
    # Build response
    result = {
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'bio': user.get('bio', '') or '',
            'profile_picture': user.get('profile_picture', '') or '',
            'favorite_sport': user.get('favorite_sport', '') or '',
            'location': user.get('location', '') or '',
        }
    }
    
    if user_stat:
        result['stats'] = {
            'total_points': user_stat['total_points'],
            'match_points': user_stat['match_points'],
            'manual_points': user_stat['manual_points'],
            'matches_played': user_stat['matches_played'],
            'wins': user_stat['wins'],
            'losses': user_stat['losses'],
            'draws': user_stat['draws'],
            'win_rate': round((user_stat['wins'] / user_stat['matches_played'] * 100) if user_stat['matches_played'] > 0 else 0, 2)
        }
    else:
        result['stats'] = {
            'total_points': 0,
            'match_points': 0,
            'manual_points': 0,
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0.0
        }
    
    result['badges'] = [{
        'badge_code': b['badge_code'],
        'badge_name': b['badge_name'],
        'description': b['description'],
        'icon': b['icon'],
        'awarded_at': b['awarded_at'].isoformat() if hasattr(b['awarded_at'], 'isoformat') else str(b['awarded_at'])
    } for b in badges]
    
    result['followers_count'] = followers_count
    result['following_count'] = following_count
    
    return jsonify({'success': True, **result})


# ========================================
# AI MATCH REPORT APIs
# ========================================

@social_bp.route('/api/leaderboard/adjust-points', methods=['POST'])
def api_adjust_points():
    """Adjust points for a player in specific season."""
    resp = login_required_json()
    if resp:
        return resp
    
    data = request.get_json() or {}
    user_id = data.get('user_id')
    season = data.get('season')
    amount = data.get('amount')
    reason = data.get('reason')
    
    if not user_id or not season or amount is None or not reason:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    if season not in ['weekly', 'monthly', 'lifetime']:
        return jsonify({'success': False, 'message': 'Invalid season type'}), 400
    
    # Get current seasonal leaderboard entry
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT id, points FROM seasonal_leaderboard 
            WHERE user_id = %s AND period_type = %s AND is_current = TRUE
        """, (user_id, season))
        entry = cur.fetchone()
        cur.close()
        
        if not entry:
            return jsonify({'success': False, 'message': 'Player not found in leaderboard'}), 404
        
        current_points = entry['points']
        new_points = current_points + amount
        
        if new_points < 0:
            return jsonify({'success': False, 'message': 'Points cannot be negative'}), 400
        
        # Update points using a fresh cursor
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE seasonal_leaderboard 
            SET points = %s 
            WHERE id = %s
        """, (new_points, entry['id']))
        mysql.connection.commit()
        cur.close()
        
        # Recalculate ranks for this season using another fresh cursor
        cur = mysql.connection.cursor()
        cur.execute("SET @rank = 0")
        cur.execute("""
            UPDATE seasonal_leaderboard sl
            INNER JOIN (
                SELECT id, (@rank := @rank + 1) as new_rank
                FROM seasonal_leaderboard
                WHERE period_type = %s AND is_current = TRUE
                ORDER BY points DESC, wins DESC
            ) ranked ON sl.id = ranked.id
            SET sl.rank_position = ranked.new_rank
            WHERE sl.period_type = %s AND sl.is_current = TRUE
        """, (season, season))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True, 
            'message': f'Points adjusted successfully. New total: {new_points}'
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if cur:
            cur.close()


@social_bp.route('/api/user/badges')
def api_user_badges():
    """Get badges for multiple users."""
    user_ids = request.args.get('user_ids', '')
    if not user_ids:
        return jsonify({'success': False, 'message': 'No user IDs provided'}), 400
    
    ids = [int(x.strip()) for x in user_ids.split(',') if x.strip().isdigit()]
    if not ids:
        return jsonify({'success': False, 'message': 'Invalid user IDs'}), 400
    
    cur = mysql.connection.cursor()
    placeholders = ','.join(['%s'] * len(ids))
    cur.execute(f"""
        SELECT ub.user_id, b.badge_code, b.badge_name, b.description, b.icon
        FROM user_badges ub
        JOIN badges b ON ub.badge_code = b.badge_code
        WHERE ub.user_id IN ({placeholders})
        ORDER BY ub.awarded_at DESC
    """, tuple(ids))
    rows = cur.fetchall()
    cur.close()
    
    result = {}
    for row in rows:
        uid = row['user_id']
        if uid not in result:
            result[uid] = []
        result[uid].append({
            'badge_code': row['badge_code'],
            'badge_name': row['badge_name'],
            'description': row['description'],
            'icon': row['icon']
        })
    
    return jsonify({'success': True, 'badges': result})


@social_bp.route('/api/ai-match-report', methods=['POST'])
def api_generate_ai_match_report():
    """Generate an AI match report."""
    resp = login_required_json()
    if resp:
        return resp
    
    data = request.get_json() or {}
    match_id = data.get('match_id')
    
    if not match_id:
        return jsonify({'success': False, 'message': 'Match ID is required'}), 400
    
    # Get match details
    match = Match.get_by_id(match_id)
    if not match:
        return jsonify({'success': False, 'message': 'Match not found'}), 404
    
    # Get participants
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT mp.user_id, u.name, mr.points_awarded
        FROM match_participants mp
        JOIN users u ON mp.user_id = u.id
        LEFT JOIN match_results_new mr ON mp.match_id = mr.match_id AND mp.user_id = mr.user_id
        WHERE mp.match_id = %s
    """, (match_id,))
    participants = cur.fetchall()
    cur.close()
    
    # Generate report (simplified - in real app would use AI)
    winner = next((p for p in participants if p['points_awarded'] == 10), None)
    
    report_data = {
        'match_id': match_id,
        'sport_name': match['sport_name'],
        'match_date': str(match['match_date']),
        'participants': [{'name': p['name'], 'points': p['points_awarded']} for p in participants],
        'winner': winner['name'] if winner else None,
        'summary': f"Match played on {match['match_date']} at {match['venue_name']}",
        'mvp': winner['name'] if winner else 'N/A',
        'key_stats': {
            'total_participants': len(participants),
            'winner': winner['name'] if winner else 'Draw'
        },
        'strengths': ['Good teamwork', 'Excellent sportsmanship'],
        'improvements': ['Practice more', 'Work on strategy']
    }
    
    # Save report to database
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ai_match_reports (match_id, user_id, report_data, summary, mvp_user_id, key_statistics, strengths, improvements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE report_data = VALUES(report_data), generated_at = NOW()
        """, (
            match_id,
            session['user_id'],
            str(report_data).replace("'", '"'),
            report_data['summary'],
            winner['user_id'] if winner else None,
            str(report_data['key_stats']),
            ', '.join(report_data['strengths']),
            ', '.join(report_data['improvements'])
        ))
        mysql.connection.commit()
        report_id = cur.lastrowid
        cur.close()
        
        # Log event to trigger notification
        from models.events import EventLog
        EventLog.log(
            'ai_report_generated',
            user_id=session['user_id'],
            entity_type='match',
            entity_id=match_id,
            event_data={'report_id': report_id}
        )
        
        return jsonify({
            'success': True,
            'report': report_data,
            'message': 'AI match report generated successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500