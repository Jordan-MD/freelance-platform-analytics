<?php
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/functions.php';

header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { echo json_encode(['success'=>false,'message'=>'Methode non autorisee']); exit; }
requireRole('teacher');

$teacherId = $_SESSION['user_id'];
global $pdo;
$action = $_POST['action'] ?? '';

switch ($action) {

    case 'add_lesson':
    case 'edit_lesson':
        $titre = trim($_POST['titre'] ?? '');
        $desc = trim($_POST['description'] ?? '');
        $moduleId = (int)($_POST['module_id'] ?? 0);
        $type = $_POST['type'] ?? '';
        $lessonId = (int)($_POST['lesson_id'] ?? 0);

        if ($titre === '' || $moduleId === 0 || !in_array($type, ['pdf','video'])) {
            echo json_encode(['success'=>false,'message'=>'Champs obligatoires manquants']); exit;
        }

        $filePath = null;
        if (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
            $sub = $type === 'pdf' ? 'lessons/pdf' : 'lessons/video';
            $filePath = uploadFile($_FILES['file'], $sub);
            if (!$filePath) {
                echo json_encode(['success'=>false,'message'=>'Echec upload. Verifiez le type (PDF/MP4) et la taille (max 100Mo).']); exit;
            }
        }

        if ($action === 'edit_lesson') {
            if (!$lessonId) { echo json_encode(['success'=>false,'message'=>'ID invalide']); exit; }
            $owner = $pdo->prepare("SELECT id, file_path FROM lessons WHERE id=? AND created_by=?");
            $owner->execute([$lessonId, $teacherId]); $old = $owner->fetch();
            if (!$old) { echo json_encode(['success'=>false,'message'=>'Lecon introuvable']); exit; }
            if ($filePath && $old['file_path']) { $f = __DIR__.'/'.$old['file_path']; if(file_exists($f)) unlink($f); }
            if ($filePath) {
                $pdo->prepare("UPDATE lessons SET titre=?, description=?, module_id=?, type=?, file_path=? WHERE id=?")->execute([$titre,$desc,$moduleId,$type,$filePath,$lessonId]);
            } else {
                $pdo->prepare("UPDATE lessons SET titre=?, description=?, module_id=?, type=? WHERE id=?")->execute([$titre,$desc,$moduleId,$type,$lessonId]);
            }
            echo json_encode(['success'=>true,'message'=>'Lecon mise a jour']); break;
        } else {
            if (!$filePath) { echo json_encode(['success'=>false,'message'=>'Fichier obligatoire']); exit; }
            $maxO = $pdo->prepare("SELECT COALESCE(MAX(ordre),0) FROM lessons WHERE module_id=? AND created_by=?");
            $maxO->execute([$moduleId, $teacherId]); $next = (int)$maxO->fetchColumn() + 1;
            $pdo->prepare("INSERT INTO lessons (module_id, titre, description, type, file_path, ordre, created_by) VALUES (?,?,?,?,?,?,?)")->execute([$moduleId,$titre,$desc,$type,$filePath,$next,$teacherId]);
            echo json_encode(['success'=>true,'message'=>'Lecon ajoutee']); break;
        }

    case 'delete_lesson':
        $lessonId = (int)($_POST['lesson_id'] ?? 0);
        if (!$lessonId) { echo json_encode(['success'=>false,'message'=>'ID invalide']); exit; }
        $owner = $pdo->prepare("SELECT id, file_path FROM lessons WHERE id=? AND created_by=?");
        $owner->execute([$lessonId, $teacherId]); $lesson = $owner->fetch();
        if (!$lesson) { echo json_encode(['success'=>false,'message'=>'Lecon introuvable']); exit; }
        $pdo->prepare("DELETE FROM lessons WHERE id=?")->execute([$lessonId]);
        if ($lesson['file_path']) { $f = __DIR__.'/'.$lesson['file_path']; if(file_exists($f)) unlink($f); }
        echo json_encode(['success'=>true,'message'=>'Lecon supprimee']); break;

    case 'add_evaluation':
        $lessonId = (int)($_POST['lesson_id'] ?? 0);
        $titre = trim($_POST['titre'] ?? '');
        if (!$lessonId || $titre === '') { echo json_encode(['success'=>false,'message'=>'Champs requis']); exit; }
        $owner = $pdo->prepare("SELECT id FROM lessons WHERE id=? AND created_by=?");
        $owner->execute([$lessonId, $teacherId]);
        if (!$owner->fetch()) { echo json_encode(['success'=>false,'message'=>'Lecon introuvable']); exit; }
        $pdo->prepare("INSERT INTO evaluations (lesson_id, titre) VALUES (?, ?)")->execute([$lessonId, $titre]);
        echo json_encode(['success'=>true,'message'=>'Evaluation creee']); break;

    case 'add_question':
        $evalId = (int)($_POST['evaluation_id'] ?? 0);
        $text = trim($_POST['question_text'] ?? '');
        $a = trim($_POST['option_a'] ?? '');
        $b = trim($_POST['option_b'] ?? '');
        $c = trim($_POST['option_c'] ?? '');
        $d = trim($_POST['option_d'] ?? '');
        $correct = $_POST['correct_option'] ?? '';
        if (!$evalId || $text==='' || $a==='' || $b==='' || $c==='' || $d==='' || !in_array($correct,['A','B','C','D'])) {
            echo json_encode(['success'=>false,'message'=>'Tous les champs sont requis']); exit;
        }
        $owner = $pdo->prepare("SELECT e.id FROM evaluations e JOIN lessons l ON e.lesson_id=l.id WHERE e.id=? AND l.created_by=?");
        $owner->execute([$evalId, $teacherId]);
        if (!$owner->fetch()) { echo json_encode(['success'=>false,'message'=>'Evaluation introuvable']); exit; }
        $pdo->prepare("INSERT INTO questions (evaluation_id, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?,?,?,?,?,?,?)")->execute([$evalId,$text,$a,$b,$c,$d,$correct]);
        echo json_encode(['success'=>true,'message'=>'Question ajoutee']); break;

    case 'delete_evaluation':
        $evalId = (int)($_POST['evaluation_id'] ?? 0);
        if (!$evalId) { echo json_encode(['success'=>false,'message'=>'ID invalide']); exit; }
        $owner = $pdo->prepare("SELECT e.id FROM evaluations e JOIN lessons l ON e.lesson_id=l.id WHERE e.id=? AND l.created_by=?");
        $owner->execute([$evalId, $teacherId]);
        if (!$owner->fetch()) { echo json_encode(['success'=>false,'message'=>'Introuvable']); exit; }
        $pdo->prepare("DELETE FROM evaluations WHERE id=?")->execute([$evalId]);
        echo json_encode(['success'=>true,'message'=>'Evaluation supprimee']); break;

    default:
        echo json_encode(['success'=>false,'message'=>'Action inconnue']); break;
}
