<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('admin');

$modules = $pdo->query("SELECT m.*, COUNT(l.id) AS nb_lessons FROM modules m LEFT JOIN lessons l ON l.module_id=m.id GROUP BY m.id ORDER BY m.date_creation DESC")->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modules - Admin - E-Learn</title>
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
                <a href="dashboard.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="students.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg> Etudiants</a>
                <a href="teachers.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> Enseignants</a>
                <a href="modules.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Modules</a>
                <a href="certificates.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header-row">
                <h1>Modules</h1>
                <button class="btn btn-primary" onclick="openModal('addModuleModal')">+ Nouveau module</button>
            </div>
            <div id="modulesAlert"></div>
            <div class="panel">
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Titre</th><th>Description</th><th>Lecons</th><th>Date</th><th style="text-align:right">Actions</th></tr></thead>
                        <tbody>
                            <?php foreach ($modules as $m): ?>
                            <tr id="mod-<?= $m['id'] ?>">
                                <td><strong><?= sanitize($m['titre']) ?></strong></td>
                                <td style="max-width:300px;color:var(--gray-500)"><?= sanitize(mb_strimwidth($m['description'] ?? '', 0, 60, '...')) ?></td>
                                <td><span class="badge badge-success"><?= $m['nb_lessons'] ?></span></td>
                                <td style="font-size:0.8rem;color:var(--gray-400)"><?= date('d/m/Y', strtotime($m['date_creation'])) ?></td>
                                <td class="actions">
                                    <button class="btn btn-outline btn-sm" onclick='editModule(<?= json_encode($m) ?>)'>Modifier</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteModule(<?= $m['id'] ?>)">Supprimer</button>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($modules)): ?>
                            <tr><td colspan="5" style="text-align:center;color:var(--gray-400);padding:2rem">Aucun module</td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <div class="modal-overlay" id="addModuleModal">
        <div class="modal">
            <div class="modal-header"><h3 id="modModalTitle">Nouveau module</h3><button class="modal-close" onclick="closeModal('addModuleModal')">&times;</button></div>
            <div class="modal-body">
                <div id="modFormAlert"></div>
                <form id="moduleForm">
                    <input type="hidden" name="module_id" id="mod_id" value="">
                    <div class="form-group"><label>Titre</label><input type="text" name="titre" id="mod_titre" class="form-control" required></div>
                    <div class="form-group"><label>Description</label><textarea name="description" id="mod_desc" class="form-control" rows="3"></textarea></div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('addModuleModal')">Annuler</button>
                <button class="btn btn-primary" onclick="saveModule()">Enregistrer</button>
            </div>
        </div>
    </div>

    <script src="../../js/app.js"></script>
    <script>
    function editModule(m) {
        document.getElementById('modModalTitle').textContent = 'Modifier le module';
        document.getElementById('mod_id').value = m.id;
        document.getElementById('mod_titre').value = m.titre;
        document.getElementById('mod_desc').value = m.description || '';
        openModal('addModuleModal');
    }
    function saveModule() {
        var id = document.getElementById('mod_id').value;
        var titre = document.getElementById('mod_titre').value.trim();
        var desc = document.getElementById('mod_desc').value.trim();
        if (!titre) { document.getElementById('modFormAlert').innerHTML = '<div class="alert alert-danger">Le titre est requis.</div>'; return; }
        var action = id ? 'update_module' : 'add_module';
        postAjax('../../ajax/admin_handler.php', {action:action, id:id, titre:titre, description:desc}, function(err, data) {
            if (data && data.success) { location.reload(); }
            else { document.getElementById('modFormAlert').innerHTML = '<div class="alert alert-danger">' + (data ? data.message : 'Erreur') + '</div>'; }
        });
    }
    function deleteModule(id) {
        if (!confirm('Supprimer ce module et toutes ses lecons ?')) return;
        postAjax('../../ajax/admin_handler.php', {action:'delete_module', id:id}, function(err, data) {
            if (data && data.success) location.reload();
            else alert(data ? data.message : 'Erreur');
        });
    }
    </script>
</body>
</html>
