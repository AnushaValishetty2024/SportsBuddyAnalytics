<?php
require_once __DIR__ . '/db.php';

$user_id = isset($_GET['user_id']) ? intval($_GET['user_id']) : 0;
$sport_type = isset($_GET['sport_type']) ? trim($_GET['sport_type']) : '';
$skill_level = isset($_GET['skill_level']) ? trim($_GET['skill_level']) : '';
$max_distance = isset($_GET['max_distance']) ? floatval($_GET['max_distance']) : 50;
$lat = isset($_GET['lat']) ? floatval($_GET['lat']) : 0;
$lng = isset($_GET['lng']) ? floatval($_GET['lng']) : 0;

if ($user_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid user ID']);
    exit();
}

try {
    // Get connected user IDs (friends + self)
    $stmt = $pdo->prepare("
        SELECT DISTINCT CASE 
            WHEN fr.sender_id = ? THEN fr.receiver_id 
            ELSE fr.sender_id 
        END AS connected_id
        FROM friend_requests fr
        WHERE (fr.sender_id = ? OR fr.receiver_id = ?) AND fr.status = 'accepted'
    ");
    $stmt->execute([$user_id, $user_id, $user_id]);
    $connected = $stmt->fetchAll(PDO::FETCH_COLUMN);
    $connected[] = $user_id; // Exclude self

    $exclude_ids = implode(',', array_map('intval', $connected));

    // Build query
    $sql = "SELECT id, name, email, latitude, longitude FROM users WHERE id NOT IN ($exclude_ids)";
    $params = [];

    if (!empty($sport_type)) {
        $sql .= " AND id IN (SELECT DISTINCT creator_id FROM matches WHERE sport_type = ?)";
        $params[] = $sport_type;
    }

    $sql .= " ORDER BY name ASC";

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $players = $stmt->fetchAll();

    // Filter by proximity if lat/lng provided
    if ($lat != 0 && $lng != 0) {
        $filtered = [];
        foreach ($players as $player) {
            if ($player['latitude'] !== null && $player['longitude'] !== null) {
                $playerLat = floatval($player['latitude']);
                $playerLng = floatval($player['longitude']);
                if ($playerLat < -90 || $playerLat > 90 || $playerLng < -180 || $playerLng > 180) {
                    continue;
                }
                $distance = calculateDistance($lat, $lng, $playerLat, $playerLng);
                if ($distance <= $max_distance) {
                    $player['distance_km'] = round($distance, 1);
                    $filtered[] = $player;
                }
            }
            // Skip users without location - do NOT include with null distance
        }
        $players = $filtered;
        usort($players, function($a, $b) {
            if ($a['distance_km'] === null && $b['distance_km'] === null) return 0;
            if ($a['distance_km'] === null) return 1;
            if ($b['distance_km'] === null) return -1;
            return $a['distance_km'] <=> $b['distance_km'];
        });
    }

    echo json_encode([
        'success' => true,
        'players' => $players,
        'count' => count($players)
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}

function calculateDistance($lat1, $lon1, $lat2, $lon2) {
    $earthRadius = 6371;
    $dLat = deg2rad($lat2 - $lat1);
    $dLon = deg2rad($lon2 - $lon1);
    $a = sin($dLat / 2) * sin($dLat / 2) +
         cos(deg2rad($lat1)) * cos(deg2rad($lat2)) *
         sin($dLon / 2) * sin($dLon / 2);
    $c = 2 * atan2(sqrt($a), sqrt(1 - $a));
    return $earthRadius * $c;
}