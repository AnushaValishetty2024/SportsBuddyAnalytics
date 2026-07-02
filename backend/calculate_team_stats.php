<?php
require_once __DIR__ . '/db.php';
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only GET method allowed']);
    exit();
}

$team_id = isset($_GET['team_id']) ? intval($_GET['team_id']) : 0;

if ($team_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid team ID']);
    exit();
}

try {
    // Get team statistics with safe defaults
    $stmt = $pdo->prepare("
        SELECT 
            COALESCE(t.points, 0) as points,
            COALESCE(t.wins, 0) as wins,
            COALESCE(t.losses, 0) as losses,
            COALESCE(t.draws, 0) as draws,
            COALESCE(t.matches_played, 0) as matches_played,
            COUNT(DISTINCT tm.user_id) as total_members
        FROM teams t
        LEFT JOIN team_members tm ON t.id = tm.team_id
        WHERE t.id = ?
        GROUP BY t.id
    ");
    
    $stmt->execute([$team_id]);
    $stats = $stmt->fetch();
    
    if (!$stats) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }
    
    // Calculate win rate safely
    $matches_played = intval($stats['matches_played']);
    $wins = intval($stats['wins']);
    $win_rate = $matches_played > 0 ? round(($wins / $matches_played) * 100, 1) : 0;
    
    // Calculate rank
    $rankStmt = $pdo->prepare("
        SELECT COUNT(*) + 1 as rank
        FROM teams
        WHERE points > ? OR (points = ? AND wins > ?)
    ");
    $rankStmt->execute([$stats['points'], $stats['points'], $stats['wins']]);
    $rank_result = $rankStmt->fetch();
    $rank = $rank_result ? intval($rank_result['rank']) : 1;
    
    // Ensure all values are integers
    $safe_stats = [
        'success' => true,
        'team_id' => $team_id,
        'points' => intval($stats['points']),
        'wins' => $wins,
        'losses' => intval($stats['losses']),
        'draws' => intval($stats['draws']),
        'matches_played' => $matches_played,
        'win_rate' => $win_rate,
        'rank' => $rank,
        'total_members' => intval($stats['total_members'])
    ];
    
    echo json_encode($safe_stats);
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to calculate stats: ' . $e->getMessage()
    ]);
}
?>