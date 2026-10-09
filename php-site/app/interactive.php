<?php
declare(strict_types=1);

function search_tokens(string $text): array {
    $aliases=['perros'=>'perro','perras'=>'perro','perra'=>'perro','gatos'=>'gato','gatas'=>'gato','gata'=>'gato',
        'vomitos'=>'vomito','vomita'=>'vomito','vomitar'=>'vomito','vomitando'=>'vomito',
        'alimentos'=>'alimento','comida'=>'alimento','comidas'=>'alimento','racion'=>'alimento',
        'hamsters'=>'hamster','cachorros'=>'cachorro','veterinarias'=>'veterinaria','veterinario'=>'veterinaria',
        'veterinarios'=>'veterinaria','razas'=>'raza','cuidados'=>'cuidado'];
    $stop=['a','al','con','como','de','del','el','en','es','la','las','lo','los','mi','mis','para','por','que','se','su','sus','tu','tus','un','una','y'];
    $tokens=preg_split('/[^a-z0-9]+/',normalized($text),-1,PREG_SPLIT_NO_EMPTY);
    return array_values(array_unique(array_map(fn($t)=>$aliases[$t] ?? $t,array_filter($tokens,fn($t)=>!in_array($t,$stop,true)))));
}
function search_strings(mixed $value): string {
    if (is_string($value)) return $value;
    if (!is_array($value)) return '';
    return implode(' ',array_map('search_strings',$value));
}
function search_guides(string $query): array {
    $tokens=search_tokens($query); if (!$tokens) return [];
    $matches=[];
    foreach (content()['articles'] as $article) {
        $title=search_tokens($article['title'].' '.($article['h1'] ?? '').' '.$article['short']);
        $description=search_tokens($article['description']);
        $sections=array_map(fn($s)=>[$s['title'],$s['paragraphs'] ?? [],$s['bullets'] ?? [],$s['table'] ?? [],array_column($s['links'] ?? [],'label')],$article['sections']);
        $body=search_tokens(search_strings([$article['answer'],$article['intro'],$sections,$article['faqs']]));
        $all=array_unique([...$title,...$description,...$body]);
        if (array_diff($tokens,$all)) continue;
        $score=0;
        foreach ($tokens as $token) $score+=in_array($token,$title,true)?12:(in_array($token,$description,true)?5:1);
        $matches[]=['article'=>$article,'score'=>$score];
    }
    usort($matches,fn($a,$b)=>($b['score']<=>$a['score']) ?: strcmp($a['article']['title'],$b['article']['title']));
    return array_column($matches,'article');
}
function perro_reference(array $article): void {
    if ((config()['perro_links_enabled'] ?? false)!==true) return;
    $links=[
        'perros'=>['/perros','Conocé perros en adopción en Perro'],
        'primer-perro'=>['/requisitos-para-adoptar','Revisá los requisitos para adoptar en Perro'],
        'perros/razas'=>['/elegir-perro','Cómo elegir un perro para adoptar'],
        'perros/razas/labrador'=>['/perros-de-raza-en-adopcion','Qué comprobar al buscar perros de raza en adopción'],
        'perros/razas/golden-retriever'=>['/perros-de-raza-en-adopcion','Qué comprobar al buscar perros de raza en adopción'],
        'comida-para-perros'=>['/hogar-temporal','Cómo acordar los gastos de un hogar temporal'],
        'calculadora-presupuesto-mascota'=>['/primeros-dias-perro-adoptado','Planificá los primeros días de un perro adoptado'],
    ];
    if (!isset($links[$article['slug']])) return;
    [$path,$label]=$links[$article['slug']];
    echo '<aside class="portfolio-reference"><h2>Si estás pensando en adoptar</h2><p><a href="https://perro.com.py'.h($path).'">'.h($label).' '.icon('arrow').'</a></p><p class="small-note">Mascota y Perro comparten propietario. Perro se dedica a la adopción y los avisos de perros; consultá allí la disponibilidad real.</p></aside>';
}
function render_pet_tool(string $kind): void {
    if (!in_array($kind,['budget','planner'],true)) return;
    echo '<section id="herramienta" class="pet-tool" data-tool="'.h($kind).'">';
    if ($kind==='budget') {
        echo '<h2>Calculá con tus propios importes</h2><p>Ingresá guaraníes enteros, sin puntos ni comas. Dejá en blanco lo que todavía no conocés: la suma será parcial. Un cero indica que verificaste que ese rubro no tiene gasto.</p><noscript><p>Para actualizar las sumas activá JavaScript, o usá las fórmulas explicadas debajo. Podés imprimir la guía.</p></noscript><form class="tool-form" autocomplete="off"><div class="tool-grid">';
        $fields=[['food','Alimento por mes','monthly'],['hygiene','Higiene y consumibles por mes','monthly'],['services','Cuidados, traslados y servicios por mes','monthly'],['other','Otros gastos por mes','monthly'],['annual','Total de gastos previstos por año','annual'],['initial','Compras y preparación iniciales','initial'],['reserve','Aporte a tu reserva por mes','reserve']];
        foreach($fields as [$id,$label,$group]) echo '<label for="budget-'.h($id).'">'.h($label).' (Gs.)<input id="budget-'.h($id).'" type="number" inputmode="numeric" min="0" max="1000000000000" step="1" data-cost="'.h($group).'" placeholder="Pendiente"></label>';
        echo '</div><p class="small-note">En el total anual anotá solo gastos que no estén incluidos en los cuatro rubros mensuales, por ejemplo controles cotizados para todo el año. El aporte a la reserva es ahorro disponible, no un gasto clínico estimado.</p><p id="budget-status" role="status">Completá tus importes para ver una suma parcial.</p><div class="budget-results" aria-live="polite"><p>Suma mensual de gastos cargados <output id="budget-result-monthly">Gs. 0</output></p><p>Aporte mensual a la reserva <output id="budget-result-reserve">Gs. 0</output></p><p>Gastos recurrentes cargados para 12 meses <output id="budget-result-annual">Gs. 0</output></p><p>Caja prevista para el primer año, con instalación y aportes a reserva <output id="budget-result-year">Gs. 0</output></p></div><button class="button" type="button" data-print>Imprimir mi presupuesto</button> <button class="tool-reset" type="reset">Limpiar importes</button></form>';
    } else {
        echo '<h2>Tu hoja de cuidados</h2><p>Completá lo que ya acordaste y dejá los demás campos pendientes. Las fechas de consultas y tratamientos las define tu veterinario.</p><form class="tool-form planner-form" autocomplete="off"><div class="tool-grid"><label for="pet-name">Nombre de la mascota<input id="pet-name" type="text" maxlength="80"></label><label for="pet-species">Especie<input id="pet-species" type="text" maxlength="60"></label><label for="care-person">Persona responsable<input id="care-person" type="text" maxlength="100"></label><label for="care-backup">Reemplazo durante ausencias<input id="care-backup" type="text" maxlength="100"></label></div><label for="care-daily">Rutina acordada: alimento, agua, ambiente y actividades<textarea id="care-daily" rows="4" maxlength="1400"></textarea></label><label for="care-supplies">Compras pendientes y fecha de reposición<textarea id="care-supplies" rows="3" maxlength="1000"></textarea></label><label for="care-professional">Contacto veterinario y atención fuera de horario, confirmados por vos<textarea id="care-professional" rows="3" maxlength="1000"></textarea></label><label for="care-appointments">Consultas acordadas: fecha, lugar y preguntas<textarea id="care-appointments" rows="3" maxlength="1000"></textarea></label><label for="care-handover">Indicaciones profesionales que debe conocer quien cuide la mascota<textarea id="care-handover" rows="4" maxlength="1600"></textarea></label><p class="small-note">Copiá solamente indicaciones recibidas para esta mascota. Esta hoja no prescribe tratamientos, dosis ni un calendario sanitario.</p><div class="planner-week"><h3>Registro de esta semana</h3><p>Anotá una observación o marcá los cuidados realizados. Completar la casilla no confirma que el animal esté sano.</p>';
        foreach(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'] as $i=>$day) echo '<label for="care-day-'.$i.'">'.h($day).'<input id="care-day-'.$i.'" type="text" maxlength="120"></label>';
        echo '</div><button class="button" type="button" data-print>Imprimir mi planificador</button> <button class="tool-reset" type="reset">Limpiar hoja</button><noscript><p>Podés imprimir desde el menú de tu navegador.</p></noscript></form>';
    }
    echo '<p class="small-note">Tus datos permanecen en esta página del navegador: esta herramienta no los envía ni los guarda. Al recargar se borran. Imprimí o elegí guardar como PDF para conservar una copia; protegé los datos de contacto que incluyas.</p></section><script src="/assets/tools.js?v=20261009-portfolio" defer></script>';
}
