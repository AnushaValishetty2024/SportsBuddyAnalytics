<?php
require_once __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

// Read JSON input (support both JSON and FormData)
$input = json_decode(file_get_contents('php://input'), true);
if ($input) {
    $match_id = isset($input['match_id']) ? intval($input['match_id']) : 0;
    $winner_id = isset($input['winner_id']) ? intval($input['winner_id']) : 0;
    $is_draw = isset($input['is_draw']) ? intval($input['is_draw']) : 0;
    $submitted_by = isset($input['submitted_by']) ? intval($input['submitted_by']) : 0;
    $points_awarded = isset($input['points_awarded']) ? intval($input['points_awarded']) : 10;
} else {
    $match_id = isset($_POST['match_id']) ? intval($_POST['match_id']) : 0;
    $winner_id = isset($_POST['winner_id']) ? intval($_POST['winner_id']) : 0;
    $is_draw = isset($_POST['is_draw']) ? intval($_POST['is_draw']) : 0;
    $submitted_by = isset($_POST['submitted_by']) ? intval($_POST['submitted_by']) : 0;
    $points_awarded = isset($_POST['points_awarded']) ? intval($_POST['points_awarded']) : 10;
}

if ($match_id <= 0 || $submitted_by <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Match ID and submitted_by are required']);
    exit();
}

try {
    $pdo->beginTransaction();

    // Check if match exists
    $matchStmt = $pdo->prepare("SELECT id, sport_name FROM matches WHERE id = ?");
    $matchStmt->execute([$match_id]);
    $match = $matchStmt->fetch();

    if (!$match) {
        $pdo->rollBack();
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Match not found']);
        exit();
    }

    // Check for duplicate result submission (match_results has UNIQUE on match_id)
    $dupStmt = $pdo->prepare("SELECT id FROM match_results WHERE match_id = ?");
    $dupStmt->execute([$match_id]);
    if ($dupStmt->fetch()) {
        $pdo->rollBack();
        http_response_code(409);
        echo json_encode(['success' => false, 'message' => 'Result already submitted for this match. Duplicate not allowed.']);
        exit();
    }

    // Get all participants for this match
    $partStmt = $pdo->prepare("SELECT user_id FROM match_participants WHERE match_id = ?");
    $partStmt->execute([$match_id]);
    $participants = $partStmt->fetchAll();

    if (count($participants) < 2) {
        $pdo->rollBack();
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Match must have at least 2 participants to submit a result']);
        exit();
    }

    // Validate draw or winner
    if ($is_draw) {
        $winner_id = null;
    } else {
        if ($winner_id <= 0) {
            $pdo->rollBack();
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Winner ID is required when is_draw is 0']);
            exit();
        }

        // Verify winner is a participant
        $isWinnerParticipant = false;
        foreach ($participants as $p) {
            if (intval($p['user_id']) === $winner_id) {
                $isWinnerParticipant = true;
                break;
            }
        }
        if (!$isWinnerParticipant) {
            $pdo->rollBack();
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Winner must be a participant of this match']);
            exit();
        }
    }

    // Insert match result
    $insertResultStmt = $pdo->prepare(
        "INSERT INTO match_results (match_id, winner_id, is_draw, submitted_by) VALUES (?, ?, ?, ?)"
    );
    $insertResultStmt->execute([$match_id, $winner_id, $is_draw, $submitted_by]);

    // Update player_points for each participant
    foreach ($participants as $participant) {
        $uid = intval($participant['user_id']);

        if ($is_draw) {
            // Draw: each player gets +5 points, +1 draw, +1 match played
            $updateStmt = $pdo->prepare(
                "UPDATE player_points 
                 SET points = points + 5, draws = draws + 1, matches_played = matches_played + 1 
                 WHERE user_id = ?"
            );
            $updateStmt->execute([$uid]);
        } elseif ($uid === $winner_id) {
            // Winner: +10 points, +1 win, +1 match played
            $updateStmt = $pdo->prepare(
                "UPDATE player_points 
                 SET points = points + 10, wins = wins + 1, matches_played = matches_played + 1 
                 WHERE user_id = ?"
            );
            $updateStmt->execute([$uid]);
        } else {
            // Loser: +0 points, +1 loss, +1 match played
            $updateStmt = $pdo->prepare(
                "UPDATE player_points 
                 SET losses = losses + 1, matches_played = matches_played + 1 
                 WHERE user_id = ?"
            );
            $updateStmt->execute([$uid]);
        }
    }

    $pdo->commit();

    // Fetch updated leaderboard data to return to frontend
    $lbStmt = $pdo->query(
        "SELECT u.id, u.name, u.email, 
                COALESCE(pp.points, 0) AS points, 
                COALESCE(pp.wins, 0) AS wins, 
                COALESCE(pp.losses, 0) AS losses, 
                COALESCE(pp.draws, 0) AS draws, 
                COALESCE(pp.matches_played, 0) AS matches_played
         FROM users u
         LEFT JOIN player_points pp ON u.id = pp.user_id
         ORDER BY pp.points DESC, u.name ASC"
    );
    $leaderboard = $lbStmt->fetchAll();

    echo json_encode([
        'success' => true,
        'message' => 'Match result submitted successfully. Leaderboard updated.',
        'match_id' => $match_id,
        'winner_id' => $winner_id,
        'is_draw' => $is_draw ? true : false,
        'leaderboard' => $leaderboard
    ]);

} catch (PDOException $e) {
    $pdo->rollBack();
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to submit match result: ' . $e->getMessage()
    ]);
}