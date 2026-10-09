"""Regression fixtures for immutable packaging and read-only launch checks."""
from pathlib import Path
import copy
import hashlib
import http.server
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_release import verify
from package import build
from release_metadata import ALLOWLIST, encoded, release_files, metadata

class ReleaseTests(unittest.TestCase):
    def test_local_http_requires_explicit_loopback(self):
        for origin,flag in [('http://127.0.0.1',False),('http://example.com',True),('https://user:pass@example.com',False)]:
            with self.assertRaises(ValueError): verify(origin,{},flag)

    def test_package_source_determinism_and_overwrite(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            first=build(root,output); archive=output/first['package']; original=archive.read_bytes()
            self.assertEqual(build(root,output),first)
            self.assertEqual(archive.read_bytes(),original)
            expected=release_files(root)
            with zipfile.ZipFile(archive) as zipped:
                for name,body in expected.items(): self.assertEqual(zipped.read(name),body)
                self.assertEqual(json.loads(zipped.read('public_html/release.json')),metadata(root,expected))
                self.assertEqual(set(zipped.namelist()),set(first['files']))
            archive.write_bytes(b'preexisting different release')
            with self.assertRaises(ValueError): build(root,output)
            self.assertEqual(archive.read_bytes(),b'preexisting different release')

    def test_synthetic_checker_failures(self):
        state={'fault':None,'requests':[]}
        asset=b'body { color: green; }'
        manifest={'schema':1,'version':'fixture-version','commit':'fixture-commit','sourceState':'committed',
            'fingerprint':'fixture-fingerprint','paths':['/','/guide/'],
            'assets':{'/assets/site.css':hashlib.sha256(asset).hexdigest()},'privatePaths':['/content/articles.json','/missing/']}
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                state['requests'].append(self.path)
                fault=state['fault']; status=200; extra={}
                if self.path=='/release.json':
                    value=copy.deepcopy(manifest)
                    if fault=='fingerprint': value['fingerprint']='wrong'
                    body=encoded(value)
                elif self.path=='/robots.txt': body=b'Sitemap: https://mascota.com.py/sitemap.xml\n'+(b'Disallow: /\n' if fault=='robots' else b'')
                elif self.path=='/sitemap.xml':
                    paths=['/'] if fault=='sitemap' else manifest['paths']
                    body=('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://mascota.com.py'+p+'</loc></url>' for p in paths)+'</urlset>').encode()
                elif self.path in manifest['paths']:
                    extra['X-Mascota-Release']=manifest['version']
                    canonical='https://mascota.com.py'+('/wrong/' if fault=='canonical' else self.path)
                    body=('<html><title>Fixture</title><link rel="canonical" href="'+canonical+'"><h1>Fixture</h1><link rel="stylesheet" href="'+('https://example.invalid/track.css' if fault=='external' else '/assets/site.css')+'">'+('<meta name="robots" content="noindex">' if fault=='noindex' else '')+'</html>').encode()
                    if fault=='default': body=b'<title>Hostinger default page</title>'
                    if fault=='404': status=404
                    if fault=='header': extra['X-Robots-Tag']='noindex'
                    if fault=='runtime': extra['X-Mascota-Release']='wrong'
                    if fault=='redirect': status=302; extra['Location']='https://example.invalid/'
                elif self.path=='/assets/site.css': body=b'wrong' if fault=='asset' else asset
                else:
                    status=200 if fault=='private' else 404
                    body=b'{"articles":[]}' if fault=='private' else b'Missing'
                self.send_response(status)
                for key,value in extra.items(): self.send_header(key,value)
                self.end_headers(); self.wfile.write(body)
            def log_message(self,*args): pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            base='http://127.0.0.1:'+str(server.server_port)
            self.assertEqual(verify(base,manifest,True,'mascota.com.py')['status'],'PASS')
            for fault in ('fingerprint','runtime','robots','sitemap','canonical','noindex','header','default','404','redirect','asset','private','external'):
                with self.subTest(fault=fault):
                    state['fault']=fault
                    with self.assertRaises((AssertionError,ValueError)): verify(base,manifest,True,'mascota.com.py')
            self.assertFalse(any('example.invalid' in p for p in state['requests']))
        finally: server.shutdown();server.server_close();thread.join()

if __name__=='__main__': unittest.main()
