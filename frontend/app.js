const API_BASE = 'http://localhost/sports_buddy';
const FLASK_API_BASE = 'http://127.0.0.1:5000';
let currentUserId = 1;
let currentSport = null;
let currentMatches = [];
let matchPollInterval = null;
let userLat = null;
let userLng = null;
let mapInstance = null;
let mapMarkers = [];
let mapInitialized = false;
let userMarker = null;

// ============================================================
// SPORT DEFINITIONS - Expanded to 15 sports (FIX issues #3, #4, #5)
// ============================================================
const SPORTS = [
    // Outdoor Sports
    { name: 'Cricket', icon: '🏏', type: 'outdoor' },
    { name: 'Football', icon: '⚽', type: 'outdoor' },
    { name: 'Basketball', icon: '🏀', type: 'outdoor' },
    { name: 'Kabaddi', icon: '🛡️', type: 'outdoor' },
    { name: 'Tennis', icon: '🎾', type: 'outdoor' },
    { name: 'Hockey', icon: '🏑', type: 'outdoor' },
    { name: 'Cycling', icon: '🚴', type: 'outdoor' },
    { name: 'Running', icon: '🏃', type: 'outdoor' },
    // Indoor Sports
    { name: 'Badminton', icon: '🏸', type: 'indoor' },
    { name: 'Table Tennis', icon: '🏓', type: 'indoor' },
    { name: 'Chess', icon: '♟️', type: 'indoor' },
    { name: 'Carrom', icon: '🎯', type: 'indoor' },
    { name: 'Snooker', icon: '🎱', type: 'indoor' },
    { name: 'Squash', icon: '🏐', type: 'indoor' },
    { name: 'Gym', icon: '💪', type: 'indoor' }
];

// ============================================================
// DOM READY - Main page initializer
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('leaderboardContainer')) {
        fetchLeaderboard();
        setupLeaderboardForms();
        return;
    }

    var dateInput = document.getElementById('match_date');
    if (!dateInput) return;

    var tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.value = tomorrow.toISOString().split('T')[0];
    document.getElementById('match_time').value = '18:00';

    document.getElementById('userSelect').addEventListener('change', function () {
        currentUserId = parseInt(this.value);
        if (currentSport) loadMatchesBySport(currentSport);
        else loadAllMatches();
        loadFriendData();
        captureLocation();
    });

    currentUserId = parseInt(document.getElementById('userSelect').value);

    document.getElementById('backToSportsBtn').addEventListener('click', function () { goBackToSports(); });
    document.getElementById('modalCloseBtn').addEventListener('click', closeMatchDetails);
    document.getElementById('matchDetailsModal').addEventListener('click', function (e) {
        if (e.target === this) closeMatchDetails();
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMatchDetails();
    });

    loadSportsDashboard();
    loadAllMatches();
    startMatchPolling();

    document.getElementById('createMatchForm').addEventListener('submit', function (e) {
        e.preventDefault();
        createMatch();
    });

    captureLocation();
    loadFriendData();
});

function captureLocation() {
    var statusEl = document.getElementById('locationStatus');
    if (!statusEl) return;
    if (!navigator.geolocation) {
        statusEl.textContent = '📍 Geolocation not supported';
        statusEl.className = 'location-status error';
        return;
    }
    statusEl.textContent = '📍 Locating...';
    statusEl.className = 'location-status';
    navigator.geolocation.getCurrentPosition(
        function (position) {
            userLat = position.coords.latitude;
            userLng = position.coords.longitude;
            statusEl.textContent = '📍 Location acquired (' + userLat.toFixed(4) + ', ' + userLng.toFixed(4) + ')';
            statusEl.className = 'location-status active';
            updateUserLocation(userLat, userLng);
            if (document.getElementById('tabMap').classList.contains('active')) initMap();
        },
        function (error) {
            userLat = 16.5062;
            userLng = 80.6480;
            statusEl.textContent = '📍 Using approximate location (Vijayawada)';
            statusEl.className = 'location-status error';
            updateUserLocation(userLat, userLng);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
}

function updateUserLocation(lat, lng) {
    var formData = new FormData();
    formData.append('user_id', currentUserId);
    formData.append('latitude', lat);
    formData.append('longitude', lng);
    fetch(API_BASE + '/update_location.php', { method: 'POST', body: formData })
        .then(function (r) { return r.json(); })
        .then(function (d) { if (!d.success) console.warn('Location update failed:', d.message); })
        .catch(function (e) { console.warn('Location update network error:', e); });
}

function switchTab(tabName) {
    var tabs = document.querySelectorAll('.tab-btn');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
        if (tabs[i].getAttribute('data-tab') === tabName) tabs[i].classList.add('active');
    }
    var contents = document.querySelectorAll('.tab-content');
    for (var i = 0; i < contents.length; i++) contents[i].classList.remove('active');
    var target = document.getElementById('tab' + tabName.charAt(0).toUpperCase() + tabName.slice(1));
    if (target) target.classList.add('active');
    if (tabName === 'map') {
        if (userLat !== null && userLng !== null) {
            setTimeout(function () { initMap(); if (mapInstance) setTimeout(function () { mapInstance.invalidateSize(); }, 100); }, 300);
        } else { if (userLat === null) captureLocation(); }
    }
    if (tabName === 'buddies') loadFriendData();
}

function initMap() {
    if (userLat === null || userLng === null) {
        var mapLoading = document.getElementById('mapLoading');
        if (mapLoading) mapLoading.textContent = 'Waiting for location...';
        return;
    }
    var mapContainer = document.getElementById('map');
    var mapLoading = document.getElementById('mapLoading');
    if (!mapContainer) return;
    if (mapLoading) mapLoading.style.display = 'none';
    if (!mapInstance) {
        mapInstance = L.map('map', { center: [userLat, userLng], zoom: 12 });
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 }).addTo(mapInstance);
        userMarker = L.marker([userLat, userLng]).addTo(mapInstance).bindPopup('📍 Your Location');
        setTimeout(function () { mapInstance.invalidateSize(); }, 200);
    } else {
        mapInstance.setView([userLat, userLng], 12);
        if (userMarker) userMarker.setLatLng([userLat, userLng]);
    }
    loadMapMarkers();
}

function safeFetchJSON(url) {
    return fetch(url).then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        var contentType = response.headers.get('Content-Type') || '';
        if (contentType.indexOf('application/json') === -1) {
            return response.text().then(function (text) {
                if (text.trim().charAt(0) !== '{' && text.trim().charAt(0) !== '[') throw new Error('Backend returned non-JSON');
                return JSON.parse(text);
            });
        }
        return response.json();
    });
}

