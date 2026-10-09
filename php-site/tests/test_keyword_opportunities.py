"""Synthetic evidence tests; never use private Search Console exports in fixtures."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'tools' / 'keyword_opportunities.py'
if not MODULE.exists():
    MODULE = Path(__file__).with_name('keyword_opportunities.py')
spec = importlib.util.spec_from_file_location('keyword_opportunities', MODULE)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

KWP = '''# Part 1 — Summary
- Country / location of the data: **Paraguay** · language: Spanish
# Part 2 — Meaning groups
| Group | Phrases | Searches/mo | Top searches |
| --- | --- | --- | --- |
| gatos | 8 | 1,000 | gatos (100) |
| san bernardo | 3 | 300 | san bernardo (200) |
# Part 3 — Group details
## gatos — Example
- data location **Paraguay** · CPC currency: SEK
- 4 phrases, 3 distinct searches, **170 searches/mo (deduplicated)**.
| Phrase | Searches/mo | Low CPC | High CPC | Same numbers (Google groups them) |
| --- | --- | --- | --- | --- |
| gatos | 100 | 0.10 | 0.20 | gato |
| purina gatos | 50 | 0.10 | 0.20 | |
| mascota | 20 | 0.10 | 0.20 | |
## san bernardo — Example
- data location **Paraguay** · CPC currency: SEK
- 3 phrases, 3 distinct searches, **300 searches/mo (deduplicated)**.
| Phrase | Searches/mo | Low CPC | High CPC | Same numbers (Google groups them) |
| --- | --- | --- | --- | --- |
| san bernardo | 200 | 0.10 | 0.20 | |
| mascota | 20 | 0.10 | 0.20 | |
| perro san bernardo | 80 | 0.10 | 0.20 | |
'''


class Opportunities(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.kwp = self.write('kwp.md', KWP)
        self.content = self.write('content.json', json.dumps({'articles': [
            {'category': 'mascotas', 'slug': 'gatos', 'title': 'Gatos', 'h1': 'Gatos en casa'}]}))
        self.mapping = self.write('map.csv', 'group,main_keyword,relevant_variants,page_or_section\n'
            'gatos,gatos,gato,/mascotas/gatos/\n')

    def write(self, name, value, encoding='utf-8'):
        path = self.base / name
        path.write_text(value, encoding=encoding)
        return path

    def report(self):
        return tool.build_report(self.kwp, self.content, self.mapping)

    def test_alias_one_volume_cap_and_exact_coverage(self):
        report = self.report()
        cat = report['groups'][0]
        self.assertEqual(report['coverage']['detail_rows'], 6)
        self.assertEqual(cat['capped_detail_volume'], 170)
        self.assertEqual(cat['relevant_observed_seed_volume'], 100)
        self.assertEqual(cat['rows'][0]['aliases'], ['gato'])
        self.assertEqual(cat['cap_gap_volume'], 830)
        self.assertEqual(cat['content_status'], 'present')

    def test_overlap_not_summed_and_missing_mapping(self):
        report = self.report()
        self.assertEqual(report['overlapping_phrases']['mascota'], ['gatos', 'san bernardo'])
        dog = report['groups'][1]
        self.assertEqual(dog['mapping_status'], 'missing_mapping_manual_review')
        self.assertIn('ambiguous_head_intent', dog['raw_head']['phrase_flags']['san bernardo'])
        self.assertNotIn('total_volume', report)
        self.assertEqual(report['coverage']['unmapped_groups'], ['san bernardo'])

    def test_same_numbers_distinct_rows_remain_distinct(self):
        self.kwp.write_text(KWP.replace('purina gatos | 50', 'purina gatos | 100').replace(
            '**170 searches', '**220 searches'), encoding='utf-8')
        self.assertEqual(self.report()['groups'][0]['capped_detail_volume'], 220)

    def test_unreviewed_same_number_alias_not_assumed_relevant(self):
        self.kwp.write_text(KWP.replace('0.20 | gato |', '0.20 | caballo |'), encoding='utf-8')
        cat = self.report()['groups'][0]
        self.assertEqual(cat['relevant_observed_seed_volume'], 0)
        self.assertEqual(cat['rows'][0]['relevance'], 'mapped_seed_with_unreviewed_aliases')
        self.assertEqual(cat['rows'][0]['volume'], 100)

    def test_counts_and_encodings(self):
        self.assertEqual(tool.number('1.234', True), 1234)
        self.assertEqual(tool.number('1,234', True), 1234)
        self.assertEqual(tool.number('1\u202f234', True), 1234)
        self.assertEqual(tool.number('1.234,56'), 1234.56)
        self.assertEqual(tool.number('1,234.56'), 1234.56)
        self.assertEqual(tool.number('1,5%'), .015)
        for value in ('1,23', '1.2.34', '-10', 'NaN'):
            with self.assertRaises(ValueError):
                tool.number(value, True)
        for enc in ('utf-8-sig', 'utf-16'):
            path = self.write('encoded.md', KWP, enc)
            self.assertEqual(len(tool.parse_kwp(path)['groups']), 2)

    def test_corrupt_coverage_and_different_location_rejected(self):
        for text in (KWP.replace('4 phrases', '5 phrases'), KWP.replace('170 searches', '180 searches'),
                     KWP.replace('data location **Paraguay**', 'data location **Chile**', 1),
                     KWP.replace('## gatos — Example', '## unknown — Example')):
            self.kwp.write_text(text, encoding='utf-8')
            with self.assertRaises(ValueError):
                self.report()

    def test_independent_query_page_exports_never_join(self):
        query = self.write('queries.csv', 'Consulta;Clics;Impresiones;CTR;Posición\n'
                           'gatos;1;200;0,5%;4,5\n;0;50;0%;5\n', 'utf-16')
        page = self.write('pages.csv', 'Page,Clicks,Impressions,CTR,Position\n'
                          'https://example.test/mascotas/gatos/,1,200,0.5%,4.5\n', 'utf-8-sig')
        q, p = tool.gsc_report(query, 'query'), tool.gsc_report(page, 'page')
        self.assertEqual(q['skipped_missing_rows'], 1)
        self.assertEqual(len(q['ctr_review']), 1)
        self.assertEqual(q['cannibalization'], [])
        self.assertEqual(p['cannibalization'], [])
        self.assertNotIn('page', q['rows'][0])
        self.assertNotIn('query', p['rows'][0])

    def test_combined_only_supports_possible_cannibalization(self):
        path = self.write('combined.csv', 'Query,Page,Clicks,Impressions,Position\n'
                          'gatos,https://example.test/a/,1,200,4\n'
                          'gatos,https://example.test/b/,0,120,7\n')
        report = tool.gsc_report(path, 'combined')
        self.assertEqual(len(report['cannibalization']), 1)
        with self.assertRaises(ValueError):
            tool.gsc_report(path, 'query')
        self.write('combined.csv', path.read_text() + 'gatos,https://example.test/a/,1,20,3\n')
        with self.assertRaises(ValueError):
            tool.gsc_report(path, 'combined')

    def test_missing_metrics_not_zero_and_ragged_csv_rejected(self):
        p = self.write('queries.csv', 'Query,Clicks,Impressions\ncat,,100\n')
        self.assertEqual(tool.gsc_report(p, 'query')['rows'], [])
        self.assertEqual(self.report()['gsc'], {})
        self.assertIn('Unmeasured: no export supplied', tool.markdown(self.report()))
        self.write('queries.csv', 'Query,Clicks,Impressions\ncat,1,100,200\n')
        with self.assertRaises(ValueError):
            tool.gsc_report(p, 'query')

    def test_nonpublic_output_and_no_input_mutations(self):
        original = self.kwp.read_bytes()
        with self.assertRaises(ValueError):
            tool.safe_output(self.base / 'public_html' / 'reports', [])
        with self.assertRaises(ValueError):
            tool.safe_output(self.base, [self.base / 'opportunities.json'])
        out = self.base / 'private-reports'
        tool.main(['--kwp', str(self.kwp), '--content', str(self.content), '--mapping', str(self.mapping),
                   '--output', str(out)])
        self.assertEqual(self.kwp.read_bytes(), original)
        self.assertTrue((out / 'opportunities.md').exists())
        self.assertEqual(json.loads((out / 'opportunities.json').read_text())['coverage']['groups'], 2)

    def test_flags_and_mapping_uniqueness(self):
        self.assertIn('city_intent_manual_review', tool.flags('veterinaria San Lorenzo'))
        self.assertIn('medicine_intent_do_not_target', tool.flags('ibuprofeno para perros'))
        self.assertIn('brand_or_competitor_do_not_target', tool.flags('Nexgard para perros'))
        self.mapping.write_text(self.mapping.read_text() + 'gatos,gatos,,/otra/\n')
        with self.assertRaises(ValueError):
            self.report()

    def test_brand_group_and_mapping_exclusion_never_recommend_content(self):
        self.kwp.write_text(KWP.replace('san bernardo', 'royal canin'), encoding='utf-8')
        report = self.report()
        brand = report['groups'][1]
        self.assertEqual(brand['content_status'], 'excluded_no_content_recommendation')
        self.assertEqual(brand['targeting_status'], 'do_not_target_brand_or_medicine')
        self.assertIn('do_not_target_brand_or_medicine', tool.markdown(report))
        self.mapping.write_text('group,main_keyword,relevant_variants,page_or_section,implementation\n'
                                'gatos,gatos,,,EXCLUDED_MANUAL_REVIEW\n')
        report = self.report()
        self.assertEqual(report['groups'][0]['targeting_status'], 'excluded_by_mapping')
        self.assertEqual(report['coverage']['unmapped_groups'], ['royal canin'])
        self.assertEqual(report['coverage']['excluded_groups'], ['gatos', 'royal canin'])

    def test_explicit_excluded_and_deferred_decisions_are_not_missing_mappings(self):
        self.mapping.write_text('group,main_keyword,relevant_variants,page_or_section,implementation\n'
                                'gatos,gatos,,,EXCLUDED_PENDING_INTENT_REVIEW\n'
                                'san bernardo,san bernardo,,/directorio/,DEFERRED_PAID_FINDER\n')
        report = self.report()
        self.assertEqual(report['coverage']['unmapped_groups'], [])
        self.assertEqual(report['coverage']['excluded_groups'], ['gatos'])
        self.assertEqual(report['coverage']['deferred_groups'], ['san bernardo'])
        self.assertEqual(report['groups'][1]['content_status'], 'deferred_no_immediate_content_recommendation')


if __name__ == '__main__':
    unittest.main()
