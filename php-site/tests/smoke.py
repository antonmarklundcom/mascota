"""Portable SEO, route, security and paid-placement checks. Synthetic fixtures only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, quote
import argparse
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('--php', default='php')
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
args = parser.parse_args()
checks = 0
def check(condition, label):
    global checks
    if not condition: raise AssertionError(label)
    checks += 1

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.images=[]; self.canonical=''; self.description=''; self.robots=''; self.h1=0; self.title=''; self.in_title=False; self.schemas=[]; self.ld=False; self.ld_text=''
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.links.append(a.get('href',''))
        if tag=='img': self.images.append(a.get('src','')); check(bool(a.get('alt')), 'image alt')
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a.get('href','')
        if tag=='meta' and a.get('name')=='description': self.description=a.get('content','')
        if tag=='meta' and a.get('name')=='robots': self.robots=a.get('content','')
        if tag=='h1': self.h1+=1
        if tag=='title': self.in_title=True
        if tag=='script' and a.get('type')=='application/ld+json': self.ld=True; self.ld_text=''
    def handle_data(self, data):
        if self.in_title: self.title+=data
        if self.ld: self.ld_text+=data
    def handle_endtag(self, tag):
        if tag=='title': self.in_title=False
        if tag=='script' and self.ld: self.schemas.append(json.loads(self.ld_text)); self.ld=False

root=args.root.resolve()
data=json.loads((root/'content/articles.json').read_text(encoding='utf-8'))
slugs=[a['slug'] for a in data['articles']]
check(len(slugs)==len(set(slugs)), 'unique slugs')
titles=[a['title'] for a in data['articles']]
check(len(titles)==len(set(titles)), 'unique titles')
descriptions=[a['description'] for a in data['articles']]
check(len(descriptions)==len(set(descriptions)), 'unique descriptions')
for a in data['articles']:
    check(len(a['sections'])>=4, f'substantive sections {a["slug"]}')
    check(all(s in data['sources'] for s in a['sources']), f'source references {a["slug"]}')
    check(all(s in slugs for s in a['related']), f'related references {a["slug"]}')
    text=' '.join([a['answer'],a['intro'],*[p for s in a['sections'] for p in s['paragraphs']],*[p for s in a['sections'] for p in s.get('bullets',[])],*[cell for s in a['sections'] for row in s.get('table',{}).get('rows',[]) for cell in row],*[f['a'] for f in a['faqs']]])
    check(len(text.split())>=350, f'article minimum substance {a["slug"]}: {len(text.split())}')
check(json.loads((root/'content/sponsors.json').read_text())==[], 'no free/demo listings shipped')
for phpfile in root.rglob('*.php'):
    check(subprocess.run([args.php,'-l',str(phpfile)],capture_output=True).returncode==0, f'PHP lint {phpfile.name}')

with tempfile.TemporaryDirectory(prefix='mascota-smoke-') as temporary:
    isolated=Path(temporary)/'php-site'; shutil.copytree(root, isolated)
    with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    log=open(Path(temporary)/'server.log','w',encoding='utf-8')
    server=subprocess.Popen([args.php,'-S',f'127.0.0.1:{port}','-t',str(isolated/'public'),str(isolated/'router.php')],stdout=log,stderr=log,env={**os.environ,'MASCOTA_ENV':'production'})
    def fetch(path, method='GET', production=True):
        headers={'Host':'mascota.com.py'} if production else {}
        request=urllib.request.Request(base+path,headers=headers,method=method)
        try: response=urllib.request.urlopen(request,timeout=10)
        except urllib.error.HTTPError as error: response=error
        return response.status, dict(response.headers), response.read().decode('utf-8',errors='replace')
    try:
        for _ in range(60):
            try: fetch('/'); break
            except (ConnectionError,urllib.error.URLError): time.sleep(.1)
        else: raise AssertionError('preview failed to start')
        code,headers,body=fetch('/sitemap.xml')
        check(code==200,'sitemap response')
        urls=[item.text for item in ET.fromstring(body).findall('{*}url/{*}loc')]
        check(len(urls)==33,'complete 33-page launch sitemap')
        check(not any('/buscar/' in u or '/veterinarias/' in u for u in urls),'no search/empty listing pages in sitemap')
        paths=set(urlparse(u).path for u in urls); internal=set(); all_titles=set()
        for path in paths:
            code,headers,body=fetch(path)
            check(code==200,f'200 {path}')
            page=Page();page.feed(body)
            check(page.h1==1,f'one H1 {path}')
            check(page.canonical=='https://mascota.com.py'+path,f'canonical {path}')
            check(bool(page.description),f'description {path}')
            check('index,follow' in page.robots,f'production indexable {path}')
            check(page.title not in all_titles,f'unique rendered title {path}');all_titles.add(page.title)
            check(bool(page.schemas),f'valid structured data {path}')
            check('Set-Cookie' not in headers,f'no application cookies {path}')
            check('Content-Security-Policy' in headers,f'CSP {path}')
            internal.update(urlparse(link).path for link in page.links+page.images if link.startswith('/'))
        for path in internal:
            check(fetch(path)[0]==200,f'internal link/asset {path}')
        for path in ['/not-a-page/','/.htaccess','/app/bootstrap.php','/content/articles.json','/config/site.local.php','/content/sponsors.local.json','/%2e%2e/app/bootstrap.php','/veterinarias/','/veterinarias/demo/']:
            code,headers,body=fetch(path)
            check(code==404,f'unknown/private {path}')
            check('noindex' in body,f'404 noindex {path}')
        code,headers,body=fetch('/buscar/?q='+quote('<script>alert(1)</script>'))
        check(code==200 and '<script>alert(1)</script>' not in body and '&lt;script&gt;' in body,'search escaping')
        check('noindex,follow' in body,'search noindex')
        check(fetch('/buscar/?q[]=gato')[0]==200,'array query handled')
        check(fetch('/buscar/?q=gato')[2].count('Leer la guía')>0,'search finds content')
        check(fetch('/buscar?q=gato')[2].count('Leer la guía')>0,'canonical redirect preserves search')
        check(fetch('/',method='POST')[0]==405,'POST rejected')
        check(fetch('/',method='HEAD')[2]=='','HEAD empty body')
        check('Disallow: /' in fetch('/robots.txt',production=False)[2],'local robots noindex')
        check('X-Robots-Tag' in fetch('/',production=False)[1],'local noindex header')
        check('Sitemap: https://mascota.com.py/sitemap.xml' in fetch('/robots.txt')[2],'production robots sitemap')
        # Publication gating uses synthetic private files in the isolated copy.
        (isolated/'config/site.local.php').write_text("<?php return ['sponsorship_enabled'=>true];",encoding='utf-8')
        sample={'slug':'fixture-vet','name':'Fixture clinic','city':'Fixture city','description':'Synthetic test only','paid':False,'approved':True,'starts':'2026-01-01','ends':'2099-12-31'}
        (isolated/'content/sponsors.local.json').write_text(json.dumps([sample]))
        check('Fixture clinic' not in fetch('/')[2],'unpaid invisible')
        sample['paid']=True;sample['approved']=False
        (isolated/'content/sponsors.local.json').write_text(json.dumps([sample]))
        check('Fixture clinic' not in fetch('/')[2],'unapproved invisible')
        sample['approved']=True;sample['ends']='2020-01-01'
        (isolated/'content/sponsors.local.json').write_text(json.dumps([sample]))
        check('Fixture clinic' not in fetch('/')[2],'expired invisible')
        sample['ends']='2099-12-31';sample['starts']='2026-99-99'
        (isolated/'content/sponsors.local.json').write_text(json.dumps([sample]))
        check('Fixture clinic' not in fetch('/')[2],'invalid date invisible')
        sample['starts']='2099-01-01'
        (isolated/'content/sponsors.local.json').write_text(json.dumps([sample]))
        check('Fixture clinic' not in fetch('/')[2],'future invisible')
        sample['starts']='2026-01-01'
        (isolated/'content/sponsors.local.json').write_text(json.dumps([sample]))
        check('Fixture clinic' in fetch('/')[2],'paid approved current visible')
        check(fetch('/veterinarias/fixture-vet/')[0]==200,'paid profile reachable')
        check('fixture-vet' in fetch('/sitemap.xml')[2],'paid profile in sitemap')
    finally:
        server.terminate();server.wait(timeout=10);log.close()
print(f'PASS: {checks} content, SEO, route, privacy and sponsorship checks on PHP {subprocess.check_output([args.php,"-r","echo PHP_VERSION;"],text=True)}.')
