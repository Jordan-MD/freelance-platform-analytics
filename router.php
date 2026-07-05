<?php
// Routeur pour php -S - gere les fichiers statiques avec Range requests
$uri = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));

// Fichiers statiques (ignorer les .php - PHP les gere lui-meme)
$ext = pathinfo($uri, PATHINFO_EXTENSION);
if ($uri !== '/' && $ext !== 'php' && file_exists(__DIR__ . $uri)) {
    $mimeTypes = [
        'mp4'  => 'video/mp4',
        'webm' => 'video/webm',
        'ogg'  => 'video/ogg',
        'pdf'  => 'application/pdf',
        'jpg'  => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'png'  => 'image/png',
        'css'  => 'text/css',
        'js'   => 'application/javascript',
    ];
    $mime = $mimeTypes[$ext] ?? mime_content_type(__DIR__ . $uri) ?: 'application/octet-stream';
    $file = __DIR__ . $uri;
    $fileSize = filesize($file);

    // Videos et PDF : supporter Range requests
    if (in_array($ext, ['mp4', 'webm', 'ogg', 'pdf'])) {
        header('Accept-Ranges: bytes');
        header("Content-Type: $mime");

        if (isset($_SERVER['HTTP_RANGE'])) {
            $range = $_SERVER['HTTP_RANGE'];
            preg_match('/bytes=(\d+)-(\d*)/', $range, $matches);
            $start = (int)$matches[1];
            $end = isset($matches[2]) && $matches[2] !== '' ? (int)$matches[2] : $fileSize - 1;
            $end = min($end, $fileSize - 1);
            $length = $end - $start + 1;

            header('HTTP/1.1 206 Partial Content');
            header("Content-Range: bytes $start-$end/$fileSize");
            header("Content-Length: $length");

            $fp = fopen($file, 'rb');
            fseek($fp, $start);
            $bufferSize = 8192;
            $remaining = $length;
            while ($remaining > 0 && !feof($fp)) {
                $chunk = min($bufferSize, $remaining);
                echo fread($fp, $chunk);
                $remaining -= $chunk;
                flush();
            }
            fclose($fp);
        } else {
            header("Content-Length: $fileSize");
            readfile($file);
        }
        exit;
    }

    // Autres fichiers statiques
    header("Content-Type: $mime");
    header("Content-Length: " . $fileSize);
    readfile(__DIR__ . $uri);
    exit;
}

// Fallback vers index.php
return false;
