<?php
require_once __DIR__ . '/config.php';

function login(string $email, string $password): ?array {
    global $pdo;
    $stmt = $pdo->prepare('SELECT * FROM users WHERE email = ?');
    $stmt->execute([$email]);
    $user = $stmt->fetch();
    if ($user && password_verify($password, $user['password'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_role'] = $user['role'];
        $_SESSION['user_name'] = $user['prenom'] . ' ' . $user['nom'];
        return $user;
    }
    return null;
}

function logout(): void {
    session_destroy();
    header('Location: ' . BASE_URL . '/pages/login.php');
    exit;
}

function isLoggedIn(): bool {
    return isset($_SESSION['user_id']);
}

function getUser(): ?array {
    if (!isLoggedIn()) return null;
    global $pdo;
    $stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?');
    $stmt->execute([$_SESSION['user_id']]);
    return $stmt->fetch();
}

function isTeacher(): bool {
    return isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'teacher';
}

function isStudent(): bool {
    return isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'student';
}

function isAdmin(): bool {
    return isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'admin';
}

function requireRole(string $role): void {
    if (!isLoggedIn()) {
        header('Location: ' . BASE_URL . '/pages/login.php');
        exit;
    }
    if ($_SESSION['user_role'] !== $role) {
        header('Location: ' . BASE_URL . '/index.php');
        exit;
    }
}

function getRoleDashboard(): string {
    if (isAdmin()) return BASE_URL . '/pages/admin/dashboard.php';
    if (isTeacher()) return BASE_URL . '/pages/teacher/dashboard.php';
    if (isStudent()) return BASE_URL . '/pages/student/dashboard.php';
    return BASE_URL . '/pages/login.php';
}
