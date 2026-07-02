<?php
require_once __DIR__ . '/db.php';
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only GET method allowed']);
    exit();
}

try {
    $sql = "SELECT t.*, 
            u.name as captain_name,
            COUNT(tm.user_id) as current_members
            FROM teams t
            LEFT JOIN users u ON t.captain_id = u.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            GROUP BY t.id
            ORDER BY t.created_at DESC";

    $stmt = $pdo->query($sql);
    $teams = $stmt->fetchAll();

    echo json_encode([
        'success' => true,
        'teams' => $teams
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch teams: ' . $e->getMessage()
    ]);
}