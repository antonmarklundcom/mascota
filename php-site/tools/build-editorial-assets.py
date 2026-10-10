"""Generate original code-native illustrations and page-specific social cards locally.
Requires Pillow at build time; production runtime uses only PHP and local assets.
Run from any directory. No external images, requests, private data, or licenses.
"""
from pathlib import Path
import json, textwrap
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/assets'
OUT.joinpath('og').mkdir(exist_ok=True)
def font(size):
    for p in [Path('C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default(size=size)
def canvas(): return Image.new('RGB',(960,540),'#fffdf7')
im=canvas(); d=ImageDraw.Draw(im)
d.rounded_rectangle((30,25,930,515),radius=28,fill='#dcebdd')
for x,label in [(135,'A'),(520,'B')]:
    d.rounded_rectangle((x,80,x+270,390),radius=18,fill='#f2e8c9',outline='#245640',width=5)
    d.rectangle((x+25,125,x+245,280),fill='#fffdf7')
    d.text((x+45,145),'Etiqueta '+label,font=font(28),fill='#245640')
    d.text((x+45,193),'Peso neto (kg)',font=font(22),fill='#245640')
    d.text((x+45,237),'Precio (Gs.)',font=font(22),fill='#245640')
    d.ellipse((x+103,310,x+167,365),fill='#dc886a')
d.text((180,440),'Compará el precio por kg con tus datos',font=font(28),fill='#245640')
assets={}
for width in (480,960):
    p=f'/assets/food-label-{width}.webp'; im.resize((width,width*540//960),Image.Resampling.LANCZOS).save(OUT/p.rsplit('/',1)[-1],quality=82,method=6)
assets['food-label']={'path':'/assets/food-label-960.webp','width':960,'height':540,'alt':'Ilustración de dos bolsas genéricas con campos de peso neto y precio, sin marcas ni raciones','creator':'Mascota · ilustración original dibujada por código','license':'Ilustración original creada para este proyecto','source':'tools/build-editorial-assets.py','caption':'Ilustración educativa de etiquetas genéricas; no representa marcas ni productos reales.','variants':[{'path':f'/assets/food-label-{w}.webp','width':w,'height':w*540//960} for w in (480,960)]}
# The existing repository illustration is not presented as a breed specimen or external licensed photo.
assets['companions']={'path':'/assets/companions.svg','width':600,'height':530,'alt':'Ilustración general de un perro y un gato juntos; no representa una raza concreta','creator':'Mascota · arte incluido en el repositorio','license':'Arte del proyecto; conservar registro de titularidad al reutilizar','source':'public/assets/companions.svg','caption':'Ilustración general de compañía; no representa un ejemplar de una raza específica.'}
data=json.loads((ROOT/'content/articles.json').read_text(encoding='utf-8'))
for a in data['articles']:
    slug=a['slug'].replace('/','-'); card=Image.new('RGB',(1200,630),'#fffdf7'); d=ImageDraw.Draw(card)
    d.rounded_rectangle((35,35,1165,595),radius=30,fill='#dcebdd')
    d.text((80,70),'MASCOTA.COM.PY',font=font(30),fill='#245640')
    title=a.get('h1',a['title']); lines=textwrap.wrap(title,width=34)
    size=48 if len(lines)<=4 else 39
    for i,line in enumerate(lines): d.text((80,155+i*(size+16)),line,font=font(size),fill='#243b32')
    d.text((80,540),'Guías con fuentes · Paraguay',font=font(27),fill='#245640')
    path=f'/assets/og/{slug}.png'; card.save(OUT/'og'/f'{slug}.png',optimize=True)
    assets['og-'+slug]={'path':path,'width':1200,'height':630,'alt':title,'creator':'Mascota · tarjeta editorial original dibujada por código','license':'Ilustración original creada para este proyecto','source':'tools/build-editorial-assets.py'}
(ROOT/'content/assets.json').write_text(json.dumps({'assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Generated {len(assets)} registered assets; no external media used.')
