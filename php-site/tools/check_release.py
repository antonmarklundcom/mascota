"""Read-only production launch verification. Only same-origin HTTP(S) GETs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin
import argparse
import hashlib
import ipaddress
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonical=[]; self.robots=[]; self.assets=set(); self.h1=0; self.title=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a.get('href',''))
        if tag=='meta' and a.get('name','').lower() in ('robots','googlebot'): self.robots.append(a.get('content',''))
        if tag=='h1': self.h1+=1
        if tag=='title': self.title=True
        if tag in ('img','script') and a.get('src'): self.assets.add(a['src'])
        if tag=='link' and a.get('rel') in ('stylesheet','icon'): self.assets.add(a.get('href',''))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None

def verify(base, manifest, allow_local_http=False, host=None):
    origin=urlsplit(base)
    if origin.username or origin.password or origin.query or origin.fragment or origin.path not in ('','/'):
        raise ValueError('Base must be a bare origin without credentials')
    if origin.scheme != 'https':
        local=origin.hostname=='localhost'
        try: local=local or ipaddress.ip_address(origin.hostname).is_loopback
        except ValueError: pass
        if not (allow_local_http and origin.scheme=='http' and local): raise ValueError('HTTPS required; HTTP is only allowed explicitly on loopback')
    base=base.rstrip('/')
    canonical_origin='https://'+host if host else base
    opener=urllib.request.build_opener(NoRedirect)
    checks=0
    def check(value,label):
        nonlocal checks
        if not value: raise AssertionError(label)
        checks+=1
    def fetch(path):
        target=urlsplit(urljoin(base+'/',path))
        check((target.scheme,target.netloc)==(origin.scheme,origin.netloc),'Refusing external request '+path)
        headers={'User-Agent':'Mascota-Release-Check/1.0'}
        if host: headers['Host']=host
        req=urllib.request.Request(target.geturl(),headers=headers,method='GET')
        try: response=opener.open(req,timeout=15)
        except urllib.error.HTTPError as error: response=error
        with response:
            body=response.read(8*1024*1024+1)
            check(len(body)<=8*1024*1024,'Response too large '+path)
            return response.status,response.headers,body
    code,_,body=fetch('/release.json')
    check(code==200,'Release fingerprint missing')
    actual=json.loads(body)
    for key in ('schema','version','commit','sourceState','fingerprint','paths','assets','privatePaths'):
        check(actual.get(key)==manifest.get(key),'Wrong release '+key)
    code,_,body=fetch('/robots.txt'); robots=body.decode('utf-8')
    check(code==200 and 'Sitemap: '+canonical_origin+'/sitemap.xml' in robots,'Robots sitemap')
    check(not any(line.strip().lower()=='disallow: /' for line in robots.splitlines()),'Production robots blocks indexing')
    code,_,body=fetch('/sitemap.xml'); check(code==200,'Sitemap missing')
    urls=[e.text for e in ET.fromstring(body).findall('{*}url/{*}loc')]
    check(set(urls)=={canonical_origin+p for p in manifest['paths']} and len(urls)==len(manifest['paths']),'Sitemap inventory mismatch')
    assets=set(manifest['assets'])
    for path in manifest['paths']:
        check(path.startswith('/') and not path.startswith('//') and '..' not in path.split('/'),'Unsafe manifest path')
        code,headers,body=fetch(path); check(code==200,'Page missing '+path)
        page=Page(); page.feed(body.decode('utf-8'))
        check(headers.get('X-Mascota-Release')==manifest['version'],'Runtime release header mismatch '+path)
        check(page.h1==1 and page.title,'Default or incomplete page '+path)
        check(page.canonical==[canonical_origin+path],'Canonical mismatch '+path)
        check('noindex' not in ','.join(page.robots).lower() and 'noindex' not in headers.get('X-Robots-Tag','').lower(),'Page noindex '+path)
        for asset in page.assets:
            target=urlsplit(urljoin(base+path,asset))
            # External assets are rejected without fetching them.
            check((target.scheme,target.netloc)==(origin.scheme,origin.netloc),'External linked asset '+asset)
            assets.add(target.path)
    for path in sorted(assets):
        check(path in manifest['assets'],'Linked asset absent from release inventory '+path)
        code,_,body=fetch(path)
        check(code==200 and hashlib.sha256(body).hexdigest()==manifest['assets'][path],'Asset mismatch '+path)
    for path in manifest['privatePaths']:
        code,_,body=fetch(path)
        check(code in (403,404),'Private or absent path exposed '+path)
        check(b'<?php' not in body and b'"articles"' not in body,'Private content leaked '+path)
    return {'status':'PASS','checks':checks,'pages':len(manifest['paths']),'version':manifest['version'],'base':base,'method':'GET'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--allow-local-http',action='store_true')
    parser.add_argument('--host',help='Production Host/canonical override for explicit local HTTP testing')
    args=parser.parse_args()
    if args.host and not args.allow_local_http: parser.error('--host requires --allow-local-http')
    try: print(json.dumps(verify(args.base_url,json.loads(args.manifest.read_text(encoding='utf-8')),args.allow_local_http,args.host),indent=2))
    except Exception as error: parser.exit(1,'FAIL: '+str(error)+'\n')
