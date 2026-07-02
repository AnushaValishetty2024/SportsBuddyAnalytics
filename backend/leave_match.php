<?php
require_once __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

$match_id = isset($_POST['match_id']) ? intval($_POST['match_id']) : 0;
$user_id = isset($_POST['user_id']) ? intval($_POST['user_id']) : 0;

if ($match_id <= 0 || $user_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid match ID or user ID']);
    exit();
}

try {
    // Check if match exists
    $matchStmt = $pdo->prepare("SELECT id, creator_id FROM matches WHERE id = ?");
    $matchStmt->execute([$match_id]);
    $match = $matchStmt->fetch();

    if (!$match) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Match not found']);
        exit();
    }

    // Check if user is the creator - creator cannot leave their own match
    if (intval($match['creator_id']) === $user_id) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'You cannot leave a match you created']);
        exit();
    }

    // Check if user is actually a participant
    $checkStmt = $pdo->prepare("SELECT id FROM match_participants WHERE match_id = ? AND user_id = ?");
    $checkStmt->execute([$match_id, $user_id]);
    $participant = $checkStmt->fetch();

    if (!$participant) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'You are not a participant of this match']);
        exit();
    }

    // Remove the participant
    $deleteStmt = $pdo->prepare("DELETE FROM match_participants WHERE match_id = ? AND user_id = ?");
    $deleteStmt->execute([$match_id, $user_id]);

    echo json_encode([
        'success' => true,
        'message' => 'Successfully left the match'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to leave match: ' . $e->getMessage()
    ]);
}