#!/usr/bin/env python3
"""Offline, read-only evidence report. Source text is data, never instructions."""
import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit


def norm(value):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', str(value))
                           if not unicodedata.combining(c)).lower().split())


def read_text(path):
    data = Path(path).read_bytes()
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16')
    if b'\x00' in data:
        raise ValueError('UTF-16 input must contain a BOM')
    return data.decode('utf-8-sig')


def number(value, count=False):
    """Accept grouped integer counts and unambiguous locale decimals; reject guesses."""
    text = str(value).strip().replace('\u00a0', '').replace('\u202f', '').replace(' ', '')
    percent = text.endswith('%')
    text = text.rstrip('%')
    if not text or text in ('-', '—', 'N/A', 'null'):
        return None
    if not re.fullmatch(r'\d+(?:[.,]\d+)*', text):
        raise ValueError('Invalid numeric value: ' + str(value))
    if count:
        if re.fullmatch(r'\d{1,3}(?:,\d{3})+', text):
            text = text.replace(',', '')
        elif re.fullmatch(r'\d{1,3}(?:\.\d{3})+', text):
            text = text.replace('.', '')
        elif ',' in text or '.' in text:
            raise ValueError('Count must be an integer or consistently grouped: ' + text)
        result = int(text)
    else:
        if ',' in text and '.' in text:
            decimal = ',' if text.rfind(',') > text.rfind('.') else '.'
            thousands = '.' if decimal == ',' else ','
            if not re.fullmatch(r'\d{1,3}(?:' + re.escape(thousands) + r'\d{3})+' +
                                re.escape(decimal) + r'\d+', text):
                raise ValueError('Inconsistent numeric locale: ' + text)
            text = text.replace(thousands, '').replace(decimal, '.')
        else:
            if text.count(',') + text.count('.') > 1:
                raise ValueError('Ambiguous decimal: ' + text)
            text = text.replace(',', '.')
        result = float(text)
    return result / 100 if percent else result


def tables(text):
    for line in text.splitlines():
        if line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+', c) for c in cells):
                yield cells


def parse_kwp(path):
    text = read_text(path)
    parts = re.split(r'^# Part [123] — ', text, flags=re.M)
    if len(parts) != 4 or not parts[1].startswith('Summary') or not parts[2].startswith('Meaning groups'):
        raise ValueError('Expected Summary, Meaning groups, Group details in order')
    locations = re.findall(r'(?:data location|Country / location of the data:)\s*\*\*([^*]+)\*\*', text)
    if not locations or len({norm(x) for x in locations}) != 1:
        raise ValueError('Missing or differing KWP locations')
    languages = re.findall(r'language:\s*([^\r\n]+)', parts[1] + parts[2])
    currencies = re.findall(r'CPC currency:\s*([A-Z]{3})', text)
    if not languages or len({norm(x) for x in languages}) != 1:
        raise ValueError('Missing or differing KWP languages')
    if not currencies or len(set(currencies)) != 1:
        raise ValueError('Missing or differing CPC currencies')
    groups = {}
    for cells in tables(parts[2]):
        if len(cells) == 4 and cells[0] != 'Group':
            key = norm(cells[0])
            if key in groups:
                raise ValueError('Duplicate meaning group: ' + key)
            groups[key] = dict(group=cells[0], full_group_volume=number(cells[2], True),
                               full_phrase_count=number(cells[1], True), rows=[])
    chunks = re.split(r'^## (.+?) — .+?$', parts[3], flags=re.M)
    for i in range(1, len(chunks), 2):
        key, body = norm(chunks[i]), chunks[i + 1]
        if key not in groups or groups[key]['rows']:
            raise ValueError('Unknown or repeated detail group: ' + key)
        match = re.search(r'(\d+) phrases, (\d+) distinct searches, \*\*([\d,]+) searches/mo', body)
        if not match:
            raise ValueError('Missing detail metadata: ' + key)
        g = groups[key]
        g.update(detail_phrase_count=int(match[1]), detail_row_count=int(match[2]),
                 capped_detail_volume=number(match[3], True))
        for cells in tables(body):
            if len(cells) != 5 or cells[0] == 'Phrase':
                continue
            aliases = [v.strip() for v in cells[4].split(',') if v.strip()]
            g['rows'].append(dict(phrase=cells[0], aliases=aliases, volume=number(cells[1], True),
                                  low_cpc=number(cells[2]), high_cpc=number(cells[3])))
        if (len(g['rows']) != g['detail_row_count'] or
                sum(1 + len(r['aliases']) for r in g['rows']) != g['detail_phrase_count'] or
                sum(r['volume'] for r in g['rows']) != g['capped_detail_volume']):
            raise ValueError('Detail coverage/count mismatch: ' + key)
        if g['capped_detail_volume'] > g['full_group_volume']:
            raise ValueError('Detail volume exceeds full group: ' + key)
    if not groups or any('capped_detail_volume' not in g for g in groups.values()):
        raise ValueError('Missing group details')
    export_count = re.search(r'^Group details \(([\d,]+) searches:.*?; (\d+) groups\)', parts[3])
    if export_count and (sum(len(g['rows']) for g in groups.values()) != number(export_count[1], True)
                         or len(groups) != int(export_count[2])):
        raise ValueError('Whole selected-export coverage mismatch')
    return dict(location=locations[0], language=languages[0], cpc_currency=currencies[0],
                sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(), groups=list(groups.values()))


