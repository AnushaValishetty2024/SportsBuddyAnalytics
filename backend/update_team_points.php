<?php
require_once __DIR__ . '/db.php';
session_start();
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

$team_id = isset($_POST['team_id']) ? intval($_POST['team_id']) : 0;
$points_change = isset($_POST['points_change']) ? intval($_POST['points_change']) : 0;
$reason = isset($_POST['reason']) ? trim($_POST['reason']) : '';

if ($team_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid team ID']);
    exit();
}

if ($points_change === 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Points change cannot be zero']);
    exit();
}

if (empty($reason)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Reason is required']);
    exit();
}

try {
    // Verify team exists
    $teamStmt = $pdo->prepare("SELECT id, team_name, points FROM teams WHERE id = ?");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();
    
    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }
    
    $old_points = $team['points'];
    $new_points = $old_points + $points_change;
    
    // Ensure points don't go negative
    if ($new_points < 0) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Points cannot go below 0']);
        exit();
    }
    
    // Start transaction
    $pdo->beginTransaction();
    
    // Update team points
    $updateStmt = $pdo->prepare("UPDATE teams SET points = ? WHERE id = ?");
    $updateStmt->execute([$new_points, $team_id]);
    
    // Record in point history
    $updated_by = isset($_SESSION['user_id']) ? $_SESSION['user_id'] : null;
    $historyStmt = $pdo->prepare("
        INSERT INTO team_point_history (team_id, change_value, reason, updated_by, timestamp)
        VALUES (?, ?, ?, ?, NOW())
    ");
    $historyStmt->execute([$team_id, $points_change, $reason, $updated_by]);
    
    // Log activity
    $action_type = $points_change > 0 ? 'points_added' : 'points_removed';
    $description = sprintf(
        'Points %s by %s: %s (%+d). Total: %d → %d',
        $points_change > 0 ? 'added' : 'removed',
        isset($_SESSION['user_name']) ? $_SESSION['user_name'] : 'Admin',
        $reason,
        $points_change,
        $old_points,
        $new_points
    );
    
    $activityStmt = $pdo->prepare("
        INSERT INTO team_activity_log (team_id, action_type, description, user_id, timestamp)
        VALUES (?, ?, ?, ?, NOW())
    ");
    $activityStmt->execute([$team_id, $action_type, $description, $updated_by]);
    
    $pdo->commit();
    
    echo json_encode([
        'success' => true,
        'message' => 'Points updated successfully',
        'team_id' => $team_id,
        'old_points' => $old_points,
        'new_points' => $new_points,
        'change' => $points_change
    ]);
    
} catch (PDOException $e) {
    $pdo->rollBack();
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to update points: ' . $e->getMessage()
    ]);
}
?>