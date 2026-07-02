<?php
session_start();

// Check if user is logged in (optional - some features require login)
$user_id = isset($_SESSION['user_id']) ? $_SESSION['user_id'] : null;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Details - Sports Buddy</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🏆 Sports Buddy</h1>
            <p class="subtitle">Team Details</p>
        </header>

        <!-- Navigation -->
        <nav class="main-nav">
            <a href="index.html" class="btn btn-secondary" style="width:auto;margin-top:0;">← Back to Home</a>
            <a href="teams.php" class="btn btn-primary" style="width:auto;margin-top:0;">View All Teams</a>
        </nav>

        <main>
            <!-- Team Details -->
            <section class="team-details-section" id="teamDetails">
                <p class="loading">Loading team details...</p>
            </section>
        </main>

        <!-- Footer -->
        <footer>
            <p>&copy; 2026 Sports Buddy. All rights reserved.</p>
        </footer>
    </div>

    <script>
        let currentTeamId = null;
        let teamData = null;

        // Get team ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        currentTeamId = urlParams.get('team_id');

        if (!currentTeamId) {
            document.getElementById('teamDetails').innerHTML = 
                '<p class="error">Team ID not provided.</p>';
        } else {
            loadTeamDetails();
        }

        async function loadTeamDetails() {
            try {
                const response = await fetch('backend/get_team_details.php?team_id=' + currentTeamId);
                const result = await response.json();

                if (result.success) {
                    teamData = result;
                    renderTeamDetails(result);
                } else {
                    document.getElementById('teamDetails').innerHTML = 
                        '<p class="error">' + result.message + '</p>';
                }
            } catch (error) {
                document.getElementById('teamDetails').innerHTML = 
                    '<p class="error">An error occurred while loading team details.</p>';
            }
        }

        function renderTeamDetails(data) {
            const { team, members, is_captain, is_member } = data;
            const container = document.getElementById('teamDetails');

            const logoHtml = team.logo 
                ? `<img src="${team.logo}" alt="${team.team_name} logo" class="team-logo-large">`
                : `<div class="team-logo-large-placeholder">🏆</div>`;

            const memberProgress = (members.length / team.max_members) * 100;
            const progressClass = memberProgress >= 100 ? 'full' : memberProgress >= 80 ? 'almost-full' : '';

            let actionsHtml = '';

            if (<?php echo $user_id ? 'true' : 'false'; ?> && !is_member) {
                actionsHtml = `
                    <button onclick="joinTeam()" class="btn btn-primary btn-large">Join Team</button>
                `;
            } else if (<?php echo $user_id ? 'true' : 'false'; ?> && is_member && !is_captain) {
                actionsHtml = `
                    <button onclick="leaveTeam()" class="btn btn-danger btn-large">Leave Team</button>
                `;
            }

            if (is_captain) {
                actionsHtml = `
                    <a href="edit_team.php?team_id=${team.id}" class="btn btn-secondary btn-large">Edit Team</a>
                    <button onclick="deleteTeam()" class="btn btn-danger btn-large">Delete Team</button>
                ` + actionsHtml;
            }

            container.innerHTML = `
                <div class="team-detail-card">
                    <div class="team-header">
                        ${logoHtml}
                        <div class="team-title">
                            <h2>${escapeHtml(team.team_name)}</h2>
                            <p class="team-sport">${escapeHtml(team.sport_type)}</p>
                        </div>
                    </div>

                    <div class="team-info-grid">
                        <div class="info-item">
                            <span class="info-label">Captain:</span>
                            <span class="info-value">${escapeHtml(team.captain_name)}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Location:</span>
                            <span class="info-value">${escapeHtml(team.location)}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Created:</span>
                            <span class="info-value">${new Date(team.created_at).toLocaleDateString()}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Max Members:</span>
                            <span class="info-value">${team.max_members}</span>
                        </div>
                    </div>

                    <div class="team-description">
                        <h3>Description</h3>
                        <p>${team.description ? escapeHtml(team.description) : 'No description provided.'}</p>
                    </div>

                    <div class="team-members-count">
                        <h3>Current Members: ${members.length} / ${team.max_members}</h3>
                        <div class="progress-bar ${progressClass}">
                            <div class="progress-fill" style="width: ${Math.min(memberProgress, 100)}%"></div>
                        </div>
                    </div>

                    <div class="team-actions">
                        ${actionsHtml}
                    </div>
                </div>

                <div class="members-section">
                    <h3>Members</h3>
                    <div class="members-list">
                        ${members.map(member => `
                            <div class="member-card">
                                <div class="member-avatar">
                                    ${member.profile_picture 
                                        ? `<img src="${member.profile_picture}" alt="${member.name}">` 
                                        : `<span>${member.name.charAt(0).toUpperCase()}</span>`}
                                </div>
                                <div class="member-info">
                                    <p class="member-name">${escapeHtml(member.name)}</p>
                                    <p class="member-joined">Joined: ${new Date(member.joined_at).toLocaleDateString()}</p>
                                </div>
                                ${is_captain && member.id != team.captain_id ? 
                                    `<button onclick="removeMember(${member.id})" class="btn btn-sm btn-danger">Remove</button>` 
                                    : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        async function joinTeam() {
            try {
                const formData = new FormData();
                formData.append('team_id', currentTeamId);

                const response = await fetch('backend/join_team.php', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert(result.message);
                    loadTeamDetails();
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
            }
        }

        async function leaveTeam() {
            if (!confirm('Are you sure you want to leave this team?')) return;

            try {
                const formData = new FormData();
                formData.append('team_id', currentTeamId);

                const response = await fetch('backend/leave_team.php', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert(result.message);
                    window.location.href = 'teams.php';
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
            }
        }

        async function removeMember(memberId) {
            if (!confirm('Are you sure you want to remove this member?')) return;

            try {
                const formData = new FormData();
                formData.append('team_id', currentTeamId);
                formData.append('member_id', memberId);

                const response = await fetch('backend/remove_member.php', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert('Member removed successfully');
                    loadTeamDetails();
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
            }
        }

        async function deleteTeam() {
            if (!confirm('Are you sure you want to delete this team? This action cannot be undone.')) return;

            try {
                const formData = new FormData();
                formData.append('team_id', currentTeamId);

                const response = await fetch('backend/delete_team.php', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert(result.message);
                    window.location.href = 'teams.php';
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>