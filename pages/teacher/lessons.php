<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('teacher');

$teacherId = $_SESSION['user_id'];
$teacher = getUser();

$lessons = $pdo->prepare("SELECT l.*, m.titre AS module_titre, (SELECT COUNT(*) FROM evaluations e WHERE e.lesson_id=l.id) AS eval_count FROM lessons l JOIN modules m ON l.module_id=m.id WHERE l.created_by=? ORDER BY l.date_creation DESC");
$lessons->execute([$teacherId]); $lessons = $lessons->fetchAll();

$modules = $pdo->prepare("SELECT * FROM modules ORDER BY titre");
$modules->execute(); $modules = $modules->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lecons - Enseignant - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
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
                <a href="dashboard.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Tableau de bord</a>
                <a href="lessons.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Mes lecons</a>
                <a href="evaluations.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg> Evaluations</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header-row">
                <h1>Mes lecons</h1>
                <button class="btn btn-primary" onclick="openModal('addLessonModal')">+ Ajouter une lecon</button>
            </div>
            <div id="lessonsAlert"></div>
            <div class="panel">
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Titre</th><th>Module</th><th>Type</th><th>Evaluations</th><th style="text-align:right">Actions</th></tr></thead>
                        <tbody>
                            <?php foreach ($lessons as $l): ?>
                            <tr id="lesson-<?= $l['id'] ?>">
                                <td><strong><?= sanitize($l['titre']) ?></strong></td>
                                <td style="color:var(--gray-500)"><?= sanitize($l['module_titre']) ?></td>
                                <td><span class="badge badge-<?= $l['type']==='pdf' ? 'primary' : 'success' ?>"><?= strtoupper($l['type']) ?></span></td>
                                <td><?= $l['eval_count'] ?></td>
                                <td class="actions">
                                    <button class="btn btn-outline btn-sm" onclick='editLesson(<?= json_encode($l) ?>)'>Modifier</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteLesson(<?= $l['id'] ?>)">Supprimer</button>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($lessons)): ?>
                            <tr><td colspan="5" style="text-align:center;color:var(--gray-400);padding:2rem">Aucune lecon</td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <div class="modal-overlay" id="addLessonModal">
        <div class="modal modal-lg">
            <div class="modal-header"><h3 id="lessonModalTitle">Ajouter une lecon</h3><button class="modal-close" onclick="closeModal('addLessonModal')">&times;</button></div>
            <div class="modal-body">
                <div id="lessonFormAlert"></div>
                <form id="lessonForm" enctype="multipart/form-data">
                    <input type="hidden" name="lesson_id" id="lesson_id" value="">
                    <div class="form-group"><label>Titre *</label><input type="text" name="titre" id="lesson_titre" class="form-control" required></div>
                    <div class="form-group"><label>Description</label><textarea name="description" id="lesson_desc" class="form-control" rows="2"></textarea></div>
                    <div class="form-row">
                        <div class="form-group"><label>Module *</label>
                            <select name="module_id" id="lesson_module" class="form-control" required>
                                <option value="">Choisir un module</option>
                                <?php foreach ($modules as $m): ?>
                                <option value="<?= $m['id'] ?>"><?= sanitize($m['titre']) ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        <div class="form-group"><label>Type *</label>
                            <select name="type" id="lesson_type" class="form-control" required>
                                <option value="pdf">PDF</option>
                                <option value="video">Video</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group"><label>Fichier (PDF ou MP4, max 100 Mo) *</label>
                        <input type="file" name="file" id="lesson_file" class="form-control" accept=".pdf,.mp4,.webm,.ogg">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('addLessonModal')">Annuler</button>
                <button class="btn btn-primary" onclick="submitLesson()">Enregistrer</button>
            </div>
        </div>
    </div>

    <script src="../../js/app.js"></script>
    <script>
    function editLesson(l) {
        document.getElementById('lessonModalTitle').textContent = 'Modifier la lecon';
        document.getElementById('lesson_id').value = l.id;
        document.getElementById('lesson_titre').value = l.titre;
        document.getElementById('lesson_desc').value = l.description || '';
        document.getElementById('lesson_module').value = l.module_id;
        document.getElementById('lesson_type').value = l.type;
        document.getElementById('lesson_file').removeAttribute('required');
        openModal('addLessonModal');
    }
    function submitLesson() {
        var form = document.getElementById('lessonForm');
        var fd = new FormData(form);
        var isEdit = fd.get('lesson_id') !== '';
        if (isEdit) fd.set('action', 'edit_lesson'); else fd.set('action', 'add_lesson');
        if (!isEdit && !document.getElementById('lesson_file').files.length) {
            document.getElementById('lessonFormAlert').innerHTML = '<div class="alert alert-danger">Selectionnez un fichier.</div>'; return;
        }
        fetch('../../ajax/teacher_handler.php', { method: 'POST', body: fd })
        .then(function(r){return r.json();})
        .then(function(d){ if(d.success){closeModal('addLessonModal');showToast(d.message,'success');setTimeout(function(){location.reload();},800);} else {document.getElementById('lessonFormAlert').innerHTML='<div class="alert alert-danger">'+d.message+'</div>';}})
        .catch(function(){document.getElementById('lessonFormAlert').innerHTML='<div class="alert alert-danger">Erreur de connexion.</div>';});
    }
    function deleteLesson(id) {
        if (!confirm('Supprimer cette lecon ?')) return;
        var fd = new FormData(); fd.append('action','delete_lesson'); fd.append('lesson_id',id);
        fetch('../../ajax/teacher_handler.php',{method:'POST',body:fd}).then(function(r){return r.json();}).then(function(d){if(d.success)location.reload();else alert(d.message);});
    }
    </script>
</body>
</html>
