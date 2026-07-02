#!/usr/bin/env python
"""Run Day 7 migration script."""
import pymysql

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sports_buddy'
}

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # Read and execute the migration SQL
    with open('sql/day7_migration.sql', 'r') as f:
        sql_content = f.read()
    
    # Execute each statement separately to handle IF NOT EXISTS properly
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        # Skip comments
        if line.startswith('--') or line.startswith('/*') or line.startswith('*') or line == '':
            continue
        current_statement.append(line)
        
        # Check if statement ends
        if line.endswith(';'):
            statement = ' '.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    # Execute all statements
    executed = 0
    errors = 0
    for statement in statements:
        try:
            cursor.execute(statement)
            executed += 1
        except Exception as e:
            errors += 1
            print(f"Warning executing statement: {e}")
            print(f"Statement: {statement[:100]}...")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Migration completed: {executed} statements executed, {errors} warnings")
    
except Exception as e:
    print(f"Migration failed: {e}")