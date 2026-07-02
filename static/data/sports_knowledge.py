"""
Sports Buddy - Demo AI Assistant
Offline knowledge base and intelligent response system.
"""

# Knowledge base structure: sport name -> details
SPORTS_DETAILS = {}

# Platform help articles
PLATFORM_HELP = {
    "create_match": {
        "title": "How to Create a Match",
        "response": (
            "To create a match on Sports Buddy:\n\n"
            "1. Go to your Dashboard or Matches page\n"
            "2. Click 'Create Match' button\n"
            "3. Select the sport you want to play\n"
            "4. Choose date, time, and venue\n"
            "5. Set max players and skill level\n"
            "6. Add any additional details\n"
            "7. Click 'Create' to publish the match\n\n"
            "Your match will appear in the listings and other players can join."
        )
    },
    "join_match": {
        "title": "How to Join a Match",
        "response": (
            "To join a match on Sports Buddy:\n\n"
            "1. Browse available matches from the Dashboard or Matches page\n"
            "2. Use filters to find matches by sport, location, or skill level\n"
            "3. Click on a match to view details\n"
            "4. Click the 'Join' button\n"
            "5. Confirm your participation\n\n"
            "You'll receive a notification when the match creator accepts your request."
        )
    },
    "leaderboard": {
        "title": "How the Leaderboard Works",
        "response": (
            "The Sports Buddy leaderboard ranks players based on their performance:\n\n"
            "• Points are awarded after each match (win = 10 points, draw = 5 points)\n"
            "• Rankings update automatically when match results are recorded\n"
            "• Your rank is determined by total points, then by wins\n"
            "• You can view the leaderboard from the 'Leaderboard' page\n"
            "• Filter by sport to see rankings for specific games\n\n"
            "Keep playing to climb the ranks!"
        )
    },
    "points": {
        "title": "How Points Are Calculated",
        "response": (
            "Points on Sports Buddy are calculated as follows:\n\n"
            "• Win: 10 points\n"
            "• Draw: 5 points\n"
            "• Loss: 0 points\n"
            "• Manual adjustments by admins may apply\n\n"
            "Your total points = sum of all match points + any manual adjustments."
        )
    },
    "nearby_venues": {
        "title": "Finding Nearby Sports Venues",
        "response": (
            "To find nearby sports venues:\n\n"
            "1. Go to the 'Discover' or 'Nearby Venues' section\n"
            "2. The map shows all venues near your location\n"
            "3. You can filter by sport type\n"
            "4. Click on any venue for details:\n"
            "   - Available slots\n"
            "   - Rating\n"
            "   - Supported sports\n"
            "   - Distance from you\n\n"
            "Venues are ordered by distance to help you find the closest options."
        )
    },
    "improve_ranking": {
        "title": "How to Improve Your Ranking",
        "response": (
            "To improve your ranking on Sports Buddy:\n\n"
            "• Play more matches and win consistently\n"
            "• Complete matches you've joined (no-shows don't earn points)\n"
            "• Challenge higher-ranked players\n"
            "• Maintain good sportsmanship\n"
            "• Join tournaments for bonus points\n\n"
            "Remember: Every win adds 10 points to your total. Stay active!"
        )
    },
    "badges": {
        "title": "How Badges Work",
        "response": (
            "Badges on Sports Buddy recognize your achievements:\n\n"
            "• Earned automatically based on your activity\n"
            "• Examples: 'First Match', 'Tournament Winner', 'Centurion'\n"
            "• Displayed on your profile\n"
            "• Cannot be purchased - only earned through play\n\n"
            "Check your profile to see all earned badges."
        )
    },
    "tournaments": {
        "title": "How Tournaments Work",
        "response": (
            "Sports Buddy tournaments offer competitive play:\n\n"
            "• admins organize and publish tournaments\n"
            "• Register your team or join as an individual\n"
            "• Follow the tournament bracket or round-robin format\n"
            "• Win matches to advance\n"
            "• Final standings determine rankings and prizes\n\n"
            "Watch the announcements page for upcoming tournaments."
        )
    }
}

