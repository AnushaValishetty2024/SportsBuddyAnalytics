"""
Sports Buddy - Demo AI Assistant (Offline)
Provides intelligent responses without any external API calls.
"""

import re
import json
import random
from datetime import datetime, date
from flask import request, jsonify, session
from models import mysql, Match, Leaderboard, SportsVenue, GameCategory


# Initialize knowledge base
def init_knowledge_base():
    from static.data.sports_knowledge import SPORTS_DETAILS, PLATFORM_HELP, MATCH_SUGGESTIONS
    return SPORTS_DETAILS, PLATFORM_HELP, MATCH_SUGGESTIONS


def detect_intent(message):
    """
    Detect user intent from message using keyword matching.
    Returns (intent, confidence, entities)
    """
    msg = message.lower().strip()

    # Greeting patterns
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy']
    if any(g in msg for g in greetings):
        return 'greeting', 0.9, {}

    # Help / capabilities
    if any(k in msg for k in ['help', 'what can you do', 'capabilities', 'features']):
        return 'help', 0.9, {}

    # Sports rules queries
    sports = ['cricket', 'football', 'volleyball', 'basketball', 'badminton', 'tennis',
              'table tennis', 'hockey', 'kabaddi', 'chess', 'athletics', 'cycling',
              'rugby', 'baseball', 'golf', 'archery']
    rule_keywords = ['rule', 'rules', 'how to play', 'how does', 'explain', 'tell me about', 'basics']
    if any(s in msg for s in sports) and any(k in msg for k in rule_keywords):
        detected_sport = next((s for s in sports if s in msg), None)
        return 'sport_rules', 0.8, {'sport': detected_sport}

    # Sports details queries (rules, scoring, equipment, etc.)
    detail_keywords = ['scoring', 'score', 'equipment', 'gear', 'duration', 'time',
                       'players', 'team size', 'points', 'tournament', 'competition',
                       'tips', 'beginner', 'safety', 'introduction']
    if any(s in msg for s in sports) and any(k in msg for k in detail_keywords):
        detected_sport = next((s for s in sports if s in msg), None)
        return 'sport_details', 0.7, {'sport': detected_sport}

    # Platform-related queries
    platform_keywords = {
        'create match': 'create_match',
        'create a match': 'create_match',
        'how to create': 'create_match',
        'start a match': 'create_match',
        'join match': 'join_match',
        'join a match': 'join_match',
        'how to join': 'join_match',
        'leaderboard': 'leaderboard',
        'ranking': 'leaderboard',
        'rankings': 'leaderboard',
        'points': 'points',
        'scoring system': 'points',
        'how points': 'points',
        'nearby venues': 'nearby_venues',
        'venues': 'nearby_venues',
        'near me': 'nearby_venues',
        'find venue': 'nearby_venues',
        'improve ranking': 'improve_ranking',
        'improve my rank': 'improve_ranking',
        'climb ranks': 'improve_ranking',
        'badges': 'badges',
        'badge': 'badges',
        'achievements': 'badges',
        'tournament': 'tournaments',
        'tournaments': 'tournaments'
    }

    for keyword, intent in platform_keywords.items():
        if keyword in msg:
            return intent, 0.8, {}

    # Match suggestions
    suggestion_keywords = ['want to play', 'i want to', 'suggest', 'recommendation', 'recommend',
                           'should i play', 'looking for']
    if any(k in msg for k in suggestion_keywords) and any(s in msg for s in sports):
        detected_sport = next((s for s in sports if s in msg), None)
        return 'match_suggestion', 0.7, {'sport': detected_sport}

    # Leaderboard queries
    if any(k in msg for k in ['leaderboard', 'ranking', 'rank', 'top player', 'number 1', 'rank 1']):
        if any(k in msg for k in ['who is', 'who\'s', 'top', 'best', 'rank 1', 'number 1']):
            return 'leaderboard_top', 0.8, {}
        return 'leaderboard_general', 0.7, {}

    # Match analysis
    analysis_keywords = ['analyze', 'analysis', 'summary', 'today', 'matches today', 'match today']
    if any(k in msg for k in analysis_keywords) and any(k in msg for k in ['match', 'matches', 'game']):
        return 'match_analysis', 0.7, {}

    # General sport mention (no specific query)
    if any(s in msg for s in sports):
        detected_sport = next((s for s in sports if s in msg), None)
        return 'sport_mention', 0.5, {'sport': detected_sport}

    # Fallback
    return 'unknown', 0.3, {}


