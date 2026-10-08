<?php
declare(strict_types=1);
// PHP's development server only. Hostinger uses public/.htaccess.
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$public = realpath(__DIR__.'/public');
$file = is_string($path) ? realpath($public.'/'.rawurldecode($path)) : false;
if ($file && str_starts_with($file, $public.DIRECTORY_SEPARATOR.'assets'.DIRECTORY_SEPARATOR) && is_file($file) && preg_match('/\.(css|svg|png|webp|jpg)$/D',$file)) return false;
require __DIR__.'/public/index.php';
