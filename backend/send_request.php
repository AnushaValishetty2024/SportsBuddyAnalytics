<?php
require_once __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit();
}

$sender_id = isset($_POST['sender_id']) ? intval($_POST['sender_id']) : 0;
$receiver_id = isset($_POST['receiver_id']) ? intval($_POST['receiver_id']) : 0;

// Validate inputs
if ($sender_id <= 0 || $receiver_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid sender or receiver ID']);
    exit();
}

// Cannot send request to self
if ($sender_id === $receiver_id) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Cannot send friend request to yourself']);
    exit();
}

try {
    // Check if sender exists
    $stmt = $pdo->prepare("SELECT id FROM users WHERE id = ?");
    $stmt->execute([$sender_id]);
    if (!$stmt->fetch()) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Sender not found']);
        exit();
    }

    // Check if receiver exists
    $stmt = $pdo->prepare("SELECT id, name FROM users WHERE id = ?");
    $stmt->execute([$receiver_id]);
    $receiver = $stmt->fetch();
    if (!$receiver) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Receiver not found']);
        exit();
    }

    // Check for existing friendship (accepted)
    $stmt = $pdo->prepare("
        SELECT id FROM friend_requests 
        WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
        AND status = 'accepted'
    ");
    $stmt->execute([$sender_id, $receiver_id, $receiver_id, $sender_id]);
    if ($stmt->fetch()) {
        echo json_encode(['success' => false, 'message' => 'Already friends with this user']);
        exit();
    }

    // Check for existing pending/rejected request (either direction)
    $stmt = $pdo->prepare("
        SELECT id, status FROM friend_requests 
        WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
        AND status IN ('pending', 'rejected')
        ORDER BY created_at DESC LIMIT 1
    ");
    $stmt->execute([$sender_id, $receiver_id, $receiver_id, $sender_id]);
    $existing = $stmt->fetch();

    if ($existing) {
        if ($existing['status'] === 'pending') {
            echo json_encode(['success' => false, 'message' => 'A pending friend request already exists']);
            exit();
        }
        // If previously rejected, allow resending by updating
        $stmt = $pdo->prepare("UPDATE friend_requests SET status = 'pending', created_at = NOW() WHERE id = ?");
        $stmt->execute([$existing['id']]);
    } else {
        // Insert new request
        $stmt = $pdo->prepare("INSERT INTO friend_requests (sender_id, receiver_id, status) VALUES (?, ?, 'pending')");
        $stmt->execute([$sender_id, $receiver_id]);
    }

    echo json_encode([
        'success' => true,
        'message' => 'Friend request sent to ' . htmlspecialchars($receiver['name'])
    ]);

} catch (PDOException $e) {
    // Handle duplicate entry gracefully
    if ($e->getCode() == 23000) {
        echo json_encode(['success' => false, 'message' => 'Friend request already exists']);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
    }
}