function loadMapMarkers() {
    for (var i = 0; i < mapMarkers.length; i++) mapInstance.removeLayer(mapMarkers[i]);
    mapMarkers = [];
    var mapInfo = document.getElementById('mapInfo');
    if (!mapInfo) return;
    mapInfo.textContent = 'Loading match data...';
    safeFetchJSON(API_BASE + '/get_matches.php').then(function (data) {
        if (!data.success || !data.matches || data.matches.length === 0) {
            mapInfo.textContent = 'No matches to display on map. Create a match first!';
            return;
        }
        var plotted = 0;
        for (var i = 0; i < data.matches.length; i++) {
            var m = data.matches[i];
            var mLat = parseFloat(m.venue_lat || m.lat);
            var mLng = parseFloat(m.venue_lng || m.lng);
            if (mLat && mLng && !isNaN(mLat) && !isNaN(mLng)) {
                var marker = L.marker([mLat, mLng]).addTo(mapInstance);
                marker.bindPopup('<div style="color:#333;font-family:sans-serif;font-size:13px;min-width:180px;"><strong style="font-size:15px;">' + escapeHtml(m.sport_name) + '</strong><br><span>📍 ' + escapeHtml(m.venue_name) + '</span><br><span>📅 ' + formatDate(m.match_date) + ' at ' + formatTime(m.match_time) + '</span><br><span>👤 ' + escapeHtml(m.creator_name) + '</span><br><span>👥 ' + m.joined_players + '/' + m.max_players + ' players</span></div>');
                mapMarkers.push(marker);
                plotted++;
            }
        }
        if (plotted === 0) mapInfo.textContent = 'No matches with location data. Add venue coordinates to matches.';
        else {
            mapInfo.textContent = plotted + ' match(es) shown on map. Click markers for details.';
            if (mapMarkers.length > 0 && mapInstance) {
                var group = L.featureGroup(mapMarkers);
                mapInstance.fitBounds(group.getBounds().pad(0.1));
            }
        }
    }).catch(function (err) {
        mapInfo.textContent = 'Failed to load match data for map.';
        console.error('loadMapMarkers error:', err.message || err);
    });
}

function setupLeaderboardForms() {
    var submitForm = document.getElementById('submitResultForm');
    if (submitForm) submitForm.addEventListener('submit', function (e) { e.preventDefault(); submitMatchResult(); });
    var overrideForm = document.getElementById('adminOverrideForm');
    if (overrideForm) overrideForm.addEventListener('submit', function (e) { e.preventDefault(); submitAdminOverride(); });
    var drawCheckbox = document.getElementById('result_is_draw');
    var winnerInput = document.getElementById('result_winner_id');
    if (drawCheckbox && winnerInput) {
        drawCheckbox.addEventListener('change', function () {
            if (this.checked) { winnerInput.disabled = true; winnerInput.value = ''; winnerInput.placeholder = 'Draw - no winner'; }
            else { winnerInput.disabled = false; winnerInput.placeholder = 'Winner User ID'; }
        });
    }
}

function loadFriendData() { loadFriendRequests(); loadFriends(); loadOutgoingRequests(); }

function loadFriendRequests() {
    var container = document.getElementById('friendRequestsList');
    if (!container) return;
    container.innerHTML = '<p class="loading">Loading requests...</p>';
    fetch(API_BASE + '/get_friend_requests.php?user_id=' + currentUserId)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) { container.innerHTML = '<p class="no-matches">Error loading requests</p>'; return; }
            var incoming = data.incoming || [];
            if (incoming.length === 0) { container.innerHTML = '<p class="no-matches">No pending friend requests</p>'; return; }
            var html = '';
            for (var i = 0; i < incoming.length; i++) {
                var req = incoming[i];
                var initial = req.sender_name ? req.sender_name.charAt(0).toUpperCase() : '?';
                html += '<div class="buddy-card" id="req-' + req.request_id + '">';
                html += '  <div class="buddy-avatar">' + initial + '</div>';
                html += '  <div class="buddy-info"><div class="buddy-name">' + escapeHtml(req.sender_name) + '</div><div class="buddy-email">' + escapeHtml(req.sender_email) + '</div></div>';
                html += '  <div class="buddy-actions"><button class="btn-buddy-accept" onclick="acceptFriendRequest(' + req.request_id + ')">✓ Accept</button><button class="btn-buddy-reject" onclick="rejectFriendRequest(' + req.request_id + ')">✗ Reject</button></div>';
                html += '</div>';
            }
            container.innerHTML = html;
        })
        .catch(function (err) { container.innerHTML = '<p class="no-matches">Network error loading requests</p>'; console.error(err); });
}

function loadFriends() {
    var container = document.getElementById('friendsList');
    if (!container) return;
    container.innerHTML = '<p class="loading">Loading friends...</p>';
    var url = API_BASE + '/get_friends.php?user_id=' + currentUserId;
    if (userLat !== null && userLng !== null) {
        url += '&lat=' + userLat + '&lng=' + userLng;
    }
    fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) { container.innerHTML = '<p class="no-matches">Error loading friends</p>'; return; }
            var friends = data.friends || [];
            if (friends.length === 0) { container.innerHTML = '<p class="no-matches">No friends yet. Discover players to add!</p>'; return; }
            var html = '';
            for (var i = 0; i < friends.length; i++) {
                var f = friends[i];
                var initial = f.name ? f.name.charAt(0).toUpperCase() : '?';
                var distanceHtml = '';
                if (f.distance_km !== null && f.distance_km !== undefined) {
                    distanceHtml = '<div class="buddy-distance">📍 ' + f.distance_km + ' km away</div>';
                } else {
                    distanceHtml = '<div class="buddy-distance" style="color:#888;">📍 distance not available</div>';
                }
                html += '<div class="buddy-card"><div class="buddy-avatar">' + initial + '</div><div class="buddy-info"><div class="buddy-name">' + escapeHtml(f.name) + '</div><div class="buddy-email">' + escapeHtml(f.email) + '</div>' + distanceHtml + '</div><span class="buddy-status accepted">Friends</span></div>';
            }
            container.innerHTML = html;
        })
        .catch(function (err) { container.innerHTML = '<p class="no-matches">Network error loading friends</p>'; console.error(err); });
}

function loadOutgoingRequests() {
    var container = document.getElementById('outgoingRequestsList');
    if (!container) return;
    container.innerHTML = '<p class="loading">Loading...</p>';
    fetch(API_BASE + '/get_friend_requests.php?user_id=' + currentUserId)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) { container.innerHTML = '<p class="no-matches">Error</p>'; return; }
            var outgoing = data.outgoing || [];
            if (outgoing.length === 0) { container.innerHTML = '<p class="no-matches">No sent requests</p>'; return; }
            var html = '';
            for (var i = 0; i < outgoing.length; i++) {
                var req = outgoing[i];
                var initial = req.receiver_name ? req.receiver_name.charAt(0).toUpperCase() : '?';
                var statusText = req.status.charAt(0).toUpperCase() + req.status.slice(1);
                html += '<div class="buddy-card"><div class="buddy-avatar">' + initial + '</div><div class="buddy-info"><div class="buddy-name">' + escapeHtml(req.receiver_name) + '</div><div class="buddy-email">' + escapeHtml(req.receiver_email) + '</div></div><span class="buddy-status ' + req.status + '">' + statusText + '</span></div>';
            }
            container.innerHTML = html;
        })
        .catch(function (err) { container.innerHTML = '<p class="no-matches">Network error</p>'; console.error(err); });
}

