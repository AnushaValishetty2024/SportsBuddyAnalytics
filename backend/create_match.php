<?php
require_once __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

$creator_id = isset($_POST['creator_id']) ? intval($_POST['creator_id']) : 0;
$sport_type = isset($_POST['sport_type']) ? trim($_POST['sport_type']) : '';
$sport_name = isset($_POST['sport_name']) ? trim($_POST['sport_name']) : '';
$match_date = isset($_POST['match_date']) ? trim($_POST['match_date']) : '';
$match_time = isset($_POST['match_time']) ? trim($_POST['match_time']) : '';
$venue_name = isset($_POST['venue_name']) ? trim($_POST['venue_name']) : '';
$venue_lat = isset($_POST['venue_lat']) ? floatval($_POST['venue_lat']) : null;
$venue_lng = isset($_POST['venue_lng']) ? floatval($_POST['venue_lng']) : null;
$max_players = isset($_POST['max_players']) ? intval($_POST['max_players']) : 0;

$errors = [];

if ($creator_id <= 0) {
    $errors[] = 'Invalid creator';
}
if (!in_array($sport_type, ['indoor', 'outdoor'])) {
    $errors[] = 'Sport type must be indoor or outdoor';
}
if (empty($sport_name)) {
    $errors[] = 'Sport name is required';
}
if (empty($match_date)) {
    $errors[] = 'Match date is required';
}
if (empty($match_time)) {
    $errors[] = 'Match time is required';
}
if (empty($venue_name)) {
    $errors[] = 'Venue name is required';
}
if ($max_players < 2) {
    $errors[] = 'Max players must be at least 2';
}

if (!empty($errors)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => implode('. ', $errors)]);
    exit();
}

// Verify creator exists
$checkUser = $pdo->prepare("SELECT id FROM users WHERE id = ?");
$checkUser->execute([$creator_id]);
if (!$checkUser->fetch()) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Creator user not found']);
    exit();
}

try {
    $sql = "INSERT INTO matches (creator_id, sport_type, sport_name, match_date, match_time, venue_name, venue_lat, venue_lng, max_players) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$creator_id, $sport_type, $sport_name, $match_date, $match_time, $venue_name, $venue_lat, $venue_lng, $max_players]);

    $match_id = $pdo->lastInsertId();

    echo json_encode([
        'success' => true,
        'message' => 'Match created successfully',
        'match_id' => intval($match_id)
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to create match: ' . $e->getMessage()
    ]);
}