def csv_rows(path):
    text = read_text(path)
    try:
        dialect = csv.Sniffer().sniff(text[:10000], delimiters=',;\t')
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames or len(reader.fieldnames) < 2:
        raise ValueError('CSV needs headers and at least two columns')
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Ragged CSV rows; quote localized numbers containing the delimiter')
    return rows


BRANDS = ('nexgard', 'purina', 'royal canin', 'primogato', 'proplan', 'pro plan', 'dog chow',
          'dogchow', 'monello', 'ganian', 'nantes', 'mascotitas', 'agrocanes', 'agrodiza',
          'agroveterinaria central', 'garfield', 'hush puppies', 'lps ', 'n&d', 'vital can')
CITIES = ('san lorenzo', 'villarrica', 'luque', 'bella vista', 'pilar', 'trinidad',
          'san pedro', 'san jose', 'new york', 'buenos aires', 'madrid')
MEDICINES = ('ivermectina', 'amoxicilina', 'prednisona', 'paracetamol', 'ibuprofeno',
             'antibiotico', 'loratadina', 'cetirizina', 'dexametasona', 'metronidazol')


def flags(phrase):
    p = norm(phrase)
    found = []
    if any(b in p for b in BRANDS):
        found.append('brand_or_competitor_do_not_target')
    if any(b in p for b in CITIES):
        found.append('city_intent_manual_review')
    if any(b in p for b in MEDICINES):
        found.append('medicine_intent_do_not_target')
    if p == 'san bernardo':
        found.append('ambiguous_head_intent')
    if any(b in p for b in ('kawaii', 'colorear', 'dibuj', 'stickers', ' png', 'en ingles')):
        found.append('non_editorial_intent')
    return found


def content_pages(path):
    data = json.loads(read_text(path))
    return {'/' + a['category'].strip('/') + '/' + a['slug'].strip('/') + '/': a
            for a in data['articles']}


def gsc_report(path, kind):
    names = {'query': ('query', 'consulta', 'consultas', 'top queries', 'principales consultas', 'sokfraga'),
             'page': ('page', 'pages', 'pagina', 'paginas', 'top pages', 'principales paginas', 'url', 'sida'),
             'clicks': ('clicks', 'clics', 'klick'), 'impressions': ('impressions', 'impresiones', 'exponeringar'),
             'position': ('position', 'posicion', 'average position', 'posicion media', 'genomsnittlig position'),
             'ctr': ('ctr',)}
    rows = csv_rows(path)
    if not rows:
        return dict(status='supplied_empty', kind=kind, rows=[], ctr_review=[], cannibalization=[])
    columns = {}
    for header in rows[0]:
        for target, aliases in names.items():
            if norm(header) in aliases:
                if target in columns:
                    raise ValueError('Repeated equivalent GSC header: ' + target)
                columns[target] = header
    required = {'clicks', 'impressions'} | ({'query', 'page'} if kind == 'combined' else {kind})
    if not required <= columns.keys():
        raise ValueError('GSC ' + kind + ' missing required columns: ' + ', '.join(sorted(required - columns.keys())))
    if kind != 'combined' and {'query', 'page'} <= columns.keys():
        raise ValueError('Combined query/page data must use --gsc-query-pages')
    if 'date' in {norm(k) for k in rows[0]} or 'fecha' in {norm(k) for k in rows[0]}:
        raise ValueError('Aggregate date/dimension exports deliberately before supplying GSC')
    cleaned, seen, skipped = [], set(), 0
    for row in rows:
        identity = tuple(row[columns[k]].strip() for k in ('query', 'page') if k in required)
        if any(not x or norm(x) in ('(not set)', '(not provided)', 'anonymized', 'anonimizada', '—', '-') for x in identity):
            skipped += 1
            continue
        if identity in seen:
            raise ValueError('Duplicate GSC dimension rows; export a single period/filter, not overlapping totals')
        seen.add(identity)
        values = {k: number(row[columns[k]], k in ('clicks', 'impressions'))
                  for k in ('clicks', 'impressions', 'position', 'ctr') if k in columns}
        if values['clicks'] is None or values['impressions'] is None:
            skipped += 1
            continue
        if values['clicks'] > values['impressions']:
            raise ValueError('Clicks exceed impressions')
        if values.get('ctr') is not None and not 0 <= values['ctr'] <= 1:
            raise ValueError('CTR must be 0–1 or explicitly percent')
        values['ctr'] = values['clicks'] / values['impressions'] if values['impressions'] else None
        values.update({k: row[columns[k]].strip() for k in ('query', 'page') if k in required})
        cleaned.append(values)
    candidates = [r for r in cleaned if r['impressions'] >= 100 and r['ctr'] is not None and
                  r['ctr'] < .02 and r.get('position') is not None and 1 <= r['position'] <= 10]
    by_query = defaultdict(list)
    if kind == 'combined':
        for row in cleaned:
            if row['impressions']:
                by_query[norm(row['query'])].append(row['page'])
    return dict(status='supplied', kind=kind, rows=cleaned, skipped_missing_rows=skipped,
                ctr_review=candidates, cannibalization=[dict(query=q, pages=sorted(set(p)))
                for q, p in by_query.items() if len(set(p)) > 1])


