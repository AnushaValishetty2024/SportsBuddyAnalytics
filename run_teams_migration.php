<?php
// Simple script to run the teams migration
// Access this file in your browser: http://localhost/sports_buddy/run_teams_migration.php

$host = 'localhost';
$dbname = 'sports_buddy';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    echo "<h2>Running Teams Migration...</h2>";
    
    // Read and execute the SQL file
    $sql = file_get_contents('sql/teams_migration.sql');
    
    // Split by semicolons to execute multiple statements
    $statements = array_filter(array_map('trim', explode(';', $sql)));
    
    foreach ($statements as $statement) {
        if (!empty($statement)) {
            try {
                $pdo->exec($statement);
                echo "<p style='color:green;'>✓ Executed: " . substr($statement, 0, 60) . "...</p>";
            } catch (PDOException $e) {
                echo "<p style='color:orange;'>⚠ Statement skipped (may already exist): " . $e->getMessage() . "</p>";
            }
        }
    }
    
    echo "<h3 style='color:green;'>✓ Teams migration completed successfully!</h3>";
    echo "<p><a href='teams.php'>Go to Teams Page</a></p>";
    
} catch (PDOException $e) {
    echo "<h3 style='color:red;'>✗ Database connection failed: " . $e->getMessage() . "</h3>";
}
?>