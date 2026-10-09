"""Isolated synthetic checks for activation/privacy and private cash reporting."""
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

parser=argparse.ArgumentParser(); parser.add_argument('--php',default='php'); args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('commercial_report',root/'tools/commercial_report.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
checks=0

def check(value,label):
    global checks
    if not value: raise AssertionError(label)
    checks+=1

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw): return None

with tempfile.TemporaryDirectory(prefix='mascota-commercial-') as temp:
    private=Path(temp); app=private/'site/php-site'; shutil.copytree(root,app)
    counts=private/'clinic-clicks.json'
    fixture={'slug':'synthetic-vet','name':'Synthetic clinic only','city':'Test city','description':'Isolated fixture','paid':True,'approved':True,'starts':'2000-01-01','ends':'2099-12-31','verified_on':date.today().isoformat(),'contact_approved':True,'address':'Synthetic <address>','services':['Synthetic service'],'hours':'Synthetic hours','phone':'+595981234567','whatsapp':'+595981234567','website':'https://clinic.example/contact'}
    def setup(**config):
        pairs=','.join(json.dumps(k)+'=>'+('true' if v is True else 'false' if v is False else json.dumps(str(v))) for k,v in config.items())
        (app/'config/site.local.php').write_text('<?php return ['+pairs+'];',encoding='utf-8')
    def save(): (app/'content/sponsors.local.json').write_text(json.dumps([fixture]),encoding='utf-8')
    save()
    with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    log=(private/'server.log').open('w'); process=subprocess.Popen([args.php,'-S',f'127.0.0.1:{port}','-t',str(app/'public'),str(app/'router.php')],stdout=log,stderr=log)
    opener=urllib.request.build_opener(NoRedirect)
    def fetch(path,method='GET'):
        req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,method=method,headers={'Host':'mascota.com.py'})
        try: response=opener.open(req,timeout=10)
        except urllib.error.HTTPError as error: response=error
        return response.status,dict(response.headers),response.read().decode()
    contact='/contacto-clinica/synthetic-vet/whatsapp/'
    try:
        for _ in range(60):
            try:fetch('/');break
            except urllib.error.URLError: time.sleep(.1)
        check(fetch(contact)[0]==404,'default disabled even with synthetic partner')
        setup(sponsorship_enabled=True)
        check(fetch(contact)[0]==404,'contact feature gate separate')
        setup(sponsorship_enabled=True,clinic_contact_enabled=True)
        body=fetch('/veterinarias/synthetic-vet/')[2]
        check('Synthetic &lt;address&gt;' in body and 'Synthetic service' in body,'verified escaped fields rendered')
        check('Eleg\u00eds' in body,'Spanish UTF-8 contact copy')
        code,headers,body=fetch(contact+'?next=https://attacker.example&symptom=private')
        check(code==302 and headers['Location']=='https://wa.me/595981234567','request cannot choose redirect or transfer symptoms')
        check(headers['Cache-Control']=='no-store' and 'noindex' in headers['X-Robots-Tag'] and headers['Referrer-Policy']=='no-referrer','private uncached redirect')
        check('Set-Cookie' not in headers and not counts.exists(),'no cookies/count persistence by default')
        check(fetch(contact,'POST')[0]==405,'no lead intake')
        check('/contacto-clinica/' not in fetch('/sitemap.xml')[2],'contact endpoint not indexable')
        for field,value in [('paid',False),('approved',False),('ends','2000-01-01'),('starts','2099-01-01'),('verified_on','2099-01-01'),('verified_on','2000-01-01'),('verified_on','2026-02-30'),('contact_approved',False),('whatsapp','+595123\r\nX-Bad: injected')]:
            old=fixture[field];fixture[field]=value;save()
            check(fetch(contact)[0]==404,'fail closed '+field+' '+str(value));fixture[field]=old;save()
        fixture['website']='javascript:alert(1)';save();check(fetch('/contacto-clinica/synthetic-vet/website/')[0]==404,'unsafe scheme rejected')
        fixture['website']='https://user:pass@clinic.example/';save();check(fetch('/contacto-clinica/synthetic-vet/website/')[0]==404,'credentials rejected')
        fixture['website']='https://clinic.example/contact';save()
        setup(sponsorship_enabled=True,clinic_contact_enabled=True,clinic_click_tracking_enabled=True,clinic_clicks_path=counts)
        fetch(contact,'HEAD');check(not counts.exists(),'HEAD does not count')
        fetch(contact+'?ip=secret&phone=private')
        stored=json.loads(counts.read_text()); period=next(iter(stored['months']))
        check(stored=={'version':1,'months':{period:{'synthetic-vet':{'whatsapp':1}}}},'only aggregate profile/month/channel persisted')
        check(not any(word in counts.read_text() for word in ('secret','private','ip','phone','symptom','inquiry')),'no visitor/symptom/inquiry data')
        # Independent PHP workers exercise the separate lock and atomic replacement.
        code="require "+json.dumps(str(app/'app/bootstrap.php'))+"; record_clinic_click('synthetic-vet','whatsapp');"
        def bump(_):return subprocess.run([args.php,'-r',code],capture_output=True).returncode
        with ThreadPoolExecutor(max_workers=6) as workers: results=list(workers.map(bump,range(24)))
        check(all(x==0 for x in results) and json.loads(counts.read_text())['months'][period]['synthetic-vet']['whatsapp']==25,'concurrent increments retained')
        counts.write_text('{broken');fetch(contact);check(counts.read_text()=='{broken','corrupt counts not overwritten and contact works')
        bad={'version':1,'months':{period:{'synthetic-vet':{'visitor_ip':'secret'}}}}
        counts.write_text(json.dumps(bad));fetch(contact);check(json.loads(counts.read_text())==bad,'tampered identifier fields not retained by writer')
        forbidden=app/'public/leak.json'
        setup(sponsorship_enabled=True,clinic_contact_enabled=True,clinic_click_tracking_enabled=True,clinic_clicks_path=forbidden)
        check(fetch(contact)[0]==302 and not forbidden.exists(),'public persistence rejected without blocking contact')
        for path in ['/tools/commercial_report.py','/commercial-ledger.json','/clinic-clicks.json','/app/commercial.php']:
            check(fetch(path)[0]==404,'private route '+path)
    finally:process.terminate();process.wait(timeout=10);log.close()
    row={'slug':'synthetic-vet','billed_pyg':500000,'collected_pyg':400000,'refunds_pyg':50000,'confirmed_inquiries':3,'confirmed_appointments':1,'renewal':'renewed','service_hours':2}
    ledger={'version':1,'months':[{'month':'2026-10','costs_pyg':dict.fromkeys(module.COSTS,None),'capacity_hours':10,'reserve_pyg':1000000,'partners':[row]}]}
    clicks={'version':1,'months':{'2026-10':{'synthetic-vet':{'whatsapp':25}}}}
    result=module.report(ledger,clicks)['months'][0]
    check(result['net_collected_pyg']==350000 and result['billed_minus_collected_pyg']==100000,'billing collections and refunds separate')
    check(result['partners'][0]['clinic_contact_clicks']==25 and result['confirmed_inquiries']==3 and result['confirmed_appointments']==1,'clicks not confirmed outcomes')
    check(result['margin_after_declared_costs_pyg'] is None and len(result['missing_costs'])==6,'missing costs suppress margin claim')
    check(module.report(ledger)['months'][0]['partners'][0]['clinic_contact_clicks'] is None,'unavailable clicks not reported as zero')
    ledger['months'][0]['costs_pyg']=dict.fromkeys(module.COSTS,0);ledger['months'][0]['costs_pyg']['labor']=200000
    result=module.report(ledger,clicks)['months'][0]
    check(result['margin_after_declared_costs_pyg']==150000 and result['remaining_capacity_hours']==8 and result['renewals']['renewed']==1,'recorded costs workload renewal')
    row['service_hours']=None;check(module.report(ledger)['months'][0]['remaining_capacity_hours'] is None,'unknown hours suppress capacity claim');row['service_hours']=2
    for field,value in [('collected_pyg',-1),('confirmed_inquiries',True),('service_hours',float('nan')),('renewal','fake')]:
        old=row[field];row[field]=value
        try:module.report(ledger);rejected=False
        except ValueError:rejected=True
        check(rejected,'invalid ledger '+field);row[field]=old
    row['visitor_phone']='private'
    try:module.report(ledger);rejected=False
    except ValueError:rejected=True
    check(rejected,'ledger identifiers rejected');del row['visitor_phone']
    ledger_path=private/'commercial-ledger.json';ledger_path.write_text(json.dumps(ledger))
    output=private/'commercial-report.json'
    cli=[sys.executable,str(root/'tools/commercial_report.py'),'--ledger',str(ledger_path),'--output',str(output)]
    completed=subprocess.run(cli,capture_output=True,text=True)
    check(completed.returncode==0 and output.exists() and 'synthetic-vet' not in completed.stdout,'CLI private export without printing records')
    check(subprocess.run(cli,capture_output=True).returncode==2,'report overwrite rejected')
    try:module.private_path(root/'public/leak.json');rejected=False
    except ValueError:rejected=True
    check(rejected,'CLI rejects repo/public output')
print(f'PASS: {checks} isolated commercial contact/privacy/concurrency/report checks.')