function sendFriendRequest(receiverId) {
    var formData = new FormData();
    formData.append('sender_id', currentUserId);
    formData.append('receiver_id', receiverId);
    fetch(API_BASE + '/send_request.php', { method: 'POST', body: formData })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) { showMessage(data.message, 'success'); loadFriendData(); discoverPlayers(); }
            else { showMessage(data.message, 'error'); }
        })
        .catch(function (err) { showMessage('Network error sending request', 'error'); console.error(err); });
}

function acceptFriendRequest(requestId) {
    var formData = new FormData();
    formData.append('request_id', requestId);
    formData.append('user_id', currentUserId);
    fetch(API_BASE + '/accept_request.php', { method: 'POST', body: formData })
        .then(function (r) { return r.json(); })
        .then(function (data) { if (data.success) { showMessage(data.message, 'success'); loadFriendData(); } else { showMessage(data.message, 'error'); } })
        .catch(function (err) { showMessage('Network error accepting request', 'error'); console.error(err); });
}

function rejectFriendRequest(requestId) {
    var formData = new FormData();
    formData.append('request_id', requestId);
    formData.append('user_id', currentUserId);
    fetch(API_BASE + '/reject_request.php', { method: 'POST', body: formData })
        .then(function (r) { return r.json(); })
        .then(function (data) { if (data.success) { showMessage(data.message, 'success'); loadFriendData(); } else { showMessage(data.message, 'error'); } })
        .catch(function (err) { showMessage('Network error rejecting request', 'error'); console.error(err); });
}

function discoverPlayers() {
    var container = document.getElementById('discoverPlayersList');
    if (!container) return;
    var sportType = document.getElementById('discoverSport').value;
    var maxDistance = document.getElementById('discoverDistance').value || 50;
    container.innerHTML = '<p class="loading">Searching for players...</p>';
    var url = API_BASE + '/suggest_players.php?user_id=' + currentUserId + '&max_distance=' + maxDistance;
    if (sportType) url += '&sport_type=' + encodeURIComponent(sportType);
    if (userLat !== null && userLng !== null) url += '&lat=' + userLat + '&lng=' + userLng;
    console.log("currentUserId =", currentUserId);
    console.log("userLat =", userLat);
    console.log("userLng =", userLng);
    console.log("URL =", url);
    fetch(url).then(function (r) { return r.json(); }).then(function (data) {
        if (!data.success) { container.innerHTML = '<p class="no-matches">Error: ' + escapeHtml(data.message) + '</p>'; return; }
        var players = data.players || [];
        if (players.length === 0) { container.innerHTML = '<p class="no-matches">No players found matching your filters</p>'; return; }
        var html = '';
        for (var i = 0; i < players.length; i++) {
            var p = players[i];
            var initial = p.name ? p.name.charAt(0).toUpperCase() : '?';
            var distanceHtml = '';
            if (p.distance_km !== null && p.distance_km !== undefined) {
                distanceHtml = '<div class="buddy-distance">📍 ' + p.distance_km + ' km away</div>';
            } else {
                distanceHtml = '<div class="buddy-distance" style="color:#888;">📍 distance not available</div>';
            }
            html += '<div class="buddy-card"><div class="buddy-avatar">' + initial + '</div><div class="buddy-info"><div class="buddy-name">' + escapeHtml(p.name) + '</div><div class="buddy-email">' + escapeHtml(p.email) + '</div>' + distanceHtml + '</div><div class="buddy-actions"><button class="btn-buddy-add" onclick="sendFriendRequest(' + p.id + ')">+ Add Friend</button></div></div>';
        }
        container.innerHTML = html;
    }).catch(function (err) { container.innerHTML = '<p class="no-matches">Network error searching players</p>'; console.error(err); });
}

function discoverMatches() {
    var container = document.getElementById('discoverMatchesList');
    if (!container) return;
    var sportName = document.getElementById('filterSportName').value;
    var sportType = document.getElementById('filterSportType').value;
    var maxDistance = document.getElementById('filterDistance').value || 50;
    container.innerHTML = '<p class="loading">Searching for matches...</p>';
    var url = API_BASE + '/filter_matches.php?';
    if (sportName) url += 'sport_name=' + encodeURIComponent(sportName) + '&';
    if (sportType) url += 'sport_type=' + encodeURIComponent(sportType) + '&';
    if (userLat !== null && userLng !== null) url += 'lat=' + userLat + '&lng=' + userLng + '&max_distance=' + maxDistance;
    fetch(url).then(function (r) { return r.json(); }).then(function (data) {
        if (!data.success) { container.innerHTML = '<p class="no-matches">Error: ' + escapeHtml(data.message) + '</p>'; return; }
        var matches = data.matches || [];
        if (matches.length === 0) { container.innerHTML = '<p class="no-matches">No matches found matching your filters</p>'; return; }
        var html = '';
        for (var i = 0; i < matches.length; i++) {
            var m = matches[i];
            var joinedCount = parseInt(m.joined_players);
            var maxPlayers = parseInt(m.max_players);
            var isFull = joinedCount >= maxPlayers;
            var badgeClass = m.sport_type === 'outdoor' ? 'badge-outdoor' : 'badge-indoor';
            var sportIcon = getSportIcon(m.sport_name);
            var distanceHtml = '';
            if (m.distance_km !== null && m.distance_km !== undefined) {
                distanceHtml = '<span>📍 ' + m.distance_km + ' km</span>';
            }
            html += '<div class="match-card"><div class="match-info"><h3><span class="sport-icon-sm">' + sportIcon + '</span> ' + escapeHtml(m.sport_name) + ' <span class="sport-type-badge ' + badgeClass + '">' + m.sport_type + '</span></h3><div class="match-details"><span>📅 ' + formatDate(m.match_date) + '</span><span>⏰ ' + formatTime(m.match_time) + '</span><span>📍 ' + escapeHtml(m.venue_name) + '</span>' + distanceHtml + '</div></div><div class="match-meta"><div class="creator-name">👤 ' + escapeHtml(m.creator_name) + '</div><div class="player-count">' + joinedCount + ' / <span class="max">' + maxPlayers + '</span></div><div class="match-actions">' + (isFull ? '<button class="btn btn-join" disabled>Full</button>' : '<button class="btn btn-join" onclick="joinMatchFromList(' + m.id + ')">Join</button>') + '<button class="btn btn-details" onclick="openMatchDetails(' + m.id + ')">Details</button></div></div></div>';
        }
        container.innerHTML = html;
    }).catch(function (err) { container.innerHTML = '<p class="no-matches">Network error searching matches</p>'; console.error(err); });
}

