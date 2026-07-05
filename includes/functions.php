<?php

function sanitize(string $input): string {
    return htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
}

function redirect(string $url): void {
    header('Location: ' . $url);
    exit;
}

function flash(string $type, string $message): void {
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function getFlash(): ?array {
    if (isset($_SESSION['flash'])) {
        $flash = $_SESSION['flash'];
        unset($_SESSION['flash']);
        return $flash;
    }
    return null;
}

function uploadFile(array $file, string $subfolder): ?string {
    $maxSize = 200 * 1024 * 1024;

    if ($file['error'] !== UPLOAD_ERR_OK) {
        error_log('Upload error code: ' . $file['error']);
        return null;
    }

    if ($file['size'] > $maxSize) return null;

    // Detection MIME reelle cote serveur
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $realMime = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);

    $allowedMimes = [
        'application/pdf',
        'video/mp4',
        'video/webm',
        'video/ogg',
        'image/jpeg',
        'image/png',
    ];

    if (!in_array($realMime, $allowedMimes)) {
        error_log('MIME rejected: ' . $realMime . ' for file ' . $file['name']);
        return null;
    }

    $uploadDir = __DIR__ . '/../uploads/' . $subfolder;
    if (!is_dir($uploadDir)) {
        mkdir($uploadDir, 0755, true);
    }

    // Extension basee sur le MIME reel
    $extMap = [
        'application/pdf' => 'pdf',
        'video/mp4' => 'mp4',
        'video/webm' => 'webm',
        'video/ogg' => 'ogg',
        'image/jpeg' => 'jpg',
        'image/png' => 'png',
    ];
    $ext = $extMap[$realMime] ?? pathinfo($file['name'], PATHINFO_EXTENSION);
    $filename = uniqid('file_', true) . '.' . $ext;
    $filepath = $uploadDir . '/' . $filename;

    if (move_uploaded_file($file['tmp_name'], $filepath)) {
        return 'uploads/' . $subfolder . '/' . $filename;
    }
    error_log('move_uploaded_file failed for: ' . $filepath);
    return null;
}

function generateCertificateCode(): string {
    return 'CERT-' . strtoupper(bin2hex(random_bytes(6)));
}

function formatDate(string $date): string {
    $ts = strtotime($date);
    $months = [1=>'janvier',2=>'fevrier',3=>'mars',4=>'avril',5=>'mai',6=>'juin',7=>'juillet',8=>'aout',9=>'septembre',10=>'octobre',11=>'novembre',12=>'decembre'];
    return date('d', $ts) . ' ' . $months[(int)date('m', $ts)] . ' ' . date('Y', $ts);
}

function timeAgo(string $date): string {
    $diff = time() - strtotime($date);
    if ($diff < 60) return "a l'instant";
    if ($diff < 3600) return 'il y a ' . floor($diff / 60) . ' min';
    if ($diff < 86400) return 'il y a ' . floor($diff / 3600) . ' h';
    return 'il y a ' . floor($diff / 86400) . ' j';
}
