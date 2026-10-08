# Mascota — subir la versión PHP a Hostinger

Actualizado 8 de octubre de 2026. Esta versión es un sitio editorial de SEO: **24 guías originales + 4 secciones + 4 páginas editoriales + inicio = 33 páginas**. No necesita Node.js, Composer, MySQL ni instalación de dependencias en el servidor. Las fichas veterinarias pagadas están desactivadas.

## La forma rápida para esta noche

1. En hPanel, elegí **mascota.com.py** y comprobá que sea un sitio PHP/HTML. Seleccioná **PHP 8.3 o 8.4**. Este proyecto fue probado localmente con PHP 8.3.33; el PHP real de tu cuenta todavía debe comprobarse.
2. Abrí el administrador de archivos. Guardá una copia privada de los archivos actuales y de cualquier configuración real antes de reemplazar el inicio. Esta tarea no inspeccionó tu cuenta ni generó una copia de producción.
3. Subí `mascota-hostinger-2026-10-08.zip` a la carpeta del dominio, **un nivel por encima de `public_html`**, y extraelo allí. El ZIP contiene estas dos carpetas hermanas:

```text
carpeta-del-dominio/
  mascota-app/                 # Privada: NO debe estar dentro de public_html
    app/bootstrap.php
    config/site.example.php
    content/articles.json
    content/sponsors.json
  public_html/
    .htaccess
    index.php
    assets/
```

4. Confirmá que `.htaccess` se haya extraído y que la página de bienvenida anterior no tenga prioridad. `DirectoryIndex index.php` está configurado en el archivo nuevo. Conservá la copia anterior fuera de la carpeta pública; no dejes un respaldo accesible por URL.
5. Comprobá HTTPS en `https://mascota.com.py/`. No conectes esta versión con la configuración Node.js del antiguo `DEPLOY.md`. Si tu administrador de archivos solo permite abrir `public_html`, entrá al administrador completo de la cuenta o usá SFTP para colocar la carpeta privada al lado; no la metas dentro del directorio público para salir del paso.
6. Revisá inicio, una guía, búsqueda, móvil, `/robots.txt` y `/sitemap.xml`. Las URL `/app/bootstrap.php`, `/content/articles.json`, `/config/site.local.php` y `/veterinarias/` deben devolver 404 (o denegación de acceso para rutas privadas), sin archivos de configuración ni listado gratuito.

El ZIP no publica documentos del repositorio ni la tienda Next.js anterior. No activa pagos, formularios ni anuncios. Si desplegás únicamente `public_html` y falta `mascota-app`, el inicio responde 503 con una indicación de despliegue.

## Configuración opcional

El dominio canónico predeterminado es `https://mascota.com.py`. Para cambiar una opción, copiá `mascota-app/config/site.example.php` a `mascota-app/config/site.local.php`, siempre fuera del directorio público. No subas ese archivo privado a Git.

Opciones: `site_url`, `environment`, `contact_email` y `sponsorship_enabled`. Un correo real es opcional; si está vacío, el sitio no inventa una dirección. Esta primera versión no necesita credenciales. Si se configura un correo editorial, el enlace aparece en las páginas informativas.

Para una copia de pruebas, usá `environment => 'preview'`; responde con instrucciones de no indexar. Antes de lanzar el dominio real, confirmá `environment => 'production'`. La vista local también está excluida por su host. No uses `preview` en la web que querés posicionar.

El sitio admite `MASCOTA_SITE_URL`, `MASCOTA_ENV` y `MASCOTA_CONTACT_EMAIL` desde el entorno PHP si el hosting los configura realmente. PHP no lee automáticamente archivos `.env`.

## SEO después de subir

- Verificá el dominio en Google Search Console y enviá `https://mascota.com.py/sitemap.xml`. La propiedad debe estar bajo tu control; no se configuró desde esta tarea.
- Comprobá la indexación de las páginas reales y que la vista de pruebas esté excluida.
- Mantené enlaces internos, títulos y descripciones únicos. La búsqueda está marcada `noindex`; no crees miles de páginas por filtros o ciudades sin contenido propio.
- Revisá consultas e impresiones cuando haya datos y priorizá nuevas guías con esa evidencia. El mapa de palabras clave es una hipótesis editorial; no contiene volúmenes medidos ni garantiza posicionamiento.

## Editar una guía

