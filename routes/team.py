from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import mysql, Team, TeamMember, User, Match, TeamMatch, TeamStatistics, TeamActivityLog, PointHistory, EventLog

team_bp = Blueprint('team', __name__)


@team_bp.route('/teams')
def teams():
    if 'user_id' not in session:
        flash('Please log in to view teams.', 'warning')
        return redirect(url_for('auth.login'))

    sport_filter = request.args.get('sport')
    location_filter = request.args.get('location')
    search = request.args.get('search')

    if search:
        teams_list = Team.search(search)
    elif sport_filter or location_filter:
        teams_list = Team.get_filtered(sport_filter, location_filter)
    else:
        teams_list = Team.get_all()

    return render_template('teams.html', teams=teams_list, current_user=User.get_by_id(session['user_id']))


@team_bp.route('/teams/create', methods=['GET', 'POST'])
def create_team():
    if 'user_id' not in session:
        flash('Please log in to create a team.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        team_name = request.form.get('team_name', '').strip()
        description = request.form.get('description', '').strip()
        sport_type = request.form.get('sport_type', '').strip()
        location = request.form.get('location', '').strip()
        max_members = int(request.form.get('max_members', 10))
        logo_file = request.files.get('logo')

        if not team_name or not sport_type or not location:
            flash('Team name, sport type, and location are required.', 'danger')
            return render_template('create_team.html')
        logo_path = None
        if logo_file and logo_file.filename:
            from werkzeug.utils import secure_filename
            import os
            filename = secure_filename(logo_file.filename)
            logo_path = f'static/uploads/teams/{filename}'
            full_path = os.path.join(current_app.root_path, logo_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            logo_file.save(full_path)

        try:
            team_id = Team.create(
                team_name=team_name,
                description=description,
                sport_type=sport_type,
                location=location,
                captain_id=session['user_id'],
                max_members=max_members,
                logo=logo_path
            )
            TeamMember.add_member(team_id, session['user_id'])
            flash('Team created successfully!', 'success')
            return redirect(url_for('team.team_details', team_id=team_id))
        except Exception as e:
            flash(f'Error creating team: {str(e)}', 'danger')
            return render_template('create_team.html')

    return render_template('create_team.html', current_user=User.get_by_id(session['user_id']))


@team_bp.route('/teams/<int:team_id>')
def team_details(team_id):
    if 'user_id' not in session:
        flash('Please log in to view team details.', 'warning')
        return redirect(url_for('auth.login'))
    team = Team.get_by_id(team_id)
    if not team:
        flash('Team not found.', 'danger')
        return redirect(url_for('team.teams'))

    members = TeamMember.get_members(team_id)
    is_member = TeamMember.is_member(team_id, session['user_id'])
    is_captain = Team.is_captain(team_id, session['user_id'])

    return render_template('team_details.html',
                           team=team,
                           members=members,
                           is_member=is_member,
                           is_captain=is_captain,
                           current_user=User.get_by_id(session['user_id']))


@team_bp.route('/teams/join/<int:team_id>', methods=['POST'])
def join_team(team_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    team = Team.get_by_id(team_id)
    if not team:
        return jsonify({'success': False, 'message': 'Team not found.'}), 404

    if TeamMember.is_member(team_id, session['user_id']):
        return jsonify({'success': False, 'message': 'You are already a member.'}), 400

    member_count = TeamMember.get_member_count(team_id)
    if member_count >= team['max_members']:
        return jsonify({'success': False, 'message': 'Team is full.'}), 400

    try:
        TeamMember.add_member(team_id, session['user_id'])
        return jsonify({'success': True, 'message': 'Successfully joined the team!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@team_bp.route('/teams/leave/<int:team_id>', methods=['POST'])
def leave_team(team_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    if Team.is_captain(team_id, session['user_id']):
        return jsonify({'success': False, 'message': 'Captain cannot leave the team. Transfer ownership or delete the team.'}), 400

    try:
        TeamMember.remove_member(team_id, session['user_id'])
        return jsonify({'success': True, 'message': 'Successfully left the team.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@team_bp.route('/teams/remove_member/<int:team_id>/<int:member_id>', methods=['POST'])
def remove_member(team_id, member_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    if not Team.is_captain(team_id, session['user_id']):
        return jsonify({'success': False, 'message': 'Only the captain can remove members.'}), 403

    if member_id == session['user_id']:
        return jsonify({'success': False, 'message': 'Cannot remove yourself.'}), 400

    try:
        TeamMember.remove_member(team_id, member_id)
        return jsonify({'success': True, 'message': 'Member removed successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@team_bp.route('/teams/delete/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    if not Team.is_captain(team_id, session['user_id']):
        return jsonify({'success': False, 'message': 'Only the captain can delete the team.'}), 403

    try:
        Team.delete(team_id)
        return jsonify({'success': True, 'message': 'Team deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@team_bp.route('/teams/update/<int:team_id>', methods=['GET', 'POST'])
def update_team(team_id):
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    team = Team.get_by_id(team_id)

    if not team:
        flash('Team not found.', 'danger')
        return redirect(url_for('team.teams'))

    if not Team.is_captain(team_id, session['user_id']):
        flash('Only the captain can update the team.', 'danger')
        return redirect(url_for('team.team_details', team_id=team_id))

    if request.method == "GET":
        return render_template(
    "create_team.html",
    team=team,
    current_user=User.get_by_id(session["user_id"]),
    edit_mode=True
)
        

    team_name = request.form.get('team_name', '').strip()
    description = request.form.get('description', '').strip()
    sport_type = request.form.get('sport_type', '').strip()
    location = request.form.get('location', '').strip()
    max_members = int(request.form.get('max_members', 10))

    if not team_name or not sport_type or not location:
        flash('Team name, sport type, and location are required.', 'danger')
        return render_template(
    "create_team.html",
    team=team,
    current_user=User.get_by_id(session["user_id"]),
    edit_mode=True
)

    logo_file = request.files.get('logo')
    logo_path = None

    if logo_file and logo_file.filename:
        from werkzeug.utils import secure_filename
        import os

        filename = secure_filename(logo_file.filename)
        logo_path = f'static/uploads/teams/{filename}'
        full_path = os.path.join(current_app.root_path, logo_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        logo_file.save(full_path)

    try:
        Team.update(
            team_id,
            team_name,
            description,
            sport_type,
            location,
            max_members,
            logo_path
        )

        flash('Team updated successfully!', 'success')
        return redirect(url_for('team.team_details', team_id=team_id))

    except Exception as e:
        flash(str(e), 'danger')
        return render_template(
    "create_team.html",
    team=team,
    current_user=User.get_by_id(session["user_id"]),
    edit_mode=True
)

@team_bp.route('/api/teams')
def api_teams():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    teams_list = Team.get_all()
    return jsonify({'teams': teams_list})


@team_bp.route('/api/teams/<int:team_id>')
def api_team_details(team_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    team = Team.get_by_id(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404

    members = TeamMember.get_members(team_id)
    is_member = TeamMember.is_member(team_id, session['user_id'])
    is_captain = Team.is_captain(team_id, session['user_id'])

    return jsonify({
        'team': team,
        'members': members,
        'is_member': is_member,
        'is_captain': is_captain
    })


# ========================================
# TEAM DASHBOARD
# ========================================

@team_bp.route('/teams/dashboard/<int:team_id>')
def team_dashboard(team_id):

    print("TEAM DASHBOARD ROUTE HIT")
    if 'user_id' not in session:
        flash('Please log in to view team dashboard.', 'warning')
        return redirect(url_for('auth.login'))

    team = Team.get_by_id(team_id)
    if not team:
        flash('Team not found.', 'danger')
        return redirect(url_for('team.teams'))

    # Initialize safe defaults to prevent crashes
    stats = {
        "wins": 0, "losses": 0, "draws": 0, 
        "matches_played": 0, "points": 0, "win_rate": 0, 
        "rank": 0, "total_members": 0
    }
    recent_activity = []
    matches = []
    team_members = []

    try:
        # Get match history for the team
        matches = TeamMatch.get_by_team(team_id)
        
        # Get recent activity (always available from DB)
        recent_activity = TeamActivityLog.get_recent_for_team(team_id, limit=10)
        
        # Try to get statistics (may fail if columns don't exist yet)
        try:
            stat_record = TeamStatistics.get_by_team(team_id)
            if stat_record and stat_record.get('matches_played', 0) > 0:
                stats = {
                    "wins": stat_record.get('wins', 0),
                    "losses": stat_record.get('losses', 0),
                    "draws": stat_record.get('draws', 0),
                    "matches_played": stat_record.get('matches_played', 0),
                    "points": stat_record.get('total_points', 0),
                    "win_rate": stat_record.get('win_percentage', 0),
                    "rank": stat_record.get('current_rank') or 0,
                    "total_members": TeamMember.get_member_count(team_id)
                }
            else:
                # No statistics record or empty record - compute from match history
                raise Exception("No stats to use")
        except Exception:
            # Statistics table may not exist yet or no stats record - compute from matches
            if matches:
                wins = 0
                losses = 0
                draws = 0
                points = 0
                completed_matches = [m for m in matches if m['status'] == 'completed']
                matches_played = len(completed_matches)

                for match in completed_matches:
                    if match['is_draw']:
                        draws += 1
                        points += 5
                    elif match['winner_team_id'] == team_id:
                        wins += 1
                        points += 10
                    else:
                        losses += 1

                win_rate = round((wins / matches_played * 100) if matches_played > 0 else 0, 2)

                stats = {
                    "wins": wins,
                    "losses": losses,
                    "draws": draws,
                    "matches_played": matches_played,
                    "points": points,
                    "win_rate": win_rate,
                    "rank": 0,
                    "total_members": TeamMember.get_member_count(team_id)
                }
            else:
                # No matches at all - keep defaults
                stats["total_members"] = TeamMember.get_member_count(team_id)
            
    except Exception:
        pass  # Non-critical, use empty defaults

    # Generate team analytics data
    team_analytics = {
        "points_trend": [],
        "performance_trend": [],
        "win_loss_summary": {"wins": 0, "losses": 0}
    }

    if matches:
        completed_matches = [m for m in matches if m['status'] == 'completed']
        if completed_matches:
            # Build points trend from completed matches
            cumulative_points = 0
            for idx, match in enumerate(completed_matches, 1):
                if match['is_draw']:
                    cumulative_points += 5
                elif match['winner_team_id'] == team_id:
                    cumulative_points += 10
                team_analytics["points_trend"].append({
                    "match": f"Match {idx}",
                    "points": cumulative_points
                })

                wins_cum = sum(1 for m in completed_matches[:idx] 
                              if not m['is_draw'] and m['winner_team_id'] == team_id)
                losses_cum = sum(1 for m in completed_matches[:idx] 
                                if not m['is_draw'] and m['winner_team_id'] != team_id)
                team_analytics["performance_trend"].append({
                    "match": f"Match {idx}",
                    "wins": wins_cum,
                    "losses": losses_cum
                })

            # Win/Loss summary
            final_wins = stats['wins']
            final_losses = stats['losses']
            team_analytics["win_loss_summary"] = {
                "wins": final_wins,
                "losses": final_losses
            }

    members = TeamMember.get_members(team_id)
    is_member = TeamMember.is_member(team_id, session['user_id'])
    is_captain = Team.is_captain(team_id, session['user_id'])

    # Prepare leaderboard data (team's current position)
    leaderboard_data = {
        'rank': stats.get('rank', 0),
        'points': stats.get('points', 0),
        'matches_played': stats.get('matches_played', 0),
        'wins': stats.get('wins', 0),
        'losses': stats.get('losses', 0),
        'draws': stats.get('draws', 0)
    }
    print("ANALYTICS:", team_analytics)

    return render_template('team_dashboard.html',
                           team=team,
                           stats=stats,
                           recent_activity=recent_activity,
                           matches=matches,
                           team_members=members,
                           leaderboard_data=leaderboard_data,
                           is_member=is_member,
                           is_captain=is_captain,
                           team_analytics=team_analytics,
                           current_user=User.get_by_id(session['user_id']))


# ========================================
# TEAM LEADERBOARD
# ========================================

@team_bp.route('/teams/leaderboard')
def team_leaderboard():
    if 'user_id' not in session:
        flash('Please log in to view team leaderboard.', 'warning')
        return redirect(url_for('auth.login'))

    # Initialize safe defaults
    stats = {"wins": 0, "losses": 0, "draws": 0, "matches_played": 0}
    recent_activity = []
    matches = []
    team_members = []

    # Get filters
    search = request.args.get('search', '')
    sport_filter = request.args.get('sport', '')
    location_filter = request.args.get('location', '')

    # Get leaderboard data
    leaderboard = TeamStatistics.get_leaderboard(limit=100)

    # Apply filters
    if search:
        leaderboard = [t for t in leaderboard if search.lower() in t['team_name'].lower()]
    if sport_filter:
        leaderboard = [t for t in leaderboard if t['sport_type'].lower() == sport_filter.lower()]
    if location_filter:
        leaderboard = [t for t in leaderboard if location_filter.lower() in t['location'].lower()]

    # Get user's team for highlighting
    user_teams = Team.get_by_user(session['user_id'])
    user_team_ids = [t['id'] for t in user_teams]

    # Get distinct sports and locations for filters
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT sport_type FROM teams ORDER BY sport_type")
    sports = [row['sport_type'] for row in cur.fetchall()]
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT location FROM teams ORDER BY location")
    locations = [row['location'] for row in cur.fetchall()]
    cur.close()

    return render_template(
    'team_leaderboard.html',
    leaderboard=leaderboard,
    stats=stats,
    recent_activity=recent_activity,
    matches=matches,
    team_members=team_members,
    user_team_ids=user_team_ids,
    sports=sports,
    locations=locations,
    search=search,
    sport_filter=sport_filter,
    location_filter=location_filter,
    current_user=User.get_by_id(session['user_id'])
)

# ========================================
# TEAM MATCH HISTORY
# ========================================

@team_bp.route('/teams/matches/<int:team_id>')
def team_match_history(team_id):
    if 'user_id' not in session:
        flash('Please log in to view match history.', 'warning')
        return redirect(url_for('auth.login'))

    team = Team.get_by_id(team_id)
    if not team:
        flash('Team not found.', 'danger')
        return redirect(url_for('team.teams'))

    # Get all matches for this team
    try:
        matches = TeamMatch.get_by_team(team_id)
    except Exception:
        matches = []

    # Process matches to add opponent and result info
    processed_matches = []
    for match in matches:
        opponent = match['team2_name'] if match['team1_id'] == team_id else match['team1_name']
        opponent_logo = match['team2_logo'] if match['team1_id'] == team_id else match['team1_logo']
        
        if match['is_draw']:
            result = 'Draw'
        elif match['winner_team_id'] == team_id:
            result = 'Won'
        else:
            result = 'Lost'

        processed_matches.append({
            'id': match['id'],
            'opponent': opponent,
            'opponent_logo': opponent_logo,
            'sport_type': match['sport_type'],
            'venue_name': match['venue_name'],
            'match_date': match['match_date'],
            'match_time': match['match_time'],
            'team1_score': match['team1_score'],
            'team2_score': match['team2_score'],
            'result': result,
            'status': match['status']
        })

    is_member = TeamMember.is_member(team_id, session['user_id'])
    is_captain = Team.is_captain(team_id, session['user_id'])

    return render_template('team_match_history.html',
                           team=team,
                           matches=processed_matches,
                           is_member=is_member,
                           is_captain=is_captain,
                           current_user=User.get_by_id(session['user_id']))


# ========================================
# API: CREATE TEAM MATCH
# ========================================

@team_bp.route('/api/teams/create-match', methods=['POST'])
def api_create_team_match():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    data = request.get_json()
    team1_id = data.get('team1_id')
    team2_id = data.get('team2_id')
    sport_type = data.get('sport_type')
    venue_name = data.get('venue_name')
    match_date = data.get('match_date')
    match_time = data.get('match_time')

    if not all([team1_id, team2_id, sport_type, venue_name, match_date, match_time]):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    # Verify user is captain of team1
    if not Team.is_captain(team1_id, session['user_id']):
        return jsonify({'success': False, 'message': 'Only captain can create matches.'}), 403

    try:
        match_id = TeamMatch.create(team1_id, team2_id, sport_type, venue_name, match_date, match_time)
        return jsonify({'success': True, 'message': 'Match created successfully!', 'match_id': match_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========================================
# API: RECORD TEAM MATCH RESULT
# ========================================

@team_bp.route('/api/teams/record-match-result', methods=['POST'])
def api_record_match_result():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    data = request.get_json()
    match_id = data.get('match_id')
    team1_score = data.get('team1_score')
    team2_score = data.get('team2_score')
    winner_team_id = data.get('winner_team_id')
    is_draw = data.get('is_draw', False)

    if not all([match_id, team1_score is not None, team2_score is not None]):
        return jsonify({'success': False, 'message': 'Match ID and scores are required.'}), 400

    try:
        TeamMatch.record_result(match_id, team1_score, team2_score, winner_team_id, is_draw)
        return jsonify({'success': True, 'message': 'Match result recorded successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========================================
# API: ADD TEAM POINTS (Admin/Captain)
# ========================================

@team_bp.route('/api/teams/add-points', methods=['POST'])
def api_add_team_points():
    """Add points to a team (admin/captain only)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    data = request.get_json() or request.form
    team_id = data.get('team_id')
    points = data.get('points')
    reason = data.get('reason', '')

    if not team_id or not points or not reason:
        return jsonify({'success': False, 'message': 'Team ID, points, and reason are required.'}), 400

    try:
        team_id = int(team_id)
        points = int(points)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid data types.'}), 400

    if points <= 0:
        return jsonify({'success': False, 'message': 'Points must be a positive number.'}), 400

    try:
        # Verify user is captain or admin (simplified - just check captain for now)
        if not Team.is_captain(team_id, session['user_id']):
            return jsonify({'success': False, 'message': 'Only the captain can adjust team points.'}), 403

        TeamStatistics.add_team_points(team_id, points, reason, session['user_id'])
        
        return jsonify({
            'success': True,
            'message': f'{points} points added successfully!',
            'team_id': team_id,
            'points_added': points
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========================================
# API: ADJUST TEAM POINTS (Admin/Captain)
# ========================================

@team_bp.route('/api/teams/adjust-points', methods=['POST'])
def api_adjust_team_points():
    """Adjust team points (add or subtract) - admin/captain only."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    data = request.get_json() or request.form
    team_id = data.get('team_id')
    delta = data.get('delta')
    reason = data.get('reason', '')

    if not team_id or delta is None or not reason:
        return jsonify({'success': False, 'message': 'Team ID, delta, and reason are required.'}), 400

    try:
        team_id = int(team_id)
        delta = int(delta)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid data types.'}), 400

    if delta == 0:
        return jsonify({'success': False, 'message': 'Delta cannot be zero.'}), 400

    try:
        # Verify user is captain or admin
        if not Team.is_captain(team_id, session['user_id']):
            return jsonify({'success': False, 'message': 'Only the captain can adjust team points.'}), 403

        TeamStatistics.adjust_team_points(team_id, delta, reason, session['user_id'])
        
        return jsonify({
            'success': True,
            'message': f'Points adjusted by {delta} successfully!',
            'team_id': team_id,
            'delta': delta
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========================================
# API: GET TEAM POINT HISTORY
# ========================================

@team_bp.route('/api/teams/point-history/<int:team_id>')
def api_team_point_history(team_id):
    """Get point history for a team."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    history = PointHistory.get_for_entity('team', team_id, limit=50)
    
    return jsonify({
        'success': True,
        'team_id': team_id,
        'history': history
    })


# ========================================
# TEAM FOLLOW / UNFOLLOW
# ========================================

@team_bp.route('/api/team/<int:team_id>/follow', methods=['POST'])
def api_follow_team(team_id):
    """Follow a team."""
    resp = login_required_json()
    if resp:
        return resp
    
    user_id = session['user_id']
    
    try:
        team = Team.get_by_id(team_id)
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'}), 404
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT IGNORE INTO team_followers (team_id, user_id)
            VALUES (%s, %s)
        """, (team_id, user_id))
        mysql.connection.commit()
        
        if cur.rowcount > 0:
            return jsonify({'success': True, 'message': f'Now following {team["team_name"]}!'})
        else:
            return jsonify({'success': False, 'message': 'Already following'}), 409
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@team_bp.route('/api/team/<int:team_id>/unfollow', methods=['POST'])
def api_unfollow_team(team_id):
    """Unfollow a team."""
    resp = login_required_json()
    if resp:
        return resp
    
    user_id = session['user_id']
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            DELETE FROM team_followers
            WHERE team_id = %s AND user_id = %s
        """, (team_id, user_id))
        mysql.connection.commit()
        
        if cur.rowcount > 0:
            return jsonify({'success': True, 'message': 'Unfollowed team'})
        else:
            return jsonify({'success': False, 'message': 'Not following'}), 409
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@team_bp.route('/api/team/<int:team_id>/follow-status')
def api_team_follow_status(team_id):
    """Check if user is following a team."""
    if 'user_id' not in session:
        return jsonify({'is_following': False})
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COUNT(*) as cnt FROM team_followers
        WHERE team_id = %s AND user_id = %s
    """, (team_id, user_id))
    row = cur.fetchone()
    cur.close()
    
    return jsonify({'is_following': row['cnt'] > 0 if row else False})


@team_bp.route('/api/team/<int:team_id>/followers')
def api_team_followers(team_id):
    """Get team followers."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT tf.user_id, u.name, tf.created_at as followed_at
            FROM team_followers tf
            JOIN users u ON tf.user_id = u.id
            WHERE tf.team_id = %s
            ORDER BY tf.created_at DESC
        """, (team_id,))
        followers = cur.fetchall()
        cur.close()
        
        result = [{
            'user_id': f['user_id'],
            'name': f['name'],
            'followed_at': f['followed_at'].isoformat() if hasattr(f['followed_at'], 'isoformat') else str(f['followed_at'])
        } for f in followers]
        
        return jsonify({'success': True, 'followers': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
