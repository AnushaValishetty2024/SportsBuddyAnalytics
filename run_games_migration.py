"""
Script to run the games migration SQL file.
Reads the SQL file and executes it using pymysql.
"""
import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'sports_buddy'

# Read the SQL migration file
with open('sql/games_migration.sql', 'r') as f:
    sql_content = f.read()

# Split by semicolons to execute individual statements
statements = sql_content.split(';')

connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4'
)

cursor = connection.cursor()
success_count = 0
error_count = 0

for statement in statements:
    stmt = statement.strip()
    if not stmt:
        continue
    # Skip USE statements as we already selected the database
    if stmt.upper().startswith('USE'):
        continue
    try:
        cursor.execute(stmt)
        connection.commit()
        success_count += 1
        print(f"  OK: {stmt[:80]}...")
    except Exception as e:
        error_str = str(e)
        # Ignore "already exists" errors for ALTER TABLE ADD COLUMN
        if "Duplicate column" in error_str:
            success_count += 1
            print(f"  SKIP (exists): {stmt[:60]}...")
        elif "already exists" in error_str.lower():
            success_count += 1
            print(f"  SKIP (exists): {stmt[:60]}...")
        else:
            error_count += 1
            print(f"  ERROR: {error_str[:100]}")
            print(f"  Statement: {stmt[:80]}...")

cursor.close()
connection.close()

print(f"\nMigration complete. {success_count} statements executed, {error_count} errors.")