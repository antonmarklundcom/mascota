# Editorial UI capabilities

Implemented locally 2026-10-09. No merge or deployment is implied.

## Content contract

Existing `paragraphs` remain plain strings. `inline_paragraphs` is a list of paragraphs, each a list of `{text}` or `{text,path}` segments. Text is escaped; only an existing internal public path and actual article/page anchor becomes a link. Invalid paths degrade to plain text. `inline_plain_text` exposes the same visible words to search. No raw HTML is accepted.

Existing species pages group cards by `species: ["perros"]` and `topic` from `razas`, `alimentacion`, `salud`, `preparacion`, `herramientas`, `convivencia`. Groups are server rendered on the original hub; no filter URLs are indexed. Titles and cards remain original routes.

## Images

`content/assets.json` has `assets` mapping keys to local `path`, integer `width`/`height`, `alt`, `creator`, `license`, `source`, optional `caption`, and optional `variants` (`path`, `width`, `height`). An article uses `image` to reference its figure and optional `og_image`; default social key is `og-` plus slug with slashes replaced by hyphens. All paths must be existing files under `/assets/`. Responsive dimensions, srcset, caption and local attribution are rendered. The main article figure is eager for LCP; all assets are served locally.

Run `python tools/build-editorial-assets.py` after title/article changes to refresh social PNGs and responsive food-label WebPs and the manifest. Pillow is a build dependency only. Cards and food illustration are original drawings by code; companions is existing repository artwork. Generic animal art never claims to depict a particular breed. Verify the original artwork ownership before broader reuse. No invented photograph or external license is supplied.

## Food cost tool

Set `tool: "food-cost"`. Three products (third optional) accept a visitor label, `priceGs`, `weightkg`, and an already established `dailygrams`. Price/kg = price/weight; 30-day cost = price/kg × grams/1000 × 30. No ration, diet, medicine or recommendation is calculated. Unknown fields produce partial/unknown results; any invalid field withholds that product results. Native numeric validity and finite positive values are checked. Reset, print and visible no-JS formulas are supported. Inputs have no names, requests or storage, and reset on reload.

## Truthful authorship and review

The default author is the organization Redacción Mascota. `content/editorial-team.json` initially has an empty `members` map. Add a real member only after verification: `{verified:true,name,role,profile}`. An article may reference `editor: "member-id"` and `review: {reviewer:"member-id",date:"YYYY-MM-DD",scope:"actual limited review scope"}`. An editor/reviewer must resolve to a verified member with all fields, a valid internal or HTTPS profile and a real nonfuture date. Missing/incomplete metadata never emits a person or reviewer claim. Source consultation is displayed separately and never implies clinical review. A role is published exactly as verified; no license or professional status is inferred.

For private maintenance run `php app/editorial.php` to emit an article report with source-check date, modification date, institutional/verified editor, scoped review status, and incomplete review attention flag. This CLI file is outside the web root; no public admin endpoint or database is introduced. Refresh actual review scope/date only after the named reviewer has completed that review. Record verification evidence in the owner's private workflow, never in the public release package.


## Maintenance queue and cache invalidation (2026-10-09)

`editorial_maintenance_row` and the CLI report validate source consultation dates: missing, impossible and future dates require attention. Clinical (`topic: salud` or medicine/vaccine guide) and Paraguay administrative/legal guides are due for source checks every 90 days; other guides every 180 days. Explicit `review_class: clinical | legal | general` overrides classification when editorial scope requires it. Due dates schedule source rechecking; they do not certify advice or claim a clinical review. A date equal to today is due now. Fields include `source_check_status`, `source_check_needs_attention`, `source_review_class`, `source_review_interval_days`, `source_review_due` and `source_review_due_now`.

A scoped review dated before the article's modification date is `stale` in the private queue and is withheld from the public current-review line and schema. Complete review metadata still requires an actual verified identity and role. `clinical_review_pending` is true for clinical guides unless a current scoped review declares `kind: clinical` and its verified member has `professional_review: true`. Set that team flag only after verifying an actual professional's eligibility for the requested clinical scope; the runtime never derives credentials from a name or role string. Empty team metadata therefore truthfully leaves clinical review pending. No public claim changes merely because a source was consulted.

Stylesheet and tool script cache queries derive from the first 16 hex characters of each local file's SHA-256. They change with asset contents and work in the local preview and sibling `public_html` release layout. Only these two fixed runtime asset paths can be hashed by this helper.
