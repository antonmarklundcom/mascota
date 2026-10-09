# Clinic contact and private commercial reporting

Implemented 9 October 2026 for owner review. Sponsorship, clinic contact and click tracking remain **disabled**. No real partner profiles, agreements, ledger, payments, messages or appointment flow are supplied. Launch remains editorial. The retained Next.js store is unchanged.

## Approved real partners only

Create `content/sponsors.local.json` in the private application only after a genuine agreement and permission to publish. Existing publication requirements remain: `sponsorship_enabled === true`, `paid: true`, `approved: true`, nonempty name/city/description, valid slug, valid current `starts`/`ends`. Private file overrides the shipped empty `sponsors.json`. Do not copy a free directory or fill pages with synthetic businesses.

New optional fields are `address` and `hours` (plain text up to 300 bytes), `services` (1-20 plain strings up to 100 bytes), `verified_on` (`YYYY-MM-DD`), `contact_approved` (boolean), `phone`, `whatsapp`, `website`. Publish address/hours/services only with a genuine check dated within the last 90 days; future/invalid dates and older data suppress these details. This date records a business-data check, not clinical review. Existing paid profile descriptions remain available when optional details need rechecking.

Phone/WhatsApp values require international `+` followed by 8-15 digits, beginning 1-9. Destinations are generated as `tel:` and `https://wa.me/`, with no message body. Website requires HTTPS, a conventional domain and no credentials, port, fragment, whitespace, control character or backslash; operators must verify ownership and destination. Escaping protects visible address/service copy. No visitor-provided destination is used.

`clinic_contact_enabled => true` separately enables buttons and `/contacto-clinica/{slug}/{phone|whatsapp|website}/`. Each redirect rechecks the active approved paid profile, recent `verified_on` and `contact_approved: true`; disabled, expired, stale or invalid contact returns 404. Buttons identify the contracted profile as advertising. The visitor chooses the establishment; there is no intake form, medical questionnaire, email sending, booking, session or payment. Urgent-care editorial guidance remains first. Redirects send `no-store`, `noindex,nofollow` and `no-referrer`; endpoints are outside the sitemap. GET counts optionally; HEAD never counts; POST is rejected.

## Optional aggregate click persistence

Leave `clinic_click_tracking_enabled => false` and `clinic_clicks_path => ''` until a real reporting need, private directory and partner permissions have been established. When enabled, use an **absolute `.json` path in an existing private directory outside the repository/application parent tree and every web document root**. Example locations are operator-managed private storage outside the hosting domain directory. Code refuses app/domain-parent/public roots and public/public_html path components; the operator must check other custom document roots, backups, OS ACLs and hosting access. No runtime directory is created automatically.

Only this structure is written: `{"version":1,"months":{"YYYY-MM":{"partner-slug":{"whatsapp":1}}}}`. Keys are calendar month in America/Asuncion, profile slug and approved channel. There are no IPs, IDs, cookies, names, symptoms, search parameters, referral URLs or raw events. Hosting access logs are separate and may contain request details; this implementation does not alter hosting logs.

A stable `.lock` file with `flock` serializes writes across requests; a temporary file in the same private directory is atomically renamed. Files request mode 0600 (verify Windows ACLs separately). Corrupt, oversized or structurally tampered stores are left untouched; measurement failure does not block direct contact. Back up/read the aggregate JSON privately, retaining the lock file during service. Test concurrency and replacement on the real filesystem before activation; local tests do not prove Hostinger storage semantics.

A count means a redirect GET request. Repeats, bots, prefetches and failed conversations can contribute. No unique-person, conversion-rate or causal attribution claim follows. When tracking is off or unreliable, omit `--clicks`; reports mark clicks unavailable rather than zero. No automatic confirmed inquiry/appointment derives from clicks. Decide retention with the operator; remove old monthly aggregate periods using an offline copy and safe replacement while tracking is disabled. Do not put count files in deployment ZIPs or public backups.

## Private manual ledger and CLI

`php-site/tools/commercial_report.py` runs locally with Python standard library. It is never packaged or served. Keep the real ledger, downloaded aggregate counts and exports outside Git/manuals, outside all web roots, in an owner-controlled private directory. CLI requires absolute paths, refuses repository/common public roots and existing output files, and prints no financial records. Reports are private `.json`; choose a fresh dated output filename.

