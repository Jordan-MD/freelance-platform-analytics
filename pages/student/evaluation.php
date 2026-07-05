<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('student');

$user = getUser();
$student_id = $_SESSION['user_id'];
$evaluation_id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($evaluation_id <= 0) redirect('courses.php');

$stmt = $pdo->prepare("SELECT e.*, l.id as lesson_id, l.titre as lesson_titre, m.id as module_id, m.titre as module_titre FROM evaluations e JOIN lessons l ON e.lesson_id=l.id JOIN modules m ON l.module_id=m.id WHERE e.id=?");
$stmt->execute([$evaluation_id]); $evaluation = $stmt->fetch();
if (!$evaluation) redirect('courses.php');

// VERIFICATION SERVEUR: la lecon doit etre terminee
$stmt = $pdo->prepare("SELECT status FROM student_progress WHERE student_id=? AND lesson_id=?");
$stmt->execute([$student_id, $evaluation['lesson_id']]); $prog = $stmt->fetch();
if (!$prog || $prog['status'] !== 'completed') {
    redirect('lesson.php?id=' . $evaluation['lesson_id']);
}

$stmt = $pdo->prepare("SELECT * FROM questions WHERE evaluation_id=? ORDER BY id ASC");
$stmt->execute([$evaluation_id]); $questions = $stmt->fetchAll();

$submitted = false;
$result = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $submitted = true;
    $score = 0;
    $total = count($questions);
    foreach ($questions as $q) {
        $answer = $_POST['q_' . $q['id']] ?? null;
        if ($answer === $q['correct_option']) $score++;
    }
    $stmt = $pdo->prepare("INSERT INTO student_evaluations (student_id, evaluation_id, score, max_score) VALUES (?, ?, ?, ?)");
    $stmt->execute([$student_id, $evaluation_id, $score, $total]);
    $result = [
        'score' => $score, 'total' => $total,
        'percentage' => $total > 0 ? round(($score/$total)*100) : 0,
        'passed' => $total > 0 && ($score/$total) >= 0.5
    ];
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluation - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
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
                <a href="courses.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg> Mes cours</a>
                <a href="certificates.php"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <a href="lesson.php?id=<?= $evaluation['lesson_id'] ?>" style="display:inline-flex;align-items:center;gap:0.3rem;color:var(--gray-500);font-size:0.9rem;margin-bottom:1rem">&#8592; Retour a la lecon</a>
            <div class="page-header">
                <h1><?= sanitize($evaluation['titre']) ?></h1>
                <p>Module : <?= sanitize($evaluation['module_titre']) ?> | Lecon : <?= sanitize($evaluation['lesson_titre']) ?></p>
            </div>

            <?php if ($submitted && $result): ?>
                <div class="panel">
                    <div class="result-card">
                        <h2>Resultat</h2>
                        <div class="result-score <?= $result['passed'] ? 'result-passed' : 'result-failed' ?>"><?= $result['score'] ?>/<?= $result['total'] ?></div>
                        <p style="font-size:1.1rem;margin-bottom:0.5rem">Progression : <?= $result['percentage'] ?>%</p>
                        <p style="font-size:1rem;font-weight:600;color:<?= $result['passed'] ? 'var(--success)' : 'var(--danger)' ?>">
                            <?= $result['passed'] ? 'Felications, vous avez reussi !' : 'Pas assez de points. Seuil minimum : 50%.' ?>
                        </p>
                        <div style="margin-top:1.5rem">
                            <a href="lesson.php?id=<?= $evaluation['lesson_id'] ?>" class="btn btn-primary">Retour a la lecon</a>
                            <?php if (!$result['passed']): ?>
                                <a href="evaluation.php?id=<?= $evaluation_id ?>" class="btn btn-outline" style="margin-left:0.5rem">Reessayer</a>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            <?php else: ?>
                <?php if (empty($questions)): ?>
                    <div class="empty-state"><p>Aucune question pour cette evaluation.</p></div>
                <?php else: ?>
                <form method="POST" action="">
                    <?php foreach ($questions as $i => $q): ?>
                    <div class="question-card">
                        <div><span class="q-number"><?= $i+1 ?></span><span class="q-text"><?= sanitize($q['question_text']) ?></span></div>
                        <div class="options" style="margin-top:0.8rem">
                            <?php foreach (['A','B','C','D'] as $opt): ?>
                            <label class="option-label">
                                <input type="radio" name="q_<?= $q['id'] ?>" value="<?= $opt ?>" required>
                                <?= $opt ?>. <?= sanitize($q['option_' . strtolower($opt)]) ?>
                            </label>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    <?php endforeach; ?>
                    <button type="submit" class="btn btn-primary btn-lg" style="margin-top:1rem">Soumettre les reponses</button>
                </form>
                <?php endif; ?>
            <?php endif; ?>
        </main>
    </div>
</body>
</html>
