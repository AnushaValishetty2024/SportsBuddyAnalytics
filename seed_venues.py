"""Seed script to populate the sports_venues table with realistic data.
Run once to populate the database with 15 venues around Andhra Pradesh, India.
"""
import pymysql
import json

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='sports_buddy',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()

# Drop and recreate sports_venues table
cursor.execute("DROP TABLE IF EXISTS sports_venues")
cursor.execute("""
    CREATE TABLE sports_venues (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        sport_types VARCHAR(500) NOT NULL,
        address TEXT,
        latitude DECIMAL(10, 7) NOT NULL,
        longitude DECIMAL(10, 7) NOT NULL,
        rating DECIMAL(2, 1) DEFAULT 0.0,
        available_slots INT DEFAULT 0,
        distance_km DECIMAL(6, 2) DEFAULT 0.00,
        image_url VARCHAR(500) DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

venues_data = [
    # 15 venues around Andhra Pradesh, covering all required sports
    {
        "name": "Indira Gandhi Municipal Stadium",
        "sport_types": "Cricket,Football",
        "address": "MG Road, Vijayawada, Andhra Pradesh 520001",
        "latitude": 16.5138,
        "longitude": 80.6395,
        "rating": 4.3,
        "available_slots": 12,
        "distance_km": 1.1,
        "image_url": "placeholder_venue_1.png"
    },
    {
        "name": "Swarna Cricket Grounds",
        "sport_types": "Cricket",
        "address": "Benz Circle, Vijayawada, Andhra Pradesh 520010",
        "latitude": 16.5204,
        "longitude": 80.6420,
        "rating": 4.1,
        "available_slots": 8,
        "distance_km": 1.8,
        "image_url": "placeholder_venue_2.png"
    },
    {
        "name": "APSRTC Indoor Stadium",
        "sport_types": "Badminton,Basketball",
        "address": "Pandit Nehru Bus Station Road, Vijayawada, Andhra Pradesh 520003",
        "latitude": 16.5102,
        "longitude": 80.6345,
        "rating": 4.0,
        "available_slots": 6,
        "distance_km": 1.5,
        "image_url": "placeholder_venue_3.png"
    },
    {
        "name": "Acharya Nagarjuna University Sports Grounds",
        "sport_types": "Football,Athletics Track",
        "address": "Nagarjuna Nagar, Guntur, Andhra Pradesh 522510",
        "latitude": 16.3425,
        "longitude": 80.4582,
        "rating": 4.4,
        "available_slots": 15,
        "distance_km": 24.5,
        "image_url": "placeholder_venue_4.png"
    },
    {
        "name": "Andhra Tennis Academy",
        "sport_types": "Tennis",
        "address": "Labbipet, Vijayawada, Andhra Pradesh 520010",
        "latitude": 16.5160,
        "longitude": 80.6495,
        "rating": 4.5,
        "available_slots": 4,
        "distance_km": 1.2,
        "image_url": "placeholder_venue_5.png"
    },
    {
        "name": "East Coast Beach Volleyball Arena",
        "sport_types": "Volleyball",
        "address": "RK Beach Road, Visakhapatnam, Andhra Pradesh 530017",
        "latitude": 17.7119,
        "longitude": 83.2995,
        "rating": 4.2,
        "available_slots": 10,
        "distance_km": 350.0,
        "image_url": "placeholder_venue_6.png"
    },
    {
        "name": "Vijayawada Municipal Aquatic Centre",
        "sport_types": "Swimming",
        "address": "Durga Temple Road, Vijayawada, Andhra Pradesh 520002",
        "latitude": 16.5035,
        "longitude": 80.6520,
        "rating": 3.8,
        "available_slots": 20,
        "distance_km": 0.6,
        "image_url": "placeholder_venue_7.png"
    },
    {
        "name": "Sports Authority of India Complex (SAI)",
        "sport_types": "Basketball,Volleyball,Badminton",
        "address": "Auto Nagar, Vijayawada, Andhra Pradesh 520007",
        "latitude": 16.4955,
        "longitude": 80.6385,
        "rating": 4.3,
        "available_slots": 18,
        "distance_km": 1.6,
        "image_url": "placeholder_venue_8.png"
    },
    {
        "name": "Vijayawada Badminton Centre",
        "sport_types": "Badminton",
        "address": "Governorpet, Vijayawada, Andhra Pradesh 520002",
        "latitude": 16.5090,
        "longitude": 80.6460,
        "rating": 4.2,
        "available_slots": 7,
        "distance_km": 0.5,
        "image_url": "placeholder_venue_9.png"
    },
    {
        "name": "GM Cricket Grounds",
        "sport_types": "Cricket",
        "address": "Brothers Colony, Patamata, Vijayawada, Andhra Pradesh 520008",
        "latitude": 16.4920,
        "longitude": 80.6680,
        "rating": 3.9,
        "available_slots": 14,
        "distance_km": 2.5,
        "image_url": "placeholder_venue_10.png"
    },
    {
        "name": "SNR Law College Football Ground",
        "sport_types": "Football",
        "address": "Mogalrajapuram, Vijayawada, Andhra Pradesh 520010",
        "latitude": 16.5185,
        "longitude": 80.6565,
        "rating": 3.7,
        "available_slots": 11,
        "distance_km": 1.6,
        "image_url": "placeholder_venue_11.png"
    },
    {
        "name": "NTR Stadium",
        "sport_types": "Tennis,Athletics Track",
        "address": "Vidyadharapuram, Vijayawada, Andhra Pradesh 520012",
        "latitude": 16.4850,
        "longitude": 80.6255,
        "rating": 4.1,
        "available_slots": 9,
        "distance_km": 3.1,
        "image_url": "placeholder_venue_12.png"
    },
    {
        "name": "Railway Recreation Club",
        "sport_types": "Cricket,Swimming",
        "address": "Railway Colony, Vijayawada, Andhra Pradesh 520001",
        "latitude": 16.5110,
        "longitude": 80.6300,
        "rating": 3.6,
        "available_slots": 5,
        "distance_km": 1.9,
        "image_url": "placeholder_venue_13.png"
    },
    {
        "name": "Andhra Loyola College Athletics Ground",
        "sport_types": "Athletics Track,Football",
        "address": "Loyola College Road, Vijayawada, Andhra Pradesh 520008",
        "latitude": 16.4975,
        "longitude": 80.6595,
        "rating": 3.9,
        "available_slots": 22,
        "distance_km": 1.3,
        "image_url": "placeholder_venue_14.png"
    },
    {
        "name": "VGTM Urban Sports Park",
        "sport_types": "Cricket,Football,Basketball,Badminton,Tennis,Volleyball,Swimming,Athletics Track",
        "address": "VGTM Layout, Ramavarappadu, Vijayawada, Andhra Pradesh 521108",
        "latitude": 16.5275,
        "longitude": 80.6710,
        "rating": 4.6,
        "available_slots": 30,
        "distance_km": 3.4,
        "image_url": "placeholder_venue_15.png"
    }
]

for v in venues_data:
    cursor.execute("""
        INSERT INTO sports_venues (name, sport_types, address, latitude, longitude, rating, available_slots, distance_km, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        v["name"], v["sport_types"], v["address"],
        v["latitude"], v["longitude"], v["rating"],
        v["available_slots"], v["distance_km"], v["image_url"]
    ))

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) as cnt FROM sports_venues")
count = cursor.fetchone()['cnt']
print(f"✅ Seeded {count} sports venues successfully!")

# Show sport coverage
cursor.execute("SELECT sport_types FROM sports_venues")
all_types = []
for row in cursor.fetchall():
    for sport in row['sport_types'].split(','):
        all_types.append(sport.strip())

from collections import Counter
coverage = Counter(all_types)
print("\n📊 Sport Coverage:")
for sport, cnt in sorted(coverage.items()):
    print(f"   {sport}: {cnt} venues")

cursor.close()
conn.close()