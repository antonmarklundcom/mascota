# Expanded PHP SEO release — 9 October 2026

Historical 62-route release; superseded for upload by [the 64-route portfolio release](PORTFOLIO-RELEASE.md).

The approved Paraguay/Spanish Keyword Planner editorial plan is implemented and tested. The PHP release contains **51 guides plus 2 breed collections**, or **62 indexable routes** including home, categories and editorial information pages. There are 29 new editorial routes; existing mapped pages and shared hubs were expanded. All 44 immediate mappings resolve to actual pages/anchors. The future paid vet finder remains disabled and absent.

## Tested source and artifact

- Branch: `codex/mascota-php-seo`; parent baseline `3add08c59ba3343ebd782930b2aedc298aab780f`. Checks ran against the resulting working tree. The final commit is recorded in the adjacent release manifest and local operation manual after commit.
- Draft [PR #20](https://github.com/antonmarklundcom/mascota/pull/20); no merge or production deployment performed.
- Package: `C:/AI work/mascota/release-2026-10-09/mascota-hostinger-2026-10-09.zip`.
- ZIP SHA-256: `4e72099d8ea0fe8aad9515b109b240ae39f767b3f69a7404074b6fc756fbce31`.
- Fifteen allowlisted files. `public_html/` and private sibling `mascota-app/`; no private config override, local sponsors, dependencies, old store, research docs or customer records.
- Each ZIP entry was compared byte-for-byte with its intended source. Per-file hashes are in the release's `manifest.json`.
- Keyword source SHA-256: `2000fc93e4fb1f9d9fbd2208f9e59b15e3bc776d8360df8bd4a4df82a704aade`.

## Validation results

| Check | Result | Scope |
| --- | --- | --- |
| PHP/content/HTTP/SEO | PASS — 1,567 checks, PHP 8.3.33 | PHP lint; content references; all routes; titles/H1/canonicals; schema and parent breadcrumbs; publication/modification dates; exact per-page sitemap dates; anchors; crawl reachability; robots/preview/search; escaping/private paths; paid-profile gates using isolated synthetic fixtures |
| Chrome/Playwright | PASS — 425 checks | All 62 routes at 1440 and 320 px; heading visibility; no horizontal overflow; 390 px menu/search/FAQ/anchor/breadcrumb behavior; 17 distinct dog-breed cards; 44 mapped group targets; no failed requests or page errors |
| Extracted ZIP | PASS — 78 checks | Explicit file layout, safe paths, no private overrides, clean extraction, actual private-sibling app fallback, all 62 sitemap pages/HTTP responses, assets and private/absent routes |
| Release/source correspondence | PASS — 15 exact file comparisons | Every public/private/example/runbook archive entry equals the source used for this release |
| Git diff whitespace | PASS | `git diff --check` |
| Hosted GitHub CI | SKIP | Repository Actions permissions API checked on 9 October: `enabled: false`; PHP 8.3/8.4 workflow is present and package filename updated; no hosted run claimed |
| Retained Node store | SKIP | Its application, dependencies, database and deployment path are unchanged |
| Hostinger production/HTTPS/rewrites | UNVERIFIED | Local PHP router tests cannot establish hosting account behavior |
| Search Console, rankings and traffic | UNVERIFIED | No property or external analytics account configured; supplied KWP numbers are not observed visits |

Desktop homepage/breed and mobile home/symptom/breed-hub screenshots are in the release's `preview/` folder and were visually inspected. The browser report is `preview/browser-checks.json`. The manual updater verifies dated snapshot equality, hashes and local document links separately.

## Reproduce

```sh
php -S 127.0.0.1:8180 -t php-site/public php-site/router.php
python php-site/tests/smoke.py --php php
python php-site/tools/package.py --output /private/release-folder
python php-site/tests/package_smoke.py --php php --zip /private/release-folder/mascota-hostinger-2026-10-09.zip
```

The local browser verification used Chrome and Playwright from Codex's bundled Node runtime, with the local preview on port 8180. It is supporting development tooling, not a hosting dependency. Automated tests use temporary copies and synthetic sponsorship fixtures, never production customer files. Future releases should update the named ZIP path consistently with the packager/workflow.

## Data and owner handoff

Read [the implemented keyword map and data limitations](../../seo/2026-10-09/README.md) and [the upload/rollback runbook](../../../PHP-DEPLOY.md). The 8 October release report remains historical evidence for the earlier 33-page release.

The remaining actions are actual Hostinger upload/post-upload checks, Search Console verification/sitemap submission, missing/full related KWP exports, ongoing source review and later real paid sponsorship agreements. No unsupported city/brand pages, duplicate keyword-variant pages, professional review claims or medicine doses were introduced. The uncertain groups were given relevant focused guides without treating their mixed totals as clean demand.
