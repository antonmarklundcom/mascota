<?php
declare(strict_types=1);
$local = dirname(__DIR__) . '/app/bootstrap.php';
$deployed = dirname(__DIR__) . '/mascota-app/app/bootstrap.php';
if (is_file($local)) {
    require $local;
} elseif (is_file($deployed)) {
    require $deployed;
} else {
    http_response_code(503);
    header('Content-Type: text/plain; charset=UTF-8');
    header('X-Robots-Tag: noindex');
    echo 'Faltan los archivos privados de Mascota. Revisá PHP-DEPLOY.md.';
    exit;
}
mascota_run();
