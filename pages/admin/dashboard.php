<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('admin');

$totalStudents = $pdo->query("SELECT COUNT(*) FROM users WHERE role='student'")->fetchColumn();
$totalTeachers = $pdo->query("SELECT COUNT(*) FROM users WHERE role='teacher'")->fetchColumn();
$totalModules = $pdo->query("SELECT COUNT(*) FROM modules")->fetchColumn();
$totalCerts = $pdo->query("SELECT COUNT(*) FROM module_certificates")->fetchColumn();
$recentUsers = $pdo->query("SELECT nom, prenom, email, role, date_inscription FROM users ORDER BY date_inscription DESC LIMIT 8")->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - E-Learn</title>
    <link rel="stylesheet" href="../../css/style.css">
</head>
<body>
    <nav class="navbar">
        <a class="navbar-brand" href="../../index.php">&#128218; <span>E-Learn</span></a>
        <div class="navbar-right">
            <span style="color:var(--gray-500);font-size:0.875rem"><?= sanitize($_SESSION['user_name'] ?? '') ?></span>
            <a href="../logout.php" class="btn btn-outline btn-sm">Deconnexion</a>
        </div>
    </nav>
    <div class="layout">
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-section-title">Administration</div>
                <a href="dashboard.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="students.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg> Etudiants</a>
                <a href="teachers.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> Enseignants</a>
                <a href="modules.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Modules</a>
                <a href="certificates.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header">
                <h1>Tableau de bord</h1>
                <p>Bienvenue, <?= sanitize($_SESSION['user_name'] ?? 'Admin') ?></p>
            </div>
            <div class="stats-row">
                <div class="stat-card"><div class="stat-icon blue">&#128100;</div><div><div class="stat-number"><?= $totalStudents ?></div><div class="stat-label">Etudiants</div></div></div>
                <div class="stat-card"><div class="stat-icon purple">&#9733;</div><div><div class="stat-number"><?= $totalTeachers ?></div><div class="stat-label">Enseignants</div></div></div>
                <div class="stat-card"><div class="stat-icon green">&#128218;</div><div><div class="stat-number"><?= $totalModules ?></div><div class="stat-label">Modules</div></div></div>
                <div class="stat-card"><div class="stat-icon orange">&#127891;</div><div><div class="stat-number"><?= $totalCerts ?></div><div class="stat-label">Certificats</div></div></div>
            </div>
            <div class="panel">
                <div class="panel-header"><h2>Inscriptions recentes</h2></div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Nom</th><th>Email</th><th>Role</th><th>Date</th></tr></thead>
                        <tbody>
                            <?php foreach ($recentUsers as $u): ?>
                            <tr>
                                <td><strong><?= sanitize($u['prenom'] . ' ' . $u['nom']) ?></strong></td>
                                <td><?= sanitize($u['email']) ?></td>
                                <td><span class="badge badge-<?= $u['role'] === 'teacher' ? 'primary' : 'success' ?>"><?= $u['role'] === 'teacher' ? 'Enseignant' : ($u['role'] === 'admin' ? 'Admin' : 'Etudiant') ?></span></td>
                                <td style="color:var(--gray-400);font-size:0.8rem"><?= date('d/m/Y', strtotime($u['date_inscription'])) ?></td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($recentUsers)): ?>
                            <tr><td colspan="4" style="text-align:center;color:var(--gray-400);padding:2rem">Aucune inscription</td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
