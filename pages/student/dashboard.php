<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('student');

$user = getUser();
$student_id = $_SESSION['user_id'];

$nbModules = $pdo->prepare("SELECT COUNT(DISTINCT m.id) FROM modules m JOIN lessons l ON l.module_id=m.id");
$nbModules->execute(); $nbModules = (int)$nbModules->fetchColumn();

$nbCompleted = $pdo->prepare("SELECT COUNT(*) FROM student_progress WHERE student_id=? AND status='completed'");
$nbCompleted->execute([$student_id]); $nbCompleted = (int)$nbCompleted->fetchColumn();

$nbCerts = $pdo->prepare("SELECT COUNT(*) FROM module_certificates WHERE student_id=?");
$nbCerts->execute([$student_id]); $nbCerts = (int)$nbCerts->fetchColumn();

$progression = 0;
if ($nbModules > 0) {
    $stmt = $pdo->prepare("SELECT COUNT(DISTINCT l.module_id) FROM student_progress sp JOIN lessons l ON sp.lesson_id=l.id WHERE sp.student_id=? AND sp.status='completed'");
    $stmt->execute([$student_id]);
    $progression = round(($stmt->fetchColumn() / $nbModules) * 100);
}

$modules = $pdo->prepare("SELECT m.*, (SELECT COUNT(*) FROM lessons WHERE module_id=m.id) AS total_lessons, (SELECT COUNT(*) FROM student_progress sp JOIN lessons l ON sp.lesson_id=l.id WHERE l.module_id=m.id AND sp.student_id=? AND sp.status='completed') AS done_lessons FROM modules m ORDER BY m.date_creation DESC");
$modules->execute([$student_id]); $modules = $modules->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Etudiant - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
</head>
<body>
    <nav class="navbar">
        <a class="navbar-brand" href="../../index.php">&#128218; <span>E-Learn</span></a>
        <div class="navbar-right"><span style="color:var(--gray-500);font-size:0.875rem"><?= sanitize($user['prenom'] . ' ' . $user['nom']) ?></span><a href="../logout.php" class="btn btn-outline btn-sm">Deconnexion</a></div>
    </nav>
    <div class="layout">
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-section-title">Espace etudiant</div>
                <a href="dashboard.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="courses.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Mes cours</a>
                <a href="certificates.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header"><h1>Bonjour, <?= sanitize($user['prenom']) ?></h1><p>Voici votre espace d'apprentissage</p></div>
            <div class="stats-row">
                <div class="stat-card"><div class="stat-icon blue">&#128218;</div><div><div class="stat-number"><?= $nbModules ?></div><div class="stat-label">Modules</div></div></div>
                <div class="stat-card"><div class="stat-icon green">&#9989;</div><div><div class="stat-number"><?= $nbCompleted ?></div><div class="stat-label">Lecons terminees</div></div></div>
                <div class="stat-card"><div class="stat-icon orange">&#127891;</div><div><div class="stat-number"><?= $nbCerts ?></div><div class="stat-label">Certificats</div></div></div>
                <div class="stat-card"><div class="stat-icon purple">&#128200;</div><div><div class="stat-number"><?= $progression ?>%</div><div class="stat-label">Progression</div></div></div>
            </div>
            <h2 class="section-title">Modules disponibles</h2>
            <?php foreach ($modules as $m): ?>
            <a href="courses.php?module_id=<?= $m['id'] ?>" style="text-decoration:none">
                <div class="module-card">
                    <h3><?= sanitize($m['titre']) ?></h3>
                    <p class="desc"><?= sanitize($m['description'] ?: 'Aucune description') ?></p>
                    <div class="module-meta">
                        <span><?= $m['total_lessons'] ?> lecon(s)</span>
                        <span><?= $m['done_lessons'] ?> terminee(s)</span>
                    </div>
                    <div class="progress"><div class="progress-bar <?= $m['total_lessons']>0 && $m['done_lessons']==$m['total_lessons'] ? 'green' : '' ?>" style="width:<?= $m['total_lessons']>0 ? round(($m['done_lessons']/$m['total_lessons'])*100) : 0 ?>%"></div></div>
                </div>
            </a>
            <?php endforeach; ?>
            <?php if (empty($modules)): ?>
            <div class="empty-state"><div class="icon">&#128218;</div><p>Aucun module disponible pour le moment.</p></div>
            <?php endif; ?>
        </main>
    </div>
</body>
</html>
