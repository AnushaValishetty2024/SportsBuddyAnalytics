// =============================================================
// Sports Buddy - Dashboard JavaScript
// Handles: Discover filter, Join Match, Map, All Games, Game Details
// =============================================================

(function () {
    'use strict';

    let currentJoinMatchId = null;
    let currentGameId = null;
    let currentGameName = null;
    let dashboardMap = null;
    let matchMarkers = [];
    let businessMarkers = [];
    let currentLayer = 'matches';

    // =============================================================
    // SPORT ICON MAP - SVG data URIs for each sport
    // =============================================================
    const SPORT_ICONS = {
        'cricket': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><rect x="37" y="10" width="6" height="20" rx="3" fill="#22c55e"/><ellipse cx="40" cy="10" rx="8" ry="4" fill="#22c55e"/><circle cx="40" cy="48" r="14" fill="none" stroke="#22c55e" stroke-width="2.5"/><line x1="28" y1="36" x2="52" y2="60" stroke="#22c55e" stroke-width="2" stroke-linecap="round"/><line x1="52" y1="36" x2="28" y2="60" stroke="#22c55e" stroke-width="2" stroke-linecap="round"/></svg>',
        'football': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="40" r="20" fill="none" stroke="#22c55e" stroke-width="2"/><polygon points="40,20 45,35 60,35 48,45 52,60 40,50 28,60 32,45 20,35 35,35" fill="#22c55e" opacity="0.6"/></svg>',
        'badminton': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><ellipse cx="40" cy="25" rx="10" ry="5" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="30" x2="40" y2="55" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="55" x2="30" y2="65" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="55" x2="50" y2="65" stroke="#22c55e" stroke-width="2"/><path d="M40 35 L30 40 M40 35 L50 40" stroke="#22c55e" stroke-width="1.5"/><line x1="20" y1="55" x2="60" y2="55" stroke="#22c55e" stroke-width="2" stroke-dasharray="4,3"/></svg>',
        'basketball': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="40" r="20" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="20" x2="40" y2="60" stroke="#22c55e" stroke-width="1.5"/><line x1="20" y1="30" x2="60" y2="30" stroke="#22c55e" stroke-width="1"/><line x1="20" y1="50" x2="60" y2="50" stroke="#22c55e" stroke-width="1"/><path d="M30 20 Q20 40 30 60" stroke="#22c55e" stroke-width="1" fill="none"/><path d="M50 20 Q60 40 50 60" stroke="#22c55e" stroke-width="1" fill="none"/></svg>',
        'tennis': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="38" cy="38" r="22" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="38" y1="16" x2="38" y2="60" stroke="#22c55e" stroke-width="1" stroke-dasharray="3,3"/><line x1="16" y1="38" x2="60" y2="38" stroke="#22c55e" stroke-width="1" stroke-dasharray="3,3"/><ellipse cx="55" cy="25" rx="8" ry="5" fill="none" stroke="#22c55e" stroke-width="2" transform="rotate(30,55,25)"/></svg>',
        'volleyball': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="40" r="20" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M22 28 Q40 22 58 28" stroke="#22c55e" stroke-width="1.5" fill="none"/><path d="M22 52 Q40 58 58 52" stroke="#22c55e" stroke-width="1.5" fill="none"/><path d="M33 22 L33 58" stroke="#22c55e" stroke-width="1"/><path d="M47 22 L47 58" stroke="#22c55e" stroke-width="1"/></svg>',
        'table tennis': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><rect x="20" y="45" width="40" height="4" rx="2" fill="#22c55e"/><ellipse cx="40" cy="30" rx="16" ry="12" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="42" x2="40" y2="50" stroke="#22c55e" stroke-width="2"/><line x1="36" y1="28" x2="44" y2="28" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="28" r="3" fill="#22c55e"/></svg>',
        'kabaddi': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="32" cy="32" r="8" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="48" cy="32" r="8" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M32 40 Q40 48 48 40" stroke="#22c55e" stroke-width="2" fill="none"/><line x1="36" y1="32" x2="36" y2="38" stroke="#22c55e" stroke-width="1.5"/><line x1="44" y1="32" x2="44" y2="38" stroke="#22c55e" stroke-width="1.5"/><path d="M20 55 L60 55" stroke="#22c55e" stroke-width="2"/><line x1="28" y1="55" x2="25" y2="65" stroke="#22c55e" stroke-width="2"/><line x1="52" y1="55" x2="55" y2="65" stroke="#22c55e" stroke-width="2"/></svg>',
        'hockey': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M15 40 L60 40" stroke="#22c55e" stroke-width="2"/><rect x="55" y="20" width="6" height="40" rx="2" fill="#22c55e" opacity="0.6"/><circle cx="30" cy="40" r="5" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M20 50 L25 55 L30 50 L35 55" stroke="#22c55e" stroke-width="1.5" fill="none"/></svg>',
        'baseball': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="40" r="16" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M32 32 L48 48 M48 32 L32 48" stroke="#22c55e" stroke-width="1.5"/><line x1="25" y1="25" x2="55" y2="55" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3"/></svg>',
        'rugby': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><ellipse cx="40" cy="40" rx="22" ry="14" fill="none" stroke="#22c55e" stroke-width="2" transform="rotate(-30,40,40)"/><line x1="34" y1="28" x2="46" y2="52" stroke="#22c55e" stroke-width="1.5"/><line x1="46" y1="28" x2="34" y2="52" stroke="#22c55e" stroke-width="1.5"/></svg>',
        'athletics': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="30" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="36" x2="40" y2="55" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="42" x2="28" y2="50" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="42" x2="52" y2="50" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="55" x2="32" y2="68" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="55" x2="48" y2="68" stroke="#22c55e" stroke-width="2"/></svg>',
        'cycling': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="30" cy="55" r="8" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="55" cy="55" r="8" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="38" cy="35" r="3" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="30" y1="55" x2="38" y2="35" stroke="#22c55e" stroke-width="1.5"/><line x1="55" y1="55" x2="40" y2="35" stroke="#22c55e" stroke-width="1.5"/><line x1="38" y1="35" x2="48" y2="40" stroke="#22c55e" stroke-width="1.5"/></svg>',
        'archery': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="30" cy="40" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="30" cy="40" r="2" fill="#22c55e"/><path d="M36 40 L60 30" stroke="#22c55e" stroke-width="2"/><path d="M36 40 L60 50" stroke="#22c55e" stroke-width="2"/><line x1="52" y1="30" x2="60" y2="25" stroke="#22c55e" stroke-width="2"/><line x1="52" y1="50" x2="60" y2="55" stroke="#22c55e" stroke-width="2"/></svg>',
        'golf': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="42" cy="25" r="5" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="42" y1="30" x2="42" y2="62" stroke="#22c55e" stroke-width="2"/><path d="M36 55 Q42 58 48 55" stroke="#22c55e" stroke-width="2" fill="none"/><circle cx="62" cy="30" r="3" fill="#22c55e" opacity="0.5"/></svg>',
        'chess': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="22" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="28" x2="40" y2="45" stroke="#22c55e" stroke-width="2"/><path d="M30 45 L50 45 L48 52 L32 52 Z" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="28" y1="56" x2="52" y2="56" stroke="#22c55e" stroke-width="2"/></svg>',
        'carrom': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><rect x="18" y="18" width="44" height="44" rx="4" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="28" cy="28" r="3" fill="#22c55e"/><circle cx="52" cy="28" r="3" fill="#22c55e"/><circle cx="28" cy="52" r="3" fill="#22c55e"/><circle cx="52" cy="52" r="3" fill="#22c55e"/><circle cx="40" cy="40" r="3" fill="#ef4444"/><circle cx="40" cy="28" r="2" fill="#22c55e"/><circle cx="40" cy="52" r="2" fill="#22c55e"/><circle cx="28" cy="40" r="2" fill="#22c55e"/><circle cx="52" cy="40" r="2" fill="#22c55e"/></svg>',
        'squash': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><rect x="20" y="20" width="40" height="40" rx="2" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="20" y1="50" x2="60" y2="50" stroke="#22c55e" stroke-width="1.5"/><circle cx="40" cy="35" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="29" x2="40" y2="22" stroke="#22c55e" stroke-width="2"/></svg>',
        'boxing': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="38" r="14" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="32" cy="34" r="3" fill="#22c55e"/><circle cx="48" cy="34" r="3" fill="#22c55e"/><path d="M35 44 Q40 48 45 44" stroke="#22c55e" stroke-width="2" fill="none"/><circle cx="20" cy="38" r="5" fill="none" stroke="#22c55e" stroke-width="1.5"/><circle cx="60" cy="38" r="5" fill="none" stroke="#22c55e" stroke-width="1.5"/></svg>',
        'wrestling': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="28" cy="30" r="7" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="52" cy="30" r="7" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M28 37 Q40 50 52 37" stroke="#22c55e" stroke-width="2" fill="none"/><line x1="20" y1="55" x2="60" y2="55" stroke="#22c55e" stroke-width="2"/><line x1="28" y1="37" x2="22" y2="55" stroke="#22c55e" stroke-width="1.5"/><line x1="52" y1="37" x2="58" y2="55" stroke="#22c55e" stroke-width="1.5"/></svg>',
        'martial arts': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="22" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="28" x2="40" y2="46" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="34" x2="58" y2="30" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="34" x2="58" y2="42" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="46" x2="30" y2="60" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="46" x2="50" y2="60" stroke="#22c55e" stroke-width="2"/></svg>',
        'gymnastics': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="22" r="5" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="27" x2="40" y2="42" stroke="#22c55e" stroke-width="2"/><path d="M28 38 Q40 48 52 38" stroke="#22c55e" stroke-width="2" fill="none"/><line x1="40" y1="42" x2="30" y2="55" stroke="#22c55e" stroke-width="2"/><line x1="40" y1="42" x2="50" y2="55" stroke="#22c55e" stroke-width="2"/><path d="M55 30 C65 30 65 45 55 45" stroke="#22c55e" stroke-width="1.5" fill="none"/></svg>',
        'swimming': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M15 55 Q30 45 40 55 Q50 65 65 55" stroke="#22c55e" stroke-width="2" fill="none"/><circle cx="30" cy="40" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="32" y1="42" x2="38" y2="48" stroke="#22c55e" stroke-width="1.5"/><circle cx="50" cy="38" r="5" fill="none" stroke="#22c55e" stroke-width="2"/><line x1="52" y1="40" x2="58" y2="46" stroke="#22c55e" stroke-width="1.5"/><path d="M20 48 Q25 38 35 42" stroke="#22c55e" stroke-width="1.5" fill="none"/><path d="M42 42 Q48 36 55 40" stroke="#22c55e" stroke-width="1.5" fill="none"/></svg>',
        'yoga': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="22" r="5" fill="none" stroke="#22c55e" stroke-width="2"/><path d="M40 27 Q35 40 40 50 Q45 60 40 68" stroke="#22c55e" stroke-width="2" fill="none"/><path d="M25 38 Q32 35 40 38" stroke="#22c55e" stroke-width="1.5" fill="none"/><path d="M55 38 Q48 35 40 38" stroke="#22c55e" stroke-width="1.5" fill="none"/><path d="M40 50 L30 62" stroke="#22c55e" stroke-width="2"/><path d="M40 50 L50 62" stroke="#22c55e" stroke-width="2"/></svg>',
        'default': '<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="40" cy="40" r="36" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="40" cy="40" r="20" fill="none" stroke="#22c55e" stroke-width="2"/><text x="40" y="46" font-size="24" text-anchor="middle" fill="#22c55e">?</text></svg>'
    };

    function getSportIcon(name) {
        var key = (name || '').toLowerCase().trim();
        return SPORT_ICONS[key] || SPORT_ICONS['default'];
    }

    // =============================================================
    // UTILITY: Scroll to section
    // =============================================================
    window.scrollToSection = function (sectionId) {
        const el = document.getElementById(sectionId);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    // =============================================================
    // UTILITY: Flash message helper
    // =============================================================
    function showFlash(message, category) {
        const container = document.querySelector('main.container') || document.querySelector('main');
        if (!container) return;

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${category} alert-dismissible fade show mt-2`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.prepend(alertDiv);
        setTimeout(() => { alertDiv.remove(); }, 4000);
    }

    // =============================================================
    // MODULE 7: ALL GAMES - Load & Display
    // =============================================================
    function initAllGames() {
        const container = document.getElementById('all-games-container');
        if (!container) return;

        // Fetch all games from API
        fetch('/api/games')
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (!data.success) {
                    showGamesError(container, data.message || 'Failed to load games.');
                    return;
                }

                var games = data.games;
                if (!games || games.length === 0) {
                    showGamesEmpty(container);
                    return;
                }

                renderGamesGrid(container, games);
            })
            .catch(function (err) {
                console.error('Failed to load games:', err);
                showGamesError(container, 'Unable to load games. Please try again.');
            });
    }

    function renderGamesGrid(container, games) {
        var html = '';
        games.forEach(function (game) {
            var iconSvg = getSportIcon(game.name);
            var encodedSvg = encodeURIComponent(iconSvg);
            var dataUri = 'data:image/svg+xml,' + encodedSvg;

            html += `
                <div class="col-lg-3 col-md-4 col-sm-6 col-6">
                    <div class="game-card card text-center h-100" 
                         data-game-id="${game.id}" 
                         data-game-name="${game.name}"
                         onclick="window.openGameDetails(${game.id}, '${game.name.replace(/'/g, "\\'")}')">
                        <div class="card-body d-flex flex-column align-items-center justify-content-center p-3">
                            <div class="game-icon mb-2">
                                <img src="${dataUri}" alt="${game.name}" 
                                     style="width: 64px; height: 64px; filter: drop-shadow(0 2px 4px rgba(34,197,94,0.3));" 
                                     loading="lazy"
                                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                                <div class="game-icon-fallback d-none">
                                    <i class="bi bi-trophy text-success" style="font-size: 2.2rem;"></i>
                                </div>
                            </div>
                            <h6 class="text-white mb-1 game-name-text">${game.name}</h6>
                            <small class="text-white-50">${game.match_count || 0} match${(game.match_count || 0) !== 1 ? 'es' : ''}</small>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    function showGamesError(container, message) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-exclamation-triangle text-danger" style="font-size: 3rem;"></i>
                <h5 class="text-white mt-3">${message}</h5>
                <p class="text-white-50">Please check your connection and try again.</p>
                <button class="btn btn-outline-success btn-sm mt-2" onclick="location.reload()">
                    <i class="bi bi-arrow-repeat me-1"></i>Retry
                </button>
            </div>
        `;
    }

    function showGamesEmpty(container) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-grid-3x3-gap text-white-50" style="font-size: 3rem;"></i>
                <h5 class="text-white mt-3">No games available at the moment</h5>
                <p class="text-white-50">Check back later for new games.</p>
            </div>
        `;
    }

    // =============================================================
    // MODULE 7: GAME DETAILS - Open Modal
    // =============================================================
    window.openGameDetails = function (gameId, gameName) {
        currentGameId = gameId;
        currentGameName = gameName;

        var modalEl = document.getElementById('gameDetailsModal');
        if (!modalEl) return;

        var modal = new bootstrap.Modal(modalEl);
        modal.show();
    };

    function initGameDetailsModal() {
        var modalEl = document.getElementById('gameDetailsModal');
        if (!modalEl) return;

        // When modal is shown, fetch game details
        modalEl.addEventListener('show.bs.modal', function () {
            if (!currentGameId) return;

            // Show loading, hide other states
            document.getElementById('game-details-loading').classList.remove('d-none');
            document.getElementById('game-details-content').classList.add('d-none');
            document.getElementById('game-details-no-data').classList.add('d-none');
            document.getElementById('game-details-error').classList.add('d-none');

            // Update title
            document.getElementById('gameDetailsModalLabel').textContent = currentGameName || 'Game Details';

            // Set icon in header
            var iconContainer = document.getElementById('game-modal-icon');
            if (iconContainer) {
                var iconSvg = getSportIcon(currentGameName);
                var encodedSvg = encodeURIComponent(iconSvg);
                iconContainer.innerHTML = '<img src="data:image/svg+xml,' + encodedSvg + '" alt="' + (currentGameName || '') + '" style="width: 48px; height: 48px;">';
            }

            // Fetch details from API
            fetch('/api/game/' + currentGameId)
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    document.getElementById('game-details-loading').classList.add('d-none');

                    if (!data.success || !data.game) {
                        document.getElementById('game-details-no-data').classList.remove('d-none');
                        document.getElementById('game-modal-match-count').textContent = 'Details unavailable';
                        return;
                    }

                    var game = data.game;

                    // Check if there's any actual detail content
                    var hasDescription = game.description && game.description.trim().length > 0;
                    var hasRules = game.rules && game.rules.trim().length > 0;
                    var hasLocation = game.location_info && game.location_info.trim().length > 0;

                    if (!hasDescription && !hasRules && !hasLocation) {
                        // No details available
                        document.getElementById('game-details-no-data').classList.remove('d-none');
                        document.getElementById('game-modal-match-count').textContent = 'No details';
                        return;
                    }

                    // We have details - populate them
                    document.getElementById('game-details-content').classList.remove('d-none');

                    // Name
                    document.querySelector('#game-detail-name span').textContent = game.name;

                    // Description
                    var descEl = document.getElementById('game-detail-description');
                    if (hasDescription) {
                        descEl.textContent = game.description;
                        descEl.closest('.mb-4').classList.remove('d-none');
                    } else {
                        descEl.closest('.mb-4').classList.add('d-none');
                    }

                    // Rules
                    var rulesEl = document.getElementById('game-detail-rules');
                    if (hasRules) {
                        rulesEl.textContent = game.rules;
                        rulesEl.closest('.mb-4').classList.remove('d-none');
                    } else {
                        rulesEl.closest('.mb-4').classList.add('d-none');
                    }

                    // Location
                    var locEl = document.getElementById('game-detail-location');
                    if (hasLocation) {
                        locEl.textContent = game.location_info;
                        locEl.closest('.mb-4').classList.remove('d-none');
                    } else {
                        locEl.closest('.mb-4').classList.add('d-none');
                    }

                    // Active matches
                    var matchesEl = document.getElementById('game-detail-matches');
                    var matchCount = game.active_matches || 0;
                    if (matchCount > 0) {
                        matchesEl.textContent = 'There ' + (matchCount === 1 ? 'is' : 'are') + ' ' + matchCount + ' active match' + (matchCount === 1 ? '' : 'es') + ' available for ' + game.name + '.';
                    } else {
                        matchesEl.textContent = 'No active matches available for ' + game.name + ' at the moment.';
                    }

                    // Update match count badge
                    document.getElementById('game-modal-match-count').textContent = matchCount + ' active match' + (matchCount === 1 ? '' : 'es');
                })
                .catch(function (err) {
                    console.error('Failed to load game details:', err);
                    document.getElementById('game-details-loading').classList.add('d-none');
                    document.getElementById('game-details-error').classList.remove('d-none');
                    document.getElementById('game-modal-match-count').textContent = 'Error loading';
                });
        });

        // "Find Matches" button in modal footer
        var findMatchesBtn = document.getElementById('game-detail-find-matches');
        if (findMatchesBtn) {
            findMatchesBtn.addEventListener('click', function () {
                var modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                // Set the sport in the discover filter and trigger search
                if (currentGameName) {
                    var sportSelect = document.getElementById('filter-sport');
                    if (sportSelect) {
                        sportSelect.value = currentGameName;
                        scrollToSection('discover-section');
                        setTimeout(function () {
                            var filterBtn = document.getElementById('filter-apply-btn');
                            if (filterBtn) filterBtn.click();
                        }, 300);
                    }
                }
            });
        }
    }

    // =============================================================
    // MODULE 3: DISCOVER MATCHES - FILTER & AJAX
    // =============================================================
    function initDiscoverFilters() {
        const filterBtn = document.getElementById('filter-apply-btn');
        if (!filterBtn) return;

        filterBtn.addEventListener('click', function () {
            const sport = document.getElementById('filter-sport').value;
            const location = document.getElementById('filter-location').value;
            const date = document.getElementById('filter-date').value;

            const params = new URLSearchParams();
            if (sport) params.append('sport', sport);
            if (location) params.append('location', location);
            if (date) params.append('date', date);

            const url = DASHBOARD_DATA.discoverUrl + '?' + params.toString();

            // Show loading
            const resultsContainer = document.getElementById('discover-results');
            resultsContainer.innerHTML = `
                <div class="col-12 text-center py-4">
                    <div class="spinner-border text-success" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="text-white-50 mt-2">Discovering matches...</p>
                </div>
            `;

            fetch(url)
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data.error) {
                        resultsContainer.innerHTML = `
                            <div class="col-12 text-center py-4 text-danger">
                                <i class="bi bi-exclamation-circle" style="font-size: 2rem;"></i>
                                <p class="mt-2">${data.error}</p>
                            </div>
                        `;
                        return;
                    }

                    const matches = data.matches;
                    if (!matches || matches.length === 0) {
                        resultsContainer.innerHTML = `
                            <div class="col-12 text-center py-4">
                                <i class="bi bi-search text-white-50" style="font-size: 2rem;"></i>
                                <p class="text-white mt-2">No matches found matching your criteria.</p>
                            </div>
                        `;
                        return;
                    }

                    let html = '';
                    matches.forEach(function (match) {
                        const isJoined = DASHBOARD_DATA.userJoinedIds && DASHBOARD_DATA.userJoinedIds.indexOf(match.id) !== -1;
                        const isFull = match.player_count >= match.max_players;
                        let btnHtml = '';

                        if (isJoined) {
                            btnHtml = '<button class="btn btn-sm btn-success w-100" disabled><i class="bi bi-check-circle me-1"></i>Joined</button>';
                        } else if (isFull) {
                            btnHtml = '<button class="btn btn-sm btn-secondary w-100" disabled><i class="bi bi-x-circle me-1"></i>Full</button>';
                        } else {
                            btnHtml = `<button class="btn btn-sm btn-outline-success w-100 join-match-btn" data-match-id="${match.id}" data-bs-toggle="modal" data-bs-target="#joinConfirmModal"><i class="bi bi-hand-index-thumb me-1"></i>Join Match</button>`;
                        }

                        html += `
                            <div class="col-lg-3 col-md-4 col-sm-6">
                                <div class="card match-card h-100">
                                    <div class="card-body d-flex flex-column p-3">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <span class="badge bg-${match.sport_type === 'outdoor' ? 'success' : 'info'} bg-opacity-75">
                                                <i class="bi bi-${match.sport_type === 'outdoor' ? 'sun' : 'house-door'} me-1"></i>
                                                ${match.sport_type.charAt(0).toUpperCase() + match.sport_type.slice(1)}
                                            </span>
                                            <span class="badge bg-dark border border-secondary">
                                                <i class="bi bi-people me-1"></i>${match.player_count}/${match.max_players}
                                            </span>
                                        </div>
                                        <h5 class="card-title text-white mb-2">
                                            <i class="bi bi-trophy text-warning me-1"></i>${match.sport_name}
                                        </h5>
                                        <div class="match-details small flex-grow-1">
                                            <div class="mb-1 text-white"><i class="bi bi-geo-alt text-danger me-1"></i>${match.venue_name}</div>
                                            <div class="mb-1 text-white"><i class="bi bi-calendar-date text-primary me-1"></i>${match.match_date}</div>
                                            <div class="mb-1 text-white"><i class="bi bi-clock text-info me-1"></i>${match.match_time}</div>
                                            <div class="text-white"><i class="bi bi-person-circle me-1"></i>${match.creator_name}</div>
                                        </div>
                                        <div class="mt-3 d-flex gap-2">
                                            ${btnHtml}
                                            <button class="btn btn-sm btn-outline-info match-chat-btn" data-match-id="${match.id}" data-match-name="${match.sport_name}">
                                                <i class="bi bi-chat-dots"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });

                    resultsContainer.innerHTML = html;
                })
                .catch(function (err) {
                    resultsContainer.innerHTML = `
                        <div class="col-12 text-center py-4 text-danger">
                            <i class="bi bi-exclamation-triangle" style="font-size: 2rem;"></i>
                            <p class="mt-2">Unable to load matches. Please try again.</p>
                        </div>
                    `;
                    console.error('Discover fetch error:', err);
                });
        });
    }

    // =============================================================
    // MODULE 7: ALL GAMES - Filter by sport click (legacy support)
    // =============================================================
    window.filterBySport = function (sportName) {
        const sportSelect = document.getElementById('filter-sport');
        if (sportSelect) {
            sportSelect.value = sportName;
            scrollToSection('discover-section');
            setTimeout(function () {
                const filterBtn = document.getElementById('filter-apply-btn');
                if (filterBtn) filterBtn.click();
            }, 300);
        }
    };

    // =============================================================
    // MODULE 2: JOIN MATCH - Modal confirmation
    // =============================================================
    function initJoinMatch() {
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.join-match-btn');
            if (btn) {
                currentJoinMatchId = btn.getAttribute('data-match-id');
            }
        });

        const confirmBtn = document.getElementById('confirm-join-btn');
        if (!confirmBtn) return;

        confirmBtn.addEventListener('click', function () {
            if (!currentJoinMatchId) return;

            const modalEl = document.getElementById('joinConfirmModal');
            const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);

            const url = DASHBOARD_DATA.joinUrl.replace('0', currentJoinMatchId);

            fetch(url, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    modal.hide();
                    if (data.success) {
                        showFlash(data.message, 'success');
                        const btn = document.querySelector(`.join-match-btn[data-match-id="${currentJoinMatchId}"]`);
                        if (btn) {
                            btn.outerHTML = '<button class="btn btn-sm btn-success w-100" disabled><i class="bi bi-check-circle me-1"></i>Joined</button>';
                        }
                    } else {
                        showFlash(data.error || 'Failed to join match', 'danger');
                    }
                })
                .catch(function (err) {
                    modal.hide();
                    showFlash('Network error. Please try again.', 'danger');
                    console.error('Join match error:', err);
                });
        });
    }

    // =============================================================
    // MODULE 5: MAP - Initialize Leaflet Map
    // =============================================================
    function initMap() {
        const mapContainer = document.getElementById('dashboard-map');
        if (!mapContainer) return;

        // Default center (Vijayawada)
        dashboardMap = L.map('dashboard-map').setView([16.5062, 80.6480], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18
        }).addTo(dashboardMap);

        // Wire up tab buttons
        document.querySelectorAll('.map-toggle').forEach(function (btn) {
            btn.addEventListener('click', function () {
                document.querySelectorAll('.map-toggle').forEach(function (b) { b.classList.remove('active'); });
                this.classList.add('active');
                currentLayer = this.getAttribute('data-layer');
                loadCurrentLayer();
            });
        });

        // Load default layer
        loadCurrentLayer();
    }

    function loadCurrentLayer() {
        if (!dashboardMap) return;

        // Clear existing markers
        clearMarkers();

        if (currentLayer === 'matches') {
            loadMatchMarkers();
        } else if (currentLayer === 'businesses') {
            loadVenueMarkers();
        }
    }

    function clearMarkers() {
        matchMarkers.forEach(function (m) { dashboardMap.removeLayer(m); });
        matchMarkers = [];
        businessMarkers.forEach(function (m) { dashboardMap.removeLayer(m); });
        businessMarkers = [];
    }

    function loadMatchMarkers() {
        const url = DASHBOARD_DATA.mapMatchesUrl;
        if (!url) {
            showMapEmpty();
            return;
        }

        const mapContainer = document.getElementById('dashboard-map');
        mapContainer.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;background:#1a1a2e;border-radius:12px;"><div class="spinner-border text-success" role="status"></div><p class="text-white ms-2 mb-0">Loading match locations...</p></div>';

        // Re-create map element after clearing
        const inner = document.createElement('div');
        inner.id = 'dashboard-map-inner';
        inner.style.cssText = 'height: 400px; width: 100%; border-radius: 12px;';
        mapContainer.innerHTML = '';
        mapContainer.appendChild(inner);

        if (dashboardMap) {
            dashboardMap.remove();
            dashboardMap = null;
        }

        dashboardMap = L.map('dashboard-map-inner').setView([16.5062, 80.6480], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(dashboardMap);

        fetch(url)
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (!data || !data.success || !data.matches || data.matches.length === 0) {
                    showMapEmpty();
                    return;
                }

                const bounds = [];
                data.matches.forEach(function (m) {
                    if (!m.latitude || !m.longitude) return;

                    const marker = L.circleMarker([m.latitude, m.longitude], {
                        radius: 8,
                        fillColor: '#22c55e',
                        color: '#16a34a',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.85
                    });

                    let popup = '<div style="color:#0f172a;min-width:180px;">';
                    popup += '<strong style="color:#16a34a;">' + escapeHtml(m.sport_name || 'Match') + '</strong><br>';
                    popup += '<small>Venue: ' + escapeHtml(m.venue_name || '') + '</small><br>';
                    popup += '<small>Date: ' + escapeHtml(m.date || '') + '</small><br>';
                    popup += '<small>Time: ' + escapeHtml(m.time || '') + '</small><br>';
                    if (m.skill_level) {
                        popup += '<small>Level: ' + escapeHtml(m.skill_level) + '</small><br>';
                    }
                    popup += '<small>Slots: ' + (m.available_slots || 0) + '</small>';
                    popup += '</div>';

                    marker.bindPopup(popup);
                    marker.addTo(dashboardMap);
                    matchMarkers.push(marker);
                    bounds.push([m.latitude, m.longitude]);
                });

                if (bounds.length > 0) {
                    dashboardMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
                }

                currentLayer = 'matches';
                updateToggleButtons();
            })
            .catch(function (err) {
                console.error('Failed to load match markers:', err);
                showMapError();
            });
    }

    function loadVenueMarkers() {
        const url = DASHBOARD_DATA.mapVenuesUrl;
        if (!url) {
            showMapEmpty();
            return;
        }

        const mapContainer = document.getElementById('dashboard-map');
        mapContainer.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;background:#1a1a2e;border-radius:12px;"><div class="spinner-border text-success" role="status"></div><p class="text-white ms-2 mb-0">Loading venues...</p></div>';

        const inner = document.createElement('div');
        inner.id = 'dashboard-map-inner';
        inner.style.cssText = 'height: 400px; width: 100%; border-radius: 12px;';
        mapContainer.innerHTML = '';
        mapContainer.appendChild(inner);

        if (dashboardMap) {
            dashboardMap.remove();
            dashboardMap = null;
        }

        dashboardMap = L.map('dashboard-map-inner').setView([16.5062, 80.6480], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(dashboardMap);

        fetch(url)
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (!data || !data.success || !data.venues || data.venues.length === 0) {
                    showMapEmpty();
                    return;
                }

                const bounds = [];
                data.venues.forEach(function (v) {
                    if (!v.latitude || !v.longitude) return;

                    const marker = L.circleMarker([v.latitude, v.longitude], {
                        radius: 8,
                        fillColor: '#3b82f6',
                        color: '#2563eb',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.85
                    });

                    let popup = '<div style="color:#0f172a;min-width:180px;">';
                    popup += '<strong style="color:#2563eb;">' + escapeHtml(v.venue_name || 'Venue') + '</strong><br>';
                    popup += '<small>Address: ' + escapeHtml(v.address || '') + '</small><br>';
                    popup += '<small>Rating: ' + (v.rating || 0) + '/5</small><br>';
                    popup += '<small>Slots: ' + (v.available_slots || 0) + '</small><br>';
                    if (v.sport_types && v.sport_types.length > 0) {
                        popup += '<small>Sports: ' + escapeHtml(v.sport_types.join(', ')) + '</small>';
                    }
                    popup += '</div>';

                    marker.bindPopup(popup);
                    marker.addTo(dashboardMap);
                    businessMarkers.push(marker);
                    bounds.push([v.latitude, v.longitude]);
                });

                if (bounds.length > 0) {
                    dashboardMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
                }

                currentLayer = 'businesses';
                updateToggleButtons();
            })
            .catch(function (err) {
                console.error('Failed to load venue markers:', err);
                showMapError();
            });
    }

    function updateToggleButtons() {
        document.querySelectorAll('.map-toggle').forEach(function (btn) {
            if (btn.getAttribute('data-layer') === currentLayer) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        return String(text)
            .replace(/&/g, '&')
            .replace(/</g, '<')
            .replace(/>/g, '>')
            .replace(/"/g, '"');
    }

    function showMapEmpty() {
        const mapContainer = document.getElementById('dashboard-map');
        if (!mapContainer) return;
        mapContainer.innerHTML = '<div id="dashboard-map" style="height: 400px; width: 100%; border-radius: 12px; background: #1a1a2e; display: flex; flex-direction: column; align-items: center; justify-content: center;"><i class="bi bi-geo-alt text-white-50" style="font-size: 3rem;"></i><p style="color: white; text-align: center; margin-top: 1rem;">No locations available</p></div>';
    }

    function showMapError() {
        const mapContainer = document.getElementById('dashboard-map');
        if (!mapContainer) return;
        mapContainer.innerHTML = '<div id="dashboard-map" style="height: 400px; width: 100%; border-radius: 12px; background: #1a1a2e; display: flex; flex-direction: column; align-items: center; justify-content: center;"><i class="bi bi-exclamation-triangle text-danger" style="font-size: 3rem;"></i><p style="color: red; text-align: center; margin-top: 1rem;">Unable to load map data.</p></div>';
    }

    // =============================================================
    // SPORTS CATEGORIES - Current sport ID for detail modal
    // =============================================================
    let currentSportId = null;
    let currentSportName = null;
    let allSportsData = [];

    // =============================================================
    // SPORTS CATEGORIES - Load and render
    // =============================================================
    function initSportsCategories() {
        const container = document.getElementById('sports-categories-container');
        if (!container) return;

        fetch('/api/sports-categories')
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (!data.success) {
                    showSportsError(container, data.message || 'Failed to load sports.');
                    return;
                }

                var sports = data.sports;
                if (!sports || sports.length === 0) {
                    showSportsEmpty(container);
                    return;
                }

                allSportsData = sports;
                renderSportsGrid(container, sports);
                initSportsFilters();
            })
            .catch(function (err) {
                console.error('Failed to load sports:', err);
                showSportsError(container, 'Unable to load sports. Please try again.');
            });
    }

    function renderSportsGrid(container, sports) {
        var html = '';
        sports.forEach(function (sport) {
            var iconSvg = getSportIcon(sport.name);
            var encodedSvg = encodeURIComponent(iconSvg);
            var dataUri = 'data:image/svg+xml,' + encodedSvg;
            var isOutdoor = sport.category === 'Outdoor';
            var badgeClass = isOutdoor ? 'bg-success' : 'bg-info';
            var iconName = isOutdoor ? 'sun' : 'house-door';

            html += `
                <div class="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6 sport-card-col" data-category="${sport.category.toLowerCase()}">
                    <div class="card sport-card h-100" onclick="window.openSportDetail(${sport.id}, '${sport.name.replace(/'/g, "\\'")}')">
                        <div class="card-body d-flex flex-column p-3">
                            <!-- Badge row -->
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="badge ${badgeClass} bg-opacity-75">
                                    <i class="bi bi-${iconName} me-1"></i>${sport.category}
                                </span>
                            </div>

                            <!-- Icon and Name -->
                            <div class="text-center mb-2 flex-grow-1 d-flex flex-column align-items-center justify-content-center">
                                <div class="sport-icon mb-2">
                                    <img src="${dataUri}" alt="${sport.name}" 
                                         style="width: 56px; height: 56px;" 
                                         loading="lazy"
                                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                                    <div class="sport-icon-fallback d-none">
                                        <i class="bi bi-trophy text-warning" style="font-size: 2rem;"></i>
                                    </div>
                                </div>
                                <h6 class="text-white mb-0 sport-name-text">${sport.name}</h6>
                            </div>

                            <!-- Stats row -->
                            <div class="d-flex justify-content-between small text-white-50 mt-auto pt-2 border-top border-secondary">
                                <span><i class="bi bi-building me-1"></i>${sport.venue_count || 0} venues</span>
                                <span><i class="bi bi-calendar-event me-1"></i>${sport.match_count || 0} matches</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    function showSportsError(container, message) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
                <h5 class="text-white mt-3">${message}</h5>
                <p class="text-white-50">Please check your connection and try again.</p>
                <button class="btn btn-outline-warning btn-sm mt-2" onclick="location.reload()">
                    <i class="bi bi-arrow-repeat me-1"></i>Retry
                </button>
            </div>
        `;
    }

    function showSportsEmpty(container) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-grid text-white-50" style="font-size: 3rem;"></i>
                <h5 class="text-white mt-3">No sports available</h5>
                <p class="text-white-50">Check back later for new sports.</p>
            </div>
        `;
    }

    // =============================================================
    // SPORTS CATEGORIES - Filter by Indoor/Outdoor
    // =============================================================
    function initSportsFilters() {
        var filterBtns = document.querySelectorAll('.sports-filter-btn');
        if (!filterBtns.length) return;

        filterBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                // Update active state
                filterBtns.forEach(function (b) { b.classList.remove('active'); });
                this.classList.add('active');

                var filter = this.getAttribute('data-filter');
                var cards = document.querySelectorAll('.sport-card-col');

                cards.forEach(function (card) {
                    if (filter === 'all') {
                        card.style.display = '';
                    } else {
                        var category = card.getAttribute('data-category');
                        card.style.display = category === filter ? '' : 'none';
                    }
                });
            });
        });
    }

    // =============================================================
    // SPORTS CATEGORIES - Open Sport Detail Modal
    // =============================================================
    window.openSportDetail = function (sportId, sportName) {
        currentSportId = sportId;
        currentSportName = sportName;

        var modalEl = document.getElementById('sportDetailModal');
        if (!modalEl) return;

        var modal = new bootstrap.Modal(modalEl);
        modal.show();
    };

    // =============================================================
    // SPORTS CATEGORIES - Init Sport Detail Modal
    // =============================================================
    function initSportDetailModal() {
        var modalEl = document.getElementById('sportDetailModal');
        if (!modalEl) return;

        modalEl.addEventListener('show.bs.modal', function () {
            if (!currentSportId) return;

            // Show loading, hide other states
            document.getElementById('sport-details-loading').classList.remove('d-none');
            document.getElementById('sport-details-content').classList.add('d-none');
            document.getElementById('sport-details-error').classList.add('d-none');

            // Update title
            document.getElementById('sportDetailModalLabel').textContent = currentSportName || 'Sport Details';
            document.getElementById('sport-modal-subtitle').textContent = 'Loading details...';

            // Set icon in header
            var iconContainer = document.getElementById('sport-modal-icon');
            if (iconContainer) {
                var iconSvg = getSportIcon(currentSportName);
                var encodedSvg = encodeURIComponent(iconSvg);
                iconContainer.innerHTML = '<img src="data:image/svg+xml,' + encodedSvg + '" alt="' + (currentSportName || '') + '" style="width: 56px; height: 56px;">';
            }

            // Fetch details from API
            fetch('/api/sport-detail/' + currentSportId)
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    document.getElementById('sport-details-loading').classList.add('d-none');

                    if (!data.success || !data.sport) {
                        document.getElementById('sport-details-error').classList.remove('d-none');
                        document.getElementById('sport-modal-subtitle').textContent = 'Details unavailable';
                        return;
                    }

                    var sport = data.sport;
                    document.getElementById('sport-details-content').classList.remove('d-none');

                    // Name
                    document.getElementById('sport-detail-name').textContent = sport.name;

                    // Category badge
                    var badgeEl = document.getElementById('sport-detail-badge');
                    var isOutdoor = sport.category === 'Outdoor';
                    badgeEl.className = 'badge ' + (isOutdoor ? 'bg-success' : 'bg-info');
                    badgeEl.innerHTML = '<i class="bi bi-' + (isOutdoor ? 'sun' : 'house-door') + ' me-1"></i>' + sport.category;

                    // Difficulty
                    var diffEl = document.getElementById('sport-detail-difficulty');
                    if (sport.difficulty_level) {
                        diffEl.textContent = sport.difficulty_level;
                        diffEl.classList.remove('d-none');
                    } else {
                        diffEl.classList.add('d-none');
                    }

                    // Description
                    document.getElementById('sport-detail-description').textContent = sport.description || 'No description available.';

                    // Quick stats
                    document.getElementById('sport-detail-players').textContent = sport.num_players || 'N/A';
                    document.getElementById('sport-detail-duration').textContent = sport.match_duration || 'N/A';
                    document.getElementById('sport-detail-area').textContent = sport.playing_area || 'N/A';
                    document.getElementById('sport-detail-equipment').textContent = sport.equipment || 'N/A';

                    // Rules
                    var rulesEl = document.getElementById('sport-detail-rules');
                    rulesEl.textContent = sport.basic_rules || 'No specific rules listed.';

                    // Tournaments
                    var tournEl = document.getElementById('sport-detail-tournaments');
                    tournEl.textContent = sport.popular_tournaments || 'No major tournaments listed.';

                    // Venue count and match count
                    document.getElementById('sport-detail-venue-count').textContent = sport.venue_count || 0;
                    document.getElementById('sport-detail-match-count').textContent = sport.match_count || 0;

                    // Subtitle
                    document.getElementById('sport-modal-subtitle').textContent = sport.venue_count + ' nearby venues | ' + sport.match_count + ' active matches';

                    // Upcoming matches
                    var matchesListEl = document.getElementById('sport-detail-matches-list');
                    var matchesSection = document.getElementById('sport-detail-matches-section');
                    if (sport.upcoming_matches && sport.upcoming_matches.length > 0) {
                        var matchHtml = '<div class="list-group list-group-flush">';
                        sport.upcoming_matches.forEach(function (m) {
                            matchHtml += '<div class="list-group-item bg-transparent border-secondary text-white px-0 py-2">';
                            matchHtml += '<div class="d-flex justify-content-between align-items-center">';
                            matchHtml += '<div><strong>' + m.venue_name + '</strong><br><small>' + m.match_date + ' at ' + m.match_time + '</small></div>';
                            matchHtml += '<span class="badge bg-dark border border-secondary">' + m.player_count + '/' + m.max_players + '</span>';
                            matchHtml += '</div></div>';
                        });
                        matchHtml += '</div>';
                        matchesListEl.innerHTML = matchHtml;
                        matchesSection.classList.remove('d-none');
                    } else {
                        matchesListEl.innerHTML = '<p class="text-white-50 mb-0">No upcoming matches available.</p>';
                        matchesSection.classList.remove('d-none');
                    }

                    // Nearby venues
                    var venuesListEl = document.getElementById('sport-detail-venues-list');
                    var venuesSection = document.getElementById('sport-detail-venues-section');
                    if (sport.nearby_venues && sport.nearby_venues.length > 0) {
                        var venueHtml = '<div class="list-group list-group-flush">';
                        sport.nearby_venues.forEach(function (v) {
                            venueHtml += '<div class="list-group-item bg-transparent border-secondary text-white px-0 py-2">';
                            venueHtml += '<div class="d-flex justify-content-between align-items-center">';
                            venueHtml += '<div><strong>' + v.name + '</strong><br><small>' + (v.address || '') + '</small></div>';
                            venueHtml += '<span class="badge bg-warning text-dark">' + (v.rating || 'N/A') + ' <i class="bi bi-star-fill ms-1"></i></span>';
                            venueHtml += '</div></div>';
                        });
                        venueHtml += '</div>';
                        venuesListEl.innerHTML = venueHtml;
                        venuesSection.classList.remove('d-none');
                    } else {
                        venuesListEl.innerHTML = '<p class="text-white-50 mb-0">No nearby venues found.</p>';
                        venuesSection.classList.remove('d-none');
                    }

                    // Join Match button (if there are upcoming matches)
                    var joinBtn = document.getElementById('sport-detail-join-match');
                    if (sport.upcoming_matches && sport.upcoming_matches.length > 0) {
                        joinBtn.classList.remove('d-none');
                        joinBtn.addEventListener('click', function handler() {
                            var modal = bootstrap.Modal.getInstance(modalEl);
                            if (modal) modal.hide();
                            scrollToSection('discover-section');
                            setTimeout(function () {
                                var sportSelect = document.getElementById('filter-sport');
                                if (sportSelect) {
                                    sportSelect.value = sport.name;
                                    var filterBtn = document.getElementById('filter-apply-btn');
                                    if (filterBtn) filterBtn.click();
                                }
                            }, 300);
                            joinBtn.removeEventListener('click', handler);
                        });
                    } else {
                        joinBtn.classList.add('d-none');
                    }
                })
                .catch(function (err) {
                    console.error('Failed to load sport details:', err);
                    document.getElementById('sport-details-loading').classList.add('d-none');
                    document.getElementById('sport-details-error').classList.remove('d-none');
                    document.getElementById('sport-modal-subtitle').textContent = 'Error loading details';
                });
        });

        // "Find Matches" button in modal footer
        var findMatchesBtn = document.getElementById('sport-detail-find-matches');
        if (findMatchesBtn) {
            findMatchesBtn.addEventListener('click', function () {
                var modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                if (currentSportName) {
                    var sportSelect = document.getElementById('filter-sport');
                    if (sportSelect) {
                        sportSelect.value = currentSportName;
                        scrollToSection('discover-section');
                        setTimeout(function () {
                            var filterBtn = document.getElementById('filter-apply-btn');
                            if (filterBtn) filterBtn.click();
                        }, 300);
                    }
                }
            });
        }
    }

    // =============================================================
    // INITIALIZE ALL MODULES
    // =============================================================
    document.addEventListener('DOMContentLoaded', function () {
        initGameDetailsModal();
        initDiscoverFilters();
        initJoinMatch();
        initMap();
        initSportsCategories();
        initSportDetailModal();
    });

})();
