<?php
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/functions.php';

header('Content-Type: application/json');
if (!isAdmin()) { echo json_encode(['success'=>false,'message'=>'Non autorise']); exit; }

$input = json_decode(file_get_contents('php://input'), true);
$action = $input['action'] ?? $_POST['action'] ?? '';
global $pdo;

switch ($action) {
    case 'add_module':
        $titre = trim($input['titre'] ?? '');
        $desc = trim($input['description'] ?? '');
        if (empty($titre)) { echo json_encode(['success'=>false,'message'=>'Titre requis']); exit; }
        $pdo->prepare("INSERT INTO modules (titre, description, created_by) VALUES (?, ?, ?)")->execute([$titre, $desc, $_SESSION['user_id']]);
        echo json_encode(['success'=>true,'message'=>'Module ajoute']); break;

    case 'update_module':
        $id = (int)($input['id'] ?? 0);
        $titre = trim($input['titre'] ?? '');
        $desc = trim($input['description'] ?? '');
        if (!$id || empty($titre)) { echo json_encode(['success'=>false,'message'=>'Donnees invalides']); exit; }
        $pdo->prepare("UPDATE modules SET titre=?, description=? WHERE id=?")->execute([$titre, $desc, $id]);
        echo json_encode(['success'=>true,'message'=>'Module mis a jour']); break;

    case 'delete_module':
        $id = (int)($input['id'] ?? 0);
        if (!$id) { echo json_encode(['success'=>false,'message'=>'ID invalide']); exit; }
        $pdo->prepare("DELETE FROM modules WHERE id=?")->execute([$id]);
        echo json_encode(['success'=>true,'message'=>'Module supprime']); break;

    case 'delete_user':
        $id = (int)($input['id'] ?? 0);
        if (!$id || $id == $_SESSION['user_id']) { echo json_encode(['success'=>false,'message'=>'Impossible']); exit; }
        $pdo->prepare("DELETE FROM users WHERE id=?")->execute([$id]);
        echo json_encode(['success'=>true,'message'=>'Utilisateur supprime']); break;

    default:
        echo json_encode(['success'=>false,'message'=>'Action inconnue']); break;
}