// ============================================================
// loadSportsDashboard() - NO hardcoded limit, renders ALL sports
// ============================================================
function loadSportsDashboard() {
    var container = document.getElementById('sportDashboard');
    if (!container) return;
    var html = '';
    for (var i = 0; i < SPORTS.length; i++) {
        var sport = SPORTS[i];
        var tagClass = sport.type === 'outdoor' ? 'outdoor' : 'indoor';
        var tagText = sport.type === 'outdoor' ? '🌿 Outdoor' : '🏠 Indoor';
        var isActive = (currentSport === sport.name) ? 'active' : '';
        html += '<div class="sport-card ' + isActive + '" data-sport="' + escapeHtml(sport.name) + '" onclick="onSportClick(\'' + escapeHtml(sport.name) + '\')">';
        html += '  <span class="sport-icon">' + sport.icon + '</span><span class="sport-name">' + escapeHtml(sport.name) + '</span><span class="sport-tag ' + tagClass + '">' + tagText + '</span></div>';
    }
    container.innerHTML = html;
}

function onSportClick(sportName) {
    if (currentSport === sportName) goBackToSports();
    else { currentSport = sportName; updateSportCardActive(sportName); document.getElementById('backToSportsBtn').style.display = 'inline-block'; loadMatchesBySport(sportName); }
}

function updateSportCardActive(sportName) {
    var cards = document.querySelectorAll('.sport-card');
    for (var i = 0; i < cards.length; i++) { cards[i].classList.remove('active'); if (cards[i].getAttribute('data-sport') === sportName) cards[i].classList.add('active'); }
}

function goBackToSports() {
    currentSport = null;
    document.getElementById('backToSportsBtn').style.display = 'none';
    document.getElementById('matchesTitle').textContent = 'All Matches';
    var cards = document.querySelectorAll('.sport-card');
    for (var i = 0; i < cards.length; i++) cards[i].classList.remove('active');
    loadAllMatches();
}

function loadMatchesBySport(sport) {
    var matchList = document.getElementById('matchList');
    if (!matchList) return;
    matchList.innerHTML = '<p class="loading">Loading ' + escapeHtml(sport) + ' matches...</p>';
    document.getElementById('matchesTitle').textContent = escapeHtml(sport) + ' Matches';
    fetch(API_BASE + '/get_matches.php?sport=' + encodeURIComponent(sport))
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (data) { if (data.success) { currentMatches = data.matches; renderMatchCards(data.matches); } else { matchList.innerHTML = '<p class="no-matches">Error: ' + escapeHtml(data.message) + '</p>'; } })
        .catch(function (err) { matchList.innerHTML = '<p class="no-matches">Failed to load matches.</p>'; console.error(err); });
}

function loadAllMatches() {
    var matchList = document.getElementById('matchList');
    if (!matchList) return;
    matchList.innerHTML = '<p class="loading">Loading matches...</p>';
    fetch(API_BASE + '/get_matches.php')
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (data) { if (data.success) { currentMatches = data.matches; renderMatchCards(data.matches); } else { matchList.innerHTML = '<p class="no-matches">Error: ' + escapeHtml(data.message) + '</p>'; } })
        .catch(function (err) { matchList.innerHTML = '<p class="no-matches">Failed to load matches.</p>'; console.error(err); });
}

function renderMatchCards(matches) {
    var matchList = document.getElementById('matchList');
    if (!matchList) return;
    if (!matches || matches.length === 0) { matchList.innerHTML = '<p class="no-matches">' + (currentSport ? 'No ' + escapeHtml(currentSport) + ' matches available.' : 'No matches available. Create one!') + '</p>'; return; }
    var html = '';
    for (var i = 0; i < matches.length; i++) {
        var m = matches[i];
        var joinedCount = parseInt(m.joined_players);
        var maxPlayers = parseInt(m.max_players);
        var isFull = joinedCount >= maxPlayers;
        var badgeClass = m.sport_type === 'outdoor' ? 'badge-outdoor' : 'badge-indoor';
        var sportIcon = getSportIcon(m.sport_name);
        html += '<div class="match-card"><div class="match-info"><h3><span class="sport-icon-sm">' + sportIcon + '</span> ' + escapeHtml(m.sport_name) + ' <span class="sport-type-badge ' + badgeClass + '">' + m.sport_type + '</span></h3><div class="match-details"><span><span class="icon">📅</span> ' + formatDate(m.match_date) + '</span><span><span class="icon">⏰</span> ' + formatTime(m.match_time) + '</span><span><span class="icon">📍</span> ' + escapeHtml(m.venue_name) + '</span></div></div><div class="match-meta"><div class="creator-name">👤 ' + escapeHtml(m.creator_name) + '</div><div class="player-count">' + joinedCount + ' / <span class="max">' + maxPlayers + '</span></div><div class="match-actions">' + (isFull ? '<button class="btn btn-join" disabled>Full</button>' : '<button class="btn btn-join" onclick="joinMatchFromList(' + m.id + ')">Join</button>') + '<button class="btn btn-details" onclick="openMatchDetails(' + m.id + ')">Details</button></div></div></div>';
    }
    matchList.innerHTML = html;
}

function openMatchDetails(matchId) {
    var modal = document.getElementById('matchDetailsModal');
    var modalBody = document.getElementById('modalBody');
    var modalTitle = document.getElementById('modalTitle');
    if (!modal) return;
    modalTitle.textContent = 'Loading...';
    modalBody.innerHTML = '<p style="text-align:center;padding:40px;color:#888;">Loading match details...</p>';
    modal.style.display = 'flex';
    fetch(API_BASE + '/get_match_details.php?id=' + matchId)
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (data) { if (data.success) renderMatchDetails(data); else modalBody.innerHTML = '<p class="no-matches">Error: ' + escapeHtml(data.message) + '</p>'; })
        .catch(function (err) { modalBody.innerHTML = '<p class="no-matches">Failed to load match details.</p>'; console.error(err); });
}

