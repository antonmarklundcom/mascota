<?php
// Direct runtime regression checks: no network or content mutation.
declare(strict_types=1);
require dirname(__DIR__).'/app/bootstrap.php';
$cases=[
 ['cómo cuidar a un gato','gatos'],
 ['como cuidar a un gato','gatos'],
 ['cómo cuidar a un perro','perros'],
 ['cuánto cuesta un perro','presupuesto-mascota'],
 ['cuanto cuesta un gato','presupuesto-mascota'],
 ['gastos de un perro','presupuesto-mascota'],
 ['precio shih tzu','perros/razas/shih-tzu'],
 ['cuánto cuesta un shih tzu','perros/razas/shih-tzu'],
 ['precio labrador','perros/razas/labrador'],
 ['precio gran danes','perros/razas/gran-danes'],
 ['mi perro vomita','vomitos-en-perros'],
 ['vomito perro','vomitos-en-perros'],
 ['perro vomitando','vomitos-en-perros'],
 ['que hacer si mi gato vomita','vomitos-en-gatos'],
 ['perro con tos','tos-en-perros'],
 ['alimento para perros','comida-para-perros'],
 ['racion perros','comida-para-perros'],
 ['precio de comida para perros','comida-para-perros'],
 ['gato siames','gatos/razas/siames'],
 ['hamster ruso','hamsters'],
];
$checks=0;$results=[];
foreach($cases as [$query,$expected]) {
 $rows=search_guides($query);$actual=$rows[0]['slug']??null;
 if($actual!==$expected) throw new RuntimeException($query.': expected '.$expected.', got '.($actual??'no result'));
 $results[]=['query'=>$query,'first'=>$actual];$checks++;
}
foreach(['palabraquenuncaexiste','perro palabraquenuncaexiste','precio gato palabraquenuncaexiste','cómo cuidar a un gato palabraquenuncaexiste','cuánto cuesta un shih tzu palabraquenuncaexiste','como cuanto para un'] as $query) {
 if(search_guides($query)!==[]) throw new RuntimeException('Unknown/filler query must remain empty: '.$query);
 $results[]=['query'=>$query,'first'=>null];$checks++;
}
foreach(['precio shih tzu','precio labrador','precio gran danes'] as $query) {
 if(in_array('presupuesto-mascota',array_column(search_guides($query),'slug'),true)) throw new RuntimeException('Breed query broadened into a shared budget guide: '.$query);
 $checks++;
}
echo json_encode(['status'=>'PASS','checks'=>$checks,'results'=>$results],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).PHP_EOL;
