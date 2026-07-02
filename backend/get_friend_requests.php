<?php
require_once __DIR__ . '/db.php';

$user_id = isset($_GET['user_id']) ? intval($_GET['user_id']) : 0;

if ($user_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid user ID']);
    exit();
}

try {
    // Get incoming pending requests (sent TO this user)
    $stmt = $pdo->prepare("
        SELECT fr.id AS request_id, fr.sender_id, fr.status, fr.created_at,
               u.name AS sender_name, u.email AS sender_email
        FROM friend_requests fr
        JOIN users u ON fr.sender_id = u.id
        WHERE fr.receiver_id = ? AND fr.status = 'pending'
        ORDER BY fr.created_at DESC
    ");
    $stmt->execute([$user_id]);
    $incoming = $stmt->fetchAll();

    // Get outgoing requests (sent BY this user) - all statuses
    $stmt = $pdo->prepare("
        SELECT fr.id AS request_id, fr.receiver_id, fr.status, fr.created_at,
               u.name AS receiver_name, u.email AS receiver_email
        FROM friend_requests fr
        JOIN users u ON fr.receiver_id = u.id
        WHERE fr.sender_id = ?
        ORDER BY fr.created_at DESC
    ");
    $stmt->execute([$user_id]);
    $outgoing = $stmt->fetchAll();

    // Get accepted friends (both directions)
    $stmt = $pdo->prepare("
        SELECT 
            fr.id AS friendship_id,
            CASE 
                WHEN fr.sender_id = ? THEN fr.receiver_id 
                ELSE fr.sender_id 
            END AS friend_id,
            u.name AS friend_name,
            u.email AS friend_email,
            fr.created_at AS friends_since
        FROM friend_requests fr
        JOIN users u ON (CASE WHEN fr.sender_id = ? THEN fr.receiver_id ELSE fr.sender_id END) = u.id
        WHERE (fr.sender_id = ? OR fr.receiver_id = ?) AND fr.status = 'accepted'
        ORDER BY u.name ASC
    ");
    $stmt->execute([$user_id, $user_id, $user_id, $user_id]);
    $friends = $stmt->fetchAll();

    echo json_encode([
        'success' => true,
        'incoming' => $incoming,
        'outgoing' => $outgoing,
        'friends' => $friends
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}