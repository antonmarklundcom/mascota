"""Verify the extracted Hostinger ZIP works with its private sibling application.

The test router simulates URL rewrites; the hosting account's Apache/LiteSpeed
configuration and actual HTTPS certificate must still be verified after upload.
"""
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import os
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--php', default='php')
parser.add_argument('--zip', type=Path, required=True)
args = parser.parse_args()
checks = 0
def check(condition, message):
    global checks
    if not condition: raise AssertionError(message)
    checks += 1

with tempfile.TemporaryDirectory(prefix='mascota-restore-') as temporary:
    restored = Path(temporary)
    with zipfile.ZipFile(args.zip) as archive:
        names = archive.namelist()
        check(len(names) == 15, 'explicit release file count')
        check(all(name.startswith(('public_html/', 'mascota-app/')) or name == 'LEEME-HOSTINGER.md' for name in names), 'domain-root layout')
        check(not any('local.' in name or '.env' in name or 'node_modules' in name or 'tests/' in name for name in names), 'no private overrides, dependencies or tests')
        check(all(not name.startswith('/') and '..' not in Path(name).parts for name in names), 'safe archive paths')
        archive.extractall(restored)
    check(json.loads((restored/'mascota-app/content/sponsors.json').read_text()) == [], 'no paid/customer records in launch ZIP')
    router = restored/'test-router.php'
    router.write_text("""<?php
    $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    $asset = realpath(__DIR__.'/public_html'.$path);
    $assets = realpath(__DIR__.'/public_html/assets');
    if ($asset && str_starts_with($asset, $assets.DIRECTORY_SEPARATOR) && is_file($asset)) return false;
    require __DIR__.'/public_html/index.php';
    """, encoding='utf-8')
    with socket.socket() as sock: sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    log = open(restored/'test-server.log', 'w', encoding='utf-8')
    process = subprocess.Popen([args.php, '-S', f'127.0.0.1:{port}', '-t', str(restored/'public_html'), str(router)], stdout=log, stderr=log, env={**os.environ, 'MASCOTA_ENV':'production'})
    def fetch(path):
        request = urllib.request.Request(f'http://127.0.0.1:{port}'+path, headers={'Host':'mascota.com.py'})
        try: response = urllib.request.urlopen(request, timeout=10)
        except urllib.error.HTTPError as error: response = error
        return response.status, response.read()
    try:
        for _ in range(60):
            try: fetch('/'); break
            except (ConnectionError, urllib.error.URLError): time.sleep(.1)
        else: raise AssertionError('restored server did not start')
        code, body = fetch('/sitemap.xml')
        check(code == 200, 'restored sitemap response')
        paths = [urlparse(element.text).path for element in ET.fromstring(body).findall('{*}url/{*}loc')]
        data=json.loads((restored/'mascota-app/content/articles.json').read_text(encoding='utf-8'))
        check(len(paths)==1+4+len(data['articles'])+len(data['pages']), 'restored complete content sitemap')
        check(len(paths)==62,'restored 62-page SEO release')
        for path in paths:
            code, body = fetch(path)
            check(code == 200 and b'<h1' in body, f'restored page {path}')
        for path in ['/assets/site.css', '/assets/social.png', '/assets/companions.svg']:
            code, body = fetch(path)
            check(code == 200 and len(body) > 100, f'restored asset {path}')
        for path in ['/app/bootstrap.php', '/content/articles.json', '/config/site.local.php', '/mascota-app/app/bootstrap.php', '/veterinarias/']:
            check(fetch(path)[0] == 404, f'private/absent route {path}')
    finally:
        process.terminate(); process.wait(timeout=10); log.close()
print(f'PASS: {checks} ZIP layout, clean extraction and private-sibling HTTP checks.')
