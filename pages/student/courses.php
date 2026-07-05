<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('student');

$user = getUser();
$student_id = $_SESSION['user_id'];
$module_id = isset($_GET['module_id']) ? (int)$_GET['module_id'] : 0;

if ($module_id > 0) {
    $stmt = $pdo->prepare("SELECT * FROM modules WHERE id=?"); $stmt->execute([$module_id]); $module = $stmt->fetch();
    if (!$module) redirect('courses.php');
    $stmt = $pdo->prepare("SELECT l.*, sp.status, (SELECT COUNT(*) FROM evaluations WHERE lesson_id=l.id) AS has_eval FROM lessons l LEFT JOIN student_progress sp ON l.id=sp.lesson_id AND sp.student_id=? WHERE l.module_id=? ORDER BY l.ordre ASC");
    $stmt->execute([$student_id, $module_id]); $lessons = $stmt->fetchAll();
} else {
    $stmt = $pdo->prepare("SELECT m.*, (SELECT COUNT(*) FROM lessons WHERE module_id=m.id) AS total_lessons, (SELECT COUNT(*) FROM student_progress sp JOIN lessons l ON sp.lesson_id=l.id WHERE l.module_id=m.id AND sp.student_id=? AND sp.status='completed') AS done_lessons FROM modules m ORDER BY m.date_creation DESC");
    $stmt->execute([$student_id]); $modules = $stmt->fetchAll();
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mes cours - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
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
                <a href="dashboard.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="courses.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Mes cours</a>
                <a href="certificates.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <?php if ($module_id > 0 && isset($module)): ?>
                <a href="courses.php" style="display:inline-flex;align-items:center;gap:0.3rem;color:var(--gray-500);font-size:0.9rem;margin-bottom:1rem">&#8592; Retour aux modules</a>
                <div class="page-header"><h1><?= sanitize($module['titre']) ?></h1><p><?= sanitize($module['description'] ?: '') ?></p></div>
                <?php foreach ($lessons as $i => $l): ?>
                <div class="lesson-item">
                    <div class="info">
                        <h4><?= ($i+1) . '. ' . sanitize($l['titre']) ?></h4>
                        <div class="meta"><?= strtoupper($l['type']) ?> <?= $l['has_eval'] ? ' - Evaluation disponible' : '' ?></div>
                    </div>
                    <div class="right">
                        <span class="badge badge-<?= $l['status']==='completed' ? 'success' : ($l['status']==='in_progress' ? 'warning' : 'gray') ?>">
                            <?= $l['status']==='completed' ? 'Termine' : ($l['status']==='in_progress' ? 'En cours' : 'Non commence') ?>
                        </span>
                        <a href="lesson.php?id=<?= $l['id'] ?>" class="btn btn-primary btn-sm">
                            <?= $l['status']==='completed' ? 'Revoir' : ($l['status']==='in_progress' ? 'Continuer' : 'Commencer') ?>
                        </a>
                    </div>
                </div>
                <?php endforeach; ?>
                <?php if (empty($lessons)): ?>
                <div class="empty-state"><p>Aucune lecon dans ce module.</p></div>
                <?php endif; ?>
            <?php else: ?>
                <div class="page-header"><h1>Mes cours</h1><p>Selectionnez un module</p></div>
                <?php foreach ($modules as $m): ?>
                <a href="courses.php?module_id=<?= $m['id'] ?>" style="text-decoration:none">
                    <div class="module-card">
                        <h3><?= sanitize($m['titre']) ?></h3>
                        <p class="desc"><?= sanitize($m['description'] ?: 'Aucune description') ?></p>
                        <div class="module-meta"><span><?= $m['total_lessons'] ?> lecon(s)</span><span><?= $m['done_lessons'] ?> terminee(s)</span></div>
                        <div class="progress"><div class="progress-bar <?= $m['total_lessons']>0 && $m['done_lessons']==$m['total_lessons'] ? 'green' : '' ?>" style="width:<?= $m['total_lessons']>0 ? round(($m['done_lessons']/$m['total_lessons'])*100) : 0 ?>%"></div></div>
                    </div>
                </a>
                <?php endforeach; ?>
                <?php if (empty($modules)): ?>
                <div class="empty-state"><div class="icon">&#128218;</div><p>Aucun module disponible.</p></div>
                <?php endif; ?>
            <?php endif; ?>
        </main>
    </div>
</body>
</html>
