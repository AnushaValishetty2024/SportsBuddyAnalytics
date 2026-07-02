<?php
session_start();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Team - Sports Buddy</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🏆 Sports Buddy</h1>
            <p class="subtitle">Create Your Team</p>
        </header>

        <!-- Navigation -->
        <nav class="main-nav">
            <a href="index.html" class="btn btn-secondary" style="width:auto;margin-top:0;">← Back to Home</a>
            <a href="teams.php" class="btn btn-primary" style="width:auto;margin-top:0;">View Teams</a>
        </nav>

        <main>
            <!-- Create Team Form -->
            <section class="create-team-section">
                <h2>Create New Team</h2>
                <form id="createTeamForm" enctype="multipart/form-data">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="team_name">Team Name *</label>
                            <input type="text" id="team_name" name="team_name" placeholder="Enter team name" required maxlength="100">
                        </div>
                        <div class="form-group">
                            <label for="sport_type">Sport Type *</label>
                            <input type="text" id="sport_type" name="sport_type" placeholder="e.g. Cricket, Football" required>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="location">Location *</label>
                            <input type="text" id="location" name="location" placeholder="e.g. Vijayawada" required>
                        </div>
                        <div class="form-group">
                            <label for="max_members">Maximum Members *</label>
                            <input type="number" id="max_members" name="max_members" min="2" max="100" value="10" required>
                        </div>
                    </div>

                    <div class="form-group full-width">
                        <label for="description">Description</label>
                        <textarea id="description" name="description" rows="4" placeholder="Describe your team..." maxlength="500"></textarea>
                    </div>

                    <div class="form-group full-width">
                        <label for="logo">Team Logo (Optional)</label>
                        <input type="file" id="logo" name="logo" accept="image/jpeg,image/png,image/gif,image/webp">
                        <small>Max size: 5MB. Formats: JPG, PNG, GIF, WebP</small>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Create Team</button>
                        <button type="reset" class="btn btn-secondary">Clear Form</button>
                    </div>
                </form>
                <div id="createMessage" class="message"></div>
            </section>
        </main>

        <!-- Footer -->
        <footer>
            <p>&copy; 2026 Sports Buddy. All rights reserved.</p>
        </footer>
    </div>

    <script>
        document.getElementById('createTeamForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const messageDiv = document.getElementById('createMessage');
            messageDiv.innerHTML = '<p class="loading">Creating team...</p>';
            messageDiv.className = 'message';

            const formData = new FormData(this);

            try {
                const response = await fetch('backend/create_team.php', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    messageDiv.innerHTML = '<p class="success">' + result.message + '! Redirecting...</p>';
                    messageDiv.className = 'message success';
                    setTimeout(() => {
                        window.location.href = 'team_details.php?team_id=' + result.team_id;
                    }, 1500);
                } else {
                    messageDiv.innerHTML = '<p class="error">' + result.message + '</p>';
                    messageDiv.className = 'message error';
                }
            } catch (error) {
                messageDiv.innerHTML = '<p class="error">An error occurred. Please try again.</p>';
                messageDiv.className = 'message error';
            }
        });
    </script>
</body>
</html>