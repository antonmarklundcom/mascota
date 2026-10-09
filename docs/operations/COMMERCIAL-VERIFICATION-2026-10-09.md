# Commercial implementation verification — 9 October 2026

Branch `codex/commercial-measurement-20261009`, based on PHP portfolio branch `codex/mascota-php-seo` at `6a71faf4ec38695ec01484dda5524c870df79430`. This follow-up is stacked on PR20, because main still contains the retained Next.js store. Neither PHP PR is assumed merged or deployed.

| Check | Result |
| --- | --- |
| PHP 8.3 syntax | PASS 6 application/router/config files |
| Existing content, tools, search and SEO regression | PASS 1,703 assertions |
| New commercial privacy, gates, concurrent counts and private report checks | PASS 45 assertions |
| Extracted 18-file release | PASS 81 assertions |
| Actual Chrome mobile/desktop commercial profile | PASS 14 assertions |

Synthetic copies test approved/paid/current/recently verified contact, disabled defaults, expiry, malformed destinations, request-controlled redirect attempts, HEAD/no-count and POST rejection, no session/cookie/visitor record, missing/corrupt counters, 24 independent concurrent PHP increments, no lost aggregate updates, strict ledger schema, costs unknown versus verified zero, billed versus collected/refunds, clicks versus confirmed outcomes and safe private exports. New Spanish labels were corrected for UTF-8 and have regression coverage. Synthetic mobile/desktop screenshots were visually reviewed.

The allowlisted package adds only `mascota-app/app/commercial.php`; Python CLI, tests, real partners, ledgers, counter files, local configuration, agreements and backups remain outside the public/private application release. The final post-commit artifact is checked separately with the same extracted-package suite and identified in the local operating manual.

```sh
python php-site/tests/smoke.py --php php
python php-site/tests/commercial_smoke.py --php php
python php-site/tools/package.py --output /absolute/release-folder
python php-site/tests/package_smoke.py --php php --zip /absolute/release-folder/mascota-hostinger-2026-10-09.zip
```

Sponsorship, clinic contact and click tracking remain off and sponsor content remains empty. No database is required for the PHP launch; do not run retained Next.js/MySQL migrations against it. No real ledger/costs/rates/salary, partner permission, qualified-lead conversion, delivery or payment is established. The private monthly report helps measure a real pilot; it does not prove profit or fund a salary. Real Hostinger runtime/rewrites/HTTPS, private paths/ACLs, filesystem replacement behavior, genuine partners and business activation remain owner actions. Repository Actions status is inspected separately; absence of hosted checks is not success.
