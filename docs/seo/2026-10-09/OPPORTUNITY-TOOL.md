# Offline keyword opportunity report

Status: implemented locally on 2026-10-09; no deployment, account access or Search Console measurements. Python standard library only. The script reads the source Markdown in Summary → Meaning groups → Group details order as data. It never executes instructions embedded in the export.

From `php-site`, run with Python 3:

```powershell
python tools/keyword_opportunities.py --kwp C:/path/keywords-for-ai.md --content content/articles.json --mapping ../docs/seo/2026-10-09/KEYWORD-PAGE-MAP.csv --output C:/path/private-reports/mascota
python -m unittest discover -s tests -p test_keyword_opportunities.py -v
```

Optional separate files:

```powershell
python tools/keyword_opportunities.py --kwp C:/path/keywords-for-ai.md --content content/articles.json --mapping ../docs/seo/2026-10-09/KEYWORD-PAGE-MAP.csv --gsc-queries C:/private/queries.csv --gsc-pages C:/private/pages.csv --gsc-query-pages C:/private/actual-query-page.csv --output C:/private/reports
```

`--gsc` is an alias of `--gsc-queries`. Supply only the files you actually have. A query-only CSV needs Query/Consulta, Clicks/Clics and Impressions/Impresiones. A page-only CSV needs Page/Página/URL and the same metrics. A genuinely combined CSV needs both query and page dimensions. English, Spanish and common Swedish headers are supported. Position/Posición and CTR are optional; CTR is recomputed from observed clicks and impressions. No login, API or Google account access occurs.

Inputs can use UTF-8, UTF-8 BOM or UTF-16 BOM, and comma, semicolon or tab CSV delimiters. Quote values containing the delimiter. Integer count grouping supports `1,234`, `1.234` and spaces; decimals support `1.5`, `1,5`, `1,234.56` and `1.234,56`. Mixed inconsistent formats, malformed counts, duplicate dimension rows and ragged CSV rows fail explicitly. Blank/anonymized dimensions and missing clicks/impressions are skipped and counted. Date/dimension exports need deliberate aggregation by the owner before import; the script does not silently sum overlapping exports. Use a single period, property, country, device and search-type filter; cross-file comparability is the owner's responsibility.

The two outputs are `opportunities.json` and `opportunities.md`. Keep them outside the document root and release archive. Output paths containing `public`, `public_html`, `htdocs` or `wwwroot` are rejected after path resolution. Do not configure an arbitrary custom document root around the chosen report folder. Reports may contain private query/page data, so keep them private and outside Git. Re-running replaces only those two output files; inputs remain unchanged.

## Evidence rules

- Full group and capped detail volumes are separate. Detail phrase, distinct-row and volume counts are validated exactly against source metadata. Alias lists share one row and one volume. Equal counts alone do not merge distinct rows. Overlapping phrases are reported across groups; no cross-group volume total is calculated.
- `raw_head` preserves the export head, volume, aliases and flags. `relevant_observed_seed_volume` is only the conservative subset of exact group/mapping main-keyword/variant matches without brand/medicine-contaminated or unreviewed aliases. Unmapped alias phrases exclude the row from this subset even if its primary phrase matches: identical KWP numbers alone do not prove equivalent meaning. It is neither complete relevant demand nor traffic. Unknown rows remain manual review; lexical screening is incomplete and does not substitute for reading Group details.
- Brand/competitor and medicine rows are flagged despite the export Summary's claim of no brands. City intent requires verification. The bare `san bernardo` head is explicitly ambiguous. Individual aliases retain their own flags; a contaminated alias conservatively prevents the row volume entering the relevant seed subset.
- A mapping resolves one meaning group to one page or section, or records an explicit exclusion/defer decision. Multiple rows for the same group fail; many groups may intentionally map to the same page. Absent mappings are reported separately from mapped-but-missing pages: blank paths on explicit decisions are not missing mappings. Coverage separately lists excluded and deferred groups. Existing article title/H1 seed matches are recorded in JSON; synonyms and editorial fit still require review. Missing pages are suggestions only. Brand/medicine group heads carry a do-not-target status in Markdown and JSON, with no missing-content recommendation. Mapping implementation values beginning `EXCLUDED` are explicit exclusions even for an otherwise unflagged group; values beginning `DEFERRED` suppress immediate content-gap recommendations, including the paid finder.
- Without GSC, performance is **unmeasured**, never zero. Query-only and page-only exports remain independent, with no invented query-to-page join. Possible cannibalization is reported only from actual combined query/page data with positive impressions on multiple distinct pages; it is not proof of a problem.
- CTR review requires supplied average position 1–10, at least 100 observed impressions and observed CTR below 2%. These are explicit editorial review thresholds, not a promised gain or a prediction. No revenue or traffic forecasts are produced. No summaries are merged across independent GSC exports.

## Validation on supplied KWP source

Source SHA-256: `2000fc93e4fb1f9d9fbd2208f9e59b15e3bc776d8360df8bd4a4df82a704aade`.

The complete source parses as 60 selected groups and 2,858 detail rows. The initial map contained 45 rows and left 15 groups unmapped. The current map records 60 decisions: the original 45 plus five guide mappings, eight brand exclusions and two pending-intent exclusions. All selected groups now have a documented decision; explicit blank-path exclusions are not unmapped. Changes to mapping/content should be followed by regenerating the private report. No actual GSC CSV was supplied. The synthetic suite covers alias equivalence, distinct equal-volume rows, group overlap, cap gaps, exact count mismatch failures, locations, encoding and count formats, independent and combined GSC dimensions, blank metrics, duplicate rows, flags, mapping uniqueness, exclusion/defer decisions and nonpublic output restrictions.