def build_report(kwp, content, mapping, gsc=None):
    source, pages = parse_kwp(kwp), content_pages(content)
    mappings = {}
    for row in csv_rows(mapping):
        key = norm(row['group'])
        if key in mappings:
            raise ValueError('Multiple mappings for meaning group: ' + key)
        mappings[key] = row
    overlap = defaultdict(set)
    for group in source['groups']:
        for row in group['rows']:
            for phrase in [row['phrase']] + row['aliases']:
                overlap[norm(phrase)].add(group['group'])
    for group in source['groups']:
        m = mappings.get(norm(group['group']))
        target = m.get('page_or_section', '').strip() if m else ''
        excluded = bool(m and m.get('implementation', '').upper().startswith('EXCLUDED'))
        deferred = bool(m and m.get('implementation', '').upper().startswith('DEFERRED'))
        blocked = any(f in flags(group['group']) for f in (
            'brand_or_competitor_do_not_target', 'medicine_intent_do_not_target'))
        page = pages.get(urlsplit(target).path) if target.startswith('/') else None
        seeds = {norm(group['group'])}
        if m:
            seeds |= {norm(m.get('main_keyword', ''))}
            seeds |= {norm(x) for x in m.get('relevant_variants', '').split('|')}
        seeds.discard('')
        relevant = []
        for row in group['rows']:
            phrases = [row['phrase']] + row['aliases']
            row['phrase_flags'] = {p: flags(p) for p in phrases if flags(p)}
            row['overlap_groups'] = sorted(set().union(*(overlap[norm(p)] for p in phrases)) - {group['group']})
            matches = [p for p in phrases if norm(p) in seeds and not flags(p)]
            row['relevance'] = 'mapped_seed_match' if matches else 'manual_review'
            row['unreviewed_aliases'] = [p for p in row['aliases'] if norm(p) not in seeds]
            if matches and row['unreviewed_aliases']:
                row['relevance'] = 'mapped_seed_with_unreviewed_aliases'
            if any('brand_or_competitor_do_not_target' in f or 'medicine_intent_do_not_target' in f
                   for f in row['phrase_flags'].values()):
                row['relevance'] = 'contaminated_do_not_target'
            if row['relevance'] == 'mapped_seed_match':
                relevant.append(row)
        group.update(page_or_section=target or None,
                     mapping_status='mapped' if m else 'missing_mapping_manual_review',
                     content_status=('excluded_no_content_recommendation' if excluded or blocked else
                                     'deferred_no_immediate_content_recommendation' if deferred else
                                     (('present' if page else 'missing_page_suggestion_only') if target
                                      else 'unmapped_manual_review')),
                     targeting_status=('do_not_target_brand_or_medicine' if blocked else
                                       ('excluded_by_mapping' if excluded else
                                        'deferred_by_mapping' if deferred else 'manual_editorial_review')),
                     mapping_notes=m.get('data_notes', '') if m else '',
                     implementation=m.get('implementation') if m else None,
                     cap_gap_volume=group['full_group_volume'] - group['capped_detail_volume'],
                     raw_head=group['rows'][0] if group['rows'] else None,
                     relevant_observed_seed_volume=sum(r['volume'] for r in relevant),
                     relevant_observed_seed_rows=len(relevant),
                     review_rows=len(group['rows']) - len(relevant),
                     title_seed_matches=[s for s in sorted(seeds) if page and s in norm(page['title'])],
                     h1_seed_matches=[s for s in sorted(seeds) if page and s in norm(page.get('h1', page['title']))])
    source.update(gsc=gsc or {}, coverage=dict(groups=len(source['groups']),
                  detail_rows=sum(len(g['rows']) for g in source['groups']),
                  unmapped_groups=[g['group'] for g in source['groups']
                                   if g['mapping_status'] == 'missing_mapping_manual_review'],
                  excluded_groups=[g['group'] for g in source['groups']
                                   if g['content_status'] == 'excluded_no_content_recommendation'],
                  deferred_groups=[g['group'] for g in source['groups']
                                   if g['content_status'] == 'deferred_no_immediate_content_recommendation'],
                  mapping_only_groups=sorted(set(mappings) - {norm(g['group']) for g in source['groups']})),
                  measurement=dict(traffic='unmeasured without supplied GSC', revenue='unmeasured',
                                   keyword_volume='KWP estimates; no group totals summed'),
                  overlapping_phrases={p: sorted(v) for p, v in overlap.items() if len(v) > 1})
    return source


