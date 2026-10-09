<?php
declare(strict_types=1);
function inline_plain_text(array $paragraph): string {
    return implode('',array_map(static fn($s)=>is_array($s)&&is_string($s['text']??null)?$s['text']:'',$paragraph));
}
function valid_internal_path(string $path): bool {
    if (!preg_match('~^(/[a-z0-9/-]*)(?:#([a-z][a-z0-9-]*))?$~D',$path,$m)) return false;
    $base=$m[1]; if (!in_array($base,public_paths(),true)) return false;
    if (!isset($m[2])) return true;
    foreach(content()['articles'] as $a) if(article_path($a)===$base) {
        $anchors=['fuentes']; if(isset($a['tool'])) $anchors[]='herramienta';
        foreach($a['sections'] as $i=>$s) $anchors[]=section_id($s,$i);
        foreach(content()['articles'] as $child) if(($child['parent']??null)===$a['slug']) $anchors[]='explorar';
        if($groups=species_hub_groups($a)) { $anchors[]='por-tema'; foreach(array_keys($groups) as $topic) $anchors[]='tema-'.$topic; }
        return in_array($m[2],$anchors,true);
    }
    foreach(content()['pages'] as $key=>$p) if('/'.$key.'/'===$base) foreach($p['sections'] as $i=>$s) if(section_id($s,$i)===$m[2]) return true;
    return false;
}
function render_inline_paragraphs(array $paragraphs): void {
    foreach($paragraphs as $p) { if(!is_array($p)) continue; echo '<p>'; foreach($p as $s) {
        if(!is_array($s)||!is_string($s['text']??null)) continue;
        $text=h($s['text']); $path=$s['path']??null;
        echo is_string($path)&&valid_internal_path($path)?'<a class="context-link" href="'.h($path).'">'.$text.'</a>':$text;
    } echo '</p>'; }
}
function registered_assets(): array {
    static $assets; if($assets===null) { $file=MASCOTA_ROOT.'/content/assets.json'; $assets=is_file($file)?(json_decode(file_get_contents($file),true)['assets']??[]):[]; } return $assets;
}
function public_asset_root(): string {
    $root=realpath(MASCOTA_ROOT);
    return is_dir($root.'/public')?$root.'/public':dirname($root).'/public_html';
}
function safe_asset_path(string $path): bool {
    return preg_match('~^/assets/(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_.-]+\.(?:svg|png|webp|jpg|jpeg)$~D',$path)===1 && is_file(public_asset_root().$path);
}
function asset_by_key(?string $key): ?array {
    $a=registered_assets()[$key??'']??null;
    if(!is_array($a)||!is_string($a['path']??null)||!safe_asset_path($a['path'])) return null;
    foreach(['alt','creator','license','source'] as $k) if(!is_string($a[$k]??null)||trim($a[$k])==='') return null;
    if(!is_int($a['width']??null)||!is_int($a['height']??null)||$a['width']<1||$a['height']<1) return null;
    return $a;
}
function article_og(array $a): ?array { return asset_by_key($a['og_image']??'og-'.str_replace('/','-',$a['slug'])); }
function render_article_image(array $a): void {
    $img=asset_by_key($a['image']??null); if(!$img) return;
    $srcset=[]; foreach($img['variants']??[] as $v) if(is_array($v)&&is_string($v['path']??null)&&safe_asset_path($v['path'])&&is_int($v['width']??null)&&$v['width']>0) $srcset[]=$v['path'].' '.$v['width'].'w';
    echo '<figure class="article-figure"><img src="'.h($img['path']).'" width="'.$img['width'].'" height="'.$img['height'].'" alt="'.h($img['alt']).'" loading="eager" fetchpriority="high" decoding="async"'.($srcset?' srcset="'.h(implode(', ',$srcset)).'" sizes="(max-width: 760px) calc(100vw - 36px), 740px"':'').'>';
    echo '<figcaption>'.h($img['caption']??$img['alt']).' <span>Crédito: '.h($img['creator']).' · '.h($img['license']).'</span></figcaption></figure>';
}
function editorial_members(): array { $f=MASCOTA_ROOT.'/content/editorial-team.json'; return is_file($f)?(json_decode(file_get_contents($f),true)['members']??[]):[]; }
function verified_editorial_member(mixed $id): ?array {
    if(!is_string($id)) return null; $m=editorial_members()[$id]??null;
    if(!is_array($m)||($m['verified']??false)!==true) return null;
    foreach(['name','role','profile'] as $k) if(!is_string($m[$k]??null)||trim($m[$k])==='') return null;
    $p=$m['profile']; if(!valid_internal_path($p)&&!(filter_var($p,FILTER_VALIDATE_URL)&&parse_url($p,PHP_URL_SCHEME)==='https')) return null;
    return $m;
}
function valid_editorial_review(array $a): ?array {
    $r=$a['review']??null; if(!is_array($r)||!($m=verified_editorial_member($r['reviewer']??null))) return null;
    $date=$r['date']??''; $d=is_string($date)?DateTimeImmutable::createFromFormat('!Y-m-d',$date):false;
    if(!$d||$d->format('Y-m-d')!==$date||$date>date('Y-m-d')||!is_string($r['scope']??null)||trim($r['scope'])==='') return null;
    $modified=$a['modified']??$a['date']??null;
    if(valid_editorial_date($modified)&&$date<$modified) return null;
    return [...$r,'member'=>$m];
}
function editorial_schema(array $a): array {
    $s=['author'=>['@type'=>'Organization','name'=>'Redacción Mascota','url'=>url('/sobre-mascota/')]];
    if($m=verified_editorial_member($a['editor']??null)) $s['editor']=['@type'=>'Person','name'=>$m['name'],'jobTitle'=>$m['role'],'url'=>str_starts_with($m['profile'],'/')?url($m['profile']):$m['profile']];
    if($r=valid_editorial_review($a)) { $m=$r['member']; $s['reviewedBy']=['@type'=>'Person','name'=>$m['name'],'jobTitle'=>$m['role'],'url'=>str_starts_with($m['profile'],'/')?url($m['profile']):$m['profile']]; $s['lastReviewed']=$r['date']; }
    return $s;
}
function render_editorial_status(array $a): void {
    if($m=verified_editorial_member($a['editor']??null)) echo '<p class="editorial-status">Edición: <a href="'.h($m['profile']).'">'.h($m['name']).'</a> · '.h($m['role']).'</p>';
    if($r=valid_editorial_review($a)) { $m=$r['member']; echo '<p class="editorial-status">Revisión: <a href="'.h($m['profile']).'">'.h($m['name']).'</a> · '.h($m['role']).' · '.h($r['date']).'. Alcance: '.h($r['scope']).'</p>'; }
    else echo '<p class="editorial-status">Autoría institucional: Redacción Mascota. Esta guía no declara una revisión veterinaria individual. Las fuentes consultadas se detallan al final.</p>';
}
function species_hub_groups(array $hub): array {
    if($hub['category']!=='mascotas'||isset($hub['parent'])||str_contains($hub['slug'],'/')) return [];
    $topics=['razas'=>'Razas y elección','alimentacion'=>'Alimentación','salud'=>'Salud y consulta veterinaria','preparacion'=>'Preparar la llegada','herramientas'=>'Herramientas para organizarte','convivencia'=>'Convivencia y cuidados cotidianos']; $groups=[];
    foreach($topics as $topic=>$label) { $rows=[]; foreach(content()['articles'] as $a) if($a['slug']!==$hub['slug']&&in_array($hub['slug'],$a['species']??[],true)&&($a['topic']??null)===$topic) $rows[]=$a; if($rows) $groups[$topic]=['label'=>$label,'articles'=>$rows]; }
    return $groups;
}
function render_species_hub(array $a): void {
    $groups=species_hub_groups($a); if(!$groups) return;
    echo '<section id="por-tema" class="species-hub section"><h2>Guías de '.h($a['short']).' por tema</h2><nav aria-label="Temas de '.h($a['short']).'" class="hub-nav">';
    foreach($groups as $topic=>$g) echo '<a href="#tema-'.h($topic).'">'.h($g['label']).'</a>';
    echo '</nav>'; foreach($groups as $topic=>$g) { echo '<section id="tema-'.h($topic).'"><h3>'.h($g['label']).'</h3><div class="article-grid">'; foreach($g['articles'] as $row) article_card($row); echo '</div></section>'; } echo '</section>';
}
function valid_editorial_date(mixed $value): bool {
    if(!is_string($value)) return false;
    $d=DateTimeImmutable::createFromFormat('!Y-m-d',$value);
    return $d!==false && $d->format('Y-m-d')===$value && $value<=date('Y-m-d');
}
function editorial_review_class(array $a): string {
    if(in_array($a['review_class']??null,['clinical','legal','general'],true)) return $a['review_class'];
    if(($a['topic']??null)==='salud'||in_array($a['slug'],['pipetas-para-perros','vacunas-perros','vacunas-gatos'],true)) return 'clinical';
    // Conservative administrative/legal queue; this does not classify reader advice or invent professional review.
    if($a['category']==='paraguay') return 'legal';
    return 'general';
}
function actual_clinical_review(array $a): bool {
    $review=valid_editorial_review($a);
    return $review!==null && ($review['kind']??null)==='clinical' && ($review['member']['professional_review']??false)===true;
}
function editorial_maintenance_row(array $a): array {
    $checked=$a['sources_checked']??null; $valid=valid_editorial_date($checked); $class=editorial_review_class($a);
    $interval=in_array($class,['clinical','legal'],true)?90:180;
    $due=$valid?(new DateTimeImmutable($checked))->modify('+'.$interval.' days')->format('Y-m-d'):null;
    $modified=$a['modified']??$a['date']??null; $r=$a['review']??null;
    $stale=is_array($r)&&valid_editorial_date($r['date']??null)&&valid_editorial_date($modified)&&$r['date']<$modified;
    return ['path'=>article_path($a),'source_check'=>$checked,'source_check_status'=>$checked===null?'missing':($valid?'valid':'invalid'),
        'source_check_needs_attention'=>!$valid,'source_review_class'=>$class,'source_review_interval_days'=>$interval,'source_review_due'=>$due,
        'source_review_due_now'=>$due!==null&&$due<=date('Y-m-d'),'modified'=>$modified,
        'editor'=>verified_editorial_member($a['editor']??null)?'verified':'institutional',
        'review'=>valid_editorial_review($a)?'verified-scoped':($stale?'stale':'not-declared'),
        'review_metadata_needs_attention'=>isset($a['review'])&&!valid_editorial_review($a),
        'clinical_review_pending'=>$class==='clinical'&&!actual_clinical_review($a)];
}
function editorial_maintenance_report(): array {
    return array_map('editorial_maintenance_row',content()['articles']);
}
function asset_cache_token(string $path): string {
    return in_array($path,['/assets/tools.js','/assets/site.css'],true)&&is_file(public_asset_root().$path)?substr(hash_file('sha256',public_asset_root().$path),0,16):'missing';
}

if(PHP_SAPI==='cli'&&isset($_SERVER['SCRIPT_FILENAME'])&&realpath($_SERVER['SCRIPT_FILENAME'])===__FILE__) { require_once __DIR__.'/bootstrap.php'; echo json_encode(editorial_maintenance_report(),JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).PHP_EOL; }
