# Mascota — SEO primero, veterinarias pagadas después

Actualizado 8 de octubre de 2026. Este documento **reemplaza el plan inicial de directorio gratuito**, según la decisión de Anton en este chat. La prioridad es conseguir tráfico orgánico con contenido útil sobre mascotas; la monetización posterior será vender fichas y ubicaciones patrocinadas a veterinarias. El build PHP de esta etapa materializa esa decisión.

## Modelo acordado

1. Publicar un sitio editorial de mascotas con contexto de Paraguay, contenido sustancial y navegación entre temas.
2. Medir consultas, impresiones, páginas posicionadas y lecturas a partir del lanzamiento.
3. Con audiencia y evidencia de interés, ofrecer ubicaciones comerciales pagadas a veterinarias.
4. Publicar solo los acuerdos pagados, aprobados y vigentes, con publicidad claramente identificada.

**No se ofrece un directorio general gratis ni se importan todas las veterinarias para publicarlas.** Los enlaces a organismos oficiales en guías son fuentes editoriales, no fichas comerciales. No hay venta de leads ni comisión por consulta en el modelo de lanzamiento. Productos y acuerdos de afiliación quedan como expansión opcional después de demostrar tráfico.

## Primera versión construida

- HTML renderizado por PHP 8.3+, CSS local y contenido en JSON versionado.
- 24 guías en cuatro grupos: tipos de mascotas, cuidados, Paraguay y equipamiento.
- 33 páginas indexables en total: inicio, cuatro secciones, 24 guías y cuatro páginas editoriales.
- Búsqueda útil sin depender de JavaScript, navegación móvil, fuentes y fecha por guía, preguntas frecuentes visibles y enlaces relacionados.
- Títulos/descripciones/canónicas, Open Graph y estructura Article/Breadcrumb/WebSite; sitemap y robots generados.
- Ilustraciones SVG propias, una imagen social local y ausencia de dependencias de renderizado externas.
- El módulo de patrocinio existe pero viene desactivado y vacío. No aparece una falsa lista de negocios ni un formulario para cobrar.

No necesita instalación de Node, Composer, base de datos ni credenciales para leer el contenido. La tienda Next.js anterior se conserva en el repositorio y no forma parte del paquete PHP.

## Prioridades editoriales de SEO

| Grupo | Intención | Ejemplos publicados |
| --- | --- | --- |
| Mascotas | Conocer y comparar necesidades antes de convivir | Perros, gatos, conejos, cobayos, hámsters, aves, peces, reptiles |
| Cuidados | Resolver decisiones cotidianas y preparar consultas | Llegada a casa, calor, presupuesto, vacunas, convivencia, elegir veterinaria, adopción |
| Paraguay | Encontrar fuentes y organizar trámites locales | Leyes, viaje, fauna silvestre, denunciar maltrato |
| Equipamiento | Comparar características antes de comprar | Transportadoras, equipo de paseo, rascadores |

Los temas y palabras clave son hipótesis editoriales, **sin volúmenes medidos ni promesas de rankings**. El contenido responde preguntas, no se genera cambiando una ciudad en el mismo texto. No se publican páginas vacías para cada municipio, raza o servicio. La expansión se prioriza cuando Search Console y la investigación indiquen oportunidades y haya material original para cubrirlas.

## Conexión entre páginas

Inicio → sección → guía. Cada guía enlaza tres temas relacionados y vuelve a su sección. Las fichas de especie conectan con preparación, presupuesto y cuidados. Las guías de viaje se conectan con vacunas y transportadoras; las de fauna con aves, reptiles y reglas. La intención es que la persona complete una tarea o decisión, no solo acumular visitas.

Los artículos contienen preparación, preguntas y fuentes, con autoría editorial real. No afirman revisión clínica no realizada ni prescriben dosis. Las páginas legales son guías de fuentes y jurisdicción; no inventan multas, permisos ni procedimientos. Los contenidos extranjeros de bienestar no se presentan como derecho paraguayo.

## Monetización: una fase comercial posterior

Cuando exista tráfico relevante, ofrecer dos productos sencillos: **ficha profesional pagada** y **ubicación patrocinada** en contenidos apropiados. La tarifa y el entregable se fijan después de evaluar alcance real y hablar con negocios. Las cifras del plan anterior no son precios aprobados.

La contratación requiere datos comprobables, autorización de publicación, fechas, pago y aprobación. No se vende una credencial clínica. Los clics no se describen como turnos o consultas realizadas. No se promete exclusividad, renovación automática o resultados que no estén acordados.

El código mantiene invisibles todas las fichas salvo que `sponsorship_enabled` esté activado y la ficha tenga `paid`, `approved` y fechas válidas dentro de vigencia. Cero acuerdos = cero anuncios y cero fichas. No hay cobro, portal profesional ni facturación implementados.

## Trabajo después del lanzamiento

1. Verificar la cuenta de Hostinger, publicar el paquete y comprobar indexabilidad del dominio real.
2. Configurar Search Console y enviar sitemap; medición y verificación de propiedad son acciones del dueño pendientes.
3. Revisar consultas y páginas con señales reales antes de ampliar. No asumir que el contenido ya trae tráfico.
4. Añadir guías específicas con nuevas fuentes y contexto: necesidades por etapa de vida, preguntas locales frecuentes y comparación responsable de equipamiento.
5. Cuando haya audiencia, definir precio, ubicación y período para el piloto pagado de veterinarias; activar únicamente acuerdos reales.

La meta de esta entrega es **una versión publicable esta noche**, no una afirmación de que ya posiciona, genera ingresos o está desplegada. Ver [estructura](SITE-STRUCTURE.md), [fuentes](SOURCES.md) y el runbook del repositorio `PHP-DEPLOY.md`.
