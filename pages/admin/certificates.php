<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('admin');

$certs = $pdo->query("SELECT mc.*, u.nom, u.prenom, m.titre AS module_titre FROM module_certificates mc JOIN users u ON u.id=mc.student_id JOIN modules m ON m.id=mc.module_id ORDER BY mc.date_obtained DESC")->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificats - Admin - E-Learn</title>
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
                <a href="students.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg> Etudiants</a>
                <a href="teachers.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> Enseignants</a>
                <a href="modules.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Modules</a>
                <a href="certificates.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header-row"><h1>Certificats</h1></div>
            <div class="panel">
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Etudiant</th><th>Module</th><th>Code</th><th>Date</th></tr></thead>
                        <tbody>
                            <?php foreach ($certs as $c): ?>
                            <tr>
                                <td><strong><?= sanitize($c['prenom'] . ' ' . $c['nom']) ?></strong></td>
                                <td><?= sanitize($c['module_titre']) ?></td>
                                <td><code style="background:var(--gray-100);padding:2px 8px;border-radius:4px;font-size:0.8rem"><?= sanitize($c['certificate_code']) ?></code></td>
                                <td style="font-size:0.8rem;color:var(--gray-400)"><?= formatDate($c['date_obtained']) ?></td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($certs)): ?>
                            <tr><td colspan="4" style="text-align:center;color:var(--gray-400);padding:2rem">Aucun certificat</td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
