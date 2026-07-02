<?php
require_once __DIR__ . '/db.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'You must be logged in to delete a team']);
    exit();
}

$user_id = $_SESSION['user_id'];
$team_id = isset($_POST['team_id']) ? intval($_POST['team_id']) : 0;

if ($team_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid team ID']);
    exit();
}

try {
    // Get team and verify captain
    $teamStmt = $pdo->prepare("SELECT * FROM teams WHERE id = ?");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();

    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }

    if ($team['captain_id'] != $user_id) {
        http_response_code(403);
        echo json_encode(['success' => false, 'message' => 'Only the team captain can delete the team']);
        exit();
    }

    // Delete logo file if exists
    if ($team['logo'] && file_exists($team['logo'])) {
        unlink($team['logo']);
    }
    
    // Log activity before deletion
    $userNameStmt = $pdo->prepare("SELECT name FROM users WHERE id = ?");
    $userNameStmt->execute([$user_id]);
    $user_name = $userNameStmt->fetchColumn() ?: 'Captain';
    
    $activityStmt = $pdo->prepare("
        INSERT INTO team_activity_log (team_id, action_type, description, user_id, timestamp)
        VALUES (?, 'team_deleted', ?, ?, NOW())
    ");
    $activityStmt->execute([
        $team_id,
        "Team '$team[team_name]' deleted by $user_name",
        $user_id
    ]);

    // Delete team (cascade will handle related records)
    $sql = "DELETE FROM teams WHERE id = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$team_id]);

    echo json_encode([
        'success' => true,
        'message' => 'Team deleted successfully'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to delete team: ' . $e->getMessage()
    ]);
}