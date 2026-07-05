<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('student');

$user = getUser();
$student_id = $_SESSION['user_id'];
$lesson_id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($lesson_id <= 0) redirect('courses.php');

$stmt = $pdo->prepare("SELECT l.*, m.titre as module_titre, m.id as module_id FROM lessons l JOIN modules m ON l.module_id=m.id WHERE l.id=?");
$stmt->execute([$lesson_id]); $lesson = $stmt->fetch();
if (!$lesson) redirect('courses.php');

// Get or init progress
$stmt = $pdo->prepare("SELECT * FROM student_progress WHERE student_id=? AND lesson_id=?");
$stmt->execute([$student_id, $lesson_id]); $progress = $stmt->fetch();
if (!$progress) {
    $pdo->prepare("INSERT INTO student_progress (student_id, lesson_id, status, progression) VALUES (?, ?, 'in_progress', 0)")->execute([$student_id, $lesson_id]);
    $progress = ['status' => 'in_progress', 'progression' => 0];
}

// AJAX: mark complete
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'mark_complete') {
    header('Content-Type: application/json');
    $pdo->prepare("UPDATE student_progress SET status='completed', progression=100 WHERE student_id=? AND lesson_id=?")->execute([$student_id, $lesson_id]);
    echo json_encode(['success' => true]);
    exit;
}

// Get evaluation
$stmt = $pdo->prepare("SELECT * FROM evaluations WHERE lesson_id=?"); $stmt->execute([$lesson_id]); $evaluation = $stmt->fetch();

// Check if evaluation already passed
$evaluation_passed = false;
if ($evaluation) {
    $stmt = $pdo->prepare("SELECT score, max_score FROM student_evaluations WHERE student_id=? AND evaluation_id=? ORDER BY id DESC LIMIT 1");
    $stmt->execute([$student_id, $evaluation['id']]); $last = $stmt->fetch();
    if ($last && $last['max_score'] > 0 && ($last['score'] / $last['max_score']) >= 0.5) $evaluation_passed = true;
}

$is_completed = $progress['status'] === 'completed';
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= sanitize($lesson['titre']) ?> - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
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
            <a href="courses.php?module_id=<?= $lesson['module_id'] ?>" style="display:inline-flex;align-items:center;gap:0.3rem;color:var(--gray-500);font-size:0.9rem;margin-bottom:1rem">&#8592; Retour au module</a>
            <div class="page-header">
                <h1><?= sanitize($lesson['titre']) ?></h1>
                <p>Module : <?= sanitize($lesson['module_titre']) ?> | Type : <?= strtoupper($lesson['type']) ?></p>
            </div>

            <div id="statusAlert" class="alert <?= $is_completed ? 'alert-success' : 'alert-danger' ?>" style="margin-bottom:1rem">
                <?= $is_completed ? 'Lecon terminee.' : 'Lecon en cours. Regardez la video en entier pour debloquer l\'evaluation.' ?>
            </div>

            <?php if ($lesson['type'] === 'video'): ?>
            <div class="lesson-content">
                <video id="lessonVideo" controls preload="metadata">
                    <source src="<?= BASE_URL . '/' . sanitize($lesson['file_path']) ?>" type="video/mp4">
                    Votre navigateur ne supporte pas la lecture video.
                </video>
                <div class="video-info">
                    <div class="video-status">
                        <span class="video-status-text" id="videoStatusText">
                            <?= $is_completed ? 'Video terminee - Vous pouvez revoir la video' : 'Regardez la video en entier pour acceder a l\'evaluation' ?>
                        </span>
                        <span class="video-time" id="videoTime"></span>
                    </div>
                    <div class="video-progress">
                        <div class="progress"><div class="progress-bar" id="videoProgressBar" style="width:0%;transition:width 0.3s"></div></div>
                    </div>
                </div>
            </div>
            <?php else: ?>
            <div class="lesson-content">
                <iframe src="<?= BASE_URL . '/' . sanitize($lesson['file_path']) ?>" style="width:100%;height:70vh;border:none"></iframe>
            </div>
            <?php endif; ?>

            <div style="display:flex;gap:0.75rem;margin-top:1.5rem;flex-wrap:wrap;align-items:center">
                <?php if ($lesson['type'] === 'pdf' && !$is_completed): ?>
                    <button class="btn btn-success" id="markCompleteBtn">Marquer comme termine</button>
                <?php endif; ?>

                <div id="evalSection" style="<?= (!$is_completed && $lesson['type'] === 'video') ? 'display:none' : '' ?>">
                    <?php if ($evaluation): ?>
                        <a href="evaluation.php?id=<?= $evaluation['id'] ?>" class="btn btn-warning" id="evalBtn">
                            <?= $evaluation_passed ? 'Revoir l\'evaluation' : 'Passer l\'evaluation' ?>
                        </a>
                    <?php endif; ?>
                </div>
            </div>
        </main>
    </div>

    <script src="../../js/app.js"></script>
    <script>
    (function() {
        var completed = <?= $is_completed ? 'true' : 'false' ?>;
        var lessonType = '<?= $lesson['type'] ?>';
        var evalSection = document.getElementById('evalSection');
        var statusAlert = document.getElementById('statusAlert');
        var videoStatusText = document.getElementById('videoStatusText');

        // PDF: bouton marquer termine
        var markBtn = document.getElementById('markCompleteBtn');
        if (markBtn) {
            markBtn.addEventListener('click', function() {
                fetch('', { method: 'POST', headers: {'Content-Type':'application/x-www-form-urlencoded'}, body: 'action=mark_complete' })
                .then(function(r){return r.json();})
                .then(function(d){ if(d.success) location.reload(); });
            });
        }

        function markDone() {
            if (completed) return;
            fetch('', { method: 'POST', headers: {'Content-Type':'application/x-www-form-urlencoded'}, body: 'action=mark_complete' })
            .then(function(r){return r.json();})
            .then(function(d){
                if (d.success) {
                    completed = true;
                    statusAlert.className = 'alert alert-success';
                    statusAlert.textContent = 'Lecon terminee.';
                    videoStatusText.textContent = 'Video terminee ! Vous pouvez revoir la video ou passer l\'evaluation.';
                    videoStatusText.className = 'video-status-text done';
                    evalSection.style.display = '';
                    showToast('Lecon terminee ! Vous pouvez passer l\'evaluation.', 'success');
                }
            });
        }

        if (lessonType === 'video') {
            var video = document.getElementById('lessonVideo');
            var progressBar = document.getElementById('videoProgressBar');
            var timeText = document.getElementById('videoTime');

            function fmtTime(s) {
                var h = Math.floor(s / 3600);
                var m = Math.floor((s % 3600) / 60);
                var sec = Math.floor(s % 60);
                if (h > 0) return h + ':' + (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
                return m + ':' + (sec < 10 ? '0' : '') + sec;
            }

            video.addEventListener('loadedmetadata', function() {
                if (video.duration) {
                    timeText.textContent = fmtTime(0) + ' / ' + fmtTime(video.duration);
                }
            });

            video.addEventListener('timeupdate', function() {
                if (video.duration && !isNaN(video.duration)) {
                    var pct = (video.currentTime / video.duration) * 100;
                    progressBar.style.width = pct + '%';
                    var rem = video.duration - video.currentTime;
                    timeText.textContent = fmtTime(video.currentTime) + ' / ' + fmtTime(video.duration) + '  (reste ' + fmtTime(rem) + ')';
                }
            });

            video.addEventListener('ended', function() {
                progressBar.style.width = '100%';
                timeText.textContent = 'Termine !';
                markDone();
            });
        }
    })();
    </script>
</body>
</html>
