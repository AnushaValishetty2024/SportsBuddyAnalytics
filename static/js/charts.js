// =============================================================
// Sports Buddy - Analytics Charts
// Handles: Dashboard charts using Chart.js
// =============================================================

(function () {
    'use strict';

    const COLORS = {
        green: '#22c55e',
        blue: '#3b82f6',
        yellow: '#f59e0b',
        red: '#ef4444',
        purple: '#a855f7',
        teal: '#14b8a6',
        orange: '#f97316',
        gray: '#64748b'
    };

    let charts = {};

    function destroyChart(key) {
        if (charts[key]) {
            charts[key].destroy();
            delete charts[key];
        }
    }

    window.initDashboardCharts = function (analyticsData) {
        if (!analyticsData) return;

        // Top Players chart
        initTopPlayersChart(analyticsData.top_players || []);
        // Match Activity chart
        initMatchActivityChart(analyticsData.match_activity || []);
        // Sports Distribution chart
        initSportsDistributionChart(analyticsData.sports_distribution || []);
        // Indoor vs Outdoor chart
        initIndoorOutdoorChart(analyticsData.indoor_outdoor || {});
        // Weekly Trend chart
        initWeeklyTrendChart(analyticsData.weekly_trend || []);
    };

    function initTopPlayersChart(data) {
        destroyChart('topPlayers');
        const ctx = document.getElementById('chart-top-players');
        if (!ctx) return;

        const labels = data.map(p => p.name);
        const points = data.map(p => p.total_points);

        charts.topPlayers = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Points',
                    data: points,
                    backgroundColor: COLORS.green,
                    borderColor: COLORS.green,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Top Players by Points',
                        color: '#f8fafc',
                        font: { size: 14, weight: '600' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(51, 65, 85, 0.5)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function initMatchActivityChart(data) {
        destroyChart('matchActivity');
        const ctx = document.getElementById('chart-match-activity');
        if (!ctx) return;

        const labels = data.map(d => d.label);
        const counts = data.map(d => d.count);

        charts.matchActivity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Matches',
                    data: counts,
                    backgroundColor: COLORS.blue,
                    borderColor: COLORS.blue,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Match Activity',
                        color: '#f8fafc',
                        font: { size: 14, weight: '600' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#94a3b8', stepSize: 1 },
                        grid: { color: 'rgba(51, 65, 85, 0.5)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function initSportsDistributionChart(data) {
        destroyChart('sportsDistribution');
        const ctx = document.getElementById('chart-sports-distribution');
        if (!ctx) return;

        const labels = data.map(d => d.sport);
        const values = data.map(d => d.count);
        const bgColors = [
            COLORS.green, COLORS.blue, COLORS.yellow, COLORS.red,
            COLORS.purple, COLORS.teal, COLORS.orange, COLORS.gray
        ];

        charts.sportsDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: bgColors,
                    borderColor: '#1e293b',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', padding: 8, font: { size: 11 } }
                    },
                    title: {
                        display: true,
                        text: 'Sports Distribution',
                        color: '#f8fafc',
                        font: { size: 14, weight: '600' }
                    }
                }
            }
        });
    }

    function initIndoorOutdoorChart(data) {
        destroyChart('indoorOutdoor');
        const ctx = document.getElementById('chart-indoor-outdoor');
        if (!ctx) return;

        const indoor = data.indoor || 0;
        const outdoor = data.outdoor || 0;

        charts.indoorOutdoor = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Indoor', 'Outdoor'],
                datasets: [{
                    data: [indoor, outdoor],
                    backgroundColor: [COLORS.yellow, COLORS.green],
                    borderColor: '#1e293b',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', padding: 12, font: { size: 12 } }
                    },
                    title: {
                        display: true,
                        text: 'Indoor vs Outdoor',
                        color: '#f8fafc',
                        font: { size: 14, weight: '600' }
                    }
                }
            }
        });
    }

    function initWeeklyTrendChart(data) {
        destroyChart('weeklyTrend');
        const ctx = document.getElementById('chart-weekly-trend');
        if (!ctx) return;

        const labels = data.map(d => d.day || d.date);
        const values = data.map(d => d.count);

        charts.weeklyTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Matches',
                    data: values,
                    borderColor: COLORS.teal,
                    backgroundColor: 'rgba(20, 184, 166, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: COLORS.teal,
                    pointBorderColor: '#1e293b',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Weekly Match Trend',
                        color: '#f8fafc',
                        font: { size: 14, weight: '600' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#94a3b8', stepSize: 1 },
                        grid: { color: 'rgba(51, 65, 85, 0.5)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // =============================================================
    // FETCH ANALYTICS DATA FROM API
    // =============================================================

    window.fetchAnalyticsData = function () {
        fetch('/api/dashboard/analytics')
            .then(r => r.json())
            .then(data => {
                if (data.success && data.analytics) {
                    window.initDashboardCharts(data.analytics);
                    window.updateDashboardKPIs(data.analytics);
                }
            })
            .catch(err => console.error('Failed to load analytics charts:', err));
    };

    window.updateDashboardKPIs = function (analytics) {
        if (!analytics) return;
        const totalUsersEl = document.getElementById('kpi-total-users');
        if (totalUsersEl) totalUsersEl.textContent = analytics.total_users != null ? analytics.total_users : 0;
        const activeUsersEl = document.getElementById('kpi-active-users');
        if (activeUsersEl) activeUsersEl.textContent = analytics.active_users != null ? analytics.active_users : 0;
        const matchesTodayEl = document.getElementById('kpi-matches-today');
        if (matchesTodayEl) matchesTodayEl.textContent = analytics.matches_today != null ? analytics.matches_today : 0;
        const nearbyVenuesEl = document.getElementById('kpi-nearby-venues');
        if (nearbyVenuesEl) nearbyVenuesEl.textContent = analytics.nearby_venues != null ? analytics.nearby_venues : 0;
    };

})();