<?php
require_once __DIR__ . '/db.php';

try {
    $sql = "SELECT 
                m.id,
                m.creator_id,
                m.sport_type,
                m.sport_name,
                m.match_date,
                m.match_time,
                m.venue_name,
                m.venue_lat,
                m.venue_lng,
                m.max_players,
                m.created_at,
                u.name AS creator_name,
                COUNT(mp.id) AS joined_players
            FROM matches m
            JOIN users u ON m.creator_id = u.id
            LEFT JOIN match_participants mp ON m.id = mp.match_id";

    // Build WHERE clause dynamically
    $whereClauses = [];
    $params = [];

    // Filter by sport_name if provided
    if (isset($_GET['sport']) && !empty(trim($_GET['sport']))) {
        $sport = trim($_GET['sport']);
        $whereClauses[] = "LOWER(m.sport_name) = LOWER(?)";
        $params[] = $sport;
    }

    // Filter by place_type (indoor/outdoor) if provided - FIX FOR ISSUE #2
    if (isset($_GET['place_type']) && !empty(trim($_GET['place_type']))) {
        $placeType = trim($_GET['place_type']);
        $whereClauses[] = "m.sport_type = ?";
        $params[] = $placeType;
    }

    if (!empty($whereClauses)) {
        $sql .= " WHERE " . implode(" AND ", $whereClauses);
    }

    $sql .= " GROUP BY m.id, m.creator_id, m.sport_type, m.sport_name, m.match_date, m.match_time, m.venue_name, m.venue_lat, m.venue_lng, m.max_players, m.created_at, u.name
              ORDER BY m.match_date ASC, m.match_time ASC";

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $matches = $stmt->fetchAll();

    echo json_encode([
        'success' => true,
        'matches' => $matches
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to fetch matches: ' . $e->getMessage()
    ]);
}