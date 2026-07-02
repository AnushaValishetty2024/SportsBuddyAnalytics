import logging
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify, make_response
from models import mysql, User, Match, Leaderboard, NearbyBusiness, GameCategory, SportsVenue, PointHistory
from models.team import TeamStatistics

# Configure logging for leaderboard debugging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

dashboard_bp = Blueprint("dashboard", __name__)

def _add_cache_headers(response):
    """Add cache-control headers to prevent any browser caching.
    
    Ensures leaderboard and other data pages always fetch fresh data.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def clean_json(data):
    cleaned = []
    for row in data:
        new_row = {}
        for k, v in row.items():
            if hasattr(v, "total_seconds"):  # fixes timedelta
                new_row[k] = v.total_seconds()
            else:
                new_row[k] = v
        cleaned.append(new_row)
    return cleaned


def get_user_from_db(user_id):
    return User.get_by_id(user_id)


def login_required():
    """Redirect to login if not authenticated."""
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))
    return None


# ========================================
# MAIN DASHBOARD
# ========================================

@dashboard_bp.route("/dashboard")
def dashboard():
    redirect_resp = login_required()
    if redirect_resp:
        return redirect_resp

    user = get_user_from_db(session["user_id"])

    # --- Module 1: Stats Counts ---
    upcoming_matches = Match.get_upcoming(limit=12)

    # Total Games count from game_categories table
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM game_categories")
    total_games = cur.fetchone()['cnt']
    cur.close()

    # --- Module 3: Discover Matches - get distinct sport names for filter ---
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT sport_name FROM matches ORDER BY sport_name")
    sport_list = [row['sport_name'] for row in cur.fetchall()]
    cur.close()

    # --- Module 6: Nearby Sports Venues ---
    raw_venues = SportsVenue.get_all()
    nearby_businesses = []
    for v in raw_venues:
        sport_types_list = [s.strip() for s in v["sport_types"].split(",") if s.strip()]
        nearby_businesses.append({
            "id": v["id"],
            "name": v["name"],
            "business_type": "sports_venue",
            "description": f"Rating: {v['rating']}/5 | {v['available_slots']} slots available | {v['distance_km']} km away",
            "address": v["address"] or "",
            "sport_types": sport_types_list,
            "rating": float(v["rating"]),
            "latitude": float(v["latitude"]),
            "longitude": float(v["longitude"]),
            "available_slots": int(v["available_slots"]),
            "distance_km": float(v["distance_km"]),
            "image_url": v["image_url"] or ""
        })

    # --- Module 5: Map locations data ---
    match_locations = clean_json(Match.get_with_locations())
    business_locations = clean_json(SportsVenue.get_with_locations())
    # --- Module 2: Join Match check - which matches user has joined ---
    user_joined_matches = []
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT match_id FROM match_participants WHERE user_id = %s",
            (session["user_id"],)
        )
        user_joined_matches = [row['match_id'] for row in cur.fetchall()]
        cur.close()
    except Exception:
        pass

    # Get user's teams information
    user_team_count = 0
    user_teams = []
    if 'user_id' in session:
        try:
            user_teams = Team.get_by_user(session['user_id'])
            user_team_count = len(user_teams)
        except Exception:
            pass

    # Get user's stats (safe defaults)
    from models.team import TeamStatistics, TeamActivityLog
    try:
        user_stats = TeamStatistics.get_by_user_summary(session['user_id'])
    except Exception:
        user_stats = {'wins': 0, 'losses': 0, 'draws': 0, 'total_points': 0, 'rank': 0}

    return render_template(
        "dashboard.html",
        user=user,
        upcoming_matches=upcoming_matches,
        sport_list=sport_list,
        nearby_businesses=nearby_businesses,
        match_locations=match_locations,
        business_locations=business_locations,
        user_joined_matches=user_joined_matches,
        total_games=total_games,
        user_team_count=user_team_count,
        user_teams=user_teams,
        user_stats=user_stats
    )


# ========================================
# CREATE MATCH
# ========================================

@dashboard_bp.route("/create-match", methods=["GET", "POST"])
def create_match():
    redirect_resp = login_required()
    if redirect_resp:
        return redirect_resp

    if request.method == "POST":
        sport_type = request.form.get("sport_type")
        sport_name = request.form.get("sport_name")
        match_date = request.form.get("match_date")
        match_time = request.form.get("match_time")
        venue_name = request.form.get("venue_name")
        max_players = request.form.get("max_players")

        if not all([sport_type, sport_name, match_date, match_time, venue_name, max_players]):
            flash("All fields are required.", "danger")
            return render_template("create_match.html")

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO matches
                    (creator_id, sport_type, sport_name, match_date, match_time, venue_name, max_players)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session["user_id"],
                sport_type,
                sport_name,
                match_date,
                match_time,
                venue_name,
                int(max_players)
            ))
            mysql.connection.commit()
            cursor.close()

            flash("Match created successfully!", "success")
            return redirect(url_for("dashboard.dashboard"))

        except Exception as e:
            flash(f"Database error: {e}", "danger")
            return render_template("create_match.html")

    return render_template("create_match.html")


# ========================================
# API: DISCOVER / FILTER MATCHES (AJAX)
# ========================================

@dashboard_bp.route("/api/discover-matches")
def api_discover_matches():
    """Return filtered matches as JSON for the Discover section.
    
    Accepts optional query parameters: sport, location, date, skill_level,
    match_type, gender, available_slots, distance, user_lat, user_lng.
    All filters are optional - empty filters are ignored.
    Returns all matches if no filters provided (up to limit).
    """
    # Get all filter parameters from request
    sport_name = request.args.get("sport") or request.args.get("sport_name")
    location = request.args.get("location")
    match_date = request.args.get("date") or request.args.get("match_date")
    skill_level = request.args.get("skill_level")
    match_type = request.args.get("match_type")
    gender = request.args.get("gender")
    available_slots = request.args.get("available_slots")
    distance_km = request.args.get("distance")
    
    # Optional lat/lng for distance filtering (passed through)
    user_lat = request.args.get("user_lat")
    user_lng = request.args.get("user_lng")

    matches = Match.get_filtered(
        sport_name=sport_name if sport_name else None,
        location=location if location else None,
        match_date=match_date if match_date else None,
        skill_level=skill_level if skill_level else None,
        match_type=match_type if match_type else None,
        gender=gender if gender else None,
        available_slots=available_slots if available_slots else None,
        distance_km=distance_km if distance_km else None,
        user_lat=user_lat if user_lat else None,
        user_lng=user_lng if user_lng else None,
        limit=50
    )

    # Get user's joined matches (if logged in)
    user_joined_ids = []
    if 'user_id' in session:
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT match_id FROM match_participants WHERE user_id = %s",
                (session['user_id'],)
            )
            user_joined_ids = [row['match_id'] for row in cur.fetchall()]
            cur.close()
        except Exception:
            pass  # Non-critical, just won't show join status

    # Serialize for JSON
    match_list = []
    for m in matches:
        match_list.append({
            "id": m["id"],
            "sport_name": m["sport_name"],
            "sport_type": m["sport_type"],
            "venue_name": m["venue_name"],
            "match_date": str(m["match_date"]),
            "match_time": str(m["match_time"]),
            "max_players": m["max_players"],
            "player_count": m["player_count"],
            "creator_name": m["creator_name"],
            "skill_level": m.get("skill_level") or "",
            "gender_preference": m.get("gender_preference") or "",
            "latitude": float(m["latitude"]) if m.get("latitude") else None,
            "longitude": float(m["longitude"]) if m.get("longitude") else None
        })

    return jsonify({
        "success": True,
        "matches": match_list,
        "count": len(match_list),
        "user_joined_ids": user_joined_ids
    })


# ========================================
# API: JOIN MATCH
# ========================================

@dashboard_bp.route("/api/join-match/<int:match_id>", methods=["POST"])
def api_join_match(match_id):
    redirect_resp = login_required()
    if redirect_resp:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]

    try:
        cursor = mysql.connection.cursor()

        # Check if already joined
        cursor.execute(
            "SELECT id FROM match_participants WHERE match_id = %s AND user_id = %s",
            (match_id, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Already joined this match"}), 409

        # Check if match is full
        cursor.execute(
            "SELECT max_players FROM matches WHERE id = %s",
            (match_id,)
        )
        match = cursor.fetchone()
        if not match:
            cursor.close()
            return jsonify({"error": "Match not found"}), 404

        cursor.execute(
            "SELECT COUNT(*) as cnt FROM match_participants WHERE match_id = %s",
            (match_id,)
        )
        count = cursor.fetchone()["cnt"]
        if count >= match["max_players"]:
            cursor.close()
            return jsonify({"error": "Match is full"}), 409

        # Join the match
        cursor.execute(
            "INSERT INTO match_participants (match_id, user_id) VALUES (%s, %s)",
            (match_id, user_id)
        )
        mysql.connection.commit()
        cursor.close()

        # Auto-join match group chat (ensure conversation_members entry exists)
        try:
            cur2 = mysql.connection.cursor()
            cur2.execute("""
                INSERT IGNORE INTO conversation_members (match_id, user_id)
                VALUES (%s, %s)
            """, (match_id, user_id))
            mysql.connection.commit()
            cur2.close()
        except Exception:
            pass  # Non-critical if group chat auto-join fails

        return jsonify({"success": True, "message": "Joined match successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================================
# API: MATCH LOCATIONS (for map)
# ========================================

@dashboard_bp.route("/api/match-locations")
def api_match_locations():
    """Return all match locations as simple JSON array for map display.
    
    Response format:
    [
        {
            "id": 1,
            "sport_name": "Cricket",
            "venue_name": "ABC Ground",
            "latitude": 17.385,
            "longitude": 78.486,
            "match_date": "2026-06-26"
        },
        ...
    ]
    """
    matches = Match.get_with_locations()
    result = []
    for m in matches:
        lat = m.get("latitude")
        lng = m.get("longitude")
        # Only include matches with valid coordinates
        if lat is not None and lng is not None:
            result.append({
                "id": m["id"],
                "sport_name": m["sport_name"],
                "venue_name": m["venue_name"],
                "latitude": float(lat),
                "longitude": float(lng),
                "match_date": str(m["match_date"])
            })

    return jsonify(result)


# ========================================
# API: MAP MATCHES (for Map Matches tab)
# ========================================

@dashboard_bp.route("/api/map/matches")
def api_map_matches():
    """Return match locations for the Map Matches page.
    
    Response format:
    {
        "success": true,
        "matches": [
            {
                "id": 1,
                "sport_name": "Cricket",
                "venue_name": "Elite Cricket Ground",
                "address": "...",
                "latitude": 16.5062,
                "longitude": 80.6480,
                "date": "2026-07-01",
                "time": "17:00:00",
                "skill_level": "intermediate",
                "available_slots": 11
            },
            ...
        ]
    }
    """
    try:
        matches = Match.get_with_locations()
        result = []
        for m in matches:
            lat = m.get("latitude")
            lng = m.get("longitude")
            if lat is not None and lng is not None:
                result.append({
                    "id": m["id"],
                    "sport_name": m["sport_name"],
                    "venue_name": m["venue_name"],
                    "address": m.get("location") or m.get("venue_name") or "",
                    "latitude": float(lat),
                    "longitude": float(lng),
                    "date": str(m["match_date"]),
                    "time": str(m["match_time"]),
                    "skill_level": m.get("skill_level") or "",
                    "available_slots": int(m["max_players"]) - int(m["player_count"]) if m.get("max_players") and m.get("player_count") else (m.get("max_players") or 0)
                })

        return jsonify({
            "success": True,
            "matches": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "matches": []
        }), 500


# ========================================
# API: MAP VENUES (for Map Venues tab)
# ========================================

@dashboard_bp.route("/api/map/venues")
def api_map_venues():
    """Return sports venues for the Map Venues page.
    
    Response format:
    {
        "success": true,
        "venues": [
            {
                "id": 1,
                "venue_name": "Elite Cricket Ground",
                "sport_types": ["Cricket", "Football"],
                "address": "...",
                "latitude": 16.5062,
                "longitude": 80.6480,
                "rating": 4.5,
                "available_slots": 12,
                "image_url": "..."
            },
            ...
        ]
    }
    """
    try:
        venues = SportsVenue.get_with_locations()
        result = []
        for v in venues:
            sport_types = [s.strip() for s in (v.get("sport_types") or "").split(",") if s.strip()]
            result.append({
                "id": v["id"],
                "venue_name": v["name"],
                "sport_types": sport_types,
                "address": v.get("address") or "",
                "latitude": float(v["latitude"]),
                "longitude": float(v["longitude"]),
                "rating": float(v["rating"]) if v.get("rating") is not None else 0.0,
                "available_slots": int(v["available_slots"]) if v.get("available_slots") is not None else 0,
                "image_url": v.get("image_url") or ""
            })

        return jsonify({
            "success": True,
            "venues": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "venues": []
        }), 500


# ========================================
# LEADERBOARD PAGE
# ========================================

@dashboard_bp.route("/leaderboard")
def leaderboard_page():
    """Render the leaderboard page with fresh data from database.
    
    ALWAYS fetches latest data from database - never cached or stored.
    Uses dynamic aggregation from match_results_new for real-time accuracy.
    """
    redirect_resp = login_required()
    if redirect_resp:
        return redirect_resp
    
    # Fetch fresh leaderboard data directly from database
    players = User.get_leaderboard_sorted_by_points()
    
    # Render template with fresh data
    response = make_response(
    render_template("leaderboard.html", players=players)
)
    # Add cache-control headers to prevent caching
    response = _add_cache_headers(response)
    
    return response


# ========================================
# API: LEADERBOARD (Dynamic, Never Stored)
# ========================================

@dashboard_bp.route("/api/leaderboard")
def api_leaderboard():
    """Return dynamically computed leaderboard from match_results.
    
    Leaderboard is NEVER stored. It's derived via SQL aggregation.
    Always includes users even with 0 points.
    Uses COALESCE to safely handle NULL values.
    """
    try:
        leaderboard = Leaderboard.get_dynamic_leaderboard()
        summary = Leaderboard.get_leaderboard_summary()

        # Log empty leaderboard for debugging
        if not leaderboard:
            logger.warning("API /api/leaderboard: Empty leaderboard returned - no users found in database.")
        
        # Log points calculation for first few entries
        if leaderboard:
            for entry in leaderboard[:3]:
                logger.info(f"Leaderboard entry: user_id={entry['user_id']}, "
                           f"name={entry['name']}, points={entry['total_points']}, "
                           f"rank={entry['rank']}")

        response = jsonify({
            "success": True,
            "leaderboard": leaderboard,
            "summary": summary,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        response = _add_cache_headers(response)
        return response

    except Exception as e:
        logger.error(f"Failed to fetch leaderboard: {str(e)}")
        return _add_cache_headers(jsonify({
            "success": False,
            "message": f"Failed to fetch leaderboard: {str(e)}"
        }))


# ========================================
# API: SUBMIT MATCH RESULT
# ========================================

@dashboard_bp.route("/api/submit-result", methods=["POST"])
def api_submit_result():
    """Submit match result. Creates match_results entries for all participants.
    
    Points system:
    - Winner: 10 points
    - Draw: 5 points per player
    - Loser: 0 points
    
    Transaction-safe: uses Leaderboard.insert_match_result which handles rollback.
    """
    redirect_resp = login_required()
    if redirect_resp:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json() or request.form
    match_id = data.get("match_id")
    winner_id = data.get("winner_id")
    is_draw = data.get("is_draw", False)

    if not match_id:
        logger.warning("API /api/submit-result: Missing match_id")
        return jsonify({"success": False, "message": "Match ID is required"}), 400

    try:
        match_id = int(match_id)
        if winner_id is not None:
            winner_id = int(winner_id)
        if is_draw is not None:
            is_draw = bool(is_draw)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid request data types."}), 400

    try:
        # Verify match exists
        match = Match.get_by_id(match_id)
        if not match:
            logger.warning(f"API /api/submit-result: Match {match_id} not found")
            return jsonify({"success": False, "message": "Match not found"}), 404

        # Get all participants
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT user_id FROM match_participants WHERE match_id = %s",
            (match_id,)
        )
        participants = [row['user_id'] for row in cur.fetchall()]
        cur.close()

        if len(participants) < 2:
            logger.warning(f"API /api/submit-result: Match {match_id} has fewer than 2 participants")
            return jsonify({"success": False, "message": "Match must have at least 2 participants"}), 400

        # Validate winner is a participant (if not draw)
        if not is_draw and winner_id and winner_id not in participants:
            logger.warning(f"API /api/submit-result: Winner {winner_id} not in participants for match {match_id}")
            return jsonify({"success": False, "message": "Winner must be a participant"}), 400

        # Assign points and insert match results
        results_created = []
        for uid in participants:
            if is_draw:
                points = 5
            elif uid == winner_id:
                points = 10
            else:
                points = 0

            logger.info(f"API /api/submit-result: match_id={match_id}, user_id={uid}, "
                       f"points_awarded={points}, is_draw={is_draw}")

            Leaderboard.insert_match_result(
                match_id=match_id,
                user_id=uid,
                points_awarded=points,
                admin_adjustment=0
            )
            results_created.append({"user_id": uid, "points_awarded": points})

        # Update match status to 'completed'
        Leaderboard.update_match_status(match_id, "completed")

        logger.info(f"API /api/submit-result: Successfully submitted results for match {match_id}")

        return jsonify({
            "success": True,
            "message": "Match result submitted successfully. Leaderboard updated automatically.",
            "match_id": match_id,
            "is_draw": is_draw,
            "winner_id": winner_id if not is_draw else None,
            "results": results_created
        })

    except Exception as e:
        logger.error(f"Failed to submit match result for match {match_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to submit match result: {str(e)}"
        }), 500


# ========================================
# API: ALL GAMES - GET ALL GAMES
# ========================================

@dashboard_bp.route("/api/games")
def api_all_games():
    """Return all game categories with logos and match counts."""
    try:
        games = GameCategory.get_all()
        match_counts = GameCategory.get_match_count_by_sport()
        
        # Build match count map
        count_map = {}
        for row in match_counts:
            count_map[row['sport_key']] = row['match_count']
        
        game_list = []
        for game in games:
            sport_key = game['name'].lower()
            game_list.append({
                "id": game['id'],
                "name": game['name'],
                "logo": game.get('logo', '') or '',
                "description": game.get('description', '') or '',
                "rules": game.get('rules', '') or '',
                "location_info": game.get('location_info', '') or '',
                "match_count": count_map.get(sport_key, 0),
                "display_order": game['display_order']
            })
        
        return jsonify({
            "success": True,
            "games": game_list,
            "total": len(game_list)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to load games: {str(e)}"
        }), 500


# ========================================
# API: GET ALL SPORTS CATEGORIES (with counts)
# ========================================

@dashboard_bp.route("/api/sports-categories")
def api_sports_categories():
    """Return all sports categories with venue counts and match counts.
    
    Response format:
    {
        "success": true,
        "sports": [
            {
                "id": 1,
                "name": "Cricket",
                "category": "Outdoor",
                "logo": "...",
                "description": "...",
                "venue_count": 8,
                "match_count": 12
            }
        ],
        "total": 24
    }
    """
    try:
        sports = GameCategory.get_all_with_counts()
        return jsonify({
            "success": True,
            "sports": sports,
            "total": len(sports)
        })
    except Exception as e:
        logger.error(f"Failed to load sports categories: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to load sports categories: {str(e)}"
        }), 500


# ========================================
# API: GET SINGLE SPORT FULL DETAILS
# ========================================

@dashboard_bp.route("/api/sport-detail/<int:sport_id>")
def api_sport_detail(sport_id):
    """Return full detailed information for a specific sport.
    
    Response includes:
    - All basic info (name, logo, category, description)
    - Extended details (players, equipment, duration, area, rules, tournaments, difficulty)
    - Venue count, match count, nearby venues, upcoming matches
    """
    try:
        sport = GameCategory.get_by_id(sport_id)
        if not sport:
            return jsonify({
                "success": False,
                "message": "Sport not found"
            }), 404
        
        # Get counts
        sport_name = sport['name']
        venue_count = GameCategory.get_venue_count_for_sport(sport_name)
        active_match_count = GameCategory.get_active_match_count(sport_name)
        
        # Get nearby venues for this sport
        venues = SportsVenue.get_by_sport(sport_name)
        nearby_venues = []
        for v in venues:
            nearby_venues.append({
                "id": v["id"],
                "name": v["name"],
                "address": v.get("address", "") or "",
                "rating": float(v["rating"]) if v.get("rating") else 0,
                "distance_km": float(v["distance_km"]) if v.get("distance_km") else 0,
                "available_slots": int(v["available_slots"]) if v.get("available_slots") else 0,
                "latitude": float(v["latitude"]) if v.get("latitude") else None,
                "longitude": float(v["longitude"]) if v.get("longitude") else None
            })
        
        # Get upcoming matches for this sport
        matches = Match.get_filtered(sport_name=sport_name, limit=5)
        upcoming_matches = []
        for m in matches:
            upcoming_matches.append({
                "id": m["id"],
                "sport_name": m["sport_name"],
                "venue_name": m["venue_name"],
                "match_date": str(m["match_date"]),
                "match_time": str(m["match_time"]),
                "max_players": m["max_players"],
                "player_count": m["player_count"],
                "creator_name": m["creator_name"]
            })
        
        return jsonify({
            "success": True,
            "sport": {
                "id": sport['id'],
                "name": sport['name'],
                "logo": sport.get('logo', '') or '',
                "description": sport.get('description', '') or '',
                "category": sport.get('category', '') or '',
                "num_players": sport.get('num_players', '') or '',
                "equipment": sport.get('equipment', '') or '',
                "match_duration": sport.get('match_duration', '') or '',
                "playing_area": sport.get('playing_area', '') or '',
                "basic_rules": sport.get('basic_rules', '') or '',
                "popular_tournaments": sport.get('popular_tournaments', '') or '',
                "difficulty_level": sport.get('difficulty_level', '') or '',
                "location_info": sport.get('location_info', '') or '',
                "venue_count": venue_count,
                "match_count": active_match_count,
                "nearby_venues": nearby_venues,
                "upcoming_matches": upcoming_matches
            }
        })
    except Exception as e:
        logger.error(f"Failed to load sport detail for {sport_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to load sport details: {str(e)}"
        }), 500


# ========================================
# API: GET SINGLE GAME DETAILS
# ========================================

@dashboard_bp.route("/api/game/<int:game_id>")
def api_game_details(game_id):
    """Return full details of a specific game category."""
    try:
        game = GameCategory.get_by_id(game_id)
        if not game:
            return jsonify({
                "success": False,
                "message": "Game not found"
            }), 404
        
        active_matches = GameCategory.get_active_match_count(game['name'])
        
        return jsonify({
            "success": True,
            "game": {
                "id": game['id'],
                "name": game['name'],
                "logo": game.get('logo', '') or '',
                "description": game.get('description', '') or '',
                "rules": game.get('rules', '') or '',
                "location_info": game.get('location_info', '') or '',
                "active_matches": active_matches
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to load game details: {str(e)}"
        }), 500


# ========================================
# API: NEARBY SPORTS VENUES
# ========================================

@dashboard_bp.route("/api/nearby-venues")
def api_nearby_venues():
    """Return all nearby sports venues as JSON.
    
    Supports optional 'sport' query parameter for filtering.
    Response: { "venues": [ ... ] }
    """
    sport = request.args.get("sport")
    
    try:
        if sport and sport.strip():
            venues = SportsVenue.get_by_sport(sport.strip())
        else:
            venues = SportsVenue.get_all()
        
        venue_list = []
        for v in venues:
            # Parse sport_types (stored as comma-separated string)
            sport_types = [s.strip() for s in v["sport_types"].split(",") if s.strip()]
            
            venue_list.append({
                "id": v["id"],
                "name": v["name"],
                "sport_types": sport_types,
                "address": v["address"] or "",
                "latitude": float(v["latitude"]),
                "longitude": float(v["longitude"]),
                "rating": float(v["rating"]),
                "available_slots": int(v["available_slots"]),
                "distance_km": float(v["distance_km"]),
                "image_url": v["image_url"] or ""
            })
        
        return jsonify({"venues": venue_list})
    
    except Exception as e:
        logger.error(f"Failed to fetch nearby venues: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch nearby venues: {str(e)}"
        }), 500


# ========================================
# API: ADMIN ADJUST MATCH RESULT
# ========================================

@dashboard_bp.route("/api/dashboard/analytics")
def api_dashboard_analytics():
    """Return analytics data for dashboard charts."""
    try:
        # Total counts
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM users")
        total_users = cur.fetchone()['cnt']
        cur.close()

        # Active users (users who joined at least one match)
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(DISTINCT user_id) as cnt FROM match_participants")
        active_users = cur.fetchone()['cnt']
        cur.close()

        # Total matches
        total_matches = Match.count_matches()

        # Matches today
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM matches WHERE match_date = CURDATE()")
        matches_today = cur.fetchone()['cnt']
        cur.close()

        # Total sports (from game_categories)
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM game_categories")
        total_sports = cur.fetchone()['cnt']
        cur.close()

        # Indoor vs Outdoor matches
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                SUM(CASE WHEN sport_type = 'indoor' THEN 1 ELSE 0 END) as indoor,
                SUM(CASE WHEN sport_type = 'outdoor' THEN 1 ELSE 0 END) as outdoor
            FROM matches
            WHERE status = 'open' OR status IS NULL
        """)
        row = cur.fetchone()
        indoor_count = row['indoor'] if row and row['indoor'] else 0
        outdoor_count = row['outdoor'] if row and row['outdoor'] else 0
        cur.close()

        # Nearby venues count
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM sports_venues")
        nearby_venues_count = cur.fetchone()['cnt']
        cur.close()

        # Top players (top 5)
        leaderboard = Leaderboard.get_dynamic_leaderboard()
        top_players = []
        for entry in leaderboard[:5]:
            top_players.append({
                'name': entry.get('name', ''),
                'total_points': entry.get('total_points', 0)
            })

        # Match activity by sport
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT sport_name, COUNT(*) as count
            FROM matches
            WHERE status = 'open' OR status IS NULL
            GROUP BY sport_name
            ORDER BY count DESC
            LIMIT 8
        """)
        sports_distribution = [{'sport': r['sport_name'], 'count': r['count']} for r in cur.fetchall()]
        cur.close()

        # Match activity for bar chart (by status)
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT status, COUNT(*) as count
            FROM matches
            GROUP BY status
        """)
        match_activity = [{'label': r['status'] or 'open', 'count': r['count']} for r in cur.fetchall()]
        cur.close()

        # Weekly trend (last 7 days)
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT match_date, COUNT(*) as count
            FROM matches
            WHERE match_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY match_date
            ORDER BY match_date ASC
        """)
        weekly_trend = [{'date': str(r['match_date']), 'count': r['count']} for r in cur.fetchall()]
        cur.close()

        return jsonify({
            'success': True,
            'analytics': {
                'total_users': total_users,
                'active_users': active_users,
                'total_matches': total_matches,
                'matches_today': matches_today,
                'total_sports': total_sports,
                'indoor_matches': indoor_count,
                'outdoor_matches': outdoor_count,
                'nearby_venues': nearby_venues_count,
                'top_players': top_players,
                'match_activity': match_activity,
                'sports_distribution': sports_distribution,
                'indoor_outdoor': {'indoor': indoor_count, 'outdoor': outdoor_count},
                'weekly_trend': weekly_trend
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch analytics: {str(e)}'
        }), 500


@dashboard_bp.route("/api/admin/adjust-result", methods=["POST"])
def api_admin_adjust_result():
    """Admin can adjust points in match_results (NOT directly edit leaderboard).
    
    Adds admin_adjustment to existing match_results records.
    Leaderboard updates automatically because it's query-based.
    """
    redirect_resp = login_required()
    if redirect_resp:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json() or request.form
    match_id = data.get("match_id")
    user_id = data.get("user_id")
    adjustment = data.get("adjustment")

    if not match_id or not user_id or adjustment is None:
        logger.warning("API /api/admin/adjust-result: Missing required fields")
        return jsonify({
            "success": False,
            "message": "match_id, user_id, and adjustment are required"
        }), 400

    try:
        match_id = int(match_id)
        user_id = int(user_id)
        adjustment = int(adjustment)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid request data types."}), 400

    try:
        # Check if match result exists for this user
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, points_awarded, admin_adjustment FROM match_results_new "
            "WHERE match_id = %s AND user_id = %s",
            (match_id, user_id)
        )
        existing = cur.fetchone()

        if not existing:
            logger.warning(f"API /api/admin/adjust-result: No result found for match {match_id}, user {user_id}")
            return jsonify({
                "success": False,
                "message": "No match result found for this user in this match"
            }), 404

        # Apply the adjustment
        cur.execute("""
            UPDATE match_results_new 
            SET admin_adjustment = admin_adjustment + %s
            WHERE id = %s
        """, (adjustment, existing['id']))
        mysql.connection.commit()

        # Fetch updated record
        cur.execute(
            "SELECT points_awarded, admin_adjustment FROM match_results_new WHERE id = %s",
            (existing['id'],)
        )
        updated = cur.fetchone()
        cur.close()

        final_points = updated['points_awarded'] + updated['admin_adjustment']

        logger.info(f"API /api/admin/adjust-result: match_id={match_id}, user_id={user_id}, "
                   f"adjustment={adjustment}, new_final_points={final_points}")

        return jsonify({
            "success": True,
            "message": f"Adjustment of {adjustment} points applied. Final points: {final_points}",
            "match_id": match_id,
            "user_id": user_id,
            "adjustment": adjustment,
            "previous_total": existing['points_awarded'] + existing['admin_adjustment'],
            "new_final_points": final_points
        })

    except Exception as e:
        logger.error(f"Failed to adjust match result: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to adjust match result: {str(e)}"
        }), 500


# ========================================
# API: ADD PLAYER POINTS (Admin/Captain)
# ========================================

@dashboard_bp.route("/api/admin/add-player-points", methods=["POST"])
def api_add_player_points():
    """Add points to a player directly (not from match). Admin/captain only."""
    redirect_resp = login_required()
    if redirect_resp:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json() or request.form
    user_id = data.get("user_id")
    points = data.get("points")
    reason = data.get("reason", "")

    if not user_id or not points or not reason:
        return jsonify({
            "success": False,
            "message": "user_id, points, and reason are required"
        }), 400

    try:
        user_id = int(user_id)
        points = int(points)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid data types."}), 400

    if points <= 0:
        return jsonify({"success": False, "message": "Points must be a positive number."}), 400

    try:
        Leaderboard.add_player_points(user_id, points, reason, session['user_id'])
        
        logger.info(f"API /api/admin/add-player-points: Added {points} points to user {user_id}. Reason: {reason}")
        
        return jsonify({
            "success": True,
            "message": f"{points} points added successfully!",
            "user_id": user_id,
            "points_added": points
        })
    except Exception as e:
        logger.error(f"Failed to add player points: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to add points: {str(e)}"
        }), 500


# ========================================
# API: ADJUST PLAYER POINTS (Admin/Captain)
# ========================================

@dashboard_bp.route("/api/admin/adjust-player-points", methods=["POST"])
def api_adjust_player_points():
    """Adjust player points (add or subtract). Admin/captain only."""
    redirect_resp = login_required()
    if redirect_resp:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json() or request.form
    user_id = data.get("user_id")
    delta = data.get("delta")
    reason = data.get("reason", "")

    if not user_id or delta is None or not reason:
        return jsonify({
            "success": False,
            "message": "user_id, delta, and reason are required"
        }), 400

    try:
        user_id = int(user_id)
        delta = int(delta)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid data types."}), 400

    if delta == 0:
        return jsonify({"success": False, "message": "Delta cannot be zero."}), 400

    try:
        Leaderboard.adjust_player_points(user_id, delta, reason, session['user_id'])
        
        logger.info(f"API /api/admin/adjust-player-points: Adjusted user {user_id} by {delta} points. Reason: {reason}")
        
        return jsonify({
            "success": True,
            "message": f"Points adjusted by {delta} successfully!",
            "user_id": user_id,
            "delta": delta
        })
    except Exception as e:
        logger.error(f"Failed to adjust player points: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to adjust points: {str(e)}"
        }), 500


# ========================================
# API: GET PLAYER POINT HISTORY
# ========================================

@dashboard_bp.route("/api/admin/player-point-history/<int:user_id>")
def api_player_point_history(user_id):
    """Get point history for a player."""
    redirect_resp = login_required()
    if redirect_resp:
        return jsonify({"error": "Not logged in"}), 401

    history = PointHistory.get_for_entity('player', user_id, limit=50)
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "history": history
    })
