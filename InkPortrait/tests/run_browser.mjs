// Run from the repository root, with the local preview already running.
import { chromium } from 'playwright';
import fs from 'node:fs/promises';
await fs.mkdir('workspace',{recursive:true});
const browser=await chromium.launch({headless:true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE} : {})});
try {
 const page=await browser.newPage({viewport:{width:1830,height:905},deviceScaleFactor:1});
 await page.goto(process.env.PREVIEW_URL || 'http://127.0.0.1:4174/');
 for(const file of ['verify_runtime.js','verify_bugfix.js','verify_v3.js','verify_v6.js','verify_mouse_tilt.js']){
  const source=await fs.readFile(new URL(file,import.meta.url),'utf8');
  const result=await (0,eval)(`(${source})`)(page);
  await fs.writeFile(`workspace/${file}.json`,JSON.stringify(result,null,2));
  if(!result.pass)throw Error(file+' failed');
  console.log(file,JSON.stringify(result));
 }
} finally {await browser.close()}
