<?php session_start(); ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teams - Sports Buddy</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🏆 Sports Buddy</h1>
            <p class="subtitle">Find Your Team</p>
        </header>

        <!-- Navigation -->
        <nav class="main-nav">
            <a href="index.html" class="btn btn-secondary" style="width:auto;margin-top:0;">← Back to Home</a>
            <a href="create_team.php" class="btn btn-primary" style="width:auto;margin-top:0;">+ Create Team</a>
        </nav>

        <main>
            <!-- Teams Section -->
            <section class="teams-section">
                <h2>All Teams</h2>

                <!-- Search and Filters -->
                <div class="teams-filters">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="searchTeam">Search Team</label>
                            <input type="text" id="searchTeam" placeholder="Search by team name...">
                        </div>
                        <div class="form-group">
                            <label for="filterSport">Filter by Sport</label>
                            <select id="filterSport">
                                <option value="">All Sports</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="filterLocation">Filter by Location</label>
                            <input type="text" id="filterLocation" placeholder="Filter by location...">
                        </div>
                    </div>
                </div>

                <!-- Teams List -->
                <div id="teamsList" class="teams-list">
                    <p class="loading">Loading teams...</p>
                </div>
            </section>
        </main>

        <!-- Footer -->
        <footer>
            <p>&copy; 2026 Sports Buddy. All rights reserved.</p>
        </footer>
    </div>

    <script>
        let allTeams = [];

        // Load teams on page load
        document.addEventListener('DOMContentLoaded', loadTeams);

        // Search and filter listeners
        document.getElementById('searchTeam').addEventListener('input', renderTeams);
        document.getElementById('filterSport').addEventListener('change', renderTeams);
        document.getElementById('filterLocation').addEventListener('input', renderTeams);

        async function loadTeams() {
            try {
                const response = await fetch('backend/get_teams.php');
                const result = await response.json();

                if (result.success) {
                    allTeams = result.teams;
                    populateSportFilter(allTeams);
                    renderTeams();
                } else {
                    document.getElementById('teamsList').innerHTML = 
                        '<p class="error">Failed to load teams: ' + result.message + '</p>';
                }
            } catch (error) {
                document.getElementById('teamsList').innerHTML = 
                    '<p class="error">An error occurred while loading teams.</p>';
            }
        }

        function populateSportFilter(teams) {
            const sports = [...new Set(teams.map(t => t.sport_type))].sort();
            const select = document.getElementById('filterSport');
            
            sports.forEach(sport => {
                const option = document.createElement('option');
                option.value = sport;
                option.textContent = sport;
                select.appendChild(option);
            });
        }

        function renderTeams() {
            const searchTerm = document.getElementById('searchTeam').value.toLowerCase();
            const sportFilter = document.getElementById('filterSport').value;
            const locationFilter = document.getElementById('filterLocation').value.toLowerCase();

            const filteredTeams = allTeams.filter(team => {
                const matchesSearch = team.team_name.toLowerCase().includes(searchTerm);
                const matchesSport = !sportFilter || team.sport_type === sportFilter;
                const matchesLocation = !locationFilter || team.location.toLowerCase().includes(locationFilter);
                
                return matchesSearch && matchesSport && matchesLocation;
            });

            const container = document.getElementById('teamsList');

            if (filteredTeams.length === 0) {
                container.innerHTML = '<p class="no-teams">No teams found. Be the first to create a team!</p>';
                return;
            }

            container.innerHTML = filteredTeams.map(team => {
                const logoHtml = team.logo 
                    ? `<img src="${team.logo}" alt="${team.team_name} logo" class="team-logo">`
                    : `<div class="team-logo-placeholder">🏆</div>`;

                const memberProgress = (team.current_members / team.max_members) * 100;
                const progressClass = memberProgress >= 100 ? 'full' : memberProgress >= 80 ? 'almost-full' : '';

                return `
                    <div class="team-card">
                        <div class="team-card-header">
                            ${logoHtml}
                            <div class="team-info">
                                <h3>${escapeHtml(team.team_name)}</h3>
                                <p class="team-captain">Captain: ${escapeHtml(team.captain_name)}</p>
                            </div>
                        </div>
                        <div class="team-card-body">
                            <div class="team-detail">
                                <span class="label">Sport:</span>
                                <span class="value">${escapeHtml(team.sport_type)}</span>
                            </div>
                            <div class="team-detail">
                                <span class="label">Location:</span>
                                <span class="value">${escapeHtml(team.location)}</span>
                            </div>
                            <div class="team-detail">
                                <span class="label">Members:</span>
                                <span class="value">${team.current_members} / ${team.max_members}</span>
                            </div>
                            <div class="progress-bar ${progressClass}">
                                <div class="progress-fill" style="width: ${Math.min(memberProgress, 100)}%"></div>
                            </div>
                        </div>
                        <div class="team-card-actions">
                            <a href="team_details.php?team_id=${team.id}" class="btn btn-primary">View Details</a>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>