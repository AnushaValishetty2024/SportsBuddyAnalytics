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
    echo json_encode(['success' => false, 'message' => 'You must be logged in to leave a team']);
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
    // Check if user is captain
    $teamStmt = $pdo->prepare("SELECT captain_id FROM teams WHERE id = ?");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();

    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }

    if ($team['captain_id'] == $user_id) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Captain cannot leave the team. Transfer ownership or delete the team instead.']);
        exit();
    }

    // Check if user is a member
    $checkStmt = $pdo->prepare("SELECT id FROM team_members WHERE team_id = ? AND user_id = ?");
    $checkStmt->execute([$team_id, $user_id]);
    $membership = $checkStmt->fetch();

    if (!$membership) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'You are not a member of this team']);
        exit();
    }

    // Remove member
    $sql = "DELETE FROM team_members WHERE team_id = ? AND user_id = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$team_id, $user_id]);
    
    // Log activity
    $userNameStmt = $pdo->prepare("SELECT name FROM users WHERE id = ?");
    $userNameStmt->execute([$user_id]);
    $user_name = $userNameStmt->fetchColumn() ?: 'A user';
    
    $activityStmt = $pdo->prepare("
        INSERT INTO team_activity_log (team_id, action_type, description, user_id, timestamp)
        VALUES (?, 'member_left', ?, ?, NOW())
    ");
    $activityStmt->execute([
        $team_id,
        "$user_name left the team",
        $user_id
    ]);

    echo json_encode([
        'success' => true,
        'message' => 'Left team successfully'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to leave team: ' . $e->getMessage()
    ]);
}