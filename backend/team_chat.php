<?php
require_once __DIR__ . '/db.php';
session_start();
header('Content-Type: application/json');

// Handle both GET and POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Post a new message
    $team_id = isset($_POST['team_id']) ? intval($_POST['team_id']) : 0;
    
    // Get message from either POST body or JSON input
    $message = '';
    if (isset($_POST['message'])) {
        $message = trim($_POST['message']);
    } elseif (file_get_contents('php://input')) {
        $input = json_decode(file_get_contents('php://input'), true);
        $message = isset($input['message']) ? trim($input['message']) : '';
    }
    
    if ($team_id <= 0) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid team ID']);
        exit();
    }
    
    if (empty($message) || !isset($_SESSION['user_id'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Message cannot be empty']);
        exit();
    }
    
    try {
        // Verify user is team member
        $memberStmt = $pdo->prepare("
            SELECT tm.id FROM team_members tm
            WHERE tm.team_id = ? AND tm.user_id = ?
        ");
        $memberStmt->execute([$team_id, $_SESSION['user_id']]);
        
        if (!$memberStmt->fetch()) {
            http_response_code(403);
            echo json_encode(['success' => false, 'message' => 'You must be a team member to chat']);
            exit();
        }
        
        // Insert message
        $stmt = $pdo->prepare("
            INSERT INTO team_chat_messages (team_id, user_id, message, timestamp)
            VALUES (?, ?, ?, NOW())
        ");
        $stmt->execute([$team_id, $_SESSION['user_id'], $message]);
        
        echo json_encode([
            'success' => true,
            'message' => 'Message sent successfully',
            'message_id' => $pdo->lastInsertId()
        ]);
        
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Failed to send message: ' . $e->getMessage()
        ]);
    }
    
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // Get last 50 messages
    $team_id = isset($_GET['team_id']) ? intval($_GET['team_id']) : 0;
    
    if ($team_id <= 0) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid team ID']);
        exit();
    }
    
    try {
        $stmt = $pdo->prepare("
            SELECT 
                m.id,
                m.message,
                m.timestamp,
                u.id as user_id,
                u.name as user_name
            FROM team_chat_messages m
            LEFT JOIN users u ON m.user_id = u.id
            WHERE m.team_id = ?
            ORDER BY m.timestamp DESC
            LIMIT 50
        ");
        
        $stmt->execute([$team_id]);
        $messages = $stmt->fetchAll();
        
        // Reverse to show oldest first
        $messages = array_reverse($messages);
        
        // Format timestamps
        foreach ($messages as &$msg) {
            $msg['timestamp'] = date('M d, Y H:i', strtotime($msg['timestamp']));
        }
        
        echo json_encode([
            'success' => true,
            'messages' => $messages
        ]);
        
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Failed to fetch messages: ' . $e->getMessage()
        ]);
    }
} else {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only GET and POST methods allowed']);
    exit();
}
?>