def get_greeting_response():
    """Return a natural greeting response."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning! I'm your Sports Buddy AI assistant. How can I help you today? You can ask me about sports rules, matches, tournaments, or how to use the platform."
    elif hour < 17:
        return "Good afternoon! I'm your Sports Buddy AI assistant. How can I help you today? You can ask me about sports rules, matches, tournaments, or how to use the platform."
    else:
        return "Good evening! I'm your Sports Buddy AI assistant. How can I help you today? You can ask me about sports rules, matches, tournaments, or how to use the platform."


def get_help_response():
    """Return help/capabilities response."""
    return (
        "I'm your Sports Buddy AI assistant. I can help you with:\n\n"
        "• Sports Rules & Information - Ask about any sport: cricket, football, badminton, basketball, tennis, volleyball, table tennis, hockey, kabaddi, chess, athletics, cycling, rugby, baseball, golf, or archery\n"
        "• Platform Help - Creating matches, joining matches, leaderboard, points, venues, badges, tournaments\n"
        "• Match Suggestions - Tell me which sport you want to play and I'll suggest match details\n"
        "• Leaderboard Insights - Ask about top players or ranking\n"
        "• Match Analysis - Get summaries of today's matches\n\n"
        "Just type your question naturally!"
    )


def get_sport_rules_response(sport, knowledge_base):
    """Return sport rules in a formatted way."""
    sport_lower = sport.lower().strip()
    if sport_lower not in knowledge_base:
        return f"I don't have detailed information about {sport} yet. Try asking about another sport."

    data = knowledge_base[sport_lower]
    response = f"## {sport.title()} - Rules & Overview\n\n"
    response += f"**Introduction:** {data['introduction']}\n\n"
    response += f"**Basic Rules:**\n{data['basic_rules']}\n\n"
    response += f"**Number of Players:** {data['number_of_players']}\n\n"
    response += f"**Equipment:** {data['equipment']}\n\n"
    response += f"**Match Duration:** {data['match_duration']}\n\n"
    response += f"**Scoring System:** {data['scoring_system']}\n\n"
    response += f"**Tournament Format:** {data['tournament_format']}\n\n"
    response += f"**Popular Competitions:** {data['popular_competitions']}\n\n"
    response += f"**Tips for Beginners:** {data['tips_for_beginners']}\n\n"
    response += f"**Safety Guidelines:** {data['safety_guidelines']}"
    return response


def get_sport_details_response(sport, detail_type, knowledge_base):
    """Return specific sport detail."""
    sport_lower = sport.lower().strip()
    if sport_lower not in knowledge_base:
        return f"I don't have information about {sport} yet."

    data = knowledge_base[sport_lower]
    field_map = {
        'scoring': 'scoring_system',
        'score': 'scoring_system',
        'equipment': 'equipment',
        'gear': 'equipment',
        'duration': 'match_duration',
        'time': 'match_duration',
        'players': 'number_of_players',
        'team size': 'number_of_players',
        'points': 'scoring_system',
        'tournament': 'tournament_format',
        'competition': 'popular_competitions',
        'tips': 'tips_for_beginners',
        'beginner': 'tips_for_beginners',
        'safety': 'safety_guidelines',
        'introduction': 'introduction',
        'rules': 'basic_rules'
    }

    field = field_map.get(detail_type.lower())
    if not field:
        field = 'basic_rules'

    return f"**{sport.title()} - {detail_type.title()}:**\n\n{data[field]}"


def get_platform_help(help_key, platform_help):
    """Return platform help article."""
    if help_key in platform_help:
        return platform_help[help_key]['response']
    return None


def get_match_suggestion(sport, suggestions):
    """Return match suggestions for a sport."""
    sport_lower = sport.lower().strip()
    if sport_lower not in suggestions:
        return f"I don't have specific match suggestions for {sport} yet. Try asking for another sport."

    sug = suggestions[sport_lower]
    response = f"Recommended Sport:\n{sug['sport']}\n\n"
    response += f"Suggested Match Type:\n{sug['match_type']}\n\n"
    response += f"Recommended Players:\n{sug['players']}\n\n"
    response += f"Suggested Venue:\n{sug['venue']}\n\n"
    response += f"Recommended Duration:\n{sug['duration']}\n\n"
    response += f"Required Equipment:\n{sug['equipment']}"
    return response


def get_leaderboard_response(leaderboard_data, top=False):
    """Return leaderboard response."""
    if not leaderboard_data or len(leaderboard_data) == 0:
        return "Leaderboard data is currently unavailable. Please check back later."

    if top:
        top_player = leaderboard_data[0]
        response = f"Current Rank #1:\n{top_player['name']}\n\n"
        response += f"Points:\n{top_player['total_points']}\n\n"
        response += f"Wins:\n{top_player['wins']}\n\n"
        response += f"Win Rate:\n{round(top_player['wins']/top_player['matches_played']*100) if top_player['matches_played']>0 else 0}%"
        return response

    # General leaderboard
    response = "Leaderboard Summary:\n\n"
    response += f"Total Players: {len(leaderboard_data)}\n\n"
    response += "Top 5 Players:\n"
    for i, player in enumerate(leaderboard_data[:5], 1):
        response += f"{i}. {player['name']} - {player['total_points']} points ({player['wins']} wins)\n"
    return response


def get_match_analysis_response():
    """Return match analysis for today."""
    try:
        cur = mysql.connection.cursor()
        today_str = date.today().isoformat()

        # Count matches today
        cur.execute("""
            SELECT COUNT(*) as cnt FROM matches
            WHERE match_date = %s
        """, (today_str,))
        row = cur.fetchone()
        total_matches = row['cnt'] if row else 0

        # Count open matches
        cur.execute("""
            SELECT COUNT(*) as cnt FROM matches
            WHERE match_date = %s AND (status = 'open' OR status IS NULL)
        """, (today_str,))
        row = cur.fetchone()
        open_matches = row['cnt'] if row else 0

        # Get popular sport
        cur.execute("""
            SELECT sport_name, COUNT(*) as cnt FROM matches
            WHERE match_date = %s
            GROUP BY sport_name
            ORDER BY cnt DESC
            LIMIT 1
        """, (today_str,))
        row = cur.fetchone()
        popular_sport = row['sport_name'] if row else "N/A"

        # Get highest participation sport
        cur.execute("""
            SELECT m.sport_name, COUNT(mp.user_id) as participants
            FROM matches m
            LEFT JOIN match_participants mp ON m.id = mp.match_id
            WHERE m.match_date = %s
            GROUP BY m.sport_name
            ORDER BY participants DESC
            LIMIT 1
        """, (today_str,))
        row = cur.fetchone()
        highest_participation = row['sport_name'] if row else "N/A"

        # Count total slots remaining for open matches
        cur.execute("""
            SELECT SUM(m.max_players - COUNT(mp.user_id)) as remaining
            FROM matches m
            LEFT JOIN match_participants mp ON m.id = mp.match_id
            WHERE m.match_date = %s AND (m.status = 'open' OR m.status IS NULL)
            GROUP BY m.id
        """, (today_str,))
        rows = cur.fetchall()
        remaining_slots = sum(r['remaining'] for r in rows if r['remaining'])

        # Count evening matches (after 4 PM)
        cur.execute("""
            SELECT COUNT(*) as cnt FROM matches
            WHERE match_date = %s AND match_time >= '16:00:00'
        """, (today_str,))
        row = cur.fetchone()
        evening_matches = row['cnt'] if row else 0

        cur.close()

        response = f"Today's Summary:\n\n"
        response += f"{total_matches} matches scheduled.\n\n"
        response += f"Most popular sport:\n{popular_sport}\n\n"
        response += f"Highest participation:\n{highest_participation}\n\n"
        response += f"Remaining slots:\n{remaining_slots}\n\n"
        response += f"Upcoming evening matches:\n{evening_matches}"
        return response

    except Exception:
        return "I'm currently unable to access match data. Please try again later."


def get_leaderboard_data(top_n=10):
    """Get leaderboard data from DB."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.id as user_id, u.name,
                   COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) as match_points,
                   COALESCE(u.points, 0) as manual_points,
                   COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) + COALESCE(u.points, 0) as total_points,
                   COUNT(DISTINCT mr.match_id) as matches_played,
                   COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) >= 10 THEN mr.match_id END) as wins,
                   COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 0 AND mr.match_id IS NOT NULL THEN mr.match_id END) as losses,
                   COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 5 AND mr.match_id IS NOT NULL THEN mr.match_id END) as draws
            FROM users u
            LEFT JOIN match_results_new mr ON u.id = mr.user_id
            GROUP BY u.id, u.name
            ORDER BY total_points DESC, wins DESC, u.name ASC
            LIMIT %s
        """, (top_n,))
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception:
        return []


def get_unknown_response():
    """Return response for unknown queries."""
    return (
        "I don't have information about that topic yet. "
        "Try asking about sports rules, matches, tournaments, rankings, venues, or platform features."
    )


# Suggested questions for the UI
SUGGESTED_QUESTIONS = [
    "Rules of Cricket",
    "Explain Badminton Scoring",
    "How to Create a Match",
    "Improve My Ranking",
    "Nearby Sports Venues",
    "Analyze Leaderboard",
    "Tournament Rules",
    "Rules of Football",
    "How to Join a Match",
    "Best Equipment for Tennis"
]


def get_suggested_questions():
    """Return list of suggested questions."""
    return SUGGESTED_QUESTIONS


def process_message(message, conversation_history=None):
    """
    Main entry point for processing user messages.
    Returns a response string.
    """
    from static.data.sports_knowledge import SPORTS_DETAILS, PLATFORM_HELP, MATCH_SUGGESTIONS

    knowledge_base = SPORTS_DETAILS
    platform_help = PLATFORM_HELP
    match_suggestions = MATCH_SUGGESTIONS

    # Detect intent
    intent, confidence, entities = detect_intent(message)

    # Handle conversation memory - if very short message and we have context
    # could reference previous sport mentioned (simplified version)
    if intent == 'unknown' and conversation_history and len(conversation_history) > 0:
        # Check if previous messages mentioned a sport
        last_user_msg = ''
        for msg in reversed(conversation_history):
            if msg.get('role') == 'user':
                last_user_msg = msg.get('content', '').lower()
                break
        if last_user_msg:
            sports = ['cricket', 'football', 'volleyball', 'basketball', 'badminton', 'tennis',
                      'table tennis', 'hockey', 'kabaddi', 'chess', 'athletics', 'cycling',
                      'rugby', 'baseball', 'golf', 'archery']
            for s in sports:
                if s in last_user_msg:
                    entities['sport'] = s
                    intent = 'sport_details'
                    confidence = 0.5
                    break

    # Route to appropriate handler
    if intent == 'greeting':
        return get_greeting_response()

    elif intent == 'help':
        return get_help_response()

    elif intent == 'sport_rules':
        sport = entities.get('sport')
        if not sport:
            # Try to extract from original message
            sports = ['cricket', 'football', 'volleyball', 'basketball', 'badminton', 'tennis',
                      'table tennis', 'hockey', 'kabaddi', 'chess', 'athletics', 'cycling',
                      'rugby', 'baseball', 'golf', 'archery']
            for s in sports:
                if s in message.lower():
                    sport = s
                    break
        if sport:
            return get_sport_rules_response(sport, knowledge_base)
        return get_unknown_response()

    elif intent == 'sport_details':
        sport = entities.get('sport')
        if sport:
            # Find what detail they want (basic default to rules)
            detail_type = 'rules'
            for key in ['scoring', 'equipment', 'duration', 'players', 'points', 'tournament',
                       'competition', 'tips', 'safety', 'introduction']:
                if key in message.lower():
                    detail_type = key
                    break
            return get_sport_details_response(sport, detail_type, knowledge_base)
        return get_unknown_response()

    elif intent == 'sport_mention':
        sport = entities.get('sport')
        if sport:
            return get_sport_rules_response(sport, knowledge_base)
        return get_unknown_response()

    elif intent in platform_help:
        response = get_platform_help(intent, platform_help)
        if response:
            return response
        return get_unknown_response()

    elif intent == 'match_suggestion':
        sport = entities.get('sport')
        if sport:
            return get_match_suggestion(sport, match_suggestions)
        return get_unknown_response()

    elif intent == 'leaderboard_top':
        data = get_leaderboard_data(top_n=1)
        return get_leaderboard_response(data, top=True)

    elif intent == 'leaderboard_general':
        data = get_leaderboard_data(top_n=10)
        return get_leaderboard_response(data, top=False)

    elif intent == 'match_analysis':
        return get_match_analysis_response()

    else:
        return get_unknown_response()