SPORTS_DETAILS = {
    "cricket": {
        "introduction": "Cricket is a bat-and-ball game played between two teams of eleven players on a cricket field.",
        "basic_rules": "Two teams take turns to bat and bowl. The batting team scores runs by hitting the ball and running between wickets. The bowling team tries to get batsmen out.",
        "number_of_players": "11 per side (22 total)",
        "equipment": "Bat, ball, wickets, pads, gloves, helmet",
        "match_duration": "3-8 hours depending on format",
        "scoring_system": "Runs scored by running or boundaries. 1, 4, or 6 runs per hit. Team with most runs wins.",
        "tournament_format": "Round-robin, knockout, or league formats. Common formats: Test (5 days), ODI (50 overs), T20 (20 overs)",
        "popular_competitions": "ICC Cricket World Cup, IPL, T20 World Cup, Ashes, Champions Trophy",
        "tips_for_beginners": "Start with basic batting and bowling techniques. Practice catching and fielding. Learn the rules of LBW and no-balls.",
        "safety_guidelines": "Always wear protective gear when batting (pads, gloves, helmet). Stay hydrated in hot weather. Warm up before playing to avoid injuries."
    },
    "football": {
        "introduction": "Football (soccer) is a team sport played between two teams of eleven players with a spherical ball.",
        "basic_rules": "Players use feet to kick the ball into the opponent's goal. Only goalkeepers can use hands within their penalty area. The team with more goals wins.",
        "number_of_players": "11 per side (22 total)",
        "equipment": "Football, shin guards, cleats, team jersey, goalkeeper gloves",
        "match_duration": "90 minutes (two 45-minute halves)",
        "scoring_system": "1 goal = 1 point. Team with most goals wins. Draw possible if scores equal.",
        "tournament_format": "League, knockout, or group stage followed by knockout. Includes extra time and penalties if needed.",
        "popular_competitions": "FIFA World Cup, UEFA Champions League, Premier League, La Liga, ISL",
        "tips_for_beginners": "Practice dribbling, passing, and shooting. Improve stamina with cardio exercises. Watch professional matches to understand tactics.",
        "safety_guidelines": "Wear proper cleats for traction. Use shin guards to protect legs. Avoid aggressive tackles - focus on fair play."
    },
    "volleyball": {
        "introduction": "Volleyball is a team sport where two teams of six players hit a ball over a net.",
        "basic_rules": "Teams hit the ball over the net in up to 3 touches. Ball must not touch the ground on your side. Points scored when ball lands on opponent's court.",
        "number_of_players": "6 per side (12 total)",
        "equipment": "Volleyball, knee pads, court shoes, net, antennae",
        "match_duration": "60-90 minutes (best of 3 or 5 sets)",
        "scoring_system": "Rally point scoring. First team to 25 points wins a set (must win by 2). Best of 3 or 5 sets wins match.",
        "tournament_format": "Pool play followed by knockout. Sets played to 25 points, 5th set to 15.",
        "popular_competitions": "Olympics, FIVB World Championship, AVP (beach), NCAA Volleyball",
        "tips_for_beginners": "Master the bump, set, and spike techniques. Practice serving and passing. Communication with teammates is essential.",
        "safety_guidelines": "Warm up shoulders and knees before playing. Learn proper falling technique. Use knee pads for diving."
    },
    "basketball": {
        "introduction": "Basketball is a team sport played with a ball and hoop, where two teams of five players try to score points.",
        "basic_rules": "Players dribble the ball while moving and score by shooting through the opponent's hoop. fouls result in free throws.",
        "number_of_players": "5 per side (10 total on court)",
        "equipment": "Basketball, hoop, backboard, basketball shoes, athletic wear",
        "match_duration": "40-48 minutes (NBA: 48 min, FIBA: 40 min, college: 40 min)",
        "scoring_system": "Field goal = 2 points, 3-pointer (behind arc) = 3 points, Free throw = 1 point. Most points wins.",
        "tournament_format": "Group stage or round-robin, then single elimination. Quarters, semi-finals, finals.",
        "popular_competitions": "NBA, FIBA World Cup, Olympics, EuroLeague, NCAA March Madness",
        "tips_for_beginners": "Practice dribbling with both hands. Work on layups and basic shooting. Learn the triple threat position.",
        "safety_guidelines": "Wear proper basketball shoes with ankle support. Warm up thoroughly to prevent ACL injuries. Stay aware of other players."
    },
    "badminton": {
        "introduction": "Badminton is a racquet sport played using racquets to hit a shuttlecock across a net.",
        "basic_rules": "Players hit the shuttlecock over the net. It must not touch the ground on your side. You can hit only once before crossing the net (except in doubles).",
        "number_of_players": "Singles: 2, Doubles: 4",
        "equipment": "Racket, shuttlecock, court shoes, sportswear, net",
        "match_duration": "30-60 minutes",
        "scoring_system": "Best of 3 games to 21 points. Must win by 2 points. Cap at 30 points. Rally point scoring.",
        "tournament_format": "Single elimination or round-robin pools. Best of 3 games.",
        "popular_competitions": "Olympics, BWF World Championships, All England Open, Thomas Cup",
        "tips_for_beginners": "Learn proper grip and basic strokes (forehand/backhand). Practice footwork and court movement. Start with long clears and drops.",
        "safety_guidelines": "Warm up arms and shoulders. Use proper footwear for quick movements. Avoid overreaching to prevent muscle strains."
    },
    "tennis": {
        "introduction": "Tennis is a racket sport played individually against a single opponent or between two teams of two players.",
        "basic_rules": "Players use a racket to hit a ball over the net into the opponent's court. Score points by making the ball land in bounds without being returned.",
        "number_of_players": "Singles: 2, Doubles: 4",
        "equipment": "Tennis racket, tennis balls, tennis shoes, athletic wear, net",
        "match_duration": "60-120 minutes",
        "scoring_system": "Points: Love (0), 15, 30, 40, Game. Need to win by 2 games. Sets to 6 games (tiebreak at 6-6). Best of 3 or 5 sets.",
        "tournament_format": "Knockout or knockout with seeding. Best of 3 or 5 sets. Tiebreaks used at 6-6 in sets except final set (varies).",
        "popular_competitions": "Grand Slams (Australian Open, French Open, Wimbledon, US Open), ATP/WTA Tours, Davis Cup",
        "tips_for_beginners": "Start with basic forehand and backhand technique. Practice serving consistently. Work on footwork and positioning.",
        "safety_guidelines": "Warm up properly to avoid tennis elbow. Use proper tennis shoes for lateral movement. Stay hydrated during matches."
    },
    "table tennis": {
        "introduction": "Table tennis is a racket sport played on a table with a lightweight hollow ball.",
        "basic_rules": "Players hit the ball with a racket so it passes over the net and bounces on opponent's side. Ball must bounce once on each side.",
        "number_of_players": "Singles: 2, Doubles: 4",
        "equipment": "Table tennis racket, balls, table, net",
        "match_duration": "30-60 minutes",
        "scoring_system": "Best of 5 or 7 games to 11 points. Must win by 2. Serve alternates every 2 points.",
        "tournament_format": "Single elimination or team matches. Individual and doubles events.",
        "popular_competitions": "Olympics, World Table Tennis Championships, ITTF World Tour",
        "tips_for_beginners": "Master the basic grip and forehand drive. Practice serves short and long. Focus on consistency over power.",
        "safety_guidelines": "Ensure adequate space around the table. Play in a well-lit area. The lightweight ball can travel fast - stay alert."
    },
    "hockey": {
        "introduction": "Field hockey is a team sport played on grass or turf with sticks and a ball.",
        "basic_rules": "Players use sticks to hit a small hard ball into the opponent's goal. Only the flat side of the stick can be used. Eleven players per side.",
        "number_of_players": "11 per side (22 total)",
        "equipment": "Hockey stick, ball, shin guards, mouthguard, goalkeeper gear",
        "match_duration": "70 minutes (two 35-minute halves)",
        "scoring_system": "1 goal = 1 point. Team with most goals wins. If tied, extra time or shootout may be used.",
        "tournament_format": "Pool play followed by classification matches and knockout stages.",
        "popular_competitions": "Olympics, Hockey World Cup, Euro Hockey League, FIH Pro League",
        "tips_for_beginners": "Learn to dribble and pass with the stick. Practice hitting the ball accurately. Work on positioning and teamwork.",
        "safety_guidelines": "Always wear shin guards and mouthguard. Keep the stick low to avoid head injuries. Maintain safe distance from opponents."
    },
    "kabaddi": {
        "introduction": "Kabaddi is a contact team sport played between two teams of seven players.",
        "basic_rules": "Raider enters opponent's half and must tag defenders while holding breath and chanting 'kabaddi'. Returns to half without being tackled.",
        "number_of_players": "7 per side (14 total on court)",
        "equipment": "Knee pads, sportswear, mat or grass field",
        "match_duration": "40 minutes (two 20-minute halves)",
        "scoring_system": "1 point for each successful raid. Bonus points for crossing bonus line. All out = extra points.",
        "tournament_format": "Single or double round-robin followed by playoffs and final.",
        "popular_competitions": "Pro Kabaddi League, Kabaddi World Cup, Asian Games",
        "tips_for_beginners": "Develop breath-holding capacity (kabaddi chant). Practice quick raids and defensive tackles. Build footwork and agility.",
        "safety_guidelines": "Warm up thoroughly before matches. Learn proper tackling technique to avoid injury. Play on soft surfaces when possible."
    },
    "chess": {
        "introduction": "Chess is a two-player strategy board game played on a checkered board with specially designed pieces.",
        "basic_rules": "Each player moves pieces according to specific rules. Goal is to checkmate opponent's king (king in unavoidable capture).",
        "number_of_players": 2,
        "equipment": "Chess board, chess pieces, timer (optional)",
        "match_duration": "30-120 minutes (blitz: 5 min, rapid: 15 min, classical: 90+ min)",
        "scoring_system": "Win = 1 point, Draw = 0.5 points, Loss = 0 points. Tournament scoring may use tiebreaks.",
        "tournament_format": "Swiss system, round-robin, or knockout. Time controls define format.",
        "popular_competitions": "World Chess Championship, Candidates Tournament, Chess Olympiad, Tata Steel Masters",
        "tips_for_beginners": "Learn piece movements and basic tactics (pins, forks, skewers). Practice opening principles. Study endgame fundamentals.",
        "safety_guidelines": "Take regular breaks during long games. Avoid eye strain by focusing on distant objects periodically. Stay hydrated."
    },
    "athletics": {
        "introduction": "Athletics (track and field) includes a variety of running, walking, jumping, and throwing events.",
        "basic_rules": "Athletes compete in individual events. Runners race around a track, jumpers attempt height/distance, throwers launch implements.",
        "number_of_players": "Individual or team scoring events",
        "equipment": "Running shoes, event-specific gear (javelin, shot, hurdles), athletic wear",
        "match_duration": "2-4 hours (depending on events)",
        "scoring_system": "Each event scored individually (time, height, distance). Team scores = sum of individual points.",
        "tournament_format": "Heats, semifinals, finals for track events. Qualifying rounds for field events. Point-based team scoring.",
        "popular_competitions": "Olympics, World Athletics Championships, Diamond League, Commonwealth Games",
        "tips_for_beginners": "Start with basic running technique and conditioning. Focus on one or two events initially. Work with a coach for proper form.",
        "safety_guidelines": "Warm up extensively before running. Use proper footwear for each event. Stay hydrated and avoid overtraining."
    },
    "cycling": {
        "introduction": "Cycling involves riding bicycles for recreation, transport, or competition on roads, tracks, or trails.",
        "basic_rules": "Cyclists race against time or other riders. Drafting allowed in most formats. Must complete set distance or laps.",
        "number_of_players": "Individual or group races",
        "equipment": "Bicycle, helmet, cycling shoes, sportswear, gloves",
        "match_duration": "1-6 hours depending on race type",
        "scoring_system": "First to finish wins. Time trials = fastest time. Stage races = cumulative time or points.",
        "tournament_format": "One-day races, stage races, time trials, criteriums, track events.",
        "popular_competitions": "Tour de France, Giro d'Italia, Vuelta a Espana, Olympics Track Cycling, UCI World Championships",
        "tips_for_beginners": "Focus on proper bike fit and pedaling technique. Practice riding in groups. Build endurance gradually.",
        "safety_guidelines": "Always wear a helmet. Use hand signals for turns. Ride defensively and obey traffic rules."
    },
    "rugby": {
        "introduction": "Rugby is a contact team sport where players carry, pass, or kick a ball to score tries.",
        "basic_rules": "Teams advance by running with the ball or kicking it forward. Passes must be lateral or backward. Tackling allowed to stop ball carrier.",
        "number_of_players": "Rugby Union: 15 per side, Rugby Sevens: 7 per side",
        "equipment": "Rugby ball, cleats, mouthguard, scrum cap (optional), team jersey",
        "match_duration": "Union: 80 minutes (2x40), Sevens: 14 minutes (2x7)",
        "scoring_system": "Try = 5 points, Conversion = 2 points, Penalty = 3 points, Drop goal = 3 points. Most points wins.",
        "tournament_format": "League or knockout. Rugby World Cup: pool stage then knockout.",
        "popular_competitions": "Rugby World Cup, Six Nations, Super Rugby, Rugby Championship, HSBC Sevens Series",
        "tips_for_beginners": "Learn passing and basic running with the ball. Understand rucking and mauling basics. Improve fitness and tackling technique.",
        "safety_guidelines": "Master proper tackling technique (head to the side, never in front). Wear mouthguard. Strengthen neck muscles for impact."
    },
    "baseball": {
        "introduction": "Baseball is a bat-and-ball game played between two teams of nine players.",
        "basic_rules": "Pitcher throws ball, batter hits and runs bases. Fielding team tries to get batters out by catching balls or tagging bases.",
        "number_of_players": "9 per side (18 total on field)",
        "equipment": "Bat, ball, glove, helmet, cleats, team uniform",
        "match_duration": "2-3 hours (9 innings)",
        "scoring_system": "Run = 1 point. Team scores when runner circles all bases and reaches home. Most runs wins.",
        "tournament_format": "Regular season followed by playoffs (wildcard, division series, championship, World Series).",
        "popular_competitions": "MLB World Series, Olympics, World Baseball Classic, Little League World Series",
        "tips_for_beginners": "Practice batting stance and swing mechanics. Learn fielding positions and throws. Understand strike zone and basic pitch types.",
        "safety_guidelines": "Wear batting helmet when on base. Use proper glove technique. Stay alert for batted balls."
    },
    "golf": {
        "introduction": "Golf is a club-and-ball sport where players use clubs to hit balls into holes on a course.",
        "basic_rules": "Play the ball as it lies. Complete each hole in as few strokes as possible. Lowest total strokes wins.",
        "number_of_players": "1-4 typically (professional: individual or team events)",
        "equipment": "Golf clubs (14 max), golf balls, tees, golf shoes, golf bag",
        "match_duration": "3-5 hours (18 holes)",
        "scoring_system": "Stroke play = total strokes. Match play = holes won/lost. Handicap system adjusts for skill levels.",
        "tournament_format": "Stroke play (4 rounds) or match play. Cut after 2 rounds to reduce field size.",
        "popular_competitions": "The Masters, US Open, The Open Championship, PGA Championship, Ryder Cup",
        "tips_for_beginners": "Focus on grip, stance, and alignment. Learn the fundamentals before buying expensive clubs. Take beginner lessons.",
        "safety_guidelines": "Check for people ahead before swinging. Shout 'fore' if your ball might hit others. Stay hydrated and wear sunscreen."
    },
    "archery": {
        "introduction": "Archery is the art or sport of using a bow to shoot arrows at a target.",
        "basic_rules": "Archers shoot arrows at a target from a set distance. Closest to center wins. Scoring based on arrow placement.",
        "number_of_players": "Individual or team events (3-4 per team)",
        "equipment": "Bow, arrows, quiver, arm guard, finger tab, target",
        "match_duration": "1-3 hours",
        "scoring_system": "Target faces = 10 rings (10 to 1 points). Inner 10-ring (X) used for tiebreaks. Arrow closest to center wins.",
        "tournament_format": "Qualification round (72 arrows) then head-to-head knockout matches. Team scores = 3-arrow sums.",
        "popular_competitions": "Olympics, World Archery Championships, Archery World Cup",
        "tips_for_beginners": "Learn proper stance and release. Focus on consistency. Practice at shorter distances first.",
        "safety_guidelines": "Never shoot in direction of people. Use arm guard to protect bow arm. Ensure clear range ahead before shooting."
    }
}

