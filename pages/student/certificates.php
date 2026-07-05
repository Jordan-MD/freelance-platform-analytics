<?php
require_once '../../includes/config.php';
require_once '../../includes/auth.php';
require_once '../../includes/functions.php';
requireRole('student');

$user = getUser();
$student_id = $_SESSION['user_id'];

// Certificats obtenus
$stmt = $pdo->prepare("SELECT mc.*, m.titre as module_titre FROM module_certificates mc JOIN modules m ON mc.module_id=m.id WHERE mc.student_id=? ORDER BY mc.date_obtained DESC");
$stmt->execute([$student_id]); $certs = $stmt->fetchAll();

// Modules certifiables (toutes lecons terminees + evaluations réussies)
$modules_check = $pdo->prepare("SELECT m.*, (SELECT COUNT(*) FROM lessons WHERE module_id=m.id) AS total, (SELECT COUNT(*) FROM student_progress sp JOIN lessons l ON sp.lesson_id=l.id WHERE l.module_id=m.id AND sp.student_id=? AND sp.status='completed') AS done FROM modules m");
$modules_check->execute([$student_id]); $all_modules = $modules_check->fetchAll();

$certifiable = [];
foreach ($all_modules as $m) {
    if ($m['total'] == 0 || $m['done'] != $m['total']) continue;
    // Check evaluations
    $stmt2 = $pdo->prepare("SELECT COUNT(*) as total_evals FROM evaluations e JOIN lessons l ON e.lesson_id=l.id WHERE l.module_id=?");
    $stmt2->execute([$m['id']]); $te = $stmt2->fetch()['total_evals'];
    if ($te == 0) { $certifiable[] = $m; continue; }
    $stmt3 = $pdo->prepare("SELECT COUNT(DISTINCT e.id) as passed FROM student_evaluations se JOIN evaluations e ON se.evaluation_id=e.id JOIN lessons l ON e.lesson_id=l.id WHERE l.module_id=? AND se.student_id=? AND (se.score*1.0/se.max_score)>=0.5");
    $stmt3->execute([$m['id'], $student_id]); $pe = $stmt3->fetch()['passed'];
    if ($pe == $te) $certifiable[] = $m;
}

// Generate certificate
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['gen_module'])) {
    $mid = (int)$_POST['gen_module'];
    $stmt = $pdo->prepare("SELECT id FROM module_certificates WHERE student_id=? AND module_id=?");
    $stmt->execute([$student_id, $mid]);
    if (!$stmt->fetch()) {
        $code = generateCertificateCode();
        $pdo->prepare("INSERT INTO module_certificates (student_id, module_id, certificate_code) VALUES (?, ?, ?)")->execute([$student_id, $mid, $code]);
    }
    redirect('certificates.php');
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificats - E-Learn</title><link rel="stylesheet" href="../../css/style.css">
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
                <a href="certificates.php" class="active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg> Certificats</a>
            </div>
        </aside>
        <main class="main">
            <div class="page-header"><h1>Mes certificats</h1></div>

            <h2 class="section-title">Certificats obtenus</h2>
            <?php if (empty($certs)): ?>
                <div class="empty-state"><p>Aucun certificat obtenu.</p></div>
            <?php else: ?>
                <?php foreach ($certs as $c): ?>
                <div class="cert-card">
                    <div class="cert-info">
                        <h3><?= sanitize($c['module_titre']) ?></h3>
                        <div class="meta">Obtenu le <?= formatDate($c['date_obtained']) ?></div>
                        <div class="code">Code : <?= sanitize($c['certificate_code']) ?></div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="printCert('<?= sanitize($c['certificate_code']) ?>','<?= sanitize($c['module_titre']) ?>','<?= sanitize($user['prenom'].' '.$user['nom']) ?>','<?= formatDate($c['date_obtained']) ?>')">Imprimer</button>
                </div>
                <?php endforeach; ?>
            <?php endif; ?>

            <h2 class="section-title">Modules certifiables</h2>
            <?php if (empty($certifiable)): ?>
                <div class="empty-state"><p>Terminez toutes les lecons et evaluations d'un module pour obtenir son certificat.</p></div>
            <?php else: ?>
                <?php foreach ($certifiable as $m): ?>
                <div class="cert-card">
                    <div class="cert-info">
                        <h3><?= sanitize($m['titre']) ?></h3>
                        <div class="meta">Toutes les lecons terminees et evaluations reussies</div>
                    </div>
                    <form method="POST" style="margin:0"><input type="hidden" name="gen_module" value="<?= $m['id'] ?>"><button type="submit" class="btn btn-success btn-sm">Generer le certificat</button></form>
                </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </main>
    </div>
    <script>
    function printCert(code, module, name, date) {
        var w = window.open('','_blank');
        w.document.write('<!DOCTYPE html><html><head><title>Certificat '+code+'</title><style>body{font-family:Georgia,serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#f5f5f5}.cert{width:750px;padding:50px;background:white;border:3px solid #4f46e5;text-align:center}.cert h1{color:#4f46e5;margin-bottom:0.5rem}.cert h2{color:#333;margin:1rem 0}.cert p{color:#555;font-size:1.1rem;line-height:1.8}.cert .name{font-size:1.8rem;font-weight:bold;color:#4f46e5;margin:1rem 0}.cert .code{font-family:monospace;color:#888;margin-top:2rem;font-size:0.85rem}</style></head><body><div class="cert"><h1>CERTIFICAT</h1><p>Ceci certifie que</p><div class="name">'+name+'</div><p>a termine avec succes le module</p><h2>'+module+'</h2><p>'+date+'</p><div class="code">Code : '+code+'</div></div></body></html>');
        w.document.close(); w.print();
    }
    </script>
</body>
</html>
