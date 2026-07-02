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
    echo json_encode(['success' => false, 'message' => 'You must be logged in to join a team']);
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
    // Verify team exists
    $teamStmt = $pdo->prepare("SELECT * FROM teams WHERE id = ?");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();

    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }

    // Check if team is full
    $countStmt = $pdo->prepare("SELECT COUNT(*) as count FROM team_members WHERE team_id = ?");
    $countStmt->execute([$team_id]);
    $member_count = $countStmt->fetch()['count'];

    if ($member_count >= $team['max_members']) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Team is full']);
        exit();
    }

    // Check if user is already a member
    $checkStmt = $pdo->prepare("SELECT id FROM team_members WHERE team_id = ? AND user_id = ?");
    $checkStmt->execute([$team_id, $user_id]);
    if ($checkStmt->fetch()) {
        http_response_code(409);
        echo json_encode(['success' => false, 'message' => 'You are already a member of this team']);
        exit();
    }

    // Join team
    $sql = "INSERT INTO team_members (team_id, user_id) VALUES (?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$team_id, $user_id]);
    
    // Log activity
    $userNameStmt = $pdo->prepare("SELECT name FROM users WHERE id = ?");
    $userNameStmt->execute([$user_id]);
    $user_name = $userNameStmt->fetchColumn() ?: 'A user';
    
    $activityStmt = $pdo->prepare("
        INSERT INTO team_activity_log (team_id, action_type, description, user_id, timestamp)
        VALUES (?, 'member_joined', ?, ?, NOW())
    ");
    $activityStmt->execute([
        $team_id,
        "$user_name joined the team",
        $user_id
    ]);

    echo json_encode([
        'success' => true,
        'message' => 'Joined team successfully'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to join team: ' . $e->getMessage()
    ]);
}