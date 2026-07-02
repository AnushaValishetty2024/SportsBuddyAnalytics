<?php
require_once __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit();
}

$request_id = isset($_POST['request_id']) ? intval($_POST['request_id']) : 0;
$user_id = isset($_POST['user_id']) ? intval($_POST['user_id']) : 0;

if ($request_id <= 0 || $user_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid request ID or user ID']);
    exit();
}

try {
    // Fetch the request and verify it's pending and belongs to this user as receiver
    $stmt = $pdo->prepare("
        SELECT fr.*, u.name AS sender_name 
        FROM friend_requests fr
        JOIN users u ON fr.sender_id = u.id
        WHERE fr.id = ? AND fr.receiver_id = ? AND fr.status = 'pending'
    ");
    $stmt->execute([$request_id, $user_id]);
    $request = $stmt->fetch();

    if (!$request) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Pending request not found or unauthorized']);
        exit();
    }

    // Update status to accepted
    $stmt = $pdo->prepare("UPDATE friend_requests SET status = 'accepted' WHERE id = ?");
    $stmt->execute([$request_id]);

    echo json_encode([
        'success' => true,
        'message' => 'Friend request from ' . htmlspecialchars($request['sender_name']) . ' accepted!',
        'sender_name' => $request['sender_name']
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}