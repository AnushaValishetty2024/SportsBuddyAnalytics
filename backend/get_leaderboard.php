<?php
require_once __DIR__ . '/db.php';

header('Content-Type: application/json');

try {
    $sql = "SELECT 
                u.id AS user_id,
                u.name AS user_name,
                u.email AS user_email,
                COALESCE(pp.points, 0) AS points,
                COALESCE(pp.wins, 0) AS wins,
                COALESCE(pp.losses, 0) AS losses,
                COALESCE(pp.draws, 0) AS draws,
                COALESCE(pp.matches_played, 0) AS matches_played,
                CASE 
                    WHEN COALESCE(pp.matches_played, 0) > 0 
                    THEN ROUND(COALESCE(pp.wins, 0) * 100.0 / COALESCE(pp.matches_played, 0), 1)
                    ELSE 0 
                END AS win_percentage
            FROM users u
            LEFT JOIN player_points pp ON u.id = pp.user_id
            ORDER BY pp.points DESC, pp.wins DESC, u.name ASC";

    $stmt = $pdo->prepare($sql);
    $stmt->execute();
    $leaderboard = $stmt->fetchAll();

    // Add rank position
    $rankedData = [];
    $rank = 1;
    foreach ($leaderboard as $row) {
        $row['rank'] = $rank;
        $row['points'] = intval($row['points']);
        $row['wins'] = intval($row['wins']);
        $row['losses'] = intval($row['losses']);
        $row['draws'] = intval($row['draws']);
        $row['matches_played'] = intval($row['matches_played']);
        $row['win_percentage'] = floatval($row['win_percentage']);
        $rankedData[] = $row;
        $rank++;
    }

    // Get summary statistics
    $statsStmt = $pdo->query(
        "SELECT 
            COUNT(*) AS total_players,
            SUM(COALESCE(pp.matches_played, 0)) AS total_matches_played,
            SUM(COALESCE(pp.points, 0)) AS total_points_earned
         FROM users u
         LEFT JOIN player_points pp ON u.id = pp.user_id"
    );
    $summary = $statsStmt->fetch();

    echo json_encode([
        'success' => true,
        'leaderboard' => $rankedData,
        'summary' => [
            'total_players' => intval($summary['total_players']),
            'total_matches_played' => intval($summary['total_matches_played']),
            'total_points_earned' => intval($summary['total_points_earned'])
        ],
        'last_updated' => date('Y-m-d H:i:s')
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch leaderboard: ' . $e->getMessage()
    ]);
}