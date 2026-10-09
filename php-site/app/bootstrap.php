<?php
declare(strict_types=1);

const MASCOTA_ROOT = __DIR__ . '/..';
const MASCOTA_RELEASE = 'php-seo-growth-20261009';
require_once __DIR__.'/interactive.php';
require_once __DIR__.'/editorial.php';
require_once __DIR__.'/commercial.php';
date_default_timezone_set('America/Asuncion');

function h(string|int $value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function nonce(): string { static $value; return $value ??= base64_encode(random_bytes(18)); }
function config(): array {
    static $value;
    if ($value !== null) return $value;
    $value = require MASCOTA_ROOT . '/config/site.example.php';
    $private = MASCOTA_ROOT . '/config/site.local.php';
    if (is_file($private)) $value = array_replace($value, require $private);
    if ($url = getenv('MASCOTA_SITE_URL')) $value['site_url'] = rtrim($url, '/');
    if ($env = getenv('MASCOTA_ENV')) $value['environment'] = $env;
    if ($email = getenv('MASCOTA_CONTACT_EMAIL')) $value['contact_email'] = $email;
    $value['site_url'] = rtrim((string)$value['site_url'], '/');
    if (!preg_match('~^https?://[a-zA-Z0-9.-]+(?::\d+)?$~D', $value['site_url'])) throw new RuntimeException('Invalid site URL');
    if ($value['contact_email'] && !filter_var($value['contact_email'], FILTER_VALIDATE_EMAIL)) $value['contact_email'] = '';
    return $value;
}
function content(): array {
    static $data;
    if ($data === null) $data = json_decode(file_get_contents(MASCOTA_ROOT.'/content/articles.json'), true, 512, JSON_THROW_ON_ERROR);
    return $data;
}
function sections(): array { return content()['sections']; }
function article_by_slug(string $slug): ?array {
    static $index;
    if ($index === null) { $index = []; foreach (content()['articles'] as $a) $index[$a['slug']] = $a; }
    return $index[$slug] ?? null;
}
function section_id(array $section, int $index): string {
    $id = $section['id'] ?? 'seccion-'.($index+1);
    return is_string($id) && preg_match('/^[a-z][a-z0-9-]*$/D', $id) ? $id : 'seccion-'.($index+1);
}
function article_crumbs(array $a): array {
    $items = [['name'=>sections()[$a['category']]['label'], 'path'=>'/'.$a['category'].'/']];
    $parents = []; $seen = [$a['slug']]; $parent = $a['parent'] ?? null;
    while (is_string($parent) && !in_array($parent, $seen, true) && count($seen)<8) {
        $p = article_by_slug($parent); if (!$p) break;
        array_unshift($parents, ['name'=>$p['short'], 'path'=>article_path($p)]);
        $seen[] = $parent; $parent = $p['parent'] ?? null;
    }
    return [...$items, ...$parents, ['name'=>$a['short'], 'canonical'=>article_path($a)]];
}
function guide_links(array $links): void {
    if (!$links) return;
    echo '<nav class="guide-links" aria-label="Guías relacionadas"><ul>';
    foreach ($links as $link) {
        if (!is_array($link) || !is_string($link['path'] ?? null) || !valid_internal_path($link['path'])) continue;
        echo '<li><a href="'.h($link['path']).'">'.h($link['label']).' '.icon('arrow').'</a></li>';
    }
    echo '</ul></nav>';
}
function article_path(array $a): string { return '/'.$a['category'].'/'.$a['slug'].'/'; }
function url(string $path = '/'): string { return config()['site_url'].$path; }
function source(array|string $id): array { return is_array($id) ? $id : content()['sources'][$id]; }
function normalized(string $value): string {
    return strtolower(strtr($value, ['á'=>'a','é'=>'e','í'=>'i','ó'=>'o','ú'=>'u','ü'=>'u','ñ'=>'n','Á'=>'a','É'=>'e','Í'=>'i','Ó'=>'o','Ú'=>'u','Ñ'=>'n']));
}
function is_preview(): bool {
    $host = strtolower((string)($_SERVER['HTTP_HOST'] ?? ''));
    return config()['environment'] !== 'production' || preg_match('/^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/D', $host) === 1;
}
function sponsors(): array {
    if (config()['sponsorship_enabled'] !== true) return [];
    $private = MASCOTA_ROOT.'/content/sponsors.local.json';
    $file = is_file($private) ? $private : MASCOTA_ROOT.'/content/sponsors.json';
    $rows = json_decode(file_get_contents($file), true, 512, JSON_THROW_ON_ERROR);
    if (!is_array($rows)) return [];
    $today = date('Y-m-d');
    return array_values(array_filter($rows, static function ($s) use ($today) {
        if (!is_array($s) || ($s['paid'] ?? false) !== true || ($s['approved'] ?? false) !== true) return false;
        foreach (['slug','name','city','description','starts','ends'] as $key) if (!is_string($s[$key] ?? null) || trim($s[$key]) === '') return false;
        if (!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/D', $s['slug'])) return false;
        foreach (['starts','ends'] as $key) {
            $d = DateTimeImmutable::createFromFormat('!Y-m-d', $s[$key]);
            if (!$d || $d->format('Y-m-d') !== $s[$key]) return false;
        }
        return $s['starts'] <= $today && $s['ends'] >= $today && $s['ends'] >= $s['starts'];
    }));
}
function icon(string $name, string $class = ''): string {
    $paths = [
        'paw'=>'<ellipse cx="7" cy="7" rx="2" ry="3"/><ellipse cx="17" cy="7" rx="2" ry="3"/><ellipse cx="3" cy="12" rx="2" ry="2.5"/><ellipse cx="21" cy="12" rx="2" ry="2.5"/><path d="M6 20c-3-2 0-7 3-9 2-2 4-2 6 0 3 2 6 7 3 9-2 1-4-1-6-1s-4 2-6 1Z"/>',
        'arrow'=>'<path d="M4 12h15m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8"/>',
        'search'=>'<circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m16 16 5 5" stroke="currentColor" stroke-width="1.8"/>',
        'dog'=>'<path d="M6 8 2 5v10l5 2m11-9 4-3v10l-5 2M7 5h10l2 6v8l-4 3H9l-4-3v-8Z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><path d="m10 16 2 2 2-2Z"/>',
        'cat'=>'<path d="M4 10V3l7 4h2l7-4v7l1 7-5 5H8l-5-5Z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="13" r="1"/><circle cx="16" cy="13" r="1"/><path d="m10 16 2 2 2-2M2 17l5 1m15-1-5 1" fill="none" stroke="currentColor" stroke-width="1.5"/>',
        'rabbit'=>'<path d="M8 12C2-3 10-3 11 11c0-14 8-14 6 1m-5 10c-12 0-10-12 0-12s12 12 0 12Z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="16" r="1"/><circle cx="16" cy="16" r="1"/>',
        'bird'=>'<path d="M4 20 6 8c0-7 10-7 12-2l4 4-4 1c0 8-6 10-10 6L4 20Zm3-7 6 2" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="7" r="1"/>',
        'fish'=>'<path d="M18 8c-5-8-13-3-16 4 3 7 11 12 16 4l4 4V4Z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="7" cy="11" r="1"/>',
        'small'=>'<circle cx="5" cy="5" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="19" cy="5" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4 13c0-11 16-11 16 0v4c-3 7-13 7-16 0Z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="13" r="1"/><circle cx="16" cy="13" r="1"/><path d="m10 17 2 2 2-2Z"/>',
        'turtle'=>'<ellipse cx="12" cy="13" rx="7" ry="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M9 8V5a3 3 0 0 1 6 0v3M6 9 3 7m15 2 3-2M6 17l-3 3m15-3 3 3M9 10h6v6H9Z" fill="none" stroke="currentColor" stroke-width="1.5"/>',
        'book'=>'<path d="M12 5C7 2 3 3 2 4v16c3-2 7-1 10 1 3-2 7-3 10-1V4c-1-1-5-2-10 1Zm0 0v16" fill="none" stroke="currentColor" stroke-width="1.5"/>',
    ];
    return '<svg class="icon '.h($class).'" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">'.($paths[$name] ?? $paths['paw']).'</svg>';
}
function article_card(array $a, bool $large = false): void {
    $c = sections()[$a['category']];
    echo '<article class="card '.($large?'card-large':'').'"><a class="card-link" href="'.h(article_path($a)).'"><div class="card-art '.h($c['color']).'">'.icon($a['icon'] ?? 'book').'<span>'.h($c['label']).'</span></div><div class="card-body"><span class="eyebrow">'.h($a['tag']).'</span><h3>'.h($a['card_title'] ?? $a['title']).'</h3><p>'.h($a['description']).'</p><span class="read-link">Leer la guía '.icon('arrow').'</span></div></a></article>';
}
function sponsored_block(): void {
    $rows = sponsors();
    if (!$rows) return;
    echo '<section class="sponsor-box"><span class="eyebrow">Publicidad · Espacios contratados</span><h2>Servicios para tu mascota</h2><div class="article-grid">';
    foreach ($rows as $s) echo '<article><h3><a href="/veterinarias/'.h($s['slug']).'/">'.h($s['name']).'</a></h3><p>'.h($s['city']).' · '.h($s['description']).'</p></article>';
    echo '</div></section>';
}
function page_start(string $title, string $description, string $path, array $schema = [], bool $noindex = false): void {
    $index = !$noindex && !is_preview();
    $graph = [
        ['@type'=>'Organization','@id'=>url('/').'#organization','name'=>'Mascota','url'=>url('/'),'logo'=>url('/assets/logo.svg')],
        ['@type'=>'WebSite','@id'=>url('/').'#website','name'=>'Mascota','url'=>url('/'),'inLanguage'=>'es-PY','publisher'=>['@id'=>url('/').'#organization']],
        ...$schema,
    ];
    $og=null; foreach(content()['articles'] as $a) if(article_path($a)===$path) { $og=article_og($a); break; }
    $seo = ['@context'=>'https://schema.org','@graph'=>$graph];
    ?>
<!doctype html><html lang="es-PY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title><?=h($title)?> | Mascota Paraguay</title><meta name="description" content="<?=h($description)?>"><meta name="robots" content="<?=$index?'index,follow,max-image-preview:large':'noindex,follow'?>"><link rel="canonical" href="<?=h(url($path))?>"><meta property="og:type" content="<?=isset($schema[0]['@type']) && $schema[0]['@type']==='Article'?'article':'website'?>"><meta property="og:title" content="<?=h($title)?>"><meta property="og:description" content="<?=h($description)?>"><meta property="og:url" content="<?=h(url($path))?>"><meta property="og:site_name" content="Mascota"><meta property="og:locale" content="es_PY"><meta property="og:image" content="<?=h(url($og['path'] ?? '/assets/social.png'))?>"><meta property="og:image:width" content="<?=$og['width'] ?? 1200?>"><meta property="og:image:height" content="<?=$og['height'] ?? 630?>"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/assets/logo.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css?v=<?=h(asset_cache_token('/assets/site.css'))?>"><script type="application/ld+json" nonce="<?=h(nonce())?>"><?=json_encode($seo,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT)?></script></head><body>
<a class="skip" href="#contenido">Saltar al contenido</a><header class="site-header"><div class="container header-row"><a class="brand" href="/" aria-label="Mascota, inicio"><?=icon('paw')?>mascota<span>.com.py</span></a><nav class="desktop-nav" aria-label="Principal"><?php foreach(sections() as $key=>$s):?><a <?=str_starts_with($path,'/'.$key.'/')?'aria-current="page"':''?> href="/<?=h($key)?>/"><?=h($s['label'])?></a><?php endforeach;?></nav><a class="search-toggle" href="/buscar/" aria-label="Buscar guías"><?=icon('search')?></a><details class="mobile-menu"><summary>Menú</summary><nav aria-label="Menú móvil"><?php foreach(sections() as $key=>$s):?><a href="/<?=h($key)?>/"><?=h($s['label'])?></a><?php endforeach;?></nav></details></div></header><main id="contenido">
<?php }
function page_end(): void {
    ?><section class="footer-note"><div class="container"><div><?=icon('paw')?><strong>Un compañero cambia tu vida.<br>Cuidarlo empieza por aprender.</strong></div><a href="/mascotas/" class="button button-outline">Conocé sus cuidados <?=icon('arrow')?></a></div></section></main><footer class="site-footer"><div class="container footer-grid"><div><a class="brand" href="/">mascota<span>.com.py</span></a><p>Guías para convivir mejor con los animales en Paraguay.</p></div><nav aria-label="Información editorial"><a href="/sobre-mascota/">Sobre Mascota</a><a href="/metodologia/">Fuentes y criterio editorial</a><a href="/privacidad/">Privacidad</a><a href="/publicidad/">Publicidad</a></nav><div><p>Información general con fuentes. Las decisiones sobre salud se consultan con un profesional veterinario.</p><small>© <?=date('Y')?> Mascota · Paraguay</small></div></div></footer></body></html><?php
}
function breadcrumb(array $items): array {
    echo '<nav class="breadcrumbs" aria-label="Ruta"><a href="/">Inicio</a>';
    $elements = [['@type'=>'ListItem','position'=>1,'name'=>'Inicio','item'=>url('/')]];
    foreach ($items as $i=>$item) {
        echo '<span aria-hidden="true">/</span>';
        echo isset($item['path'])?'<a href="'.h($item['path']).'">'.h($item['name']).'</a>':'<span>'.h($item['name']).'</span>';
        $elements[]=['@type'=>'ListItem','position'=>$i+2,'name'=>$item['name'],'item'=>url($item['path'] ?? $item['canonical'])];
    }
    echo '</nav>';
    return ['@type'=>'BreadcrumbList','itemListElement'=>$elements];
}
function home(): void {
    $home = content()['home'];
    page_start($home['title'], $home['description'], '/');
    ?><section class="hero container"><div class="hero-copy"><span class="eyebrow pill">HECHO PARA PARAGUAY</span><h1><?=h($home['h1'])?></h1><p>Conocé sus necesidades, prepará tu casa y aprendé a cuidarla. Guías claras para acompañarte todos los días.</p><form action="/buscar/" class="hero-search" role="search"><label class="sr-only" for="home-search">¿Qué querés aprender?</label><?=icon('search')?><input id="home-search" name="q" type="search" placeholder="Probá: gatos, calor, viajar…" maxlength="120"><button type="submit" aria-label="Buscar"><?=icon('arrow')?></button></form><div class="hero-tags"><span>Para empezar:</span><a href="/mascotas/perros/">Perros</a><a href="/mascotas/gatos/">Gatos</a><a href="/paraguay/viajar-con-mascotas/">Viajes</a></div></div><div class="hero-art"><img src="/assets/companions.svg" width="600" height="530" fetchpriority="high" alt="Ilustración de un perro y un gato descansando juntos"><span class="art-sticker"><?=icon('paw')?>Pequeñas patas.<br>Gran compañía.</span></div></section>
<section class="section container"><div class="section-heading"><div><span class="eyebrow">CADA ANIMAL, UN MUNDO</span><h2>¿Con quién compartís tu casa?</h2></div><a class="text-link" href="/mascotas/">Ver todas las guías <?=icon('arrow')?></a></div><div class="pet-grid"><?php foreach(content()['articles'] as $a) if($a['category']==='mascotas' && !isset($a['parent'])):?><a class="pet-tile" href="<?=h(article_path($a))?>"><?=icon($a['icon'])?><strong><?=h($a['short'])?></strong><span><?=h($a['teaser'])?></span></a><?php endif;?></div></section>
<section class="section container"><div class="section-heading"><div><span class="eyebrow">GUÍAS Y HERRAMIENTAS</span><h2>Encontrá lo que necesitás hoy</h2></div></div><?php guide_links([["path"=>"/mascotas/perros/razas/","label"=>"Razas de perros"],["path"=>"/productos/comida-para-perros/","label"=>"Comida para perros"],["path"=>"/cuidados/elegir-veterinaria/","label"=>"Elegir veterinaria"],["path"=>"/cuidados/vomitos-en-perros/","label"=>"Vómitos en perros"],["path"=>"/cuidados/calculadora-presupuesto-mascota/","label"=>"Calculadora de presupuesto"],["path"=>"/cuidados/planificador-cuidados/","label"=>"Planificador imprimible"]]);?></section>
<section class="section featured-section"><div class="container"><div class="section-heading"><div><span class="eyebrow">PARA CUIDARLOS MEJOR</span><h2>Las preguntas de todos los días</h2></div><a class="text-link" href="/cuidados/">Explorar cuidados <?=icon('arrow')?></a></div><div class="article-grid"><?php foreach(['elegir-mascota','mascotas-y-calor','presupuesto-mascota'] as $slug) foreach(content()['articles'] as $a) if($a['slug']===$slug) article_card($a);?></div></div></section>
<section class="section container local-section"><div><span class="eyebrow">VIVIR CON MASCOTAS ACÁ</span><h2>Paraguay tiene<br>sus propias preguntas.</h2><p>Qué documentos necesitás para viajar, dónde consultar las reglas y por qué la fauna silvestre pertenece a su hábitat.</p><a href="/paraguay/" class="button">Ver las guías locales <?=icon('arrow')?></a></div><div class="local-links"><?php foreach(content()['articles'] as $a) if($a['category']==='paraguay'):?><a href="<?=h(article_path($a))?>"><span><?=h($a['short'])?></span><?=icon('arrow')?></a><?php endif;?></div></section>
<section class="container section"><?php sponsored_block();?><div class="trust-strip"><div><?=icon('book')?><strong>Fuentes a la vista</strong><p>Referencias para comprobar y seguir aprendiendo.</p></div><div><?=icon('paw')?><strong>Bienestar primero</strong><p>Cuidados y decisiones responsables para cada animal.</p></div><div><?=icon('search')?><strong>Información con contexto</strong><p>Lo cotidiano, los trámites y la vida en Paraguay.</p></div></div></section><?php page_end();
}
function category_page(string $key): void {
    $s=sections()[$key]; $rows=array_values(array_filter(content()['articles'],fn($a)=>$a['category']===$key && !isset($a['parent'])));
    $schema=[['@type'=>'CollectionPage','name'=>$s['title'],'url'=>url('/'.$key.'/'),'inLanguage'=>'es-PY']];
    page_start($s['title'],$s['description'],'/'.$key.'/',$schema);
    echo '<div class="container">'; breadcrumb([['name'=>$s['label'],'canonical'=>'/'.$key.'/']]);
    echo '<header class="page-hero '.h($s['color']).'"><span class="eyebrow">'.h($s['label']).' · Paraguay</span><h1>'.h($s['h1'] ?? $s['title']).'</h1><p>'.h($s['description']).'</p></header><section class="section article-grid">';
    foreach($rows as $a) article_card($a);
    echo '</section>'; sponsored_block(); echo '</div>'; page_end();
}
function render_section(array $s, int $i): void {
    echo '<section id="'.h(section_id($s, $i)).'"><h2>'.h($s['title']).'</h2>';
    foreach($s['paragraphs'] ?? [] as $p) echo '<p>'.h($p).'</p>';
    render_inline_paragraphs($s['inline_paragraphs'] ?? []);
    if(isset($s['bullets'])) { echo '<ul>'; foreach($s['bullets'] as $p) echo '<li>'.h($p).'</li>'; echo '</ul>'; }
    if(isset($s['table'])) { echo '<div class="table-scroll"><table><thead><tr>'; foreach($s['table']['headers'] as $v) echo '<th scope="col">'.h($v).'</th>'; echo '</tr></thead><tbody>'; foreach($s['table']['rows'] as $row) {echo '<tr>'; foreach($row as $v) echo '<td>'.h($v).'</td>'; echo '</tr>';} echo '</tbody></table></div>'; }
    guide_links($s['links'] ?? []);
    if ($s['source_refs'] ?? []) {
        echo '<p class="section-citation">Referencia: ';
        foreach ($s['source_refs'] as $i=>$id) { $ref=source($id); if($i) echo ' · '; echo '<a href="'.h($ref['url']).'" target="_blank" rel="noopener noreferrer">'.h($ref['label']).'</a>'; }
        echo '</p>';
    }
    echo '</section>';
}
function article_page(array $a): void {
    $path=article_path($a); $c=sections()[$a['category']]; $h1=$a['h1'] ?? $a['title'];
    $items=article_crumbs($a);
    $elements=[['@type'=>'ListItem','position'=>1,'name'=>'Inicio','item'=>url('/')]];
    foreach ($items as $i=>$item) $elements[]=['@type'=>'ListItem','position'=>$i+2,'name'=>$item['name'],'item'=>url($item['path'] ?? $item['canonical'])];
    $published=$a['published'] ?? $a['date']; $modified=$a['modified'] ?? $a['date'];
    $type=($a['kind'] ?? '')==='collection'?'CollectionPage':'Article';
    $articleSchema=['@type'=>$type,'headline'=>$h1,'name'=>$h1,'description'=>$a['description'],'mainEntityOfPage'=>url($path),'url'=>url($path),'image'=>url('/assets/social.png'),'datePublished'=>$published,'dateModified'=>$modified,'author'=>['@type'=>'Organization','name'=>'Redacción Mascota','url'=>url('/sobre-mascota/')],'publisher'=>['@id'=>url('/').'#organization'],'inLanguage'=>'es-PY'];
    $articleSchema=array_replace($articleSchema,editorial_schema($a));
    if($og=article_og($a)) $articleSchema['image']=url($og['path']);
    $children=array_values(array_filter(content()['articles'],fn($child)=>($child['parent'] ?? null)===$a['slug']));
    if ($type==='CollectionPage') $articleSchema['hasPart']=array_map(fn($child)=>['@type'=>'Article','name'=>$child['title'],'url'=>url(article_path($child))],$children);
    page_start($a['seo_title'] ?? $a['title'],$a['description'],$path,[$articleSchema,['@type'=>'BreadcrumbList','itemListElement'=>$elements]]);
    echo '<div class="container">'; breadcrumb($items);
    echo '<header class="article-header"><span class="eyebrow">'.h($a['tag']).' · '.h($c['label']).'</span><h1>'.h($h1).'</h1><p class="dek">'.h($a['description']).'</p><div class="byline">Redacción Mascota <span>·</span> Publicado el '.h(date('d/m/Y',strtotime($published))).' <span>·</span> Actualizado el '.h(date('d/m/Y',strtotime($modified))).'</div></header><div class="article-layout"><aside class="toc"><strong>En esta guía</strong><ol>';
    if(species_hub_groups($a)) echo '<li><a href="#por-tema">Guías por tema</a></li>';
    foreach($a['sections'] as $i=>$s) echo '<li><a href="#'.h(section_id($s,$i)).'">'.h($s['title']).'</a></li>';
    if(isset($a['tool'])) echo '<li><a href="#herramienta">Usar la herramienta</a></li>';
    if($children) echo '<li><a href="#explorar">Explorar las guías</a></li>';
    echo '</ol><a href="#fuentes">Fuentes consultadas</a></aside><article class="prose"><div class="quick-answer"><strong>Para empezar</strong><p>'.h($a['answer']).'</p></div><p>'.h($a['intro']).'</p>';
    render_editorial_status($a);
    render_article_image($a);
    if(isset($a['tool'])) render_pet_tool($a['tool']);
    foreach($a['sections'] as $i=>$s) render_section($s,$i);
    if($a['faqs'] ?? []) { echo '<section class="faq"><h2>Preguntas frecuentes</h2>'; foreach($a['faqs'] as $f) echo '<details><summary>'.h($f['q']).'</summary><p>'.h($f['a']).'</p></details>'; echo '</section>'; }
    echo '<section id="fuentes" class="sources"><h2>Fuentes consultadas</h2><ul>';
    foreach($a['sources'] as $id) {$s=source($id); echo '<li><a href="'.h($s['url']).'" target="_blank" rel="noopener noreferrer">'.h($s['label']).' ↗</a></li>';}
    $consulted=$a['sources_checked'] ?? $a['date'];
    echo '</ul><p>Consulta de fuentes: '.h(date('d/m/Y',strtotime($consulted))).'. '.h($a['scope'] ?? 'Orientación general para organizar cuidados. No reemplaza una evaluación veterinaria individual.').'</p><a href="/metodologia/">Cómo preparamos nuestras guías</a></section></article></div>';
    render_species_hub($a);
    perro_reference($a);
    if($children) {echo '<section id="explorar" class="section"><div class="section-heading"><h2>Explorá las guías</h2></div><div class="article-grid">';foreach($children as $child) article_card($child);echo '</div></section>';}
    echo '<section class="section"><div class="section-heading"><h2>Seguí aprendiendo</h2></div>';
    guide_links($a['guide_links'] ?? []);
    echo '<div class="article-grid">';
    foreach($a['related'] as $slug) if($r=article_by_slug($slug)) article_card($r);
    echo '</div></section>'; sponsored_block(); echo '</div>'; page_end();
}
function search_page(): void {
    $q=isset($_GET['q']) && is_string($_GET['q'])?trim($_GET['q']):'';
    $q=function_exists('mb_substr')?mb_substr($q,0,120):substr($q,0,120);
    $rows=search_guides($q);
    page_start('Buscar guías de mascotas','Buscá información sobre tipos de mascotas, cuidados, Paraguay y equipamiento.','/buscar/',[],true);
    echo '<section class="container section search-page"><span class="eyebrow">Encontrá tu próxima lectura</span><h1>¿Qué querés aprender?</h1><form action="/buscar/" class="hero-search" role="search"><label class="sr-only" for="search-query">Buscar guías</label>'.icon('search').'<input id="search-query" type="search" name="q" maxlength="120" value="'.h($q).'" placeholder="Gatos, viajes, cuidados…"><button type="submit">Buscar</button></form>';
    if($q!=='') echo '<p class="search-count">'.count($rows).' '.(count($rows)===1?'guía':'guías').' para “'.h($q).'”.</p>';
    if($rows) {echo '<div class="article-grid">';foreach($rows as $a) article_card($a);echo '</div>';} elseif($q!=='') echo '<div class="empty"><h2>Probá con otra palabra</h2><p>Buscá el tipo de mascota o un tema, como “calor”, “viajar” o “presupuesto”.</p><a href="/mascotas/">Explorar las guías por mascota</a></div>';
    echo '</section>';page_end();
}
function info_page(string $key): void {
    $pages=content()['pages']; $p=$pages[$key];
    page_start($p['title'],$p['description'],'/'.$key.'/');
    echo '<div class="container">';breadcrumb([['name'=>$p['title'],'canonical'=>'/'.$key.'/']]);
    echo '<header class="article-header"><span class="eyebrow">Mascota · Información editorial</span><h1>'.h($p['title']).'</h1><p class="dek">'.h($p['description']).'</p></header><article class="prose info-prose">';
    foreach($p['sections'] as $i=>$s) render_section($s,$i);
    if(config()['contact_email']) echo '<p>Para consultas editoriales: <a href="mailto:'.h(config()['contact_email']).'">'.h(config()['contact_email']).'</a>.</p>';
    echo '</article></div>';page_end();
}
function sponsor_page(array $s): void {
    $path='/veterinarias/'.$s['slug'].'/';
    page_start($s['name'].' en '.$s['city'],$s['description'],$path);
    echo '<div class="container"><header class="article-header"><span class="eyebrow">Publicidad · Ficha contratada</span><h1>'.h($s['name']).'</h1><p class="dek">'.h($s['city']).' · '.h($s['description']).'</p></header><article class="prose info-prose"><h2>Información del establecimiento</h2><p>'.h($s['details'] ?? $s['description']).'</p>';
    clinic_details($s);
    echo '<p>Confirmá directamente los servicios, horarios, disponibilidad y precios. La contratación de este espacio no constituye una recomendación clínica.</p><a href="/publicidad/">Nuestra política de publicidad</a></article></div>';page_end();
}
function not_found(): void {
    http_response_code(404);
    page_start('No encontramos esta página','Explorá nuestras guías de mascotas en Paraguay.','/',[],true);
    echo '<section class="container section empty"><span class="eyebrow">404</span><h1>Esta huella no lleva a una página.</h1><p>Podés volver al inicio o buscar una guía.</p><a class="button" href="/">Volver al inicio '.icon('arrow').'</a></section>';page_end();
}
function public_paths(): array {
    $paths=['/'];foreach(sections() as $key=>$s) $paths[]='/'.$key.'/';
    foreach(content()['articles'] as $a) $paths[]=article_path($a);
    foreach(array_keys(content()['pages']) as $p) $paths[]='/'.$p.'/';
    foreach(sponsors() as $s) $paths[]='/veterinarias/'.$s['slug'].'/';
    return $paths;
}
function sitemap(): void {
    header('Content-Type: application/xml; charset=UTF-8');
    echo '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
    $dates=[];
    foreach(content()['articles'] as $a) $dates[article_path($a)]=$a['modified'] ?? $a['date'];
    $dates['/']=content()['home']['modified'];
    foreach(sections() as $key=>$section) $dates['/'.$key.'/']=$section['modified'];
    foreach(content()['pages'] as $key=>$page) $dates['/'.$key.'/']=$page['modified'];
    foreach(public_paths() as $path) {
        echo '<url><loc>'.h(url($path)).'</loc>';
        if(isset($dates[$path])) echo '<lastmod>'.h($dates[$path]).'</lastmod>';
        echo '</url>';
    }
    echo '</urlset>';
}
function release_version(): string {
    $file=public_asset_root().'/release.json';
    if(is_file($file)) { $r=json_decode(file_get_contents($file),true); $v=$r['version']??''; if(is_string($v)&&preg_match('/^[a-zA-Z0-9._-]{1,80}$/D',$v)) return $v; }
    return MASCOTA_RELEASE;
}
function canonical_request_path(string $path): ?string {
    if ($path === '/index.php') return '/';
    $known = array_merge(public_paths(), ['/buscar/', '/robots.txt', '/sitemap.xml']);
    if (in_array($path, $known, true)) return $path;
    if ($path !== '/' && !str_ends_with($path, '/') && in_array($path.'/', $known, true)) return $path.'/';
    return null;
}
function mascota_run(): void {
    header('X-Content-Type-Options: nosniff');header('Referrer-Policy: strict-origin-when-cross-origin');header('X-Frame-Options: DENY');
    header("Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-".nonce()."'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'");
    header('Permissions-Policy: camera=(), microphone=(), geolocation=()');header('X-Mascota-Release: '.release_version());
    if(is_preview()) header('X-Robots-Tag: noindex, nofollow');
    $method=$_SERVER['REQUEST_METHOD'] ?? 'GET';
    if(!in_array($method,['GET','HEAD'],true)) {http_response_code(405);header('Allow: GET, HEAD');header('Content-Type: text/plain; charset=UTF-8');echo 'Método no permitido.';return;}
    header('Content-Type: text/html; charset=UTF-8');
    header('Cache-Control: public, max-age=300');
    if($method==='HEAD') ob_start();
    // REQUEST_URI is an origin-form path; parse_url would treat // as an authority.
    $raw=explode('?', (string)($_SERVER['REQUEST_URI'] ?? '/'), 2)[0];
    $path=rawurldecode($raw);
    $canonical = canonical_request_path($path);
    if ($canonical !== null && $raw !== $canonical) {
        $query = (string)($_SERVER['QUERY_STRING'] ?? '');
        header('Location: '.$canonical.($query !== '' ? '?'.$query : ''), true, 301);
    }
    elseif($path==='/robots.txt') {header('Content-Type: text/plain; charset=UTF-8');echo is_preview()?"User-agent: *\nDisallow: /\n":"User-agent: *\nDisallow: /contacto-clinica/\nSitemap: ".url('/sitemap.xml')."\n";}
    elseif($path==='/sitemap.xml') sitemap();
    elseif(preg_match('~^/contacto-clinica/([a-z0-9]+(?:-[a-z0-9]+)*)/(phone|whatsapp|website)/$~D', $path, $contact)) clinic_contact($contact[1], $contact[2], $method);
    elseif($path==='/') home();
    elseif($path==='/buscar/') search_page();
    else {
        $matched=false;
        foreach(sections() as $key=>$s) if($path==='/'.$key.'/') {category_page($key);$matched=true;break;}
        if(!$matched) foreach(content()['articles'] as $a) if($path===article_path($a)) {article_page($a);$matched=true;break;}
        if(!$matched) foreach(array_keys(content()['pages']) as $key) if($path==='/'.$key.'/') {info_page($key);$matched=true;break;}
        if(!$matched) foreach(sponsors() as $s) if($path==='/veterinarias/'.$s['slug'].'/') {sponsor_page($s);$matched=true;break;}
        if(!$matched) not_found();
    }
    if($method==='HEAD') ob_end_clean();
}
