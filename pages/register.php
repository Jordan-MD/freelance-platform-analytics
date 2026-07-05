<?php
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/functions.php';
if (isLoggedIn()) { header('Location: ' . getRoleDashboard()); exit; }

$errors = [];
$success = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    global $pdo;
    $nom = trim($_POST['nom'] ?? '');
    $prenom = trim($_POST['prenom'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $confirm = $_POST['confirm_password'] ?? '';
    $role = $_POST['role'] ?? '';

    if (empty($nom)) $errors[] = 'Le nom est requis.';
    if (empty($prenom)) $errors[] = 'Le prenom est requis.';
    if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'Email invalide.';
    if (strlen($password) < 6) $errors[] = 'Le mot de passe doit faire au moins 6 caracteres.';
    if ($password !== $confirm) $errors[] = 'Les mots de passe ne correspondent pas.';
    if (!in_array($role, ['student', 'teacher'])) $errors[] = 'Role invalide.';

    if (empty($errors)) {
        $hash = password_hash($password, PASSWORD_DEFAULT);
        $stmt = $pdo->prepare("INSERT INTO users (nom, prenom, email, password, role) VALUES (?, ?, ?, ?, ?)");
        try {
            $stmt->execute([$nom, $prenom, $email, $hash, $role]);
            $success = 'Compte cree. Vous pouvez vous connecter.';
        } catch (PDOException $e) {
            $errors[] = ($e->getCode() == 23000) ? 'Cet email est deja utilise.' : 'Erreur lors de l\'inscription.';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inscription - E-Learn</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body class="auth-page">
    <a href="../index.php" class="back-link">&#8592; Accueil</a>
    <div class="auth-card wide">
        <div class="auth-header">
            <div class="logo">&#127891;</div>
            <h1>Inscription</h1>
            <p>Creer votre compte E-Learn</p>
        </div>
        <?php if ($errors): ?>
            <div class="alert alert-danger"><?php foreach ($errors as $e) echo sanitize($e) . '<br>'; ?></div>
        <?php endif; ?>
        <?php if ($success): ?>
            <div class="alert alert-success"><?= sanitize($success) ?></div>
        <?php endif; ?>
        <form method="POST" action="">
            <div class="form-row">
                <div class="form-group">
                    <label>Nom</label>
                    <input type="text" name="nom" class="form-control" required placeholder="Dupont" value="<?= sanitize($_POST['nom'] ?? '') ?>">
                </div>
                <div class="form-group">
                    <label>Prenom</label>
                    <input type="text" name="prenom" class="form-control" required placeholder="Jean" value="<?= sanitize($_POST['prenom'] ?? '') ?>">
                </div>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" class="form-control" required placeholder="votre@email.com" value="<?= sanitize($_POST['email'] ?? '') ?>">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" name="password" class="form-control" required placeholder="Min. 6 caracteres">
                </div>
                <div class="form-group">
                    <label>Confirmer</label>
                    <input type="password" name="confirm_password" class="form-control" required placeholder="Repetez le mot de passe">
                </div>
            </div>
            <div class="form-group">
                <label>Role</label>
                <select name="role" class="form-control" required>
                    <option value="">Choisir un role</option>
                    <option value="student" <?= ($_POST['role'] ?? '') === 'student' ? 'selected' : '' ?>>Etudiant</option>
                    <option value="teacher" <?= ($_POST['role'] ?? '') === 'teacher' ? 'selected' : '' ?>>Enseignant</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-block btn-lg">S'inscrire</button>
        </form>
        <p class="auth-link">Deja inscrit ? <a href="login.php">Se connecter</a></p>
    </div>
</body>
</html>
