# Crawl and search readiness — 9 October 2026

This increment builds on commercial follow-up source `a660c64e62702d1af76ed59f999a0c42a4ec5ac7`, which includes PHP SEO parent `1ff9c21c4c6ebf334f7c5ef7fc0bdd77bfafc290`. Existing 67 public routes, three tools, content, assets, paid-profile gates and commercial reporting remain. No new keyword pages, clinic records, database, migrations, deployment, merge, accounts or outreach.

## Result

- Production `/buscar/` is crawlable and still `noindex,follow`, outside the sitemap. Google needs crawler access to read `noindex`: [official guidance](https://developers.google.com/search/docs/crawling-indexing/block-indexing). Production blocks only `/contacto-clinica/`; preview still disallows all crawling and sends noindex headers. The release checker verifies the exact current robots policy and search exclusion.
- Recognized encoded paths and missing trailing slashes redirect once with 301 to their canonical spelling. `/mascotas/%70erros/` becomes `/mascotas/perros/`. Original query encoding/repeated keys are preserved. Unsupported methods remain 405; private, double-encoded and unknown paths remain 404. Origin-form parsing keeps a leading double slash from being mistaken for an authority and accidentally rendering the homepage. [Google canonicalization guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
- Search normalizes care and cost phrases, weights actual title/topic evidence above species metadata and uses existing species metadata for shared guides. Cat-care questions rank the cat hub; general dog cost questions rank the budget guide; breed-specific price searches stay specific. Every meaningful query token is still required, so an unknown word does not silently broaden results.

## Local verification

| Check | Result |
| --- | --- |
| PHP/source/content/SEO/public and private routes | PASS 2,048 assertions, PHP 8.3.33 |
| Crawl, canonical redirects, methods, query preservation | PASS 25 HTTP assertions |
| Direct natural-language search | PASS 29 assertions |
| Immutable package/checker fault fixtures | PASS 3 tests; preserves all 16 parent adverse modes plus blocked-search and indexable-search failures |
| Existing commercial/privacy/concurrency/report boundaries | PASS 49 isolated checks after the rebase |
| Editorial escaping/reviewer/search boundaries | PASS 56 assertions |
| Focused browser at 1280/390px | PASS 24 checks; zero JS/CSP/console errors or failed requests |
| Git whitespace | PASS |
| Hosted Actions | SKIP: repository API still reports `enabled:false`; workflow contains the new tests |
| Production hosting, HTTPS, Apache/LiteSpeed rewrites, filesystem ACLs | Not inspected or deployed in this increment |

The focused browser helper initially failed during the local Node startup probe, then an earlier browser attempt timed out. Replacing the probe and restarting the isolated helper produced a clean passing run and exit. This is fixture evidence, not a claim that the hosting account was tested. No CSS, page-copy, food-tool, commercial-report or keyword-data changes justified repeating the prior complete browser/keyword suites; the current source smoke checks cover every public route, and changed search/URL flows were exercised in both viewport sizes.

The draft was rebased onto the newer commercial follow-up, retaining aggregate-key ordering and stricter contact-header protection. Both search fault cases and all three contact-header cases remain in the combined release fixture. The checker uses same-origin GETs plus one no-count HEAD contact-policy probe and never follows a redirect. Fresh post-rebase baseline, crawl, search, release and 49 commercial checks passed. Browser/editing evidence was retained because `bootstrap.php`, `interactive.php` and public assets are byte-identical to the tested crawl candidate; actual Apache headers still require production verification. The first d39a90c package is historical and superseded by the final rebased package.

Final immutable ZIP is generated from the subsequent clean commit and tested by extraction. Its exact commit, version, SHA-256 and package-check result are recorded in the matching manifest and owner artifact report, avoiding a circular self-referential commit in this document.

## Repeat checks

```sh
python php-site/tests/smoke.py --php php
python php-site/tests/test_crawl.py --php php
php php-site/tests/search_regression.php
python php-site/tests/test_release.py
python php-site/tests/commercial_smoke.py --php php
python php-site/tests/test_editorial.py --php php
python php-site/tools/package.py --output /private/release-directory
python php-site/tests/package_smoke.py --php php --zip /private/release-directory/mascota-hostinger-<version>.zip
```

Use the existing runtime; no new dependencies were installed. The focused browser evidence is stored outside Git under the owner's dated artifact directory.

## Git, storage and next action

The isolated Git-aware worktree is `E:/ai work/Projects/mascota/worktrees/crawl-readiness-20261009`, branch `codex/crawl-readiness-20261009`. Artifacts are under `E:/ai work/Artifacts/mascota/2026-10-09/crawl-readiness`. Canonical laptop checkout remains `C:/Projects/mascota`; parent/commercial worktrees are preserved. The external drive must be connected for this checkout; do not recreate it on C: merely because E: is absent. No node_modules/.next were copied and no dependencies were installed.

The draft continuation targets `codex/commercial-measurement-20261009` (PR21), which targets `codex/mascota-php-seo` (PR20). Review/merge parents and coordinate child targets separately. Upload only the latest integrated ZIP after separately authorized deployment and an owner-controlled private backup. Verify the exact manifest in production, then configure owned Search Console and submit the sitemap. No SQL migration is needed. Paid-listing/contact/count gates remain off and shipped sponsors remain empty.
