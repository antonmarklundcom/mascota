"""HTTP regressions for crawlable noindex and exact canonical path redirects."""
from pathlib import Path
import argparse
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import urllib.robotparser

parser=argparse.ArgumentParser()
parser.add_argument('--php',default='php')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
checks=0
def check(value,label):
    global checks
    if not value: raise AssertionError(label)
    checks+=1
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args): return None
opener=urllib.request.build_opener(NoRedirect)
with tempfile.TemporaryDirectory(prefix='mascota-crawl-') as tmp:
    copy=Path(tmp)/'php-site'; shutil.copytree(root,copy)
    with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    with (Path(tmp)/'server.log').open('w',encoding='utf-8') as log:
        proc=subprocess.Popen([args.php,'-S',f'127.0.0.1:{port}','-t',str(copy/'public'),str(copy/'router.php')],stdout=log,stderr=log,env={**os.environ,'MASCOTA_ENV':'production'})
        def fetch(path,method='GET',production=True):
            req=urllib.request.Request(base+path,headers={'Host':'mascota.com.py'} if production else {},method=method)
            try: response=opener.open(req,timeout=10)
            except urllib.error.HTTPError as error: response=error
            with response: return response.status,response.headers,response.read().decode('utf-8')
        try:
            for _ in range(60):
                try: fetch('/'); break
                except urllib.error.URLError: time.sleep(.1)
            else: raise AssertionError('preview did not start')
            for path,target in [('/mascotas/%70erros/','/mascotas/perros/'),('/%6dascotas%2Fperros','/mascotas/perros/'),('/%69ndex.php','/'),('/index.php?utm_source=test','/?utm_source=test'),('/%62uscar?q=%67ato&tag=one&tag=two','/buscar/?q=%67ato&tag=one&tag=two'),('/%73itemap.xml','/sitemap.xml')]:
                status,headers,body=fetch(path)
                check(status==301 and headers.get('Location')==target and not body,'one canonical redirect '+path)
                check(fetch(target)[0]==200,'redirect target works '+target)
            check(fetch('/mascotas/perros/')[0]==200,'canonical route has no redirect')
            for path in ['/mascotas/%2570erros/','/mascotas/%zzperros/','/%2e%2e/app/bootstrap.php','/%61pp/bootstrap.php','//example.invalid/']:
                status,headers,body=fetch(path)
                check(status==404 and headers.get('Location') is None,'unknown/private stays 404 '+path)
            status,headers,body=fetch('/mascotas/%70erros/',method='HEAD')
            check(status==301 and headers.get('Location')=='/mascotas/perros/' and not body,'HEAD redirect without body')
            check(fetch('/mascotas/%70erros/',method='POST')[0]==405,'unsupported method rejected before redirect')
            status,headers,body=fetch('/robots.txt')
            rules=urllib.robotparser.RobotFileParser();rules.parse(body.splitlines())
            check(status==200 and rules.can_fetch('Googlebot','https://mascota.com.py/buscar/?q=perro'),'production search crawl allowed')
            check(not rules.can_fetch('Googlebot','https://mascota.com.py/contacto-clinica/fixture/phone/'),'contact remains disallowed')
            check('noindex,follow' in fetch('/buscar/?q=gato')[2],'search remains noindex')
            check('Disallow: /' in fetch('/robots.txt',production=False)[2],'preview remains blocked')
            check('noindex' in fetch('/',production=False)[1].get('X-Robots-Tag',''),'preview remains noindex')
        finally: proc.terminate();proc.wait(timeout=10)
print(f'PASS: {checks} crawl and canonical-route assertions.')
