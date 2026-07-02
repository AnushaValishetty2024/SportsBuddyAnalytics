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
    <title>Edit Team - Sports Buddy</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🏆 Sports Buddy</h1>
            <p class="subtitle">Edit Your Team</p>
        </header>

        <!-- Navigation -->
        <nav class="main-nav">
            <a href="index.html" class="btn btn-secondary" style="width:auto;margin-top:0;">← Back to Home</a>
            <a href="teams.php" class="btn btn-primary" style="width:auto;margin-top:0;">View Teams</a>
        </nav>

        <main>
            <!-- Edit Team Form -->
            <section class="edit-team-section">
                <h2>Edit Team</h2>
                <form id="editTeamForm" enctype="multipart/form-data">
                    <input type="hidden" id="team_id" name="team_id" value="">

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
                            <input type="number" id="max_members" name="max_members" min="2" max="100" required>
                        </div>
                    </div>

                    <div class="form-group full-width">
                        <label for="description">Description</label>
                        <textarea id="description" name="description" rows="4" placeholder="Describe your team..." maxlength="500"></textarea>
                    </div>

                    <div class="form-group full-width">
                        <label for="logo">Team Logo (Optional - leave empty to keep current)</label>
                        <input type="file" id="logo" name="logo" accept="image/jpeg,image/png,image/gif,image/webp">
                        <small>Max size: 5MB. Formats: JPG, PNG, GIF, WebP</small>
                        <div id="currentLogo" style="margin-top: 10px;"></div>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Update Team</button>
                        <a href="team_details.php?team_id=" id="backToDetails" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
                <div id="editMessage" class="message"></div>
            </section>
        </main>

        <!-- Footer -->
        <footer>
            <p>&copy; 2026 Sports Buddy. All rights reserved.</p>
        </footer>
    </div>

    <script>
        let currentTeamId = null;

        // Get team ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        currentTeamId = urlParams.get('team_id');

        if (!currentTeamId) {
            document.querySelector('.edit-team-section').innerHTML = 
                '<p class="error">Team ID not provided.</p>';
        } else {
            document.getElementById('team_id').value = currentTeamId;
            document.getElementById('backToDetails').href = 'team_details.php?team_id=' + currentTeamId;
            loadTeamData();
        }

        async function loadTeamData() {
            try {
                const response = await fetch('backend/get_team_details.php?team_id=' + currentTeamId);
                const result = await response.json();

                if (result.success && result.is_captain) {
                    const { team } = result;
                    
                    document.getElementById('team_name').value = team.team_name;
                    document.getElementById('sport_type').value = team.sport_type;
                    document.getElementById('location').value = team.location;
                    document.getElementById('max_members').value = team.max_members;
                    document.getElementById('description').value = team.description || '';

                    // Show current logo
                    const logoContainer = document.getElementById('currentLogo');
                    if (team.logo) {
                        logoContainer.innerHTML = `<img src="${team.logo}" alt="Current logo" style="max-width: 200px; max-height: 200px;">`;
                    }
                } else {
                    document.querySelector('.edit-team-section').innerHTML = 
                        '<p class="error">Team not found or you do not have permission to edit it.</p>';
                }
            } catch (error) {
                document.querySelector('.edit-team-section').innerHTML = 
                    '<p class="error">An error occurred while loading team data.</p>';
            }
        }

        document.getElementById('editTeamForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const messageDiv = document.getElementById('editMessage');
            messageDiv.innerHTML = '<p class="loading">Updating team...</p>';
            messageDiv.className = 'message';

            const formData = new FormData(this);

            try {
                const response = await fetch('backend/update_team.php', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    messageDiv.innerHTML = '<p class="success">' + result.message + '! Redirecting...</p>';
                    messageDiv.className = 'message success';
                    setTimeout(() => {
                        window.location.href = 'team_details.php?team_id=' + currentTeamId;
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