# Integrated commercial verification - 9 October 2026

PR21 branch `codex/commercial-measurement-20261009` is rebased onto PHP parent `codex/mascota-php-seo` at `1ff9c21c4c6ebf334f7c5ef7fc0bdd77bfafc290`. Original feature commit `0593938d78c19c75f0d1e84c68cee17afdb4eb36` is preserved by the resolved rebase; integrated runtime review began at `ce8608f`. Both PHP changesets remain reviewable, with no merge or deployment implied. The legacy Next.js store is unchanged.

The integrated build preserves 67 indexable routes, parent SEO content, three browser-only tools, local assets/OG manifest, editorial safety/maintenance, offline keyword opportunities and deterministic commit/fingerprint releases. It adds gated contact and private commercial reporting. The explicit release inventory contains 82 files including the public non-secret release.json and runbook. CLI, tests, local overrides, commercial ledgers/counts/reports/locks and backups are excluded.

| Integrated local check | Result |
| --- | --- |
| PHP 8.3.33 source syntax | PASS 8 application/router/config/editorial-fixture files |
| Parent content, SEO, routes, assets, tools and sponsor baseline | PASS 2,047 assertions |
| Commercial privacy, feature gates, concurrent counts and reporting | PASS 45 assertions |
| Deterministic immutable release/checker fixtures | PASS 3 tests, including 13 adversarial checker modes |
| Truthful editorial and safe inline-link fixtures | PASS 56 checks |
| Offline keyword opportunity fixtures | PASS 13 tests |
| Parent real Chrome desktop/narrow/mobile suite | PASS 437 checks; browser/browser-checks.json beside the release |
| Final committed extracted-package suite | PASS 230 assertions on the 82-file inventory; final committed artifact rerun recorded in package-checks.json |

Integrated synthetic paid-profile desktop/mobile QA also passed 14 checks at 1440/390; both screenshots were inspected. No contact link was clicked. Commercial runtime/privacy checks ran again against the combined parent. The broad browser fixture now waits for lazy local assets before route navigation and preserves strict zero-failed-request assertions with URL/error/type diagnostics; an earlier unspecified failed request did not reproduce in the settled run. Tests use synthetic temporary copies; commercial copies exclude private local overrides, ledgers and counters, preventing test requests from touching real configured external storage. They distinguish aggregate redirect requests from manually confirmed inquiries/appointments and billing from collected/refunded cash, preserve concurrent increments, reject visitor identifiers, unknown fields and unsafe storage/output, and suppress margin claims when costs are unknown.

```sh
python php-site/tests/smoke.py --php php
python php-site/tests/commercial_smoke.py --php php
python php-site/tests/test_release.py
python php-site/tests/test_editorial.py --php php
python -m unittest discover -s php-site/tests -p test_keyword_opportunities.py -v
python php-site/tools/package.py --output /absolute/private/release
python php-site/tests/package_smoke.py --php php --zip /absolute/private/release/mascota-hostinger-<version>.zip
```

Package name, full commit, sourceState, release fingerprint and ZIP/file hashes are computed after the reviewed documentation/code commit and recorded in the matching immutable manifest. This avoids hardcoded release versions and circular guessed source revisions. Final output is `C:/AI work/mascota/commercial-integrated-20261009/`; earlier fixed-name commercial/portfolio ZIPs are preserved and superseded. The local manual records the selected final artifact and checks.

Sponsorship, contact and click tracking remain disabled; shipped sponsors remain empty. No real partner permission, commercial ledger/cost input, collection, margin, salary coverage or qualified-lead attribution is established. Real Hostinger runtime/HTTPS/rewrites, document roots, private ACLs and atomic replacement semantics need owner validation before activation. Actions remains disabled; the updated workflow supports both main and the stacked PHP base, includes commercial plus parent suites, but no hosted success is inferred. No retained store migrations/database setup, payment activation, outreach, merge or deployment occurred.

## Review fixes follow-up - 9 October 2026

Two independently reviewed findings are corrected on the existing PR21 branch: JSON object order no longer suppresses valid aggregate increments, and the Apache default no longer overwrites an existing stricter PHP/FastCGI contact referrer policy. Validation still rejects unknown/missing top-level aggregate keys. The production checker adds a same-origin no-count HEAD privacy probe and negative referrer/cache/indexability fixtures; release/extraction tests inspect the actual packaged Apache directive. No UI, bootstrap, default feature gate, financial arithmetic, real partner data or retained Next.js machinery changed.

Focused precommit validation on PHP 8.3.35: application lint PASS; commercial contact/privacy/concurrency/report suite PASS 49 checks; immutable release/checker suite PASS 3 tests with 16 adverse checker modes; extracted package PASS 231 assertions across the 82-file release and 67 routes. The existing 24-worker assertion was not relaxed. Its first run on the newly scoped E: temporary root failed; worker exit/stderr/count diagnostics were added, and the next three full commercial runs each passed all 49 checks. E: reports NTFS, fixed and healthy. This does not establish crash durability or real Hostinger filesystem behavior; verify replacement/locking before enabling measurement.

No local Apache executable was found on PATH or in C:/dev/tools, C:/Apache24 or C:/xampp/apache. Apache/FastCGI and Hostinger/LiteSpeed response behavior therefore remains UNVERIFIED. The package regression verifies configuration bytes and the loopback checker regression verifies detection of overwritten headers; PHP's development server does not execute .htaccess. [Apache documentation](https://httpd.apache.org/docs/2.4/mod/mod_headers.html#header) supports the selected `always setifempty` strategy. No server was installed or changed, and no production endpoint was probed.

New non-secret logs and releases are under `E:/ai work/Artifacts/mascota/2026-10-09/review/`; test children alone receive scoped TEMP/TMP. Existing C: artifacts are retained. After committing, the final clean build and matching manifest in `final/` provide actual version, commit, file inventory and ZIP SHA-256 without a guessed or circular revision. Final extraction validation is recorded beside that package. Source changes remain stacked on `1ff9c21c4c6ebf334f7c5ef7fc0bdd77bfafc290`, PR21 remains for review, and no merge/deployment/activation is implied. No browser repeat was needed for these non-UI fixes.