function renderMatchDetails(data) {
    var modalBody = document.getElementById('modalBody');
    var modalTitle = document.getElementById('modalTitle');
    if (!modalBody) return;
    var match = data.match, participants = data.participants, joinedCount = data.joined_count, status = data.status;
    var maxPlayers = parseInt(match.max_players), sportIcon = getSportIcon(match.sport_name), isFull = (status === 'Full');
    modalTitle.textContent = match.sport_name + ' at ' + match.venue_name;
    var userJoined = false, isCreator = (parseInt(match.creator_id) === currentUserId);
    for (var i = 0; i < participants.length; i++) { if (parseInt(participants[i].user_id) === currentUserId) { userJoined = true; break; } }
    var participantsHtml = '';
    for (var i = 0; i < participants.length; i++) {
        var p = participants[i];
        var initial = p.user_name ? p.user_name.charAt(0).toUpperCase() : '?';
        var badgeHtml = (parseInt(p.user_id) === parseInt(match.creator_id)) ? '<span class="participant-badge creator">Creator</span>' : '';
        participantsHtml += '<div class="participant-item"><div class="participant-avatar">' + initial + '</div><div class="participant-info"><div class="participant-name">' + escapeHtml(p.user_name) + '</div><div class="participant-email">' + escapeHtml(p.user_email) + '</div></div>' + badgeHtml + '</div>';
    }
    var statusClass = 'status-' + status.toLowerCase();
    var html = '';
    html += '<div class="modal-match-header"><span class="modal-sport-icon">' + sportIcon + '</span><div><div class="modal-match-title">' + escapeHtml(match.sport_name) + ' at ' + escapeHtml(match.venue_name) + '</div><div class="modal-match-subtitle">Created by ' + escapeHtml(match.creator_name) + '</div></div></div>';
    html += '<div class="modal-info-grid"><div class="modal-info-item"><div class="label">Status</div><div class="value ' + statusClass + '">' + status + '</div></div><div class="modal-info-item"><div class="label">Date</div><div class="value">' + formatDate(match.match_date) + '</div></div><div class="modal-info-item"><div class="label">Time</div><div class="value">' + formatTime(match.match_time) + '</div></div><div class="modal-info-item"><div class="label">Venue</div><div class="value">' + escapeHtml(match.venue_name) + '</div></div><div class="modal-info-item"><div class="label">Sport Type</div><div class="value">' + match.sport_type.charAt(0).toUpperCase() + match.sport_type.slice(1) + '</div></div><div class="modal-info-item"><div class="label">Players</div><div class="value">' + joinedCount + ' / ' + maxPlayers + '</div></div></div>';
    html += '<div class="participants-section"><h3>👥 Participants (' + joinedCount + ')</h3>' + (participants.length > 0 ? '<div class="participant-list">' + participantsHtml + '</div>' : '<p style="color:#888;text-align:center;padding:12px;">No participants yet. Be the first to join!</p>') + '</div>';
    html += '<div class="modal-actions">' + (isCreator ? '<button class="btn" disabled style="background:#555;color:#999;cursor:not-allowed;">You created this match</button>' : (userJoined ? '<button class="btn btn-modal-leave" onclick="leaveMatchFromModal(' + match.id + ')">Leave Match</button>' : (isFull ? '<button class="btn btn-modal-join" disabled>Match Full</button>' : '<button class="btn btn-modal-join" onclick="joinMatchFromModal(' + match.id + ')">Join Match</button>'))) + '<button class="btn btn-back" onclick="closeMatchDetails()">Close</button></div>';
    modalBody.innerHTML = html;
}

function closeMatchDetails() { var modal = document.getElementById('matchDetailsModal'); if (modal) modal.style.display = 'none'; }

function joinMatchFromList(matchId) { joinMatch(matchId, function () { if (currentSport) loadMatchesBySport(currentSport); else loadAllMatches(); }); }
function joinMatchFromModal(matchId) { joinMatch(matchId, function () { openMatchDetails(matchId); if (currentSport) loadMatchesBySport(currentSport); else loadAllMatches(); }); }

function leaveMatchFromModal(matchId) {
    var messageDiv = document.getElementById('createMessage'); if (!messageDiv) return;
    messageDiv.className = 'message'; messageDiv.textContent = 'Leaving match...'; messageDiv.style.display = 'block'; messageDiv.style.color = '#aaa';
    var formData = new FormData(); formData.append('match_id', matchId); formData.append('user_id', currentUserId);
    fetch(API_BASE + '/leave_match.php', { method: 'POST', body: formData }).then(function (r) { return r.json(); }).then(function (data) {
        if (data.success) { messageDiv.className = 'message success'; messageDiv.textContent = 'Left the match!'; openMatchDetails(matchId); if (currentSport) loadMatchesBySport(currentSport); else loadAllMatches(); }
        else { messageDiv.className = 'message error'; messageDiv.textContent = data.message || 'Failed to leave match.'; }
    }).catch(function (err) { messageDiv.className = 'message error'; messageDiv.textContent = 'Network error.'; console.error(err); });
    setTimeout(function () { messageDiv.style.display = 'none'; }, 4000);
}

function joinMatch(matchId, callback) {
    var messageDiv = document.getElementById('createMessage'); if (!messageDiv) return;
    messageDiv.className = 'message'; messageDiv.textContent = 'Joining match...'; messageDiv.style.display = 'block'; messageDiv.style.color = '#aaa';
    var formData = new FormData(); formData.append('match_id', matchId); formData.append('user_id', currentUserId);
    fetch(API_BASE + '/join_match.php', { method: 'POST', body: formData }).then(function (r) { return r.json(); }).then(function (data) {
        if (data.success) { messageDiv.className = 'message success'; messageDiv.textContent = 'Successfully joined the match!'; if (typeof callback === 'function') callback(); }
        else { messageDiv.className = 'message error'; messageDiv.textContent = data.message || 'Failed to join match.'; }
    }).catch(function (err) { messageDiv.className = 'message error'; messageDiv.textContent = 'Network error. Is the backend running?'; console.error(err); });
    setTimeout(function () { messageDiv.style.display = 'none'; }, 4000);
}

function createMatch() {
    var sportName = document.getElementById('sport_name').value, sportType = document.getElementById('sport_type').value;
    var maxPlayers = document.getElementById('max_players').value, matchDate = document.getElementById('match_date').value;
    var matchTime = document.getElementById('match_time').value, venueName = document.getElementById('venue_name').value;
    var messageDiv = document.getElementById('createMessage');
    if (!sportName || !matchDate || !matchTime || !venueName) { messageDiv.className = 'message error'; messageDiv.textContent = 'Please fill in all fields.'; messageDiv.style.display = 'block'; return; }
    var formData = new FormData();
    formData.append('creator_id', currentUserId); formData.append('sport_name', sportName); formData.append('sport_type', sportType);
    formData.append('max_players', maxPlayers); formData.append('match_date', matchDate); formData.append('match_time', matchTime);
    formData.append('venue_name', venueName);
    if (userLat !== null && userLng !== null) { formData.append('venue_lat', userLat); formData.append('venue_lng', userLng); }
    messageDiv.className = 'message'; messageDiv.textContent = 'Creating match...'; messageDiv.style.display = 'block'; messageDiv.style.color = '#aaa';
    fetch(API_BASE + '/create_match.php', { method: 'POST', body: formData }).then(function (r) { return r.json(); }).then(function (data) {
        if (data.success) { messageDiv.className = 'message success'; messageDiv.textContent = 'Match created successfully!'; document.getElementById('createMatchForm').reset(); document.getElementById('match_date').value = new Date(Date.now() + 86400000).toISOString().split('T')[0]; document.getElementById('match_time').value = '18:00'; if (currentSport) loadMatchesBySport(currentSport); else loadAllMatches(); }
        else { messageDiv.className = 'message error'; messageDiv.textContent = data.message || 'Failed to create match.'; }
    }).catch(function (err) { messageDiv.className = 'message error'; messageDiv.textContent = 'Network error. Is the backend running?'; console.error(err); });
    setTimeout(function () { messageDiv.style.display = 'none'; }, 4000);
}

