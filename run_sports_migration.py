"""
Sports Categories Migration Script
Adds new columns to game_categories and seeds all 24 sports
Run with: python run_sports_migration.py
"""
import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'sports_buddy'

def run_migration():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cur = conn.cursor()
    
    print("=" * 60)
    print("Sports Categories Migration")
    print("=" * 60)
    
    # STEP 1: Add new columns
    print("\n[Step 1] Adding new columns to game_categories...")
    new_columns = [
        ("category", "VARCHAR(20) DEFAULT NULL COMMENT 'Indoor or Outdoor'"),
        ("num_players", "VARCHAR(100) DEFAULT NULL"),
        ("equipment", "VARCHAR(500) DEFAULT NULL"),
        ("match_duration", "VARCHAR(200) DEFAULT NULL"),
        ("playing_area", "VARCHAR(300) DEFAULT NULL"),
        ("basic_rules", "TEXT DEFAULT NULL"),
        ("popular_tournaments", "VARCHAR(500) DEFAULT NULL"),
        ("difficulty_level", "VARCHAR(50) DEFAULT NULL"),
    ]
    
    # Check existing columns
    cur.execute("DESCRIBE game_categories")
    existing_cols = {row[0] for row in cur.fetchall()}
    
    for col_name, col_def in new_columns:
        if col_name not in existing_cols:
            sql = f"ALTER TABLE game_categories ADD COLUMN {col_name} {col_def} AFTER description"
            try:
                cur.execute(sql)
                conn.commit()
                print(f"  + Added column: {col_name}")
            except Exception as e:
                # If AFTER description fails, add without position
                try:
                    sql = f"ALTER TABLE game_categories ADD COLUMN {col_name} {col_def}"
                    cur.execute(sql)
                    conn.commit()
                    print(f"  + Added column: {col_name}")
                except Exception as e2:
                    print(f"  ! Could not add {col_name}: {e2}")
        else:
            print(f"  - Column already exists: {col_name}")
    
    # STEP 2: Define all 24 sports with full data
    print("\n[Step 2] Seeding/updating all 24 sports...")
    
    outdoor_sports = [
        # (name, logo, description, category, num_players, equipment, match_duration, playing_area, basic_rules, location_info, popular_tournaments, difficulty_level, display_order)
        ("Cricket", "/static/logos/cricket.png",
         "A bat-and-ball game played between two teams of eleven players on a field. One team bats while the other bowls and fields, trying to dismiss the batsmen and limit scoring. Cricket has various formats including Test, ODI, and T20 cricket.",
         "Outdoor", "11 per team",
         "Cricket bat, ball (leather), stumps, bails, protective gear (pads, gloves, helmet)",
         "T20: ~3 hrs, ODI: ~8 hrs, Test: 5 days",
         "Cricket ground with 22-yard pitch in center",
         "Each team has 11 players. The batting team sends two batsmen. The bowling team bowls 6-ball overs. Runs scored by hitting ball and running between wickets. Dismissals include bowled, caught, LBW, run out, and stumped.",
         "Cricket grounds, stadiums, open fields with pitch",
         "ICC Cricket World Cup, IPL, T20 World Cup, The Ashes",
         "Medium", 1),
        
        ("Football", "/static/logos/football.png",
         "A team sport played between two teams of eleven players with a spherical ball. Players use their feet to kick the ball into the opposing goal. The world's most popular sport with billions of fans worldwide.",
         "Outdoor", "11 per team",
         "Football, goalposts with nets, shin guards, boots, goalkeeper gloves",
         "90 mins (two 45-min halves)",
         "Football pitch (100-110m x 64-75m) with goals",
         "Two teams of 11 players. Score goals by getting ball into opposing goal. No hands/arms except goalkeeper. Offside rule applies. Draw possible or extra time/penalties in knockout stages.",
         "Football fields, stadiums, open grounds",
         "FIFA World Cup, UEFA Champions League, Premier League, La Liga",
         "Medium", 2),
        
        ("Volleyball", "/static/logos/volleyball.png",
         "A team sport where two teams of six players are separated by a net. Each team tries to score points by grounding a ball on the other team's court. Combines athletic jumping, powerful spikes, and strategic teamwork.",
         "Outdoor", "6 per team",
         "Volleyball, net, knee pads, volleyball shoes",
         "Best of 5 sets (~1-2 hrs)",
         "Volleyball court (18m x 9m) with net (2.43m/2.24m high)",
         "Two teams of 6. Hit ball over net using hands/arms. 3 touches per side. Points when ball touches opponent's ground. Sets to 25 points (15 for 5th). Rotate after winning serve.",
         "Indoor or beach volleyball courts",
         "FIVB World Championship, Olympics, FIVB World Cup",
         "Medium", 3),
        
        ("Hockey", "/static/logos/hockey.png",
         "A fast-paced team sport played on grass or turf where two teams of eleven players use curved sticks to hit a ball into the opponent's goal. One of the oldest team sports and a major Olympic sport.",
         "Outdoor", "11 per team",
         "Hockey stick, ball, shin guards, mouthguard, goalkeeper kit",
         "60 mins (four 15-min quarters)",
         "Hockey field (91.4m x 55m) with goals",
         "Two teams of 11. Use curved sticks to hit ball into opponent goal. Ball cannot be played with feet/hands. Penalty corners and penalty strokes for fouls in shooting circle.",
         "Hockey turf/stadium",
         "FIH Hockey World Cup, Olympics, Hockey India League",
         "Medium", 4),
        
        ("Baseball", "/static/logos/baseball.png",
         "A bat-and-ball game played between two teams of nine players. The batting team hits a ball thrown by the pitcher and runs around four bases to score runs. A beloved American pastime with deep strategy.",
         "Outdoor", "9 per team",
         "Baseball bat, ball, gloves, batting helmet, catcher's gear",
         "9 innings (~3 hrs)",
         "Baseball diamond (90ft bases) with outfield",
         "Pitcher throws ball, batter tries to hit it. Run bases (1st-2nd-3rd-Home) to score runs. Fielders get batters out by catching, tagging, or forcing. 9 innings per game.",
         "Baseball field/diamond",
         "MLB World Series, World Baseball Classic",
         "Hard", 5),
        
        ("Rugby", "/static/logos/rugby.png",
         "A full-contact team sport where two teams of fifteen players try to carry or kick an oval ball across the opponent's goal line. Known for physical intensity, teamwork, and sportsmanship.",
         "Outdoor", "15 per team",
         "Rugby ball (oval), mouthguard, boots, scrum cap",
         "80 mins (two 40-min halves)",
         "Rugby pitch (100m x 70m) with H-shaped goalposts",
         "Carry, pass (backwards only), and kick the ball. Ground ball in in-goal area for try (5 pts). Conversions (2 pts), penalties (3 pts), drop goals (3 pts). Tackling allowed below shoulders.",
         "Rugby union pitch",
         "Rugby World Cup, Six Nations, Rugby Championship",
         "Hard", 6),
        
        ("Athletics", "/static/logos/athletics.png",
         "A collection of sporting events involving competitive running, jumping, throwing, and walking. Foundation of the Olympic Games with track and field events testing speed, endurance, and strength.",
         "Outdoor", "Individual (varies)",
         "Running spikes, starting blocks, relay baton, javelin, discus, shot put, hurdles",
         "Seconds to hours (varies by event)",
         "Athletics track (400m oval) and field areas",
         "Track: sprints, middle/long-distance, hurdles, relays, marathon. Field: jumps (long, triple, high, pole vault) and throws (shot put, discus, javelin, hammer). Winners by fastest time or longest distance.",
         "Athletics stadium with 400m track",
         "Olympics, World Athletics Championships, Diamond League",
         "Medium", 7),
        
        ("Cycling", "/static/logos/cycling.png",
         "A sport involving racing bicycles on roads, tracks, or off-road terrain. Combines endurance, strategy, and team tactics across road racing, track, mountain biking, and BMX disciplines.",
         "Outdoor", "Individual/Team",
         "Racing bicycle, helmet, cycling shoes, jersey, gloves",
         "Minutes to weeks (multi-stage events)",
         "Road courses, velodrome, mountain trails, BMX tracks",
         "Road: mass-start long-distance races. Track: velodrome sprints/pursuits. Mountain: off-road rough terrain. BMX: short sprints with jumps. Best time or highest position wins.",
         "Roads, velodromes, mountain trails",
         "Tour de France, Giro d'Italia, Olympics, UCI Worlds",
         "Hard", 8),
        
        ("Archery", "/static/logos/archery.png",
         "A precision sport where participants use a bow to shoot arrows at a target. Requires focus, steady hands, and mental discipline. One of the oldest sports still practiced today.",
         "Outdoor", "Individual/Team",
         "Recurve/compound bow, arrows, finger tab, arm guard, quiver, sight",
         "~1-3 hrs per session",
         "Archery range with targets at 70m (Olympic)",
         "Shoot arrows at circular targets with scoring rings. Bullseye scores highest. Olympic format: 72 arrows in ranking, then head-to-head elimination. Highest score wins.",
         "Archery ranges/fields with safety zones",
         "Olympics, World Archery Championships, Asian Games",
         "Medium", 9),
        
        ("Golf", "/static/logos/golf.png",
         "A precision club-and-ball sport where players use various clubs to hit a ball into a series of holes on a course in as few strokes as possible. Played for recreation and competition worldwide.",
         "Outdoor", "Individual (groups of 2-4)",
         "Golf clubs (driver, irons, wedges, putter), balls, tee, bag, glove, shoes",
         "18 holes (~4-5 hrs)",
         "Golf course (6000-7000 yards) with fairways, bunkers, greens",
         "Tee off from tee box. Hit ball from tee into hole on green in fewest strokes. Par defines standard strokes per hole. Penalties for out-of-bounds or water hazards.",
         "Golf courses with 9 or 18 holes",
         "The Masters, US Open, The Open, PGA Championship, Ryder Cup",
         "Hard", 10),
        
        ("Kabaddi", "/static/logos/kabaddi.png",
         "A contact team sport played between two teams of seven players. A raider enters opponent's half, tags defenders, and returns without being caught. Traditional Indian sport with growing international popularity.",
         "Outdoor", "7 per team",
         "No equipment required (played on mat)",
         "40 mins (two 20-min halves)",
         "Kabaddi court (13m x 10m) divided in half",
         "Raider enters opponent half chanting kabaddi without taking breath, tags defenders. Defenders try to catch raider. Points for successful raids/tackles. Bonus point for touching bonus line.",
         "Kabaddi courts (indoor/outdoor)",
         "Pro Kabaddi League, Asian Games, Kabaddi World Cup",
         "Medium", 11),
    ]
    
    indoor_sports = [
        ("Badminton", "/static/logos/badminton.png",
         "A racket sport played with shuttlecocks across a net. Can be played as singles or doubles. The fastest racket sport with shuttlecock speeds exceeding 330 km/h, requiring agility and precision.",
         "Indoor", "Singles (1v1) or Doubles (2v2)",
         "Racket, shuttlecock (feather/nylon), net, badminton shoes",
         "Best of 3 games (~30-60 min)",
         "Court (13.4m x 5.18m singles, 13.4m x 6.1m doubles)",
         "Hit shuttlecock over net using rackets. Rally ends when shuttle hits ground or goes out. Best of 3 games to 21 points. Rally scoring - point on every serve.",
         "Indoor badminton courts",
         "BWF World Championships, Olympics, All England Open",
         "Medium", 12),
        
        ("Basketball", "/static/logos/basketball.png",
         "A team sport where two teams of five players try to score points by throwing a ball through the opposing team's hoop. Fast-paced and high-scoring, played worldwide at all levels.",
         "Indoor", "5 per team",
         "Basketball, hoop with backboard, basketball shoes",
         "48 min (NBA) or 40 min (FIBA)",
         "Court (28m x 15m) with hoops (3.05m high)",
         "5 players per team. Score by shooting through hoop (2 or 3 pts). Dribble and pass to advance. Limited physical contact. 4 quarters. Most points wins.",
         "Indoor basketball courts",
         "NBA Finals, FIBA World Cup, Olympics, EuroLeague",
         "Medium", 13),
        
        ("Table Tennis", "/static/logos/table-tennis.png",
         "Also known as ping pong, where two or four players hit a lightweight ball back and forth across a table using small rackets. Olympic sport requiring lightning-fast reflexes and strategic spin.",
         "Indoor", "Singles (1v1) or Doubles (2v2)",
         "Paddle/racket, 40mm plastic ball, table with net",
         "Best of 5 or 7 games (~20-60 min)",
         "Table (2.74m x 1.525m) with net (15.25cm high)",
         "Hit ball back and forth across table. Point when opponent fails to return. Games to 11 points (win by 2). Service alternates every 2 points.",
         "Indoor tables in sports centers",
         "ITTF World Championships, Olympics, ITTF World Cup",
         "Medium", 14),
        
        ("Tennis", "/static/logos/tennis.png",
         "A racket sport played individually or in pairs. Players hit a ball over a net into opponent's court. Global sport known for prestigious Grand Slam tournaments and legendary rivalries.",
         "Indoor", "Singles (1v1) or Doubles (2v2)",
         "Racket, tennis ball, net, tennis shoes",
         "Best of 3 or 5 sets (~1-5 hrs)",
         "Court (23.77m x 8.23m singles, 23.77m x 10.97m doubles)",
         "Hit ball over net into opponent half. Scoring: 15-30-40-game. Win set by 6 games (2-game lead). Ball must land within boundaries.",
         "Tennis courts (clay, grass, hard court)",
         "Wimbledon, US Open, French Open, Australian Open, Davis Cup",
         "Medium", 15),
        
        ("Chess", "/static/logos/chess.png",
         "A two-player strategy board game played on a checkered board with 64 squares. One of the oldest and most intellectually demanding games requiring strategic thinking and deep concentration.",
         "Indoor", "2 players",
         "Chess board, 32 pieces (16 per player), chess clock",
         "Minutes to hours (varies by time control)",
         "Chess board (8x8 grid, 64 alternating squares)",
         "16 pieces per player: King, Queen, Rooks, Bishops, Knights, Pawns. Each moves differently. Objective: checkmate opponent's King. Time controls vary (rapid, blitz, classical).",
         "Indoor chess halls, clubs, online platforms",
         "World Chess Championship, Chess Olympiad, Tata Steel Chess",
         "Hard", 16),
        
        ("Carrom", "/static/logos/carrom.png",
         "A tabletop game of skill where players use a striker to flick discs into corner pockets. Popular family game in South Asia combining precision, strategy, and fine motor control.",
         "Indoor", "Singles (1v1) or Doubles (2v2)",
         "Carrom board, striker, 9 discs per player, queen (red disc), powder",
         "~15-30 min per game",
         "Carrom board (square ~74cm sides) with 4 corner pockets",
         "Flick striker to hit carrom men into pockets. Pocket and cover the queen. First to pocket all pieces wins. Points based on remaining opponent pieces.",
         "Indoor carrom boards in homes/clubs",
         "World Carrom Championship, Asian Carrom Championship",
         "Easy", 17),
        
        ("Squash", "/static/logos/squash.png",
         "A racket sport played in a four-walled court with a small rubber ball. Players take turns hitting the ball against the front wall. Intense cardiovascular workout requiring agility and shot-making skill.",
         "Indoor", "Singles (1v1) or Doubles (2v2)",
         "Squash racket, squash ball (yellow dot), court shoes, eye protection",
         "Best of 5 games (~40-90 min)",
         "Squash court (9.75m x 6.4m) with 4 walls",
         "Hit rubber ball against front wall above tin. Ball can hit side/back walls before front. Alternate shots before double bounce. Games to 11 points.",
         "Indoor squash courts",
         "PSA World Championships, British Open, Asian Games",
         "Hard", 18),
        
        ("Boxing", "/static/logos/boxing.png",
         "A combat sport where two opponents wearing gloves punch each other in a ring. Requires speed, power, endurance, and defensive skills. Both professional sport and Olympic discipline.",
         "Indoor", "2 opponents",
         "Boxing gloves, hand wraps, mouthguard, headgear (amateur), shorts, shoes",
         "3-12 rounds of 3 min each",
         "Boxing ring (4.9m-7.3m square) with ropes",
         "Punch opponent with padded gloves above waist. No hits below belt, holding, or back of head. Points for clean punches. Win by KO, TKO, or judges decision.",
         "Boxing ring in gym/arena",
         "World Heavyweight Championship, Olympics, World Championships",
         "Hard", 19),
        
        ("Wrestling", "/static/logos/wrestling.png",
         "A combat sport involving grappling techniques like clinch fighting, throws, takedowns, joint locks, and pins. One of the oldest sports, contested in Olympic Games since ancient times.",
         "Indoor", "2 opponents",
         "Wrestling singlet, wrestling shoes, headgear",
         "Two 3-min periods (freestyle/greco-roman)",
         "Wrestling mat (12m x 12m competition area)",
         "Two opponents grapple to gain control. Points for takedowns, reversals, near falls. Win by pin (both shoulders to mat) or by points. Freestyle allows leg attacks; Greco-Roman upper body only.",
         "Wrestling mat in sports hall",
         "Olympics, World Wrestling Championships, Commonwealth Games",
         "Hard", 20),
        
        ("Martial Arts", "/static/logos/martial-arts.png",
         "Various codified combat systems and traditions practiced for self-defense, competition, physical fitness, and mental discipline. Includes Karate, Taekwondo, Judo, Kung Fu, and more.",
         "Indoor", "2 opponents (sparring)",
         "Gi/uniform, belt, protective gear (for sparring), training weapons",
         "Varies by discipline (2-5 min rounds)",
         "Dojo/martial arts studio with padded mats",
         "Varies by style. Striking arts: punches, kicks, blocks. Grappling arts: throws, pins, submissions. Forms (kata) demonstrate technique. Sparring applies skills in controlled combat.",
         "Dojos, martial arts studios, training halls",
         "Olympics (Judo/Taekwondo/Karate), World Championships, UFC",
         "Hard", 21),
        
        ("Gymnastics", "/static/logos/gymnastics.png",
         "A sport involving physical exercises requiring balance, strength, flexibility, agility, and coordination. Artistic gymnastics includes vault, floor, pommel horse, rings, bars, and beam events.",
         "Indoor", "Individual",
         "Gymnastics leotard/uniform, chalk, grips, mats, apparatus (vault, beam, bars, rings)",
         "Varies by event (~30-90 sec per routine)",
         "Gymnastics hall with various apparatus and padded floors",
         "Perform routines on apparatus or floor with tumbling and acrobatic elements. Judges score based on difficulty, execution, artistry, and landing. Highest total score wins.",
         "Indoor gymnastics centers",
         "Olympics, World Gymnastics Championships, Commonwealth Games",
         "Hard", 22),
        
        ("Swimming", "/static/logos/swimming.png",
         "A water sport where individuals or teams race through water using various strokes. Full-body workout and essential life skill. Major Olympic sport with freestyle, backstroke, breaststroke, and butterfly.",
         "Indoor", "Individual/Relay (4 per team)",
         "Swimsuit, goggles, swim cap, kickboard, pull buoy, fins",
         "Seconds to minutes (varies by distance)",
         "Swimming pool (25m or 50m lanes)",
         "Swim specified distance using designated stroke. Freestyle: front crawl. Backstroke: on back. Breaststroke: frog kick. Butterfly: dolphin kick with arm recovery. Touch wall to finish. Fastest time wins.",
         "Indoor/outdoor swimming pools",
         "Olympics, World Aquatics Championships, Commonwealth Games",
         "Medium", 23),
        
        ("Yoga", "/static/logos/yoga.png",
         "An ancient practice combining physical postures, breathing techniques, and meditation. Improves flexibility, strength, balance, and mental well-being. Practiced worldwide for health and relaxation.",
         "Indoor", "Individual (group classes available)",
         "Yoga mat, comfortable clothing, blocks, strap, blanket",
         "30-90 min per session",
         "Yoga studio, quiet room, or open space",
         "Series of physical postures (asanas) performed with breathing control (pranayama). Hold poses with proper alignment. Flow sequences (vinyasa) connect poses with breath. Meditation and relaxation at end.",
         "Yoga studios, fitness centers, quiet spaces",
         "International Day of Yoga, World Yoga Championship",
         "Easy", 24),
    ]
    
    all_sports = outdoor_sports + indoor_sports
    
    # Insert or update each sport
    insert_sql = """
        INSERT INTO game_categories 
        (name, logo, description, category, num_players, equipment, match_duration, playing_area, basic_rules, location_info, popular_tournaments, difficulty_level, display_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            logo = VALUES(logo),
            description = VALUES(description),
            category = VALUES(category),
            num_players = VALUES(num_players),
            equipment = VALUES(equipment),
            match_duration = VALUES(match_duration),
            playing_area = VALUES(playing_area),
            basic_rules = VALUES(basic_rules),
            location_info = VALUES(location_info),
            popular_tournaments = VALUES(popular_tournaments),
            difficulty_level = VALUES(difficulty_level),
            display_order = VALUES(display_order)
    """
    
    insert_count = 0
    update_count = 0
    
    for sport in all_sports:
        try:
            cur.execute(insert_sql, sport)
            conn.commit()
            if cur.rowcount == 1:
                insert_count += 1
            else:
                update_count += 1
            print(f"  {'+' if cur.rowcount == 1 else '~'} {sport[0]} ({'Indoor' if 'Indoor' in sport[3] else 'Outdoor'})")
        except Exception as e:
            print(f"  ! Error with {sport[0]}: {e}")
            conn.rollback()
    
    # STEP 3: Verify
    print("\n[Step 3] Verifying migration...")
    cur.execute("SELECT COUNT(*) as cnt FROM game_categories")
    total = cur.fetchone()[0]
    print(f"  Total sports in database: {total}")
    
    cur.execute("SELECT name, category, display_order FROM game_categories ORDER BY display_order")
    print("\n  Sports list:")
    for row in cur.fetchall():
        print(f"    {row[2]:2}. {row[0]:20} [{row[1] if row[1] else 'N/A':10}]")
    
    # Check new columns exist
    cur.execute("DESCRIBE game_categories")
    cols = [row[0] for row in cur.fetchall()]
    print(f"\n  Columns: {', '.join(cols)}")
    
    # Count indoor/outdoor
    cur.execute("SELECT category, COUNT(*) FROM game_categories GROUP BY category")
    print("\n  Category breakdown:")
    for row in cur.fetchall():
        print(f"    {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"Migration completed! {insert_count} new, {update_count} updated")
    print("=" * 60)


if __name__ == "__main__":
    run_migration()