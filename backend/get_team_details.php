<?php
require_once __DIR__ . '/db.php';
session_start();
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
    // Get team details
    $teamStmt = $pdo->prepare("
        SELECT t.*, u.name as captain_name, u.email as captain_email
        FROM teams t
        LEFT JOIN users u ON t.captain_id = u.id
        WHERE t.id = ?
    ");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();

    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }

    // Get members
    $membersStmt = $pdo->prepare("
        SELECT u.id, u.name, u.email, tm.joined_at
        FROM team_members tm
        LEFT JOIN users u ON tm.user_id = u.id
        WHERE tm.team_id = ?
        ORDER BY tm.joined_at ASC
    ");
    $membersStmt->execute([$team_id]);
    $members = $membersStmt->fetchAll();

    // Check if current user is member and their role
    $is_captain = false;
    $is_member = false;
    if (isset($_SESSION['user_id'])) {
        if ($team['captain_id'] == $_SESSION['user_id']) {
            $is_captain = true;
            $is_member = true;
        } else {
            $memberCheck = $pdo->prepare("SELECT id FROM team_members WHERE team_id = ? AND user_id = ?");
            $memberCheck->execute([$team_id, $_SESSION['user_id']]);
            $is_member = (bool)$memberCheck->fetch();
        }
    }

    echo json_encode([
        'success' => true,
        'team' => $team,
        'members' => $members,
        'is_captain' => $is_captain,
        'is_member' => $is_member
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch team details: ' . $e->getMessage()
    ]);
}