function fetchLeaderboard() {
    var container = document.getElementById('leaderboardContainer'); if (!container) return;
    container.innerHTML = '<p class="loading">Loading leaderboard...</p>';
    fetch(API_BASE + '/get_leaderboard.php').then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (data) { if (data.success) { renderLeaderboard(data); renderSummary(data); } else { container.innerHTML = '<p class="no-matches">Error: ' + escapeHtml(data.message) + '</p>'; } })
        .catch(function (err) { container.innerHTML = '<p class="no-matches">Failed to load leaderboard.</p>'; console.error(err); });
}

function renderSummary(data) {
    var totalPlayersEl = document.getElementById('totalPlayers'), totalMatchesEl = document.getElementById('totalMatches');
    var totalPointsEl = document.getElementById('totalPoints'), lastUpdatedEl = document.getElementById('lastUpdated');
    if (totalPlayersEl) totalPlayersEl.textContent = data.summary.total_players;
    if (totalMatchesEl) totalMatchesEl.textContent = data.summary.total_matches_played;
    if (totalPointsEl) totalPointsEl.textContent = data.summary.total_points_earned;
    if (lastUpdatedEl) lastUpdatedEl.textContent = data.last_updated ? data.last_updated.split(' ')[1] : '--';
}

function renderLeaderboard(data) {
    var container = document.getElementById('leaderboardContainer'); if (!container) return;
    var players = data.leaderboard;
    if (!players || players.length === 0) { container.innerHTML = '<p class="no-matches">No players found.</p>'; return; }
    var html = '<table class="lb-table"><thead><tr><th>Rank</th><th>Player</th><th>Points</th><th class="lb-stat">Wins</th><th class="lb-stat">Losses</th><th class="lb-stat">Draws</th><th>Win %</th><th>Matches</th></tr></thead><tbody>';
    for (var i = 0; i < players.length; i++) {
        var p = players[i];
        var rankClass = p.rank === 1 ? 'lb-rank-1' : p.rank === 2 ? 'lb-rank-2' : p.rank === 3 ? 'lb-rank-3' : '';
        var initial = p.user_name ? p.user_name.charAt(0).toUpperCase() : '?';
        var winBarWidth = Math.min(p.win_percentage, 100);
        var medalIcon = p.rank === 1 ? '🥇' : p.rank === 2 ? '🥈' : p.rank === 3 ? '🥉' : '';
        html += '<tr><td class="lb-rank ' + rankClass + '">' + medalIcon + ' ' + p.rank + '</td><td><div class="lb-player"><div class="lb-player-avatar">' + initial + '</div><span class="lb-player-name">' + escapeHtml(p.user_name) + '</span></div></td><td class="lb-points">' + p.points + '</td><td class="lb-stat lb-stat-wins">' + p.wins + '</td><td class="lb-stat lb-stat-losses">' + p.losses + '</td><td class="lb-stat lb-stat-draws">' + p.draws + '</td><td><div class="lb-win-bar-container"><div class="lb-win-bar" style="width:' + winBarWidth + '%;"></div></div><span class="lb-win-pct">' + p.win_percentage + '%</span></td><td>' + p.matches_played + '</td></tr>';
    }
    html += '</tbody></table>';
    container.innerHTML = html;
}

function submitMatchResult() {
    var messageDiv = document.getElementById('resultMessage'); if (!messageDiv) return;
    var matchId = document.getElementById('result_match_id').value, submittedBy = document.getElementById('result_submitted_by').value;
    var winnerId = document.getElementById('result_winner_id').value, isDraw = document.getElementById('result_is_draw').checked ? 1 : 0;
    if (!matchId || !submittedBy) { messageDiv.className = 'message error'; messageDiv.textContent = 'Match ID and Submitted By are required.'; messageDiv.style.display = 'block'; return; }
    messageDiv.className = 'message'; messageDiv.textContent = 'Submitting result...'; messageDiv.style.display = 'block'; messageDiv.style.color = '#aaa';
    var formData = new FormData(); formData.append('match_id', matchId); formData.append('submitted_by', submittedBy); formData.append('is_draw', isDraw);
    if (!isDraw && winnerId) formData.append('winner_id', winnerId);
    fetch(API_BASE + '/submit_match_result.php', { method: 'POST', body: formData }).then(function (r) { return r.json(); }).then(function (data) {
        if (data.success) { messageDiv.className = 'message success'; messageDiv.textContent = 'Result submitted! Leaderboard updated.'; document.getElementById('submitResultForm').reset(); fetchLeaderboard(); }
        else { messageDiv.className = 'message error'; messageDiv.textContent = data.message || 'Failed to submit result.'; }
    }).catch(function (err) { messageDiv.className = 'message error'; messageDiv.textContent = 'Network error.'; console.error(err); });
    setTimeout(function () { messageDiv.style.display = 'none'; }, 5000);
}

function submitAdminOverride() {
    var messageDiv = document.getElementById('overrideMessage'); if (!messageDiv) return;
    var userId = document.getElementById('override_user_id').value, points = document.getElementById('override_points').value;
    var wins = document.getElementById('override_wins').value, losses = document.getElementById('override_losses').value;
    var draws = document.getElementById('override_draws').value, matches = document.getElementById('override_matches').value, reason = document.getElementById('override_reason').value;
    if (!userId) { messageDiv.className = 'message error'; messageDiv.textContent = 'User ID is required.'; messageDiv.style.display = 'block'; return; }
    messageDiv.className = 'message'; messageDiv.textContent = 'Applying override...'; messageDiv.style.display = 'block'; messageDiv.style.color = '#aaa';
    var formData = new FormData(); formData.append('target_user_id', userId);
    if (points) formData.append('new_points', points); if (wins) formData.append('new_wins', wins); if (losses) formData.append('new_losses', losses);
    if (draws) formData.append('new_draws', draws); if (matches) formData.append('new_matches_played', matches); if (reason) formData.append('reason', reason);
    fetch(API_BASE + '/admin_override.php', { method: 'POST', body: formData }).then(function (r) { return r.json(); }).then(function (data) {
        if (data.success) { messageDiv.className = 'message success'; messageDiv.textContent = 'Override applied! ' + data.user.name + ' stats updated.'; fetchLeaderboard(); }
        else { messageDiv.className = 'message error'; messageDiv.textContent = data.message || 'Failed to apply override.'; }
    }).catch(function (err) { messageDiv.className = 'message error'; messageDiv.textContent = 'Network error.'; console.error(err); });
    setTimeout(function () { messageDiv.style.display = 'none'; }, 5000);
}

