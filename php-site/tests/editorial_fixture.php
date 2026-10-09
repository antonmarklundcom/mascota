<?php
declare(strict_types=1);
require $argv[1].'/app/bootstrap.php';
$checks=0;
function verify_fixture(bool $condition,string $label): void {
    global $checks; if(!$condition) throw new RuntimeException($label); $checks++;
}
$article=content()['articles'][0]; $path=article_path($article);
$anchor=section_id($article['sections'][0],0);
verify_fixture(valid_internal_path($path.'#'.$anchor),'existing typed fragment');
foreach(['javascript:alert(1)','//example.test/path','/missing/',$path.'#unknown',$path.'%23'.$anchor,'/#unknown','/../config/site.local.php'] as $unsafe)
    verify_fixture(!valid_internal_path($unsafe),'invalid destination '.$unsafe);
ob_start();
render_inline_paragraphs([[['text'=>'<img src=x onerror=alert(1)>','path'=>'javascript:alert(1)'],['text'=>'<safe link>','path'=>$path.'#'.$anchor],['text'=>'protocol relative','path'=>'//example.test']]]);
$html=ob_get_clean();
verify_fixture(!str_contains($html,'<img')&&!str_contains($html,'javascript:')&&!str_contains($html,'href="//'),'unsafe segments degrade to escaped text');
verify_fixture(str_contains($html,'&lt;img')&&str_contains($html,'href="'.$path.'#'.$anchor.'"')&&str_contains($html,'&lt;safe link&gt;'),'valid link with escaped label');
verify_fixture(inline_plain_text([['text'=>'one '],['text'=>'two','path'=>$path]])==='one two','inline searchable plain text');
verify_fixture(count(search_guides('fixtureuniquetoken'))===1,'inline prose included in search');
$review=['reviewer'=>'fixture','date'=>$article['modified']??$article['date'],'scope'=>'Synthetic editorial test only'];
$article['editor']='fixture'; $article['review']=$review;
verify_fixture(verified_editorial_member('fixture')!==null,'verified named editor fixture');
verify_fixture(valid_editorial_review($article)!==null,'valid actual dated scoped review fixture');
$schema=editorial_schema($article);
verify_fixture(isset($schema['editor'],$schema['reviewedBy'],$schema['lastReviewed']),'verified person schema');
verify_fixture($schema['author']['@type']==='Organization','institutional author retained');
foreach([
    ['reviewer'=>'fixture','date'=>'2020-01-01','scope'=>'Stale synthetic review'],
    ['reviewer'=>'missing','date'=>'2020-01-01','scope'=>'Fixture'],
    ['reviewer'=>'unverified','date'=>'2020-01-01','scope'=>'Fixture'],
    ['reviewer'=>'incomplete','date'=>'2020-01-01','scope'=>'Fixture'],
    ['reviewer'=>'fixture','date'=>'2099-01-01','scope'=>'Fixture'],
    ['reviewer'=>'fixture','date'=>'2026-02-30','scope'=>'Fixture'],
    ['reviewer'=>'fixture','date'=>'2020-01-01','scope'=>''],
    ['reviewer'=>'fixture','scope'=>'Date absent'],
] as $invalid) {
    $article['review']=$invalid;
    verify_fixture(valid_editorial_review($article)===null,'incomplete, future or unsupported review withheld');
    verify_fixture(!isset(editorial_schema($article)['reviewedBy']),'invalid review absent from schema');
}
unset($article['review']);$article['editor']='unverified';
verify_fixture(!isset(editorial_schema($article)['editor']),'unverified editor absent from schema');
ob_start();render_editorial_status($article);$status=ob_get_clean();
verify_fixture(str_contains($status,'no declara una revisión veterinaria individual'),'truthful review fallback');
verify_fixture(!empty($article['sources']),'source citations remain independent of review status');
$article['review_class']='clinical'; $article['review']=$review;
verify_fixture(editorial_maintenance_row($article)['clinical_review_pending'],'generic editorial review is not clinical review');
$article['review']['kind']='clinical';
verify_fixture(editorial_maintenance_row($article)['clinical_review_pending'],'clinical kind needs verified professional eligibility');
$article['review']['reviewer']='professional-nonstrict';
verify_fixture(editorial_maintenance_row($article)['clinical_review_pending'],'professional eligibility requires strict boolean verification');
$article['review']['reviewer']='professional';
verify_fixture(!editorial_maintenance_row($article)['clinical_review_pending'],'eligible dated scoped clinical fixture closes clinical queue');
$article['review']['kind']='editorial';
verify_fixture(editorial_maintenance_row($article)['clinical_review_pending'],'professional generic review still leaves clinical review pending');
$article['review']['kind']='clinical';$article['review']['date']='2020-01-01';
$row=editorial_maintenance_row($article);
verify_fixture($row['review']==='stale'&&$row['review_metadata_needs_attention']&&$row['clinical_review_pending'],'stale professional review reopens queue');
unset($article['review'],$article['sources_checked']);
$row=editorial_maintenance_row($article);
verify_fixture($row['source_check_status']==='missing'&&$row['source_check_needs_attention']&&$row['source_review_due']===null,'missing source check has no invented due date');
foreach(['2026-02-30','2099-01-01','2026-1-01','',17] as $invalidDate) {
    $article['sources_checked']=$invalidDate;$row=editorial_maintenance_row($article);
    verify_fixture($row['source_check_status']==='invalid'&&$row['source_check_needs_attention']&&$row['source_review_due']===null,'invalid or future source check flagged');
}
$article['sources_checked']='2020-01-01';
foreach(['clinical'=>[90,'2020-03-31'],'legal'=>[90,'2020-03-31'],'general'=>[180,'2020-06-29']] as $class=>[$interval,$due]) {
    $article['review_class']=$class;$row=editorial_maintenance_row($article);
    verify_fixture($row['source_check_status']==='valid'&&!$row['source_check_needs_attention'],'valid source check accepted '.$class);
    verify_fixture($row['source_review_class']===$class&&$row['source_review_interval_days']===$interval&&$row['source_review_due']===$due&&$row['source_review_due_now'],'appropriate overdue source queue '.$class);
}
$article['sources_checked']=date('Y-m-d');$row=editorial_maintenance_row($article);
verify_fixture(!$row['source_review_due_now'],'fresh valid source check is not overdue');
unset($article['review_class']);$article['topic']='salud';
verify_fixture(editorial_maintenance_row($article)['source_review_class']==='clinical','health defaults to clinical source queue');
$article['topic']='general';$article['category']='paraguay';
verify_fixture(editorial_maintenance_row($article)['source_review_class']==='legal','Paraguay administration defaults to legal source queue');
echo json_encode(['status'=>'PASS','checks'=>$checks]);
