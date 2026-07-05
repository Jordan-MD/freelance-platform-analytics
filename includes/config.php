<?php
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);

// Upload limits
ini_set('upload_max_filesize', '200M');
ini_set('post_max_size', '250M');
ini_set('max_execution_time', '300');
ini_set('max_input_time', '300');

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

define('BASE_URL', 'http://localhost:8000');

define('DB_HOST', 'localhost');
define('DB_NAME', 'elearn_db');
define('DB_USER', 'lms_user');
define('DB_PASS', 'lms_password_2026');
define('DB_SOCKET', '/run/mysqld/mysqld.sock');

try {
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ];
    try {
        $pdo = new PDO('mysql:unix_socket=' . DB_SOCKET . ';dbname=' . DB_NAME . ';charset=utf8mb4', DB_USER, DB_PASS, $options);
    } catch (PDOException $e) {
        $pdo = new PDO('mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4', DB_USER, DB_PASS, $options);
    }
} catch (PDOException $e) {
    error_log('DB connection failed: ' . $e->getMessage());
    die('Erreur de connexion a la base de donnees.');
}