function startMatchPolling() { if (matchPollInterval) clearInterval(matchPollInterval); matchPollInterval = setInterval(function () { if (currentSport) loadMatchesBySport(currentSport); else loadAllMatches(); }, 10000); }

function getSportIcon(sportName) {
    var name = (sportName || '').toLowerCase();
    if (name === 'cricket') return '🏏'; if (name === 'football') return '⚽'; if (name === 'basketball') return '🏀';
    if (name === 'kabaddi') return '🛡️'; if (name === 'tennis') return '🎾'; if (name === 'hockey') return '🏑';
    if (name === 'cycling') return '🚴'; if (name === 'running') return '🏃';
    if (name === 'badminton') return '🏸'; if (name === 'table tennis') return '🏓'; if (name === 'chess') return '♟️';
    if (name === 'carrom') return '🎯'; if (name === 'snooker') return '🎱'; if (name === 'squash') return '🏐'; if (name === 'gym') return '💪';
    return '🏅';
}

// ============================================================
// NEARBY SPORTS VENUES - State
// ============================================================
let allVenues = [];
let venuesMapInstance = null;
let venuesMapMarkers = [];
let venuesUserMarker = null;
let filteredVenueIds = [];

// ============================================================
// loadVenues() - Fetch from Flask API /api/nearby-venues
// ============================================================
function loadVenues() {
    var listContainer = document.getElementById('venuesList');
    var infoContainer = document.getElementById('venuesInfo');
    var mapLoading = document.getElementById('venuesMapLoading');
    if (!listContainer) return;

    listContainer.innerHTML = '<p class="loading">Loading nearby sports venues...</p>';
    if (infoContainer) infoContainer.textContent = 'Loading venue data...';
    if (mapLoading) mapLoading.style.display = 'block';

    // Fetch from Flask API (reads data.venues as required)
    safeFetchJSON(FLASK_API_BASE + '/api/nearby-venues')
        .then(function (data) {
            if (!data.venues || data.venues.length === 0) {
                listContainer.innerHTML = '<p class="no-matches">No nearby venues found.</p>';
                if (infoContainer) infoContainer.textContent = 'No venues available.';
                return;
            }

            allVenues = data.venues;
            filteredVenueIds = allVenues.map(function (v) { return v.id; });

            // Initialize venues map
            initVenuesMap();

            // Render venue list
            renderVenueList(allVenues);

            if (infoContainer) {
                infoContainer.textContent = allVenues.length + ' venue(s) found near Andhra Pradesh. Click markers for details.';
            }
        })
        .catch(function (err) {
            console.error('loadVenues error:', err);
            listContainer.innerHTML = '<p class="no-matches">Failed to load venues. Is the Flask server running on port 5000?</p>';
            if (infoContainer) infoContainer.textContent = 'Error loading venue data.';
        });
}

// ============================================================
// initVenuesMap() - Venues Leaflet Map
// ============================================================
function initVenuesMap() {
    var mapContainer = document.getElementById('venuesMap');
    var mapLoading = document.getElementById('venuesMapLoading');
    if (!mapContainer) return;

    if (mapLoading) mapLoading.style.display = 'none';

    var centerLat = userLat || 16.5062;
    var centerLng = userLng || 80.6480;

    if (!venuesMapInstance) {
        venuesMapInstance = L.map('venuesMap', { center: [centerLat, centerLng], zoom: 11 });
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(venuesMapInstance);

        // User location marker (blue)
        venuesUserMarker = L.marker([centerLat, centerLng], {
            icon: L.divIcon({
                className: 'user-location-marker',
                html: '<div style="background:#4285F4;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 8px rgba(0,0,0,0.4);"></div>',
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            })
        }).addTo(venuesMapInstance).bindPopup('📍 Your Location');

        setTimeout(function () { venuesMapInstance.invalidateSize(); }, 300);
    } else {
        venuesMapInstance.setView([centerLat, centerLng], 11);
        if (venuesUserMarker) venuesUserMarker.setLatLng([centerLat, centerLng]);
    }

    // Plot venue markers
    plotVenueMarkers(allVenues);
}

// ============================================================
// plotVenueMarkers() - Add markers for filtered venues
// ============================================================
function plotVenueMarkers(venues) {
    // Clear existing markers
    for (var i = 0; i < venuesMapMarkers.length; i++) {
        venuesMapInstance.removeLayer(venuesMapMarkers[i]);
    }
    venuesMapMarkers = [];

    if (!venues || venues.length === 0) return;

    var plotted = 0;
    for (var i = 0; i < venues.length; i++) {
        var v = venues[i];
        var lat = parseFloat(v.latitude);
        var lng = parseFloat(v.longitude);

        if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
            var marker = L.marker([lat, lng]).addTo(venuesMapInstance);

            // Build popup with all required info: name, sports, rating, slots, distance
            var sportsHtml = '';
            if (v.sport_types && v.sport_types.length > 0) {
                sportsHtml = v.sport_types.map(function (s) {
                    return '<span style="display:inline-block;background:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;margin:2px;font-size:11px;">' + escapeHtml(s) + '</span>';
                }).join(' ');
            }

            var popupHtml = '<div style="color:#333;font-family:sans-serif;font-size:13px;min-width:200px;">' +
                '<strong style="font-size:15px;color:#1a237e;">' + escapeHtml(v.name) + '</strong><br>' +
                '<div style="margin:6px 0;">' + sportsHtml + '</div>' +
                '<hr style="border:none;border-top:1px solid #eee;margin:6px 0;">' +
                '<span>⭐ Rating: <strong>' + v.rating + '</strong></span><br>' +
                '<span>🎯 Available Slots: <strong>' + v.available_slots + '</strong></span><br>' +
                '<span>📍 Distance: <strong>' + v.distance_km + ' km</strong></span><br>' +
                '<span style="color:#666;font-size:11px;">📍 ' + escapeHtml(v.address || '') + '</span>' +
                '</div>';

            marker.bindPopup(popupHtml);
            venuesMapMarkers.push(marker);
            plotted++;
        }
    }

    // Fit bounds to show all markers
    if (plotted > 0 && venuesMapMarkers.length > 0) {
        try {
            var group = L.featureGroup(venuesMapMarkers);
            venuesMapInstance.fitBounds(group.getBounds().pad(0.1));
        } catch (e) {
            console.warn('Could not fit bounds:', e);
        }
    }
}

