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
    echo json_encode(['success' => false, 'message' => 'You must be logged in']);
    exit();
}

$user_id = $_SESSION['user_id'];
$team_id = isset($_POST['team_id']) ? intval($_POST['team_id']) : 0;
$member_id = isset($_POST['member_id']) ? intval($_POST['member_id']) : 0;

if ($team_id <= 0 || $member_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid team ID or member ID']);
    exit();
}

try {
    // Verify team exists and user is captain
    $teamStmt = $pdo->prepare("SELECT captain_id FROM teams WHERE id = ?");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();

    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }

    if ($team['captain_id'] != $user_id) {
        http_response_code(403);
        echo json_encode(['success' => false, 'message' => 'Only the team captain can remove members']);
        exit();
    }

    // Cannot remove the captain
    if ($member_id == $team['captain_id']) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Cannot remove the team captain']);
        exit();
    }

    // Remove member
    $sql = "DELETE FROM team_members WHERE team_id = ? AND user_id = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$team_id, $member_id]);

    if ($stmt->rowCount() > 0) {
        echo json_encode([
            'success' => true,
            'message' => 'Member removed successfully'
        ]);
    } else {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Member not found in team']);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to remove member: ' . $e->getMessage()
    ]);
}