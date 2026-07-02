"""
Run the match map migration to add latitude/longitude columns and update data.
"""
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sports_buddy'
}

SQL_STATEMENTS = [
    # Add latitude and longitude columns
    "ALTER TABLE matches ADD COLUMN IF NOT EXISTS latitude DOUBLE DEFAULT NULL AFTER venue_lng",
    "ALTER TABLE matches ADD COLUMN IF NOT EXISTS longitude DOUBLE DEFAULT NULL AFTER latitude",
    
    # Copy venue_lat/lng to latitude/longitude for existing records
    "UPDATE matches SET latitude = venue_lat, longitude = venue_lng WHERE venue_lat IS NOT NULL AND venue_lng IS NOT NULL",
    
    # Update matches with realistic coordinates
    "UPDATE matches SET venue_name = 'Vijayawada Stadium', latitude = 16.5062, longitude = 80.6480 WHERE id = 1",
    "UPDATE matches SET venue_name = 'Indoor Sports Complex', latitude = 16.5200, longitude = 80.6300 WHERE id = 2",
    "UPDATE matches SET venue_name = 'City Ground', latitude = 16.4900, longitude = 80.6700 WHERE id = 3",
    "UPDATE matches SET venue_name = 'Beach Arena', latitude = 16.4800, longitude = 80.7000 WHERE id = 4",
    "UPDATE matches SET venue_name = 'YMCA Indoor Court', latitude = 16.5400, longitude = 80.6200 WHERE id = 5",
    "UPDATE matches SET venue_name = 'Sports Park', latitude = 16.5100, longitude = 80.6600 WHERE id = 6",
    
    # Add status column if not exists
    "ALTER TABLE matches ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open'",
    
    # Update all matches to have 'open' status
    "UPDATE matches SET status = 'open' WHERE status IS NULL",
]

def run_migration():
    try:
        # First connect without database to ensure it exists
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS sports_buddy")
        cursor.close()
        conn.close()
        
        # Now connect to the database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for sql in SQL_STATEMENTS:
            try:
                cursor.execute(sql)
                print(f"OK: {sql[:60]}...")
            except Exception as e:
                print(f"SKIP: {sql[:60]}... ({e})")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\nMigration completed successfully!")
        
        # Verify the data
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, sport_name, venue_name, latitude, longitude, status FROM matches ORDER BY id")
        rows = cursor.fetchall()
        print(f"\nMatches in database ({len(rows)}):")
        for row in rows:
            print(f"  ID={row['id']}, Sport={row['sport_name']}, Venue={row['venue_name']}, "
                  f"Lat={row['latitude']}, Lng={row['longitude']}, Status={row['status']}")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == '__main__':
    run_migration()