Contenido: `mascota-app/content/articles.json`. La copia canónica versionada vive en `php-site/content/articles.json` dentro del repositorio. Hacé cambios allí, validalos y armá un paquete nuevo; una modificación solo en el servidor se perderá en el siguiente despliegue.

Cada guía tiene categoría, slug estable, título, descripción, respuesta breve, introducción, secciones, fuentes, enlaces relacionados y fecha `date`. Al modificar el contenido sustancial, actualizá la fecha y comprobá las fuentes. No inventes una revisión veterinaria, tarifas, fechas de trámites o testimonios.

## Fichas pagadas: se activan después

Mantener `sponsorship_enabled => false` deja todos los anuncios y fichas fuera del sitio y del sitemap. `sponsors.json` se entrega vacío. No importes el registro completo de veterinarias como fichas gratuitas.

Cuando exista un acuerdo real, creá `mascota-app/content/sponsors.local.json` en el servidor privado con una lista de fichas. Este archivo tiene prioridad sobre el JSON vacío entregado y queda fuera de Git y del ZIP. Cada ficha necesita `paid: true`, `approved: true`, nombre (`name`), slug, ciudad (`city`), descripción (`description`) y fechas válidas `starts`/`ends` en formato `AAAA-MM-DD`. Solo se publica si el módulo está habilitado y el acuerdo está vigente. El sitio identifica estos espacios como publicidad. Una ficha impaga, no aprobada, futura o vencida queda oculta y responde 404.

Los registros comerciales se mantienen fuera de Git si contienen datos que no deben publicarse. No se incluye sistema de cobro, renovación automática, facturación, portal de clientes ni métricas comerciales. Antes de activar el módulo, confirmá contacto, derecho a publicar, datos actuales y términos del acuerdo; probá con una copia aislada.

## Desarrollo y verificaciones

Desde la raíz del repositorio:

```sh
php -S 127.0.0.1:8178 -t php-site/public php-site/router.php
python php-site/tests/smoke.py --php php
python php-site/tools/package.py --output /ruta/privada/de/salida
```

En Windows el PHP verificado está en `C:/php/php.exe`. En Linux los comandos usan el PHP instalado. Las pruebas HTTP copian la aplicación a una carpeta temporal y usan datos sintéticos; no escriben sobre anuncios reales.

El paquete incluye una lista explícita de archivos públicos, aplicación, contenido editorial y configuración de ejemplo. El empaquetador excluye `site.local.php`, `sponsors.local.json`, copias de respaldo, pruebas y código de la tienda antigua. Conservá los dos archivos locales privados cuando actualices una instalación. La imagen social PNG está incluida; no hay fuentes, scripts ni imágenes remotos necesarios para renderizar el sitio.

## Recuperación y problemas frecuentes

**503 con aviso de archivos privados:** verificá que `mascota-app/app/bootstrap.php` esté al lado de `public_html`, no dentro de él.

**Inicio funciona, guías dan 404:** comprobá que `.htaccess` esté presente y que el slot soporte reescritura de URLs. Hostinger usa configuración compatible para PHP; el comportamiento exacto de tu cuenta debe comprobarse.

**Sigue la bienvenida anterior:** revisá el dominio/document root que abriste, `DirectoryIndex` y caché del navegador/hosting. Conservá el archivo antiguo en una copia privada antes de quitarle prioridad.

**Buscadores ven `noindex`:** verificá el entorno y el host de la copia consultada. La producción debe usar su dominio real y `environment => 'production'`.

**500 después de editar JSON:** validá sintaxis y referencias en la copia local, corré las pruebas y volvé a desplegar el archivo validado. Consultá el registro PHP privado de Hostinger; no publiques errores o archivos `phpinfo()`.

Para volver atrás, conservá la versión actual y restaurá los archivos públicos y privados de la versión conocida, sin sobreescribir configuración privada o acuerdos reales que necesites mantener. Esta versión editorial no crea bases de datos ni registros de usuarios. Una prueba de recuperación del ZIP se realiza localmente; el backup y la recuperación de tu hosting siguen pendientes de comprobar.

Referencias: [Hostinger · sitios PHP/HTML con Git](https://www.hostinger.com/support/1583302-how-to-deploy-a-git-repository-in-hostinger/), [Hostinger · elegir versión PHP](https://www.hostinger.com/support/1575755-how-to-change-the-php-version-of-your-hostinger-hosting-plan/). El despliegue por Git no se asume capaz de seleccionar un subdirectorio del repositorio; para esta noche usá el paquete explícito.
