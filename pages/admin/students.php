<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('admin');

$students = $pdo->query("SELECT u.*, COUNT(DISTINCT l.module_id) AS nb_modules FROM users u LEFT JOIN student_progress sp ON sp.student_id=u.id LEFT JOIN lessons l ON sp.lesson_id=l.id WHERE u.role='student' GROUP BY u.id ORDER BY u.date_inscription DESC")->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Etudiants - Admin - E-Learn</title>
    <link rel="stylesheet" href="../../css/style.css">
</head>
<body>
    <nav class="navbar">
        <a class="navbar-brand" href="../../index.php">&#128218; <span>E-Learn</span></a>
        <div class="navbar-right"><span style="color:var(--gray-500);font-size:0.875rem"><?= sanitize($_SESSION['user_name'] ?? '') ?></span><a href="../logout.php" class="btn btn-outline btn-sm">Deconnexion</a></div>
    </nav>
    <div class="layout">
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-section-title">Administration</div>
                <a href="dashboard.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="students.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg> Etudiants</a>
                <a href="teachers.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> Enseignants</a>
                <a href="modules.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Modules</a>
                <a href="certificates.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header-row"><h1>Etudiants</h1></div>
            <div class="panel">
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Nom</th><th>Email</th><th>Modules suivis</th><th>Inscription</th><th style="text-align:right">Actions</th></tr></thead>
                        <tbody>
                            <?php foreach ($students as $s): ?>
                            <tr>
                                <td><strong><?= sanitize($s['prenom'] . ' ' . $s['nom']) ?></strong></td>
                                <td><?= sanitize($s['email']) ?></td>
                                <td><span class="badge badge-primary"><?= $s['nb_modules'] ?></span></td>
                                <td style="font-size:0.8rem;color:var(--gray-400)"><?= date('d/m/Y', strtotime($s['date_inscription'])) ?></td>
                                <td class="actions"><button class="btn btn-danger btn-sm" onclick="deleteUser(<?= $s['id'] ?>)">Supprimer</button></td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($students)): ?>
                            <tr><td colspan="5" style="text-align:center;color:var(--gray-400);padding:2rem">Aucun etudiant</td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
    <script src="../../js/app.js"></script>
    <script>
    function deleteUser(id) {
        if (!confirm('Supprimer cet utilisateur ?')) return;
        postAjax('../../ajax/admin_handler.php', {action:'delete_user', id:id}, function(e, d) { if (d && d.success) location.reload(); else alert(d ? d.message : 'Erreur'); });
    }
    </script>
</body>
</html>
