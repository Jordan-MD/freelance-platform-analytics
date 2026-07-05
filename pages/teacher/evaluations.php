<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('teacher');

$teacherId = $_SESSION['user_id'];
$teacher = getUser();

$evaluations = $pdo->prepare("SELECT e.*, l.titre AS lesson_titre, (SELECT COUNT(*) FROM questions q WHERE q.evaluation_id=e.id) AS nb_questions FROM evaluations e JOIN lessons l ON e.lesson_id=l.id WHERE l.created_by=? ORDER BY e.date_creation DESC");
$evaluations->execute([$teacherId]); $evaluations = $evaluations->fetchAll();

$lessons = $pdo->prepare("SELECT id, titre FROM lessons WHERE created_by=? ORDER BY titre");
$lessons->execute([$teacherId]); $lessons = $lessons->fetchAll();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluations - Enseignant - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
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
                <a href="lessons.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Mes lecons</a>
                <a href="evaluations.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg> Evaluations</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header-row">
                <h1>Evaluations</h1>
                <button class="btn btn-primary" onclick="openModal('addEvalModal')">+ Creer une evaluation</button>
            </div>
            <div id="evalsAlert"></div>
            <div class="panel">
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Titre</th><th>Lecon</th><th>Questions</th><th style="text-align:right">Actions</th></tr></thead>
                        <tbody>
                            <?php foreach ($evaluations as $e): ?>
                            <tr id="eval-<?= $e['id'] ?>">
                                <td><strong><?= sanitize($e['titre']) ?></strong></td>
                                <td style="color:var(--gray-500)"><?= sanitize($e['lesson_titre']) ?></td>
                                <td><span class="badge badge-primary"><?= $e['nb_questions'] ?></span></td>
                                <td class="actions">
                                    <button class="btn btn-outline btn-sm" onclick="openAddQuestion(<?= $e['id'] ?>)">+ Question</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteEval(<?= $e['id'] ?>)">Supprimer</button>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                            <?php if (empty($evaluations)): ?>
                            <tr><td colspan="4" style="text-align:center;color:var(--gray-400);padding:2rem">Aucune evaluation</td></tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <div class="modal-overlay" id="addEvalModal">
        <div class="modal">
            <div class="modal-header"><h3>Creer une evaluation</h3><button class="modal-close" onclick="closeModal('addEvalModal')">&times;</button></div>
            <div class="modal-body">
                <div id="evalFormAlert"></div>
                <div class="form-group"><label>Lecon *</label>
                    <select id="eval_lesson" class="form-control" required>
                        <option value="">Choisir une lecon</option>
                        <?php foreach ($lessons as $l): ?>
                        <option value="<?= $l['id'] ?>"><?= sanitize($l['titre']) ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="form-group"><label>Titre de l'evaluation *</label><input type="text" id="eval_titre" class="form-control" required></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('addEvalModal')">Annuler</button>
                <button class="btn btn-primary" onclick="submitEval()">Creer</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="addQuestionModal">
        <div class="modal modal-lg">
            <div class="modal-header"><h3>Ajouter une question</h3><button class="modal-close" onclick="closeModal('addQuestionModal')">&times;</button></div>
            <div class="modal-body">
                <div id="qFormAlert"></div>
                <input type="hidden" id="q_eval_id" value="">
                <div class="form-group"><label>Question *</label><textarea id="q_text" class="form-control" rows="2" required></textarea></div>
                <div class="form-row">
                    <div class="form-group"><label>Option A *</label><input type="text" id="q_a" class="form-control" required></div>
                    <div class="form-group"><label>Option B *</label><input type="text" id="q_b" class="form-control" required></div>
                </div>
                <div class="form-row">
                    <div class="form-group"><label>Option C *</label><input type="text" id="q_c" class="form-control" required></div>
                    <div class="form-group"><label>Option D *</label><input type="text" id="q_d" class="form-control" required></div>
                </div>
                <div class="form-group"><label>Reponse correcte *</label>
                    <select id="q_correct" class="form-control">
                        <option value="A">A</option><option value="B">B</option><option value="C">C</option><option value="D">D</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('addQuestionModal')">Annuler</button>
                <button class="btn btn-primary" onclick="submitQuestion()">Ajouter</button>
            </div>
        </div>
    </div>

    <script src="../../js/app.js"></script>
    <script>
    function submitEval() {
        var lesson = document.getElementById('eval_lesson').value;
        var titre = document.getElementById('eval_titre').value.trim();
        if (!lesson || !titre) { document.getElementById('evalFormAlert').innerHTML = '<div class="alert alert-danger">Remplissez tous les champs.</div>'; return; }
        postAjax('../../ajax/teacher_handler.php', {action:'add_evaluation', lesson_id:lesson, titre:titre}, function(e,d) {
            if (d && d.success) { closeModal('addEvalModal'); showToast(d.message,'success'); setTimeout(function(){location.reload();},800); }
            else { document.getElementById('evalFormAlert').innerHTML = '<div class="alert alert-danger">'+(d?d.message:'Erreur')+'</div>'; }
        });
    }
    function openAddQuestion(evalId) {
        document.getElementById('q_eval_id').value = evalId;
        document.getElementById('q_text').value = '';
        document.getElementById('q_a').value = '';
        document.getElementById('q_b').value = '';
        document.getElementById('q_c').value = '';
        document.getElementById('q_d').value = '';
        document.getElementById('q_correct').value = 'A';
        openModal('addQuestionModal');
    }
    function submitQuestion() {
        var data = {
            action: 'add_question',
            evaluation_id: document.getElementById('q_eval_id').value,
            question_text: document.getElementById('q_text').value.trim(),
            option_a: document.getElementById('q_a').value.trim(),
            option_b: document.getElementById('q_b').value.trim(),
            option_c: document.getElementById('q_c').value.trim(),
            option_d: document.getElementById('q_d').value.trim(),
            correct_option: document.getElementById('q_correct').value
        };
        if (!data.question_text || !data.option_a || !data.option_b || !data.option_c || !data.option_d) {
            document.getElementById('qFormAlert').innerHTML = '<div class="alert alert-danger">Remplissez tous les champs.</div>'; return;
        }
        postAjax('../../ajax/teacher_handler.php', data, function(e,d) {
            if (d && d.success) { closeModal('addQuestionModal'); showToast(d.message,'success'); setTimeout(function(){location.reload();},800); }
            else { document.getElementById('qFormAlert').innerHTML = '<div class="alert alert-danger">'+(d?d.message:'Erreur')+'</div>'; }
        });
    }
    function deleteEval(id) {
        if (!confirm('Supprimer cette evaluation ?')) return;
        postAjax('../../ajax/teacher_handler.php', {action:'delete_evaluation', evaluation_id:id}, function(e,d) { if(d&&d.success)location.reload(); else alert(d?d.message:'Erreur'); });
    }
    </script>
</body>
</html>
