<?php
require_once __DIR__ . '/db.php';

$user_id = isset($_GET['user_id']) ? intval($_GET['user_id']) : 0;
$lat = isset($_GET['lat']) ? floatval($_GET['lat']) : 0;
$lng = isset($_GET['lng']) ? floatval($_GET['lng']) : 0;

if ($user_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid user ID']);
    exit();
}

try {
    // Get accepted friends with their location data
    $stmt = $pdo->prepare("
        SELECT 
            u.id,
            u.name,
            u.email,
            u.latitude AS lat,
            u.longitude AS lng,
            CASE 
                WHEN fr.sender_id = ? THEN fr.receiver_id 
                ELSE fr.sender_id 
            END AS friend_id,
            fr.created_at AS friends_since
        FROM friend_requests fr
        JOIN users u ON (CASE WHEN fr.sender_id = ? THEN fr.receiver_id ELSE fr.sender_id END) = u.id
        WHERE (fr.sender_id = ? OR fr.receiver_id = ?) AND fr.status = 'accepted'
        ORDER BY u.name ASC
    ");
    $stmt->execute([$user_id, $user_id, $user_id, $user_id]);
    $friends = $stmt->fetchAll();

    // Calculate distance for each friend if user location is provided
    $hasUserLocation = ($lat != 0 && $lng != 0);
    $result = [];

    foreach ($friends as $friend) {
        $friendLat = $friend['lat'];
        $friendLng = $friend['lng'];

        // Only include if friend has valid location data
        if ($friendLat === null || $friendLng === null) {
            continue; // Exclude users without location
        }

        $friendLat = floatval($friendLat);
        $friendLng = floatval($friendLng);

        // Validate coordinates
        if ($friendLat < -90 || $friendLat > 90 || $friendLng < -180 || $friendLng > 180) {
            continue; // Exclude users with invalid coordinates
        }

        $entry = [
            'id' => (int)$friend['id'],
            'name' => $friend['name'],
            'email' => $friend['email'],
            'lat' => $friendLat,
            'lng' => $friendLng,
            'is_online' => false
        ];

        if ($hasUserLocation) {
            $distance = calculateDistance($lat, $lng, $friendLat, $friendLng);
            $entry['distance_km'] = round($distance, 1);
        } else {
            $entry['distance_km'] = null;
        }

        $result[] = $entry;
    }

    // Sort by distance (closest first), null at end
    usort($result, function($a, $b) {
        if ($a['distance_km'] === null && $b['distance_km'] === null) return 0;
        if ($a['distance_km'] === null) return 1;
        if ($b['distance_km'] === null) return -1;
        return $a['distance_km'] <=> $b['distance_km'];
    });

    echo json_encode([
        'success' => true,
        'friends' => $result,
        'count' => count($result)
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}

/**
 * Calculate distance between two coordinates using Haversine formula
 */
function calculateDistance($lat1, $lon1, $lat2, $lon2) {
    $earthRadius = 6371; // km
    $dLat = deg2rad($lat2 - $lat1);
    $dLon = deg2rad($lon2 - $lon1);
    $a = sin($dLat / 2) * sin($dLat / 2) +
         cos(deg2rad($lat1)) * cos(deg2rad($lat2)) *
         sin($dLon / 2) * sin($dLon / 2);
    $c = 2 * atan2(sqrt($a), sqrt(1 - $a));
    return $earthRadius * $c;
}