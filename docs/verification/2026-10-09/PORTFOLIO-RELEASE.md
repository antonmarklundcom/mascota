# Portfolio PHP release — 9 October 2026

Mascota now has **64 indexable routes**: 51 existing guides, two breed collections, two new planning tools, four hubs, four information pages and home. Search handles short natural phrases and relevant aliases; home/guide links and the breed index expose useful routes. Veterinary advertising stays disabled and empty. Runtime remains standalone HTML/PHP with local CSS/JavaScript; no Node/database hosting build.

Two original tools: `/cuidados/calculadora-presupuesto-mascota/` and `/cuidados/planificador-cuidados/`. User-entered guaraníes, pending costs, separate reserve/initial/annual spending, no sending/storage, reset and printing. Fields do not prescribe doses or clinical schedules. Dog-food label comparison and synonyms support the existing single food page. No new brands/cities or professional-review claims.

## Audited sources and status

Based on Mascota `e06e439846520934a82507c5316e7c412ea23988`, existing branch `codex/mascota-php-seo`, draft [PR20](https://github.com/antonmarklundcom/mascota/pull/20). Current main still contains the retained store. Perro [PR9](https://github.com/antonmarklundcom/perro/pull/9) merged at `46b3297e8995b85e00d38f06272f6d96ed604a03`; an isolated worktree adds documentation only and preserves the other session's checkout. The final reviewed commit is recorded in the local release manifest and operation manuals after commit; checks ran against this completed working tree.

Fresh public GET, 9 October 05:39 UTC: Mascota root default hosting page, six guide destinations 404. Perro root + six destinations 200 with `perro-e70f6ea29560`. Seven contextual links to those Perro destinations are allowed by `perro_links_enabled`; no mass footer exchange. Perro → Mascota stays gated until five real Mascota destinations work publicly. No production uploads, merges, account changes or messages performed here.

## Verification

| Check | Result / scope |
| --- | --- |
| PHP/content/SEO/HTTP | PASS **1,702** on PHP 8.3.33; routes, metadata, schema, dates, anchors, crawl reachability, search ranking/escaping, unique IDs, preview/private paths, link/sponsor gates with isolated fixtures |
| Desktop/mobile Chrome | PASS **410**; all 64 pages at 1440/320 px, 390 px interactions, search, arithmetic, invalid values/reset, private fields absent from browser storage, print visibility/long notes, no-JS fallback and no failed requests/errors |
| Extracted corrected ZIP | PASS **81**; 64 sitemap routes, private sibling application, assets/layout and denied private/empty clinic routes |
| ZIP/source | PASS **17** exact file comparisons, per-entry SHA-256 in manifest |
| Shared documents | Eight copies identical between repositories; local link checks recorded separately |
| Financial scenarios | Decimal arithmetic reproduced 20-client 95%/80% and 15-client 95% examples; assumptions remain unvalidated |
| GitHub hosted CI | SKIP: Actions API reports `enabled: false`; no setting changed |
| Perro runtime | Unchanged in this task; existing tests are historical evidence, not rerun claims |
| Hosting/SEO outcomes | No deployment. Actual Hostinger HTTPS/rewrites/indexability and Search Console traffic/rankings remain owner checks |

Screenshots and synthetic-input printable PDFs are in the new release `preview/`; mobile inputs/labels were visually inspected. Browser checks caught and corrected a development-router JS omission and duplicate calculator IDs before final verification. The tested totals: Gs.600,000 recurring monthly, Gs.100,000 monthly reserve, Gs.7,200,000 recurring annual, Gs.9,400,000 first-year cash for the synthetic example. These are calculations, not prices.

## Release and reproduction

- New ZIP: `C:/AI work/mascota/portfolio-2026-10-09/mascota-hostinger-2026-10-09.zip`.
- SHA-256: `8c97ba6b6cab26dd1415a488000e08803917dc15fba41f45366e113b7135f9af`.
- Seventeen allowlisted files. No private overrides, sponsor/customer records, store dependencies or research documents. Previous release folder preserved.
- Private configuration remains outside `public_html`; preserve real `site.local.php`/`sponsors.local.json` during an authorized update.

```sh
php -S 127.0.0.1:8180 -t php-site/public php-site/router.php
python php-site/tests/smoke.py --php php
python php-site/tools/package.py --output /private/new-release
python php-site/tests/package_smoke.py --php php --zip /private/new-release/mascota-hostinger-2026-10-09.zip
```

Chrome test tooling and its logs are development evidence, not hosting dependencies. The reviewed deploy procedure is [PHP-DEPLOY.md](../../../PHP-DEPLOY.md). Local package tests use a PHP router; actual Apache/LiteSpeed/HTTPS behavior must be checked after authorized upload.

## Owner handoff

Read [agreement v1.0.0](../../portfolio/2026-10-09/MASCOTA-PERRO-AGREEMENT.md), [the 90-day plan](../../portfolio/2026-10-09/90-DAY-PLAN.md) and [financial/workload hypotheses](../../portfolio/2026-10-09/REVENUE-WORKLOAD-MODEL.md). Review, authorize launch separately, verify Search Console, agree salary/role/actual accounting costs, and validate partners/deliverables before any payments or fichas. Perro runtime follow-ups have their own document; no live outreach or fabricated partners introduced.

The earlier 62-route SEO report remains historical. This increment adds tools and coordination; it does not claim maximal traffic, top-two positions or a fully operated business.
