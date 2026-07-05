<?php
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/functions.php';
if (isLoggedIn()) { header('Location: ' . getRoleDashboard()); exit; }

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    if (empty($email) || empty($password)) {
        $error = 'Veuillez remplir tous les champs.';
    } else {
        $result = login($email, $password);
        if ($result) { header('Location: ' . getRoleDashboard()); exit; }
        else { $error = 'Email ou mot de passe incorrect.'; }
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - E-Learn</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body class="auth-page">
    <a href="../index.php" class="back-link">&#8592; Accueil</a>
    <div class="auth-card">
        <div class="auth-header">
            <div class="logo">&#128218;</div>
            <h1>Connexion</h1>
            <p>Accedez a votre espace E-Learn</p>
        </div>
        <?php if ($error): ?>
            <div class="alert alert-danger"><?= sanitize($error) ?></div>
        <?php endif; ?>
        <form method="POST" action="">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" class="form-control" required placeholder="votre@email.com" value="<?= sanitize($_POST['email'] ?? '') ?>">
            </div>
            <div class="form-group">
                <label>Mot de passe</label>
                <input type="password" name="password" class="form-control" required placeholder="Votre mot de passe">
            </div>
            <button type="submit" class="btn btn-primary btn-block btn-lg">Se connecter</button>
        </form>
        <p class="auth-link">Pas encore de compte ? <a href="register.php">S'inscrire</a></p>
    </div>
</body>
</html>
