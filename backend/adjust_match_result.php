<?php
require_once __DIR__ . '/db.php';

// Only POST method allowed
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

// Read JSON input
$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    // Fallback to FormData
    $match_id = isset($_POST['match_id']) ? intval($_POST['match_id']) : 0;
    $adjustment_reason = isset($_POST['adjustment_reason']) ? trim($_POST['adjustment_reason']) : '';
    $new_points = isset($_POST['new_points']) ? intval($_POST['new_points']) : -1;
} else {
    $match_id = isset($input['match_id']) ? intval($input['match_id']) : 0;
    $adjustment_reason = isset($input['adjustment_reason']) ? trim($input['adjustment_reason']) : '';
    $new_points = isset($input['new_points']) ? intval($input['new_points']) : -1;
}

if ($match_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'match_id is required']);
    exit();
}

if ($new_points < 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'new_points must be a non-negative integer']);
    exit();
}

if (empty($adjustment_reason)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'adjustment_reason is required']);
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

    // Get all participants for this match
    $partStmt = $pdo->prepare("SELECT user_id FROM match_participants WHERE match_id = ?");
    $partStmt->execute([$match_id]);
    $participants = $partStmt->fetchAll();

    if (count($participants) === 0) {
        $pdo->rollBack();
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'No participants found for this match']);
        exit();
    }

    // Apply adjustment: distribute new_points among participants
    // How we adjust: We recalculate each player's total points by adding the delta
    // For simplicity, we award the new_points value to each participant as an adjustment bonus
    $points_per_player = $new_points; // each participant gets this many additional points

    foreach ($participants as $participant) {
        $uid = intval($participant['user_id']);

        // Update player_points - add adjustment points
        $updateStmt = $pdo->prepare(
            "UPDATE player_points 
             SET points = points + ? 
             WHERE user_id = ?"
        );
        $updateStmt->execute([$points_per_player, $uid]);

        // Also insert into player_points if not exists (create record)
        if ($updateStmt->rowCount() === 0) {
            $insertStmt = $pdo->prepare(
                "INSERT INTO player_points (user_id, points, wins, losses, draws, matches_played) 
                 VALUES (?, ?, 0, 0, 0, 0)"
            );
            $insertStmt->execute([$uid, $points_per_player]);
        }
    }

    // Log the adjustment (store in a simple audit table or just use admin_overrides)
    // Check if admin_overrides table exists, if not just log to a message
    try {
        $logStmt = $pdo->prepare(
            "INSERT INTO admin_overrides 
             (target_user_id, previous_points, new_points, previous_wins, new_wins, 
              previous_losses, new_losses, previous_draws, new_draws, 
              previous_matches_played, new_matches_played, reason) 
             VALUES (?, 0, ?, 0, 0, 0, 0, 0, 0, 0, 0, ?)"
        );
        // Log for the first participant as a general adjustment record
        if (count($participants) > 0) {
            $logStmt->execute([
                intval($participants[0]['user_id']),
                $points_per_player,
                'Match adjustment: ' . $adjustment_reason . ' (match_id: ' . $match_id . ')'
            ]);
        }
    } catch (PDOException $e) {
        // admin_overrides table may not exist, that's okay
    }

    $pdo->commit();

    // Fetch updated leaderboard
    $lbStmt = $pdo->query(
        "SELECT u.id AS user_id, u.name AS user_name, u.email AS user_email,
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
        'message' => 'Match result adjusted successfully. Points updated for all participants.',
        'match_id' => $match_id,
        'adjustment_reason' => $adjustment_reason,
        'new_points' => $points_per_player,
        'leaderboard' => $leaderboard
    ]);

} catch (PDOException $e) {
    $pdo->rollBack();
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to adjust match result: ' . $e->getMessage()
    ]);
}