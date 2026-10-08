# Mascota PHP launch verification

8 October 2026, America/Asuncion. Standalone editorial HTML/PHP release; preserved Next.js store code and database/payment systems.

## Actual local results

| Check | Result |
| --- | --- |
| PHP 8.3.33 lint and isolated HTTP/content checks | PASS: 476 checks |
| Chrome desktop/mobile browser checks | PASS: 47 checks at 1440, 390 and 320 px |
| Hostinger ZIP clean extraction and private sibling routing | PASS: 48 checks |
| Launch sitemap | 33 indexable pages, including 24 Spanish guides |
| Veterinary advertising | Disabled and empty; no free directory |
| Git whitespace check | PASS |
| Old Node store checks | Not run locally; no store code/dependencies/database changes |
| Hostinger account, Apache/LiteSpeed rewrites and HTTPS | Not verified; owner upload and post-upload checks pending |
| Organic search traffic / rankings | Not measured; Search Console setup pending |
| Clinical/legal professional review | Not claimed; guides provide preparation, questions and official sources |

The HTTP tests use isolated copies and synthetic sponsorship records. The ZIP test simulates URL rewrites through PHP's development server; it does not establish that a particular Hostinger account has enabled rewrites. Browser checks covered the homepage, species collection, dog guide, Paraguay travel guide, search, mobile navigation, image loading and horizontal overflow. Desktop and mobile screenshots were visually inspected.

## Repeat the checks

```sh
python php-site/tests/smoke.py --php php
python php-site/tools/package.py --output /private/release-folder
python php-site/tests/package_smoke.py --php php --zip /private/release-folder/mascota-hostinger-2026-10-08.zip
```

The PHP workflow repeats the two portable test suites and packaging on PHP 8.3 and 8.4. Check the current GitHub run before describing hosted CI as passed. The retained store has its own separate CI.

## Deployment and recovery

Use [PHP-DEPLOY.md](../../../PHP-DEPLOY.md), not the retained Node deployment instructions. Extract the ZIP one level above the domain's `public_html`: public files go into `public_html/`; private application/config/content go into the sibling `mascota-app/`.

A manifest beside the release ZIP records its SHA-256. Rebuild from the same committed files to produce a fresh checked release. Keep private hosting configuration and future `sponsors.local.json` separately; the packager deliberately excludes them and all backups. A dated local manual provides the source revision and exact output location. No production backup, merge or deployment was performed as part of these local checks.
