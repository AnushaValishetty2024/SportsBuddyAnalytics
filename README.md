# 🏆 Sports Buddy Analytics

# 🏆 Sports Buddy Analytics

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap)
![HTML5](https://img.shields.io/badge/HTML5-Markup-red?logo=html5)
![CSS3](https://img.shields.io/badge/CSS3-Styling-blue?logo=css3)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)
![Git](https://img.shields.io/badge/Git-Version%20Control-red?logo=git)
![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)


A full-stack Sports Event Management and Analytics web application built using Flask, Python, MySQL, HTML, CSS, JavaScript, and Bootstrap.
A full-stack **Sports Event Management and Analytics** web application built using **Flask, Python, MySQL, HTML, CSS, JavaScript, and Bootstrap**. The platform enables players to discover and join sports events, connect with teammates, track achievements, view leaderboards, receive notifications, and monitor their performance through an interactive dashboard.

---

## 📌 Project Overview

Sports Buddy Analytics is designed to simplify sports event management while enhancing player engagement through analytics and social features. The application provides separate modules for players and administrators, allowing users to register, participate in events, track rankings, earn badges, and analyze their overall performance.

The project follows a modular architecture with Flask Blueprints, MySQL database integration, responsive UI design, and interactive dashboards.

---

# ✨ Features

### 🔐 User Authentication
- User Registration
- Secure Login & Logout
- Session Management
- Profile Management

### 🏅 Player Dashboard
- Personalized Dashboard
- Performance Statistics
- Upcoming Matches
- Recent Activities
- Notifications
- Quick Access Cards

### ⚽ Match Discovery
- Browse Available Sports Events
- Search Matches
- Filter by Sport
- View Match Details
- Join Events

### 👥 Team Management
- Create Teams
- Join Teams
- Team Profiles
- Team Statistics

### 📊 Analytics Dashboard
- Player Performance
- Match Statistics
- Sports Participation Analysis
- Interactive Charts
- Activity Summary

### 🏆 Leaderboard System
- Player Rankings
- Points System
- Achievement Tracking
- Dynamic Leaderboard

### 🎖 Achievement & Badge System
- Player Badges
- Achievement Unlocks
- Progress Tracking
- Rewards Display

### 🔔 Notification System
- Event Notifications
- Match Updates
- Achievement Alerts
- User Notifications

### 💬 Team Communication
- Team Chat
- Player Interaction
- Event Discussions

### 👤 User Profile
- Personal Information
- Sports Interests
- Match History
- Achievements
- Performance Overview

### ⚙️ Admin Features
- Manage Events
- Manage Users
- View Analytics
- System Monitoring

---

# 🛠 Technologies Used

## Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Backend
- Python
- Flask
- Flask Blueprints

## Database
- MySQL
- SQL

## Development Tools
- Visual Studio Code
- XAMPP
- Git
- GitHub

---

# 📂 Project Structure

```
SportsBuddyAnalytics/
│
├── app.py
├── config.py
├── requirements.txt
├── seed_demo_data.py
├── models/
├── routes/
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── data/
├── uploads/
├── screenshots/
├── database/
└── README.md
```

---

# 📸 Project Screenshots

## 🏠 Home Page

![Home Page](screenshots/home-page.png)

---

## 🔐 User Authentication

| Login | Create Account |
|--------|----------------|
| ![Login](screenshots/login.png) | ![Create Account](screenshots/create-account.png) |

---

## 📊 Player Dashboard

![Dashboard](screenshots/dashboard.png)

---

## ⚽ Match Discovery

| Discover Matches | Game Details |
|------------------|--------------|
| ![Discover Matches](screenshots/Discover-matches.png) | ![Game Details](screenshots/game-details.png) |

### 🌍 All Sports

![All Sports](screenshots/all-sports.png)

---

## 🤖 AI Sports Assistant

![AI Assistant](screenshots/AI-assistent.png)

---

## 📈 Analytics Dashboard

![Analytics Dashboard](screenshots/analtyics.png)

---

## 👥 Team Management

| Teams | Create Team |
|-------|-------------|
| ![Teams](screenshots/Teams.png) | ![Create Team](screenshots/create-team.png) |

| Team Details | Team Leaderboard |
|--------------|------------------|
| ![Team Details](screenshots/team-details.png) | ![Team Leaderboard](screenshots/team-leaderboard.png) |

---

## 🏆 Leaderboards & Rankings

| Weekly Ranking | Monthly Ranking |
|----------------|-----------------|
| ![Weekly Ranking](screenshots/weekly-ranking.png) | ![Monthly Ranking](screenshots/monthly-ranking.png) |

| Lifetime Ranking | Player Ranking |
|------------------|----------------|
| ![Lifetime Ranking](screenshots/lifetime-ranking.png) | ![Player Ranking](screenshots/player-ranking.png) |

---

## 📅 Upcoming Sports Events

| Upcoming Matches | Nearby Sports |
|-----------------|---------------|
| ![Upcoming Matches](screenshots/upcoming-matches.png) | ![Nearby Sports](screenshots/nearby-sports.png) |

---

## 🗺 Sports Venue Maps

| Match Map | Venue Map |
|-----------|-----------|
| ![Match Map](screenshots/match-map.png) | ![Venue Map](screenshots/venue-map.png) |

---

## 💬 Team Chat

![Team Chat](screenshots/chat.png)

---

## ⚙️ Admin Features

| Score Adjustment | Adjust Points |
|-----------------|---------------|
| ![Score Adjustment](screenshots/score-adjustment.png) | ![Adjust Points](screenshots/adjust-points.png) |



# ⚙️ Installation Steps

### 1 Clone Repository

```bash
git clone https://github.com/AnushaValishetty2024/SportsBuddyAnalytics.git
```

### 2 Navigate to Project

```bash
cd SportsBuddyAnalytics
```

### 3 Create Virtual Environment

```bash
python -m venv venv
```

### 4 Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

### 5 Install Dependencies

```bash
pip install -r requirements.txt
```

### 6 Run Application

```bash
python app.py
```

---

# 🗄 Database Setup

1. Install XAMPP.

2. Start:

- Apache
- MySQL

3. Open phpMyAdmin.

4. Create a database.

```
sportsbuddy
```

5. Import the SQL file provided with the project.

6. Update database configuration in:

```
config.py
```

7. Restart the Flask application.

---

# 📈 Project Modules (7-Day Development)

## Day 1
- Project Setup
- Flask Configuration
- Database Connection
- Landing Page
- User Authentication

## Day 2
- Dashboard Development
- Player Statistics
- Navigation
- Responsive UI

## Day 3
- Match Discovery
- Search & Filters
- Event Details
- Join Match Module

## Day 4
- Team Management
- Team Chat
- Player Profiles
- Social Features

## Day 5
- Leaderboard
- Badge System
- Notifications
- Performance Tracking

## Day 6
- Analytics Dashboard
- Charts
- Reports
- Activity Monitoring

## Day 7
- UI Improvements
- Bug Fixes
- Performance Optimization
- Final Testing
- GitHub Deployment

---

# 🚀 Future Enhancements

- AI Match Recommendation
- Real-time Chat using WebSockets
- Live Match Score Tracking
- Tournament Management
- Email Notifications
- Mobile Application
- Google Authentication
- Payment Gateway Integration
- GPS-based Nearby Sports Events
- Performance Prediction using Machine Learning

---

# 📊 Key Highlights

- Full Stack Web Application
- Modular Flask Architecture
- Responsive Bootstrap UI
- SQL Database Integration
- Interactive Analytics Dashboard
- Authentication System
- Team Collaboration
- Leaderboard & Ranking System
- Achievement Tracking
- Notification Module

---

# 👩‍💻 Author

**Anusha Valishetty**

- GitHub: https://github.com/AnushaValishetty2024
- LinkedIn: *(Add Your LinkedIn Profile)*

---

# ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.
