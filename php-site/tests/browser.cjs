/** Portable real-browser regression test. Install playwright or set PLAYWRIGHT_MODULE. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),net=require('node:net');
const {spawn}=require('node:child_process');
const argv=process.argv.slice(2);
const option=(name,fallback)=>{const i=argv.indexOf('--'+name);return i<0?fallback:argv[i+1];};
const {chromium}=require(option('playwright-module',process.env.PLAYWRIGHT_MODULE||'playwright'));
const root=path.resolve(option('root',path.join(__dirname,'..')));
const out=path.resolve(option('output',path.join(os.tmpdir(),'mascota-browser-'+Date.now())));
let base=option('base-url',process.env.MASCOTA_BASE_URL),server,temporary;
const data=JSON.parse(fs.readFileSync(path.join(root,'content','articles.json'),'utf8'));
const paths=['/',...Object.keys(data.sections).map(k=>'/'+k+'/'),...data.articles.map(a=>'/'+a.category+'/'+a.slug+'/'),...Object.keys(data.pages).map(k=>'/'+k+'/')];
async function start(){
 if(base)return;
 temporary=fs.mkdtempSync(path.join(os.tmpdir(),'mascota-browser-source-'));
 // Copy only runtime source; do not import personal preview overrides.
 for(const name of ['app','content','config','public'])fs.cpSync(path.join(root,name),path.join(temporary,name),{recursive:true,filter:p=>!p.endsWith('.local.php')&&!p.endsWith('.local.json')});
 fs.copyFileSync(path.join(root,'router.php'),path.join(temporary,'router.php'));
 const port=await new Promise(resolve=>{const socket=net.createServer();socket.listen(0,'127.0.0.1',()=>{const p=socket.address().port;socket.close(()=>resolve(p));});});
 base='http://127.0.0.1:'+port;
 server=spawn(option('php',process.env.PHP_BINARY||'php'),['-S','127.0.0.1:'+port,'-t',path.join(temporary,'public'),path.join(temporary,'router.php')],{env:{...process.env,MASCOTA_ENV:'preview'},stdio:'ignore'});
 let failed;server.on('error',error=>{failed=error;});
 for(let i=0;i<100;i++){if(failed)throw failed;const ready=await new Promise(resolve=>{const socket=net.createConnection({host:'127.0.0.1',port});socket.once('connect',()=>{socket.destroy();resolve(true);});socket.once('error',()=>resolve(false));});if(ready)return;await new Promise(r=>setTimeout(r,100));}
 throw new Error('PHP preview failed to start');
}
async function cleanup(){if(browser)await browser.close();if(server&&server.pid&&server.exitCode===null&&server.signalCode===null){await new Promise(resolve=>{server.once('exit',resolve);server.kill();});}if(temporary)fs.rmSync(temporary,{recursive:true,force:true});}
let checks=0,browser;
function check(value,label){if(!value)throw new Error(label);checks++;}
(async()=>{
 await start();
 fs.mkdirSync(out,{recursive:true});
 const executablePath=option('browser-executable',process.env.BROWSER_EXECUTABLE);
 browser=await chromium.launch({...(executablePath?{executablePath}:{}),headless:true});
 const page=await browser.newPage();const errors=[],requests=[];
 page.on('pageerror',error=>errors.push(error.message));
 page.on('requestfailed',request=>requests.push(request.url()));
 for(const width of [1440,320]){
  await page.setViewportSize({width,height:900});
  for(const path of paths){
   const response=await page.goto(base+path,{waitUntil:'load'});
   check(response.status()===200,'browser route '+path);
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'horizontal overflow '+width+' '+path);
   check(await page.locator('h1').isVisible(),'visible heading '+width+' '+path);
  }
 }
 await page.setViewportSize({width:390,height:844});
 await page.goto(base+'/');
 await page.locator('.mobile-menu summary').click();
 check(await page.locator('.mobile-menu nav').isVisible(),'mobile navigation opens');
 await page.locator('.mobile-menu nav a[href="/cuidados/"]').click();
 check(new URL(page.url()).pathname==='/cuidados/','mobile navigation follows');
 for(const [query,expected] of [['mi perro vomita','/cuidados/vomitos-en-perros/'],['alimento para perros','/productos/comida-para-perros/'],['perro con tos','/cuidados/tos-en-perros/']]){
  await page.goto(base+'/');
  await page.locator('#home-search').fill(query);await page.locator('.hero-search button').click();
  check(await page.locator('.card-link').first().getAttribute('href')===expected,'search UI '+query);
 }
 await page.goto(base+'/cuidados/calculadora-presupuesto-mascota/');
 check((await page.locator('#budget-status').innerText()).includes('7 rubros pendientes'),'unknown costs stay pending');
 const values={food:'300000',hygiene:'100000',services:'50000',other:'50000',annual:'1200000',initial:'1000000',reserve:'100000'};
 for(const [id,value] of Object.entries(values))await page.locator('#budget-'+id).fill(value);
 const number=async selector=>Number((await page.locator(selector).innerText()).replace(/\D/g,''));
 check(await number('#budget-result-monthly')===600000,'annual expense prorated monthly');
 check(await number('#budget-result-reserve')===100000,'reserve separate');
 check(await number('#budget-result-annual')===7200000,'recurring annual expenses exclude initial and savings');
 check(await number('#budget-result-year')===9400000,'first year cash includes initial and reserve once');
 check(!(await page.locator('#budget-status').innerText()).includes('pendientes'),'complete input status');
 await page.locator('#budget-food').fill('-1');
 check((await page.locator('#budget-status').innerText()).includes('Revisá los importes'),'negative expense rejected');
 check((await page.locator('#budget-result-monthly').innerText()).includes('Revisá'),'invalid totals withheld');
 await page.locator('#budget-food').fill('300000.5');
 check((await page.locator('#budget-status').innerText()).includes('Revisá los importes'),'fractional guaranies rejected');
 await page.locator('#budget-food').fill('300000');
 await page.locator('#herramienta').scrollIntoViewIfNeeded();
 await page.screenshot({path:out+'/budget-mobile.png'});
 await page.emulateMedia({media:'print'});
 check(await page.locator('.pet-tool').isVisible(),'budget print visible');
 check(!(await page.locator('.site-header').isVisible()),'print removes navigation');
 check(!(await page.locator('.prose > section:not(.pet-tool)').first().isVisible()),'print focuses on tool');
 await page.pdf({path:out+'/budget-example.pdf',format:'A4',printBackground:true});
 await page.emulateMedia({media:'screen'});
 await page.locator('.tool-reset').click();
 await page.waitForFunction(()=>document.querySelector('#budget-status').textContent.includes('7 rubros pendientes'));
 check(await page.locator('#budget-food').inputValue()==='','budget reset clears costs');
 await page.goto(base+'/cuidados/planificador-cuidados/');
 await page.locator('#pet-name').fill('Mi mascota');await page.locator('#pet-species').fill('Perro');
 await page.locator('#care-daily').fill('Rutina de ejemplo para revisar con la persona responsable. '.repeat(18));
 await page.locator('#care-day-0').fill('Revisar tareas acordadas');
 check(await page.evaluate(()=>localStorage.length===0&&sessionStorage.length===0),'tools store no personal fields');
 await page.locator('#herramienta').scrollIntoViewIfNeeded();
 await page.screenshot({path:out+'/planner-mobile.png'});
 await page.emulateMedia({media:'print'});
 check(await page.locator('#care-daily').isVisible(),'planner print retains filled field');
 check(await page.locator('#care-daily').evaluate(el=>el.scrollHeight<=el.clientHeight+2),'long notes fit printable textarea');
 await page.pdf({path:out+'/planner-example.pdf',format:'A4',printBackground:true});
 await page.emulateMedia({media:'screen'});
 await page.locator('.tool-reset').click();check(await page.locator('#pet-name').inputValue()==='','planner reset clears fields');
 const foodArticle=data.articles.find(a=>a.tool==='food-cost');
 if(foodArticle){
  await page.goto(base+'/'+foodArticle.category+'/'+foodArticle.slug+'/');
  const product=page.locator('[data-food-product]').first();
  for(const [key,value] of Object.entries({priceGs:'120000',weightkg:'4',dailygrams:'100'}))await product.locator('[data-food="'+key+'"]').fill(value);
  check(Number((await product.locator('[data-food-result="kg"]').innerText()).replace(/\D/g,''))===30000,'food price per kg');
  check(Number((await product.locator('[data-food-result="month"]').innerText()).replace(/\D/g,''))===90000,'food 30 day cost from supplied daily grams');
  await product.locator('[data-food="dailygrams"]').fill('');
  check(Number((await product.locator('[data-food-result="kg"]').innerText()).replace(/\D/g,''))===30000,'food price available without daily grams');
  check((await product.locator('[data-food-result="month"]').innerText()).includes('Desconocido'),'food monthly remains unknown without daily grams');
  for(const [key,value] of Object.entries({priceGs:'-1',weightkg:'0',dailygrams:'-1'})){
   for(const [field,valid] of Object.entries({priceGs:'120000',weightkg:'4',dailygrams:'100'}))await product.locator('[data-food="'+field+'"]').fill(valid);
   await product.locator('[data-food="'+key+'"]').fill(value);
   check((await product.locator('[data-food-result="kg"]').innerText()).includes('Desconocido')&&(await product.locator('[data-food-status]').innerText()).includes('Revisá'),'food invalid '+key+' withholds totals');
  }
  check(await page.evaluate(()=>localStorage.length===0&&sessionStorage.length===0),'food inputs not persisted');
  await page.locator('.tool-reset').click();check(await product.locator('[data-food="priceGs"]').inputValue()==='','food reset');
 }
 await page.setViewportSize({width:1440,height:1000});
 await page.goto(base+'/');await page.screenshot({path:out+'/home-desktop.png',fullPage:true});
 await page.goto(base+'/cuidados/calculadora-presupuesto-mascota/');
 await page.locator('#herramienta').scrollIntoViewIfNeeded();await page.screenshot({path:out+'/budget-desktop.png'});
 const noJS=await browser.newContext({javaScriptEnabled:false});const plain=await noJS.newPage();
 await plain.goto(base+'/cuidados/calculadora-presupuesto-mascota/');
 check(await plain.locator('noscript').innerText().then(t=>t.includes('fórmulas')),'no-JS budget instructions');
 await plain.goto(base+'/cuidados/planificador-cuidados/');
 check(await plain.locator('#care-daily').isVisible(),'no-JS planner editable');
 check(errors.length===0,'no browser JS/CSP errors');check(requests.length===0,'no failed requests');
 const report={status:'PASS',checks,pages:paths.length,viewports:[1440,320,390],budgetExample:{monthly:600000,reserve:100000,annualRecurring:7200000,firstYearCash:9400000},printPDFs:['budget-example.pdf','planner-example.pdf'],noJSChecked:true,productionDeploymentPerformed:false};
 fs.writeFileSync(out+'/browser-checks.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 await cleanup();
})().catch(async error=>{console.error(error);await cleanup();process.exitCode=1;});
