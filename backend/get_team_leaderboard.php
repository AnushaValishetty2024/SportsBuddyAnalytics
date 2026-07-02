<?php
require_once __DIR__ . '/db.php';
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only GET method allowed']);
    exit();
}

try {
    $search = isset($_GET['search']) ? trim($_GET['search']) : '';
    $sport_filter = isset($_GET['sport']) ? trim($_GET['sport']) : '';
    $location_filter = isset($_GET['location']) ? trim($_GET['location']) : '';
    
    // Build query with filters
    $sql = "SELECT 
                t.id as team_id,
                t.team_name,
                t.sport_type,
                t.location,
                t.logo,
                t.captain_id,
                u.name as captain_name,
                COUNT(tm.user_id) as current_members,
                COALESCE(t.points, 0) as points,
                COALESCE(t.wins, 0) as wins,
                COALESCE(t.losses, 0) as losses,
                COALESCE(t.draws, 0) as draws,
                COALESCE(t.matches_played, 0) as matches_played,
                CASE 
                    WHEN COALESCE(t.matches_played, 0) > 0 
                    THEN ROUND(COALESCE(t.wins, 0) * 100.0 / COALESCE(t.matches_played, 0), 1)
                    ELSE 0 
                END as win_percentage
            FROM teams t
            LEFT JOIN users u ON t.captain_id = u.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE 1=1";
    
    $params = [];
    
    if ($search) {
        $sql .= " AND t.team_name LIKE ?";
        $params[] = "%$search%";
    }
    
    if ($sport_filter) {
        $sql .= " AND t.sport_type = ?";
        $params[] = $sport_filter;
    }
    
    if ($location_filter) {
        $sql .= " AND t.location = ?";
        $params[] = $location_filter;
    }
    
    $sql .= " GROUP BY t.id ORDER BY points DESC, wins DESC, t.team_name ASC";
    
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $teams = $stmt->fetchAll();
    
    // Add rank position
    $rankedData = [];
    $rank = 1;
    foreach ($teams as $team) {
        $team['current_rank'] = $rank;
        $team['points'] = intval($team['points']);
        $team['wins'] = intval($team['wins']);
        $team['losses'] = intval($team['losses']);
        $team['draws'] = intval($team['draws']);
        $team['matches_played'] = intval($team['matches_played']);
        $team['win_percentage'] = floatval($team['win_percentage']);
        $rankedData[] = $team;
        $rank++;
    }
    
    // Get filter options (distinct sports and locations)
    $sportsStmt = $pdo->query("SELECT DISTINCT sport_type FROM teams WHERE sport_type IS NOT NULL ORDER BY sport_type");
    $sports = $sportsStmt->fetchAll(PDO::FETCH_COLUMN);
    
    $locationsStmt = $pdo->query("SELECT DISTINCT location FROM teams WHERE location IS NOT NULL ORDER BY location");
    $locations = $locationsStmt->fetchAll(PDO::FETCH_COLUMN);
    
    // Get current user's team IDs if logged in
    $user_team_ids = [];
    if (isset($_SESSION['user_id'])) {
        $userTeamsStmt = $pdo->prepare("SELECT team_id FROM team_members WHERE user_id = ?");
        $userTeamsStmt->execute([$_SESSION['user_id']]);
        $user_team_ids = $userTeamsStmt->fetchAll(PDO::FETCH_COLUMN);
    }
    
    echo json_encode([
        'success' => true,
        'leaderboard' => $rankedData,
        'sports' => $sports,
        'locations' => $locations,
        'user_team_ids' => $user_team_ids
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch team leaderboard: ' . $e->getMessage()
    ]);
}
?>