# Mascota — estructura implementada para el lanzamiento PHP

8 de octubre de 2026. La instrucción actual prioriza SEO y contenido. Este documento reemplaza la propuesta anterior de directorio como conversión principal.

## Páginas publicadas en el código

| Ruta | Función |
| --- | --- |
| `/` | Entrada editorial, búsqueda y acceso a especies y guías locales |
| `/mascotas/` | Ocho guías sustanciales de tipos de mascotas |
| `/cuidados/` | Preparación, rutina, presupuesto, convivencia y consultas |
| `/paraguay/` | Leyes/fuentes, fauna, viajes y denuncias |
| `/productos/` | Criterios de equipamiento; sin catálogo ni comisiones |
| `/{seccion}/{slug}/` | 24 guías con fecha, fuentes, contenido propio y tres enlaces relacionados |
| `/buscar/?q=…` | Búsqueda GET, marcada noindex y fuera del sitemap |
| `/sobre-mascota/`, `/metodologia/`, `/privacidad/`, `/publicidad/` | Autoría editorial, fuentes, datos y política comercial |
| `/robots.txt`, `/sitemap.xml` | Descubrimiento y control de indexación |

Son 33 páginas indexables. No se han creado páginas municipales, razas o directorios vacíos para inflar ese número. Las rutas desconocidas son 404 con noindex; las URL sin slash final de páginas conocidas redirigen a la canónica.

## Tecnología y archivos

```text
php-site/
  public/index.php          # Entrada pública
  public/.htaccess          # URLs amigables, DirectoryIndex y protección
  public/assets/            # CSS, SVG originales e imagen social PNG
  app/bootstrap.php        # Enrutado, render, SEO y filtro de fichas pagadas
  content/articles.json    # Contenido y fuentes versionados
  content/sponsors.json    # Vacío de fábrica
  config/site.example.php  # Opciones públicas/no secretas
  router.php               # Vista local con el servidor PHP
  tests/smoke.py            # Pruebas de rutas, SEO, datos y publicación pagada
  tools/package.py         # ZIP permitido por lista explícita de archivos
PHP-DEPLOY.md               # Instrucciones reales para Hostinger
```

PHP mínimo: 8.3. No se usa MySQL, Composer ni Node para ejecutar el sitio. No hay CMS, cuentas, formularios, suscripciones ni procesamiento de turnos. Editar guías significa actualizar el JSON en Git, verificarlo y desplegar un nuevo paquete.

La distribución separa `public_html/` de `mascota-app/` como carpetas hermanas. El paquete excluye configuración privada, documentación técnica antigua, scripts de prueba y código Next.js. No se debe publicar la raíz completa del repositorio como un sitio PHP.

## Fichas comerciales posteriores

Las fichas se generan en `/veterinarias/{slug}/` únicamente cuando existen acuerdos activos. No hay una página general de todas las veterinarias. El filtro exige módulo habilitado, `paid: true`, `approved: true`, slug válido y período vigente con fechas válidas. Un registro que no cumple no aparece en el sitio ni sitemap y su ruta responde 404.

Las fuentes institucionales de las guías permanecen accesibles como referencias editoriales. La publicidad se identifica expresamente. El código no cobra ni gestiona contratos; esas operaciones se definirán cuando Anton lance la monetización.

## SEO y expansión

Títulos y descripciones únicos, canónicas con hostname configurado, HTML accesible sin JavaScript, datos estructurados coherentes con la autoría real, links relacionados y activos locales. No hay reviews ficticias, texto oculto, keywords con volumen inventado ni contenido de ciudades duplicado.

El sitemap incorpora guías reales y fichas comerciales solo cuando son publicables. El entorno local/preview envía noindex. Producción indexable debe comprobarse en Hostinger. Los encabezados de seguridad y aislamiento local se prueban; el comportamiento Apache/LiteSpeed y HTTPS de la cuenta real requieren la comprobación posterior al upload.
