<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('teacher');

$teacherId = $_SESSION['user_id'];
$teacher = getUser();

$nbLessons = $pdo->prepare("SELECT COUNT(*) FROM lessons WHERE created_by=?");
$nbLessons->execute([$teacherId]); $nbLessons = (int)$nbLessons->fetchColumn();

$nbStudents = $pdo->prepare("SELECT COUNT(DISTINCT sp.student_id) FROM student_progress sp JOIN lessons l ON sp.lesson_id=l.id WHERE l.created_by=?");
$nbStudents->execute([$teacherId]); $nbStudents = (int)$nbStudents->fetchColumn();

$nbEvals = $pdo->prepare("SELECT COUNT(*) FROM evaluations e JOIN lessons l ON e.lesson_id=l.id WHERE l.created_by=?");
$nbEvals->execute([$teacherId]); $nbEvals = (int)$nbEvals->fetchColumn();

$lessons = $pdo->prepare("SELECT l.*, m.titre AS module_titre, (SELECT COUNT(*) FROM student_progress sp WHERE sp.lesson_id=l.id AND sp.status='completed') AS completed FROM lessons l JOIN modules m ON l.module_id=m.id WHERE l.created_by=? ORDER BY l.date_creation DESC");
$lessons->execute([$teacherId]); $lessons = $lessons->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enseignant - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
</head>
<body>
    <nav class="navbar">
        <a class="navbar-brand" href="../../index.php">&#128218; <span>E-Learn</span></a>
        <div class="navbar-right"><span style="color:var(--gray-500);font-size:0.875rem"><?= sanitize($teacher['prenom'] . ' ' . $teacher['nom']) ?></span><a href="../logout.php" class="btn btn-outline btn-sm">Deconnexion</a></div>
    </nav>
    <div class="layout">
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-section-title">Espace enseignant</div>
                <a href="dashboard.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="lessons.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Mes lecons</a>
                <a href="evaluations.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg> Evaluations</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header"><h1>Tableau de bord</h1><p>Bienvenue, <?= sanitize($teacher['prenom']) ?></p></div>
            <div class="stats-row">
                <div class="stat-card"><div class="stat-icon blue">&#128218;</div><div><div class="stat-number"><?= $nbLessons ?></div><div class="stat-label">Lecons creees</div></div></div>
                <div class="stat-card"><div class="stat-icon green">&#128101;</div><div><div class="stat-number"><?= $nbStudents ?></div><div class="stat-label">Etudiants</div></div></div>
                <div class="stat-card"><div class="stat-icon purple">&#9997;</div><div><div class="stat-number"><?= $nbEvals ?></div><div class="stat-label">Evaluations</div></div></div>
            </div>
            <div class="panel">
                <div class="panel-header"><h2>Mes lecons recentes</h2></div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Titre</th><th>Module</th><th>Type</th><th>Terminees</th><th>Date</th></tr></thead>
                        <tbody>
                            <?php foreach (array_slice($lessons, 0, 8) as $l): ?>
                            <tr>
                                <td><strong><?= sanitize($l['titre']) ?></strong></td>
                                <td style="color:var(--gray-500)"><?= sanitize($l['module_titre']) ?></td>
                                <td><span class="badge badge-<?= $l['type']==='pdf' ? 'primary' : 'success' ?>"><?= strtoupper($l['type']) ?></span></td>
                                <td><?= $l['completed'] ?> etudiant(s)</td>
                                <td style="font-size:0.8rem;color:var(--gray-400)"><?= formatDate($l['date_creation']) ?></td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($lessons)): ?>
                            <tr><td colspan="5" style="text-align:center;color:var(--gray-400);padding:2rem">Aucune lecon. <a href="lessons.php">Creer une lecon</a></td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
