<?php
require_once __DIR__ . '/db.php';

if (!isset($_GET['id']) || empty(trim($_GET['id']))) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Match ID is required']);
    exit();
}

$match_id = intval($_GET['id']);

try {
    // Fetch match details with creator name
    $matchSql = "SELECT 
                    m.id,
                    m.creator_id,
                    m.sport_type,
                    m.sport_name,
                    m.match_date,
                    m.match_time,
                    m.venue_name,
                    m.max_players,
                    m.created_at,
                    u.name AS creator_name
                FROM matches m
                JOIN users u ON m.creator_id = u.id
                WHERE m.id = ?";

    $matchStmt = $pdo->prepare($matchSql);
    $matchStmt->execute([$match_id]);
    $match = $matchStmt->fetch();

    if (!$match) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Match not found']);
        exit();
    }

    // Fetch participant list with user names via JOIN
    $participantSql = "SELECT 
                        mp.id AS participant_id,
                        mp.user_id,
                        mp.joined_at,
                        u.name AS user_name,
                        u.email AS user_email
                      FROM match_participants mp
                      JOIN users u ON mp.user_id = u.id
                      WHERE mp.match_id = ?
                      ORDER BY mp.joined_at ASC";

    $participantStmt = $pdo->prepare($participantSql);
    $participantStmt->execute([$match_id]);
    $participants = $participantStmt->fetchAll();

    // Determine match status
    $joinedCount = count($participants);
    $maxPlayers = intval($match['max_players']);

    if ($joinedCount >= $maxPlayers) {
        $status = 'Full';
    } else {
        $status = 'Open';
    }

    echo json_encode([
        'success' => true,
        'match' => $match,
        'participants' => $participants,
        'joined_count' => $joinedCount,
        'status' => $status
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch match details: ' . $e->getMessage()
    ]);
}