"""Build an explicit allowlisted Hostinger domain-root ZIP; no secrets or old store."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

parser=argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
output=args.output.resolve(); output.mkdir(parents=True,exist_ok=True)
package=output/'mascota-hostinger-2026-10-09.zip'
files=[]
allowed = ['public/index.php', 'public/.htaccess', 'public/assets/site.css',
           'public/assets/companions.svg', 'public/assets/logo.svg',
           'public/assets/social.svg', 'public/assets/social.png',
           'app/bootstrap.php', 'app/interactive.php', 'public/assets/tools.js', 'app/.htaccess', 'content/articles.json',
           'content/sponsors.json', 'content/.htaccess',
           'config/site.example.php', 'config/.htaccess']
for name in allowed:
    source = root/name
    assert source.is_file(), f'Missing release file: {name}'
    relative = source.relative_to(root)
    destination = Path('public_html')/source.relative_to(root/'public') if name.startswith('public/') else Path('mascota-app')/relative
    files.append((source,destination.as_posix()))
assert any(name=='public_html/assets/social.png' for _,name in files), 'Generate social.png before packaging'
assert all('site.local' not in name and '.env' not in name and 'node_modules' not in name for _,name in files)
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as archive:
    for source,destination in files: archive.write(source,destination)
    archive.write(root.parent/'PHP-DEPLOY.md','LEEME-HOSTINGER.md')
manifest={'package':package.name,'files':len(files)+1,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'layout':['public_html/','mascota-app/'],'containsCustomerData':False,'containsSecrets':False}
(output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