# Match suggestions by sport
MATCH_SUGGESTIONS = {
    "badminton": {
        "sport": "Badminton",
        "match_type": "Singles",
        "players": 2,
        "venue": "Indoor Sports Arena",
        "duration": "45-60 minutes",
        "equipment": "Racket, Shuttlecock, Court Shoes, Sportswear"
    },
    "cricket": {
        "sport": "Cricket",
        "match_type": "T20 or ODI",
        "players": "22 (11 per team)",
        "venue": "Cricket Ground",
        "duration": "3-8 hours",
        "equipment": "Bat, Ball, Wickets, Pads, Gloves, Helmet"
    },
    "football": {
        "sport": "Football",
        "match_type": "5-a-side or 11-a-side",
        "players": "5-22",
        "venue": "Football Ground",
        "duration": "90 minutes",
        "equipment": "Football, Shin Guards, Cleats, Sportswear"
    },
    "basketball": {
        "sport": "Basketball",
        "match_type": "3x3 or 5x5",
        "players": "3-10",
        "venue": "Indoor Basketball Court",
        "duration": "40-48 minutes",
        "equipment": "Basketball, Basketball Shoes, Sportswear"
    },
    "tennis": {
        "sport": "Tennis",
        "match_type": "Singles or Doubles",
        "players": "2-4",
        "venue": "Tennis Court",
        "duration": "60-120 minutes",
        "equipment": "Tennis Racket, Tennis Balls, Tennis Shoes"
    },
    "volleyball": {
        "sport": "Volleyball",
        "match_type": "Indoor or Beach",
        "players": "6-12",
        "venue": "Volleyball Court",
        "duration": "60-90 minutes",
        "equipment": "Volleyball, Knee Pads, Court Shoes"
    },
    "table tennis": {
        "sport": "Table Tennis",
        "match_type": "Singles or Doubles",
        "players": "2-4",
        "venue": "Indoor Sports Hall",
        "duration": "30-60 minutes",
        "equipment": "Table Tennis Racket, Balls, Table"
    },
    "hockey": {
        "sport": "Hockey",
        "match_type": "Field Hockey",
        "players": "22 (11 per team)",
        "venue": "Hockey Field",
        "duration": "70 minutes",
        "equipment": "Hockey Stick, Ball, Shin Guards, Mouthguard"
    },
    "kabaddi": {
        "sport": "Kabaddi",
        "match_type": "Standard",
        "players": "14 (7 per team)",
        "venue": "Indoor Court or Outdoor Field",
        "duration": "40 minutes",
        "equipment": "Knee Pads, Sportswear"
    },
    "chess": {
        "sport": "Chess",
        "match_type": "Standard or Blitz",
        "players": 2,
        "venue": "Indoor Tournament Hall",
        "duration": "30-120 minutes",
        "equipment": "Chess Board, Chess Pieces, Timer"
    },
    "athletics": {
        "sport": "Athletics",
        "match_type": "Track and Field",
        "players": "Individual or Team",
        "venue": "Stadium with Track",
        "duration": "2-4 hours",
        "equipment": "Running Shoes, Athletic Wear, Event-specific gear"
    },
    "cycling": {
        "sport": "Cycling",
        "match_type": "Road Race or Track",
        "players": "Individual or Group",
        "venue": "Road or Velodrome",
        "duration": "1-6 hours",
        "equipment": "Bicycle, Helmet, Cycling Shoes, Sportswear"
    },
    "rugby": {
        "sport": "Rugby",
        "match_type": "Union or Sevens",
        "players": "15-28",
        "venue": "Rugby Field",
        "duration": "80-100 minutes",
        "equipment": "Rugby Ball, Cleats, Mouthguard, Scrum Cap"
    },
    "baseball": {
        "sport": "Baseball",
        "match_type": "Standard",
        "players": "18 (9 per team)",
        "venue": "Baseball Diamond",
        "duration": "2-3 hours",
        "equipment": "Bat, Ball, Glove, Helmet, Cleats"
    },
    "golf": {
        "sport": "Golf",
        "match_type": "Stroke Play or Match Play",
        "players": "1-4",
        "venue": "Golf Course",
        "duration": "3-5 hours",
        "equipment": "Golf Clubs, Golf Balls, Tees, Golf Shoes"
    },
    "archery": {
        "sport": "Archery",
        "match_type": "Target Archery",
        "players": "Individual or Team",
        "venue": "Archery Range",
        "duration": "1-3 hours",
        "equipment": "Bow, Arrows, Quiver, Arm Guard, Finger Tab"
    }
}
