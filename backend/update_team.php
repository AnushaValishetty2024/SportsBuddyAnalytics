<?php
require_once __DIR__ . '/db.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Only POST method allowed']);
    exit();
}

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'You must be logged in to edit a team']);
    exit();
}

$user_id = $_SESSION['user_id'];
$team_id = isset($_POST['team_id']) ? intval($_POST['team_id']) : 0;

if ($team_id <= 0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid team ID']);
    exit();
}

try {
    // Get team and verify captain
    $teamStmt = $pdo->prepare("SELECT * FROM teams WHERE id = ?");
    $teamStmt->execute([$team_id]);
    $team = $teamStmt->fetch();

    if (!$team) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit();
    }

    if ($team['captain_id'] != $user_id) {
        http_response_code(403);
        echo json_encode(['success' => false, 'message' => 'Only the team captain can edit the team']);
        exit();
    }

    $team_name = isset($_POST['team_name']) ? trim($_POST['team_name']) : $team['team_name'];
    $description = isset($_POST['description']) ? trim($_POST['description']) : $team['description'];
    $sport_type = isset($_POST['sport_type']) ? trim($_POST['sport_type']) : $team['sport_type'];
    $location = isset($_POST['location']) ? trim($_POST['location']) : $team['location'];
    $max_members = isset($_POST['max_members']) ? intval($_POST['max_members']) : $team['max_members'];

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

    // Check if team name is taken by another team
    $checkStmt = $pdo->prepare("SELECT id FROM teams WHERE team_name = ? AND id != ?");
    $checkStmt->execute([$team_name, $team_id]);
    if ($checkStmt->fetch()) {
        $errors[] = 'Team name already exists';
    }

    if (!empty($errors)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => implode('. ', $errors)]);
        exit();
    }

    // Handle logo upload
    $logo = $team['logo'];
    if (isset($_FILES['logo']) && $_FILES['logo']['error'] === UPLOAD_ERR_OK) {
        $allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        $max_size = 5 * 1024 * 1024;

        $file_type = $_FILES['logo']['type'];
        $file_size = $_FILES['logo']['size'];

        if (!in_array($file_type, $allowed_types)) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Invalid logo format']);
            exit();
        }
        if ($file_size > $max_size) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Logo file size must be less than 5MB']);
            exit();
        }

        $upload_dir = 'uploads/logos/';
        if (!file_exists($upload_dir)) {
            mkdir($upload_dir, 0777, true);
        }

        // Delete old logo if exists
        if ($logo && file_exists($logo)) {
            unlink($logo);
        }

        $file_extension = pathinfo($_FILES['logo']['name'], PATHINFO_EXTENSION);
        $logo_filename = uniqid('team_logo_') . '.' . $file_extension;
        $logo = $upload_dir . $logo_filename;

        if (!move_uploaded_file($_FILES['logo']['tmp_name'], $logo)) {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Failed to upload logo']);
            exit();
        }
    }

    // Update team
    $sql = "UPDATE teams SET team_name = ?, description = ?, sport_type = ?, location = ?, logo = ?, max_members = ?
            WHERE id = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$team_name, $description, $sport_type, $location, $logo, $max_members, $team_id]);

    echo json_encode([
        'success' => true,
        'message' => 'Team updated successfully'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Failed to update team: ' . $e->getMessage()
    ]);
}