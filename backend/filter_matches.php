<?php
require_once __DIR__ . '/db.php';

$sport_name = isset($_GET['sport_name']) ? trim($_GET['sport_name']) : '';
$sport_type = isset($_GET['sport_type']) ? trim($_GET['sport_type']) : '';
$max_distance = isset($_GET['max_distance']) ? floatval($_GET['max_distance']) : 0;
$lat = isset($_GET['lat']) ? floatval($_GET['lat']) : 0;
$lng = isset($_GET['lng']) ? floatval($_GET['lng']) : 0;

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
            LEFT JOIN match_participants mp ON m.id = mp.match_id
            WHERE 1=1";

    $params = [];

    if (!empty($sport_name)) {
        $sql .= " AND LOWER(m.sport_name) = LOWER(?)";
        $params[] = $sport_name;
    }

    if (!empty($sport_type)) {
        $sql .= " AND m.sport_type = ?";
        $params[] = $sport_type;
    }

    $sql .= " GROUP BY m.id, m.creator_id, m.sport_type, m.sport_name, m.match_date, m.match_time, m.venue_name, m.venue_lat, m.venue_lng, m.max_players, m.created_at, u.name
              ORDER BY m.match_date ASC, m.match_time ASC";

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $matches = $stmt->fetchAll();

    // Filter by distance if lat/lng and max_distance provided
    if ($lat != 0 && $lng != 0 && $max_distance > 0) {
        $filtered = [];
        foreach ($matches as $match) {
            if ($match['venue_lat'] !== null && $match['venue_lng'] !== null) {
                $matchLat = floatval($match['venue_lat']);
                $matchLng = floatval($match['venue_lng']);
                if ($matchLat < -90 || $matchLat > 90 || $matchLng < -180 || $matchLng > 180) {
                    continue;
                }
                $distance = calculateDistance($lat, $lng, $matchLat, $matchLng);
                if ($distance <= $max_distance) {
                    $match['distance_km'] = round($distance, 1);
                    $filtered[] = $match;
                }
            }
            // Skip matches without location data
        }
        $matches = $filtered;
        usort($matches, function($a, $b) {
            if ($a['distance_km'] === null && $b['distance_km'] === null) return 0;
            if ($a['distance_km'] === null) return 1;
            if ($b['distance_km'] === null) return -1;
            return $a['distance_km'] <=> $b['distance_km'];
        });
    }

    echo json_encode([
        'success' => true,
        'matches' => $matches,
        'count' => count($matches)
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