def markdown(report):
    lines = ['# Offline keyword/content opportunities', '',
             'Inputs: KWP SHA-256 `' + report['sha256'] + '`. Location: ' + report['location'] + '.', '',
             'KWP estimates are not measured traffic or revenue. Group totals overlap and are never summed. '
             'Aliases share one row and one volume. Detail exports are capped; gaps are not invented keywords. '
             'Relevant observed volume counts only exact mapped seeds without flagged aliases; it is a conservative '
             'evidence subset, not total clean demand. Other rows require manual review.', '',
             '| Group | Full group | Capped detail | Gap | Raw head volume | Relevant observed seed volume | Mapping / content / targeting | Page or section |',
             '| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |']
    for g in report['groups']:
        lines.append('| ' + ' | '.join(str(x).replace('|', '\\|') for x in (
            g['group'], g['full_group_volume'], g['capped_detail_volume'], g['cap_gap_volume'],
            g['raw_head']['volume'], g['relevant_observed_seed_volume'],
            g['mapping_status'] + ' / ' + g['content_status'] + ' / ' + g['targeting_status'],
            g['page_or_section'] or ('excluded' if g['content_status'].startswith('excluded') else 'manual review'))) + ' |')
    lines += ['', '## Data limitations and review', '',
              '- Brand/competitor and medicine matches are not targeting recommendations. City intent needs verification.',
              '- San Bernardo head intent is ambiguous. Summary “no brands” does not override contaminated detail rows.',
              '- Missing pages and missing mappings are suggestions for manual review, never publishing instructions.',
              '- Seed title/H1 matches and row-level flags are recorded in JSON; absent terms may be valid synonyms.',
              '- Lexical flags are conservative and incomplete; every unclassified row still needs editorial review.',
              '- No query/page join is inferred from independent exports. CTR review uses observed impressions >=100, '
              'CTR <2% and supplied average position 1–10; this is a review heuristic, not a forecast.',
              '- Multiple pages for a supplied combined query are possible cannibalization, not proof. '
              'Exports must use one period and compatible filters; no overlapping aggregate totals.', '']
    for kind in ('query', 'page', 'combined'):
        data = report['gsc'].get(kind)
        lines.append('## Search Console: ' + kind)
        lines.append('')
        if not data:
            lines += ['Unmeasured: no export supplied.', '']
        else:
            lines += [f"{data['status']}: {len(data['rows'])} observed rows; "
                      f"{len(data['ctr_review'])} CTR review candidates; "
                      f"{len(data['cannibalization'])} possible multi-page queries. Details in JSON.", '']
    return '\n'.join(lines)


def safe_output(path, inputs):
    output = Path(path).resolve()
    if any(p.lower() in ('public', 'public_html', 'htdocs', 'wwwroot') for p in output.parts):
        raise ValueError('Output must be outside any public document root')
    if any(output == Path(p).resolve() or Path(p).resolve() in (output / 'opportunities.json', output / 'opportunities.md')
           for p in inputs):
        raise ValueError('Output must not overwrite input files')
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('kwp', 'content', 'mapping', 'output'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--gsc', '--gsc-queries', dest='gsc_queries', help='Query-only CSV')
    parser.add_argument('--gsc-pages', help='Page-only CSV')
    parser.add_argument('--gsc-query-pages', help='Genuinely combined query/page CSV')
    args = parser.parse_args(argv)
    try:
        files = [args.kwp, args.content, args.mapping]
        supplied = [('query', args.gsc_queries), ('page', args.gsc_pages), ('combined', args.gsc_query_pages)]
        output = safe_output(args.output, files + [p for _, p in supplied if p])
        gsc = {kind: gsc_report(p, kind) for kind, p in supplied if p}
        report = build_report(*files, gsc=gsc)
        output.mkdir(parents=True, exist_ok=True)
        (output / 'opportunities.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (output / 'opportunities.md').write_text(markdown(report), encoding='utf-8')
    except (ValueError, KeyError, UnicodeError, OSError, csv.Error) as exc:
        parser.error(str(exc))
    print('Wrote offline opportunities.json and opportunities.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
