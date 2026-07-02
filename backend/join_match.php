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
    // Check if match exists and get its details
    $matchStmt = $pdo->prepare("SELECT id, max_players FROM matches WHERE id = ?");
    $matchStmt->execute([$match_id]);
    $match = $matchStmt->fetch();

    if (!$match) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Match not found']);
        exit();
    }

    // Check if user exists
    $userStmt = $pdo->prepare("SELECT id FROM users WHERE id = ?");
    $userStmt->execute([$user_id]);
    if (!$userStmt->fetch()) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'User not found']);
        exit();
    }

    // Check if user already joined
    $alreadyJoinedStmt = $pdo->prepare("SELECT id FROM match_participants WHERE match_id = ? AND user_id = ?");
    $alreadyJoinedStmt->execute([$match_id, $user_id]);
    if ($alreadyJoinedStmt->fetch()) {
        http_response_code(409);
        echo json_encode(['success' => false, 'message' => 'You have already joined this match']);
        exit();
    }

    // Check current participant count
    $countStmt = $pdo->prepare("SELECT COUNT(*) AS cnt FROM match_participants WHERE match_id = ?");
    $countStmt->execute([$match_id]);
    $countResult = $countStmt->fetch();

    if (intval($countResult['cnt']) >= intval($match['max_players'])) {
        http_response_code(409);
        echo json_encode(['success' => false, 'message' => 'Match is already full']);
        exit();
    }

    // Insert participant
    $insertStmt = $pdo->prepare("INSERT INTO match_participants (match_id, user_id) VALUES (?, ?)");
    $insertStmt->execute([$match_id, $user_id]);

    echo json_encode([
        'success' => true,
        'message' => 'Successfully joined the match'
    ]);
} catch (PDOException $e) {
    // Handle unique constraint violation as a fallback
    if ($e->getCode() == 23000) {
        http_response_code(409);
        echo json_encode(['success' => false, 'message' => 'You have already joined this match']);
    } else {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Failed to join match: ' . $e->getMessage()
        ]);
    }
}