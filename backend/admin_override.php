<?php
require_once __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

$target_user_id = isset($_POST['target_user_id']) ? intval($_POST['target_user_id']) : 0;
$new_points = isset($_POST['new_points']) ? intval($_POST['new_points']) : -1;
$new_wins = isset($_POST['new_wins']) ? intval($_POST['new_wins']) : -1;
$new_losses = isset($_POST['new_losses']) ? intval($_POST['new_losses']) : -1;
$new_draws = isset($_POST['new_draws']) ? intval($_POST['new_draws']) : -1;
$new_matches_played = isset($_POST['new_matches_played']) ? intval($_POST['new_matches_played']) : -1;
$reason = isset($_POST['reason']) ? trim($_POST['reason']) : '';

if ($target_user_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Target user ID is required']);
    exit();
}

// At least one field must be provided for override
if ($new_points < 0 && $new_wins < 0 && $new_losses < 0 && $new_draws < 0 && $new_matches_played < 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'At least one stat field (points, wins, losses, draws, matches_played) must be provided']);
    exit();
}

try {
    $pdo->beginTransaction();

    // Check user exists
    $userStmt = $pdo->prepare("SELECT id, name FROM users WHERE id = ?");
    $userStmt->execute([$target_user_id]);
    $user = $userStmt->fetch();
    if (!$user) {
        $pdo->rollBack();
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'User not found']);
        exit();
    }

    // Get current player_points (create if not exists)
    $ppStmt = $pdo->prepare("SELECT id, points, wins, losses, draws, matches_played FROM player_points WHERE user_id = ?");
    $ppStmt->execute([$target_user_id]);
    $current = $ppStmt->fetch();

    if (!$current) {
        // Create player_points record if it doesn't exist
        $createStmt = $pdo->prepare("INSERT INTO player_points (user_id, points, wins, losses, draws, matches_played) VALUES (?, 0, 0, 0, 0, 0)");
        $createStmt->execute([$target_user_id]);
        $current = [
            'points' => 0,
            'wins' => 0,
            'losses' => 0,
            'draws' => 0,
            'matches_played' => 0
        ];
    }

    // Store previous values for audit log
    $prev_points = intval($current['points']);
    $prev_wins = intval($current['wins']);
    $prev_losses = intval($current['losses']);
    $prev_draws = intval($current['draws']);
    $prev_matches_played = intval($current['matches_played']);

    // Build the update - only override fields that were provided
    $setClauses = [];
    $params = [];

    if ($new_points >= 0) {
        $setClauses[] = "points = ?";
        $params[] = $new_points;
    }
    if ($new_wins >= 0) {
        $setClauses[] = "wins = ?";
        $params[] = $new_wins;
    }
    if ($new_losses >= 0) {
        $setClauses[] = "losses = ?";
        $params[] = $new_losses;
    }
    if ($new_draws >= 0) {
        $setClauses[] = "draws = ?";
        $params[] = $new_draws;
    }
    if ($new_matches_played >= 0) {
        $setClauses[] = "matches_played = ?";
        $params[] = $new_matches_played;
    }

    if (empty($setClauses)) {
        $pdo->rollBack();
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'No valid fields to update']);
        exit();
    }

    $params[] = $target_user_id;
    $updateSql = "UPDATE player_points SET " . implode(", ", $setClauses) . " WHERE user_id = ?";
    $updateStmt = $pdo->prepare($updateSql);
    $updateStmt->execute($params);

    // Log the override in admin_overrides table
    $logStmt = $pdo->prepare(
        "INSERT INTO admin_overrides 
         (target_user_id, previous_points, new_points, previous_wins, new_wins, 
          previous_losses, new_losses, previous_draws, new_draws, 
          previous_matches_played, new_matches_played, reason) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    );
    $logStmt->execute([
        $target_user_id,
        $prev_points,
        $new_points >= 0 ? $new_points : $prev_points,
        $prev_wins,
        $new_wins >= 0 ? $new_wins : $prev_wins,
        $prev_losses,
        $new_losses >= 0 ? $new_losses : $prev_losses,
        $prev_draws,
        $new_draws >= 0 ? $new_draws : $prev_draws,
        $prev_matches_played,
        $new_matches_played >= 0 ? $new_matches_played : $prev_matches_played,
        !empty($reason) ? $reason : 'Admin override'
    ]);

    $pdo->commit();

    // Fetch the updated player record
    $fetchStmt = $pdo->prepare("SELECT points, wins, losses, draws, matches_played FROM player_points WHERE user_id = ?");
    $fetchStmt->execute([$target_user_id]);
    $updated = $fetchStmt->fetch();

    echo json_encode([
        'success' => true,
        'message' => 'Player stats overridden successfully',
        'user' => [
            'user_id' => $target_user_id,
            'name' => $user['name']
        ],
        'previous' => [
            'points' => $prev_points,
            'wins' => $prev_wins,
            'losses' => $prev_losses,
            'draws' => $prev_draws,
            'matches_played' => $prev_matches_played
        ],
        'updated' => [
            'points' => intval($updated['points']),
            'wins' => intval($updated['wins']),
            'losses' => intval($updated['losses']),
            'draws' => intval($updated['draws']),
            'matches_played' => intval($updated['matches_played'])
        ]
    ]);

} catch (PDOException $e) {
    $pdo->rollBack();
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to override player stats: ' . $e->getMessage()
    ]);
}