// ============================================================
// renderVenueList() - Render venue cards below map
// ============================================================
function renderVenueList(venues) {
    var container = document.getElementById('venuesList');
    if (!container) return;

    if (!venues || venues.length === 0) {
        container.innerHTML = '<p class="no-matches">No nearby venues found.</p>';
        return;
    }

    var html = '<div class="venue-cards">';
    for (var i = 0; i < venues.length; i++) {
        var v = venues[i];

        var sportsHtml = '';
        if (v.sport_types && v.sport_types.length > 0) {
            sportsHtml = v.sport_types.map(function (s) {
                return '<span class="venue-sport-tag">' + escapeHtml(s) + '</span>';
            }).join(' ');
        }

        var stars = '';
        var fullStars = Math.floor(v.rating);
        for (var s = 0; s < fullStars; s++) stars += '⭐';
        if (v.rating - fullStars >= 0.5) stars += '⭐';

        html += '<div class="venue-card" data-venue-id="' + v.id + '">';
        html += '  <div class="venue-card-header">';
        html += '    <h3 class="venue-name">' + escapeHtml(v.name) + '</h3>';
        html += '    <span class="venue-rating">' + stars + ' ' + v.rating + '</span>';
        html += '  </div>';
        html += '  <div class="venue-sports">' + sportsHtml + '</div>';
        html += '  <div class="venue-details">';
        html += '    <span>🎯 ' + v.available_slots + ' slots available</span>';
        html += '    <span>📍 ' + v.distance_km + ' km</span>';
        html += '  </div>';
        html += '  <div class="venue-address">📍 ' + escapeHtml(v.address || '') + '</div>';
        html += '</div>';
    }
    html += '</div>';

    container.innerHTML = html;
}

// ============================================================
// filterVenues() - Sport filter for venues
// ============================================================
function filterVenues() {
    var sportFilter = document.getElementById('venueSportFilter');
    if (!sportFilter) return;

    var selectedSport = sportFilter.value.trim();
    var infoContainer = document.getElementById('venuesInfo');

    var filtered;
    if (selectedSport === '') {
        filtered = allVenues;
    } else {
        filtered = allVenues.filter(function (v) {
            if (!v.sport_types) return false;
            return v.sport_types.some(function (s) {
                return s.toLowerCase() === selectedSport.toLowerCase();
            });
        });
    }

    filteredVenueIds = filtered.map(function (v) { return v.id; });

    // Update map markers
    if (venuesMapInstance) {
        for (var i = 0; i < venuesMapMarkers.length; i++) {
            var marker = venuesMapMarkers[i];
            var markerLat = marker.getLatLng().lat;
            var markerLng = marker.getLatLng().lng;
            var isVisible = filtered.some(function (v) {
                return Math.abs(parseFloat(v.latitude) - markerLat) < 0.001 &&
                    Math.abs(parseFloat(v.longitude) - markerLng) < 0.001;
            });
            if (isVisible) {
                venuesMapInstance.addLayer(marker);
            } else {
                venuesMapInstance.removeLayer(marker);
            }
        }
    }

    // Update venue list
    renderVenueList(filtered);

    // Update info
    if (infoContainer) {
        if (filtered.length === 0) {
            infoContainer.textContent = 'No nearby venues found. Try a different sport filter.';
        } else {
            infoContainer.textContent = filtered.length + ' venue(s) found' +
                (selectedSport ? ' for ' + selectedSport : '') + '.';
        }
    }

    // Show "no nearby venues found" message
    if (filtered.length === 0) {
        var container = document.getElementById('venuesList');
        if (container) container.innerHTML = '<p class="no-matches">No nearby venues found.</p>';
    }
}

// Hook into switchTab to load venues when venues tab is activated
// ============================================================
// TEAMS FUNCTIONALITY
// ============================================================
let allTeamsForPreview = [];

function loadTeamsPreview() {
    var container = document.getElementById('teamsPreviewList');
    if (!container) return;
    container.innerHTML = '<p class="loading">Loading teams...</p>';
    fetch(API_BASE + '/get_teams.php')
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (data) {
            if (!data.success) { container.innerHTML = '<p class="error">Failed to load teams</p>'; return; }
            allTeamsForPreview = data.teams.slice(0, 5);
            renderTeamsPreview();
        })
        .catch(function (err) { container.innerHTML = '<p class="error">Error loading teams</p>'; });
}

function renderTeamsPreview() {
    var container = document.getElementById('teamsPreviewList');
    if (!container) return;
    if (allTeamsForPreview.length === 0) { container.innerHTML = '<p class="no-teams">No teams available yet. Be the first to create one!</p>'; return; }
    var html = '';
    for (var i = 0; i < allTeamsForPreview.length; i++) {
        var t = allTeamsForPreview[i];
        html += '<div class="team-card"><div class="team-card-header">' +
            (t.logo ? '<img src="' + t.logo + '" alt="' + escapeHtml(t.team_name) + '" class="team-logo">' : '<div class="team-logo-placeholder">🏆</div>') +
            '<div class="team-info"><h3>' + escapeHtml(t.team_name) + '</h3><p class="team-captain">Captain: ' + escapeHtml(t.captain_name) + '</p></div>' +
            '</div><div class="team-card-body"><div class="team-detail"><span class="label">Sport:</span><span class="value">' + escapeHtml(t.sport_type) + '</span></div>' +
            '<div class="team-detail"><span class="label">Location:</span><span class="value">' + escapeHtml(t.location) + '</span></div>' +
            '<div class="team-detail"><span class="label">Members:</span><span class="value">' + t.current_members + ' / ' + t.max_members + '</span></div>' +
            '</div><div class="team-card-actions"><a href="team_details.php?team_id=' + t.id + '" class="btn btn-primary">View Details</a></div></div>';
    }
    container.innerHTML = html;
}

var originalSwitchTab = switchTab;
switchTab = function (tabName) {
    originalSwitchTab(tabName);
    if (tabName === 'venues') {
        loadVenues();
    }
    if (tabName === 'teams') {
        loadTeamsPreview();
    }
};

function formatDate(dateStr) { var d = new Date(dateStr); return d.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }); }
function formatTime(timeStr) { if (!timeStr) return ''; var parts = timeStr.split(':'); var h = parseInt(parts[0]), m = parts[1], ampm = h >= 12 ? 'PM' : 'AM'; h = h % 12; if (h === 0) h = 12; return h + ':' + m + ' ' + ampm; }
function escapeHtml(str) { if (!str) return ''; var div = document.createElement('div'); div.appendChild(document.createTextNode(str)); return div.innerHTML; }
function showMessage(msg, type) { var messageDiv = document.getElementById('createMessage'); if (!messageDiv) return; messageDiv.className = 'message ' + type; messageDiv.textContent = msg; messageDiv.style.display = 'block'; setTimeout(function () { messageDiv.style.display = 'none'; }, 4000); }