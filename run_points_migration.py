#!/usr/bin/env python
"""Run points adjustment migration."""
import sys
sys.path.insert(0, '.')

from config import Config
import pymysql

# Connect to MySQL
conn = pymysql.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB
)

try:
    with conn.cursor() as cursor:
        # Read and execute migration
        with open('sql/points_adjustment_migration.sql', 'r') as f:
            sql = f.read()
            cursor.execute(sql)
    conn.commit()
    print("Points adjustment migration executed successfully!")
except Exception as e:
    print(f"Error running migration: {e}")
    sys.exit(1)
finally:
    conn.close()