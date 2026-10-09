<?php
declare(strict_types=1);
// No sessions, visitor records, forms, messages or payments.
function verified_details(array $s): bool {
    $value = $s['verified_on'] ?? null;
    if (!is_string($value)) return false;
    $date = DateTimeImmutable::createFromFormat('!Y-m-d', $value);
    $today = new DateTimeImmutable('today');
    return $date && $date->format('Y-m-d') === $value && $date <= $today && $date >= $today->modify('-90 days');
}
function clinic_text(mixed $value, int $limit = 300): ?string {
    return is_string($value) && trim($value) !== '' && strlen($value) <= $limit && !preg_match('/[\x00-\x1f\x7f]/', $value) ? trim($value) : null;
}
function clinic_contacts(array $s): array {
    if (!verified_details($s) || ($s['contact_approved'] ?? false) !== true) return [];
    $result = [];
    foreach (['phone'=>'tel:', 'whatsapp'=>'https://wa.me/'] as $key=>$prefix) {
        $phone = $s[$key] ?? null;
        if (is_string($phone) && preg_match('/^\+[1-9][0-9]{7,14}$/D', $phone)) $result[$key] = $prefix.($key === 'whatsapp' ? substr($phone, 1) : $phone);
    }
    $website = $s['website'] ?? null;
    if (is_string($website) && strlen($website) <= 500 && !preg_match('/[\x00-\x20\x7f\\\\]/', $website) && filter_var($website, FILTER_VALIDATE_URL)) {
        $u = parse_url($website); $host = $u['host'] ?? '';
        if (($u['scheme'] ?? '') === 'https' && !isset($u['user']) && !isset($u['pass']) && !isset($u['port']) && !isset($u['fragment']) && preg_match('/^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}$/Di', $host) && !str_ends_with(strtolower($host), '.localhost')) $result['website'] = $website;
    }
    return $result;
}
function clinic_details(array $s): void {
    if (!verified_details($s)) return;
    foreach (['address'=>'Dirección', 'hours'=>'Horarios informados'] as $key=>$label) if ($text = clinic_text($s[$key] ?? null)) echo '<p>'.h($label).': '.h($text).'</p>';
    $services = $s['services'] ?? [];
    if (is_array($services) && array_is_list($services) && count($services) <= 20 && $services) {
        $valid = array_filter($services, fn($v)=>clinic_text($v, 100) !== null);
        if (count($valid) === count($services)) { echo '<h2>Servicios informados</h2><ul>'; foreach ($valid as $v) echo '<li>'.h($v).'</li>'; echo '</ul>'; }
    }
    echo '<p>Datos comprobados con el establecimiento: '.h($s['verified_on']).'. Confirmá disponibilidad directamente.</p>';
    if (config()['clinic_contact_enabled'] !== true) return;
    $labels = ['phone'=>'Llamar al establecimiento', 'whatsapp'=>'Abrir WhatsApp', 'website'=>'Visitar su sitio'];
    foreach (clinic_contacts($s) as $channel=>$destination) echo '<p><a class="button" rel="nofollow sponsored noreferrer" href="/contacto-clinica/'.h($s['slug']).'/'.h($channel).'/">'.h($labels[$channel]).'</a></p>';
    if (clinic_contacts($s)) echo '<p>Elegís contactar directamente a este establecimiento. No enviamos datos de salud ni reservamos turnos. Un clic no confirma una consulta.</p>';
}
function private_click_path(mixed $path): ?string {
    if (!is_string($path) || $path === '' || !preg_match('~^(?:[A-Za-z]:[/\\\\]|/)~', $path) || strtolower(pathinfo($path, PATHINFO_EXTENSION)) !== 'json') return null;
    $parent = realpath(dirname($path));
    if (!$parent || !is_dir($parent) || is_link($path) || is_link($path.'.lock')) return null;
    $normalized = strtolower(str_replace('\\', '/', $parent));
    $root = strtolower(str_replace('\\', '/', (string)realpath(MASCOTA_ROOT)));
    $public = dirname($root).'/public_html';
    foreach ([$root, $public, dirname($root)] as $forbidden) if ($normalized === $forbidden || str_starts_with($normalized, $forbidden.'/')) return null;
    if (preg_match('~/(public|public_html)(/|$)~i', $normalized)) return null;
    return $parent.DIRECTORY_SEPARATOR.basename($path);
}
function valid_click_store(array $data): bool {
    if (array_keys($data) !== ['version', 'months'] || $data['version'] !== 1 || !is_array($data['months'])) return false;
    foreach ($data['months'] as $month=>$partners) {
        if (!is_string($month) || !preg_match('/^[0-9]{4}-(0[1-9]|1[0-2])$/D', $month) || !is_array($partners)) return false;
        foreach ($partners as $slug=>$channels) {
            if ((!is_string($slug) && !is_int($slug)) || !preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/D', (string)$slug) || !is_array($channels)) return false;
            foreach ($channels as $channel=>$count) if (!in_array($channel, ['phone','whatsapp','website'], true) || !is_int($count) || $count < 0 || $count > 1000000000) return false;
        }
    }
    return true;
}
function record_clinic_click(string $slug, string $channel): void {
    if (config()['clinic_click_tracking_enabled'] !== true) return;
    $path = private_click_path(config()['clinic_clicks_path']); if (!$path) return;
    $lock = @fopen($path.'.lock', 'c'); if (!$lock) return;
    @chmod($path.'.lock', 0600); $temporary = false;
    try {
        if (!flock($lock, LOCK_EX)) return;
        $data = ['version'=>1, 'months'=>[]];
        if (is_file($path)) {
            if (filesize($path) > 2000000) return;
            $data = json_decode((string)file_get_contents($path), true, 32, JSON_THROW_ON_ERROR);
            if (!is_array($data) || !valid_click_store($data)) return;
        }
        $month = date('Y-m'); $current = $data['months'][$month][$slug][$channel] ?? 0;
        if (!is_int($current) || $current < 0 || $current >= 1000000000) return;
        $data['months'][$month][$slug][$channel] = $current + 1;
        $temporary = tempnam(dirname($path), '.clinic-clicks-'); if ($temporary === false) return;
        chmod($temporary, 0600); $json = json_encode($data, JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT | JSON_FORCE_OBJECT)."\n";
        if (file_put_contents($temporary, $json) !== strlen($json)) return;
        // Stable separate lock serializes atomic replacement, including on Windows.
        if (!rename($temporary, $path)) return;
        $temporary = false; chmod($path, 0600);
    } catch (Throwable $error) {
        // Contact remains available; never log visitor input.
    } finally {
        if ($temporary !== false && is_file($temporary)) unlink($temporary);
        flock($lock, LOCK_UN); fclose($lock);
    }
}
function clinic_contact(string $slug, string $channel, string $method): void {
    header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow'); header('Referrer-Policy: no-referrer');
    if (config()['clinic_contact_enabled'] === true) foreach (sponsors() as $s) {
        if ($s['slug'] !== $slug) continue;
        $contacts = clinic_contacts($s); if (!isset($contacts[$channel])) break;
        if ($method === 'GET') record_clinic_click($slug, $channel);
        header('Location: '.$contacts[$channel], true, 302); return;
    }
    not_found();
}
