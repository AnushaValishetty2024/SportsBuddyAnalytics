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
    // Get last 10 activities
    $stmt = $pdo->prepare("
        SELECT 
            al.id,
            al.action_type,
            al.description,
            al.timestamp,
            u.name as user_name
        FROM team_activity_log al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE al.team_id = ?
        ORDER BY al.timestamp DESC
        LIMIT 10
    ");
    
    $stmt->execute([$team_id]);
    $activities = $stmt->fetchAll();
    
    // Format timestamps
    foreach ($activities as &$activity) {
        $activity['timestamp'] = date('M d, Y H:i', strtotime($activity['timestamp']));
    }
    
    echo json_encode([
        'success' => true,
        'activities' => $activities
    ]);
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch activity log: ' . $e->getMessage()
    ]);
}
?>