```sh
python php-site/tools/commercial_report.py --ledger /absolute/private/commercial-ledger.json --output /absolute/private/commercial-report-2026-10.json
# Only when real counts are available and trustworthy:
python php-site/tools/commercial_report.py --ledger /absolute/private/commercial-ledger.json --clicks /absolute/private/clinic-clicks.json --output /absolute/private/commercial-report-2026-10-with-clicks.json
```

The exact ledger schema is `version: 1`, `months: [...]`. Each month has `month` (`YYYY-MM`), `costs_pyg`, `capacity_hours`, `reserve_pyg`, `partners`. Every key is required; unknown keys/duplicate months/duplicate partner slugs fail validation. `costs_pyg` has exactly `labor`, `hosting`, `production`, `taxes`, `fees`, `other`: each is a nonnegative integer or `null` for unknown. A verified zero is `0`; do not replace unknown costs with zero. `capacity_hours` is actual agreed monthly delivery capacity or null; `reserve_pyg` is verified available reserve or null. No presumed salary/cost/rate is supplied.

Each partner row has exactly `slug`, `billed_pyg`, `collected_pyg`, `refunds_pyg`, `confirmed_inquiries`, `confirmed_appointments`, `renewal`, `service_hours`. Financial amounts/counts are nonnegative integers; hours are finite nonnegative numeric values or null. Renewal is `not_due`, `pending`, `renewed` or `lost` for that monthly renewal decision. Populate only manually checked business totals. Keep underlying invoice/confirmation evidence separately private. No patient names, identifiers, symptoms or free-text case details are accepted. A confirmed appointment may relate to an earlier inquiry; outcomes are period totals, not linked patient records. Collect consent/verification and settle duplicate/spam/dispute rules operationally before claiming qualified leads.

Outputs separate billing, collected cash, refunds and net collections; show renewal decisions, recorded hours, missing hours/cost categories and remaining capacity only when hours are complete. They also show counts by partner/channel when provided, and click profiles absent from ledger rows. Collections can belong to earlier invoices: billed-minus-collected is a period comparison, **not an overdue-debt/aged receivables balance**. Amounts exclude taxes collected for government. `cash_after_recorded_costs_pyg` is arithmetic residue with missing-cost warnings. `margin_after_declared_costs_pyg/percent` is null whenever any required cost category is unknown; a complete declared-cost margin is still **not certified net profit or a guaranteed available salary**. Reserve coverage uses only complete declared monthly costs, not a forecast. Supply actual scope, hours, employment/contractual costs and taxes with the appropriate operator/adviser.

Monthly service packages, partner approval, content deliverables, invoices, renewals, collections and refund evidence remain manual operations outside this code. There is no new CMS/login, background job, CRM, payment, automatic renewal or email. Reports validate a pilot; they do not make it commercially active.

## Release and verification

The allowlisted release adds only private `mascota-app/app/commercial.php`. Public contact requests still use `public_html/index.php`. The integrated ZIP contains **82 files** including the runbook; no CLI, tests, ledger, counts, report, lock, real local config or sponsor agreement. Preserve private local config/partner data and external aggregate storage during updates/rollback. Back up financial records separately under owner control, never in a public restore directory or manual snapshot.

```sh
python php-site/tests/smoke.py --php php
python php-site/tests/commercial_smoke.py --php php
python php-site/tools/package.py --output /absolute/private/release
python php-site/tests/package_smoke.py --php php --zip /absolute/private/release/mascota-hostinger-<version>.zip
```

Synthetic fixtures live only in temporary copies. Tests cover disabled/default gates, approval/payment/agreement expiry, verified-data expiry, malformed phone/website and request-controlled redirect attempts, no cookies/identifiers, HEAD/POST, excluded public endpoints, corrupted count preservation, concurrent workers, collected versus billed versus refunds, clicks versus confirmed outcomes, missing costs/hours, ledger validation and safe CLI export. Production PHP/filesystem/HTTPS/ACLs, real partner permission and live destination checks remain owner work before activation.

## Updated PHP parent integration - 9 October 2026

Rebased from original PHP portfolio base onto `1ff9c21c4c6ebf334f7c5ef7fc0bdd77bfafc290`. The integrated release preserves the parent editorial module, registered local assets, 67 public pages, three planning/comparison tools, offline keyword opportunities and deterministic package/manifest verification. `release_metadata.py` owns the explicit application allowlist plus registered assets; the commercial module is added there. Package version and runtime header use the computed commit/fingerprint metadata. CLI, commercial ledgers/counts/reports/locks remain excluded. Earlier fixed-name 18-file packages are superseded and retained separately; use only the new ZIP and matching manifest.
