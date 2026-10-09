"""Explicit, reproducible release inventory shared by packaging and verification."""
from pathlib import Path
import hashlib
import json
import subprocess

ALLOWLIST = (
    'public/index.php', 'public/.htaccess', 'public/assets/site.css',
    'public/assets/companions.svg', 'public/assets/logo.svg',
    'public/assets/social.svg', 'public/assets/social.png', 'public/assets/tools.js',
    'app/bootstrap.php', 'app/interactive.php', 'app/editorial.php', 'app/.htaccess',
    'content/articles.json', 'content/sponsors.json', 'content/assets.json', 'content/editorial-team.json', 'content/.htaccess',
    'config/site.example.php', 'config/.htaccess',
)
PRIVATE_PATHS = ('/.htaccess', '/app/bootstrap.php', '/content/articles.json',
    '/content/sponsors.local.json', '/config/site.local.php', '/.env',
    '/mascota-app/app/bootstrap.php', '/mascota-app/content/articles.json',
    '/mascota-release-missing-page/')

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)+'\n').encode('utf-8')

def inventory(root):
    data = json.loads((root/'content/articles.json').read_text(encoding='utf-8'))
    paths = ['/', *('/'+key+'/' for key in data['sections']),
             *('/'+key+'/' for key in data['pages']),
             *('/'+a['category']+'/'+a['slug']+'/' for a in data['articles'])]
    if len(paths) != len(set(paths)): raise ValueError('Duplicate published paths')
    return sorted(paths)

def release_files(root):
    files = {}
    asset_manifest=json.loads((root/'content/assets.json').read_text(encoding='utf-8'))
    registered=set()
    for asset in asset_manifest['assets'].values():
        for item in [asset,*asset.get('variants',[])]:
            path=item['path']
            if not path.startswith('/assets/') or any(part in ('..','.') for part in path.split('/')) or '\\' in path or '?' in path or '#' in path:
                raise ValueError('Unsafe registered asset: '+path)
            if Path(path).suffix.lower() not in ('.svg','.webp','.png','.jpg','.jpeg'):
                raise ValueError('Unsupported registered asset: '+path)
            registered.add('public'+path)
    for name in sorted(set(ALLOWLIST)|registered):
        source = root/name
        if not source.is_file() or source.is_symlink() or not source.resolve().is_relative_to(root.resolve()): raise ValueError('Missing or unsafe release file: '+name)
        destination = 'public_html/'+name[len('public/'):] if name.startswith('public/') else 'mascota-app/'+name
        files[destination] = source.read_bytes()
    files['LEEME-HOSTINGER.md'] = (root.parent/'PHP-DEPLOY.md').read_bytes()
    if json.loads(files['mascota-app/content/sponsors.json']) != []:
        raise ValueError('Release sponsors must remain empty')
    return files

def metadata(root, files):
    repo = root.parent
    commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    hashes = {name: hashlib.sha256(body).hexdigest() for name,body in sorted(files.items())}
    fingerprint = hashlib.sha256(encoded(hashes)).hexdigest()
    source_paths=['PHP-DEPLOY.md']
    for name in files:
        if name.startswith('public_html/'):
            source_paths.append('php-site/public/'+name[len('public_html/'):])
        elif name.startswith('mascota-app/'):
            source_paths.append('php-site/'+name[len('mascota-app/'):])
    dirty = bool(subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--',*source_paths], text=True).strip())
    return {'schema':1, 'version':commit[:12]+'-'+fingerprint[:12], 'commit':commit,
            'sourceState':'working-tree' if dirty else 'committed', 'fingerprint':fingerprint,
            'paths':inventory(root), 'assets':{name[len('public_html'):]:digest for name,digest in hashes.items()
                if name.startswith('public_html/assets/')}, 'privatePaths':list(PRIVATE_PATHS)}
