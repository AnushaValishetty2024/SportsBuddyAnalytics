<?php
require_once __DIR__ . '/db.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'You must be logged in to create a team']);
    exit();
}

$captain_id = $_SESSION['user_id'];
$team_name = isset($_POST['team_name']) ? trim($_POST['team_name']) : '';
$description = isset($_POST['description']) ? trim($_POST['description']) : '';
$sport_type = isset($_POST['sport_type']) ? trim($_POST['sport_type']) : '';
$location = isset($_POST['location']) ? trim($_POST['location']) : '';
$max_members = isset($_POST['max_members']) ? intval($_POST['max_members']) : 10;

$errors = [];

if (empty($team_name)) {
    $errors[] = 'Team name is required';
}
if (strlen($team_name) > 100) {
    $errors[] = 'Team name must be less than 100 characters';
}
if (empty($sport_type)) {
    $errors[] = 'Sport type is required';
}
if (empty($location)) {
    $errors[] = 'Location is required';
}
if ($max_members < 2) {
    $errors[] = 'Maximum members must be at least 2';
}
if ($max_members > 100) {
    $errors[] = 'Maximum members cannot exceed 100';
}

// Handle logo upload
$logo = null;
if (isset($_FILES['logo']) && $_FILES['logo']['error'] === UPLOAD_ERR_OK) {
    $allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    $max_size = 5 * 1024 * 1024; // 5MB

    $file_type = $_FILES['logo']['type'];
    $file_size = $_FILES['logo']['size'];

    if (!in_array($file_type, $allowed_types)) {
        $errors[] = 'Invalid logo format. Please upload JPG, PNG, GIF, or WebP';
    }
    if ($file_size > $max_size) {
        $errors[] = 'Logo file size must be less than 5MB';
    }

    if (empty($errors)) {
        $upload_dir = 'uploads/logos/';
        if (!file_exists($upload_dir)) {
            mkdir($upload_dir, 0777, true);
        }

        $file_extension = pathinfo($_FILES['logo']['name'], PATHINFO_EXTENSION);
        $logo_filename = uniqid('team_logo_') . '.' . $file_extension;
        $logo_path = $upload_dir . $logo_filename;

        if (move_uploaded_file($_FILES['logo']['tmp_name'], $logo_path)) {
            $logo = $logo_path;
        } else {
            $errors[] = 'Failed to upload logo';
        }
    }
}

if (!empty($errors)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => implode('. ', $errors)]);
    exit();
}

try {
    // Check if team name already exists
    $checkStmt = $pdo->prepare("SELECT id FROM teams WHERE team_name = ?");
    $checkStmt->execute([$team_name]);
    if ($checkStmt->fetch()) {
        http_response_code(409);
        echo json_encode(['success' => false, 'message' => 'Team name already exists']);
        exit();
    }

    // Create team
    $sql = "INSERT INTO teams (team_name, description, sport_type, location, logo, captain_id, max_members) 
            VALUES (?, ?, ?, ?, ?, ?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$team_name, $description, $sport_type, $location, $logo, $captain_id, $max_members]);

    $team_id = $pdo->lastInsertId();

    // Automatically add captain as first member
    $memberSql = "INSERT INTO team_members (team_id, user_id) VALUES (?, ?)";
    $memberStmt = $pdo->prepare($memberSql);
    $memberStmt->execute([$team_id, $captain_id]);

    echo json_encode([
        'success' => true,
        'message' => 'Team created successfully',
        'team_id' => intval($team_id)
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to create team: ' . $e->getMessage()
    ]);
}

</parameter>
</parameter>
</tool_call>

<execute_command>
<command>mysql -u root sports_buddy < sql/teams_migration.sql</command>
<requires_approval>false</requires_approval>
</execute_command>