<?php
require_once __DIR__ . '/includes/auth.php';
if (isLoggedIn()) { header('Location: ' . getRoleDashboard()); exit; }
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Learn - Plateforme Universitaire</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <section class="landing-hero">
        <div>
            <h1>E-Learn</h1>
            <p>Plateforme d'apprentissage en ligne pour les etudiants. Suivez vos cours, passez les evaluations et obtenez vos certificats.</p>
            <div class="hero-btns">
                <a href="pages/login.php" class="btn btn-hero btn-hero-white">Se connecter</a>
                <a href="pages/register.php" class="btn btn-hero btn-hero-outline">Creer un compte</a>
            </div>
        </div>
    </section>

    <section class="landing-features">
        <h2>Fonctionnalites</h2>
        <div class="features-grid">
            <div class="feature-card">
                <div class="icon">&#128218;</div>
                <h3>Cours en ligne</h3>
                <p>Acces aux cours en PDF et video, disponibles a tout moment.</p>
            </div>
            <div class="feature-card">
                <div class="icon">&#128221;</div>
                <h3>Evaluations</h3>
                <p>QCM interactifs apres chaque lecon pour valider vos acquis.</p>
            </div>
            <div class="feature-card">
                <div class="icon">&#127891;</div>
                <h3>Certificats</h3>
                <p>Obtenez un certificat de reussite a l'issue de chaque module.</p>
            </div>
            <div class="feature-card">
                <div class="icon">&#128200;</div>
                <h3>Suivi de progression</h3>
                <p>Suivez votre avancement en temps reel.</p>
            </div>
        </div>
    </section>

    <footer class="landing-footer">
        E-Learn Platform - Plateforme Universitaire
    </footer>
</body>
</html>
