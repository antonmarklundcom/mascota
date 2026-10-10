"""Adversarial inline-link and truthful editorial metadata fixtures, no personal data."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import tempfile

parser=argparse.ArgumentParser()
parser.add_argument('--php',default='php')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
assert json.loads((root/'content/editorial-team.json').read_text(encoding='utf-8'))['members']=={},'No unverified production editor profiles'
with tempfile.TemporaryDirectory(prefix='mascota-editorial-fixture-') as temporary:
    isolated=Path(temporary)/'site'
    shutil.copytree(root,isolated,ignore=shutil.ignore_patterns('*.local.php','*.local.json','node_modules','__pycache__'))
    data=json.loads((isolated/'content/articles.json').read_text(encoding='utf-8'))
    data['articles'][0]['sections'][0].setdefault('inline_paragraphs',[]).append([{'text':'fixtureuniquetoken'}])
    (isolated/'content/articles.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    team={'members':{'fixture':{'name':'Synthetic Fixture','role':'Synthetic editorial role','profile':'/sobre-mascota/','verified':True},
        'professional':{'name':'Synthetic Professional Fixture','role':'Synthetic professional review role','profile':'/sobre-mascota/','verified':True,'professional_review':True},
        'professional-nonstrict':{'name':'Synthetic Nonboolean Flag','role':'Fixture','profile':'/sobre-mascota/','verified':True,'professional_review':1},
        'unverified':{'name':'Unverified Fixture','role':'Fixture','profile':'/sobre-mascota/','verified':False},
        'incomplete':{'name':'Incomplete Fixture','verified':True}}}
    (isolated/'content/editorial-team.json').write_text(json.dumps(team),encoding='utf-8')
    subprocess.run([args.php,str(root/'tests/editorial_fixture.php'),str(isolated)],check=True)
