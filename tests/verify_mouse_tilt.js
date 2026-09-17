async(page)=>{
 await page.bringToFront();await page.reload();await page.waitForFunction(()=>window.live2dQA?.model);
 const bounds=await page.locator('input[data-param="ParamAngleZ"]').evaluate(e=>({min:Number(e.min),max:Number(e.max)}));
 await page.locator('#idle').click();
 await page.evaluate(()=>{window.tiltSamples=[];window.tiltSampling=true;const tick=()=>{if(!window.tiltSampling)return;const m=window.live2dQA.model;const values=Object.fromEntries(['ParamAngleX','ParamAngleY','ParamAngleZ'].map(id=>{const i=Array.from({length:m.getParameterCount()},(_,i)=>m.getParameterId(i).getString()).indexOf(id);return [id,m.getParameterValueByIndex(i)]}));window.tiltSamples.push(values);requestAnimationFrame(tick)};requestAnimationFrame(tick)});
 const size=await page.evaluate(()=>({w:innerWidth,h:innerHeight}));
 await page.mouse.move(size.w/2,size.h/2);await page.mouse.down();
 for(const [x,y] of [[size.w-2,2],[size.w-2,size.h-2],[2,2],[2,size.h-2],[size.w/2,size.h/2]]){
  await page.mouse.move(x,y,{steps:12});await page.evaluate(async()=>{for(let i=0;i<35;i++)await new Promise(r=>requestAnimationFrame(r))});
 }
 await page.mouse.up();
 const samples=await page.evaluate(()=>{window.tiltSampling=false;return window.tiltSamples});
 if(samples.length<100||samples.some(p=>p.ParamAngleZ<bounds.min-1e-5||p.ParamAngleZ>bounds.max+1e-5))throw Error('Mouse tilt exceeds panel range');
 if(Math.max(...samples.map(p=>Math.abs(p.ParamAngleX)))<=12)throw Error('Yaw unexpectedly limited or mouse did not move');
 for(const value of [bounds.min,bounds.max]){
  await page.locator('input[data-param="ParamAngleZ"]').evaluate((e,v)=>{e.value=String(v);e.dispatchEvent(new Event('input',{bubbles:true}))},value);
  await page.evaluate(async()=>{for(let i=0;i<3;i++)await new Promise(r=>requestAnimationFrame(r))});
  const actual=await page.evaluate(()=>{const m=window.live2dQA.model;const i=Array.from({length:m.getParameterCount()},(_,i)=>m.getParameterId(i).getString()).indexOf('ParamAngleZ');return m.getParameterValueByIndex(i)});
  if(Math.abs(actual-value)>1e-5)throw Error('Manual tilt changed');
 }
 await page.locator('#idle').click();
 const report={pass:true,panelBounds:bounds,frames:samples.length,mouseTiltMin:Math.min(...samples.map(p=>p.ParamAngleZ)),mouseTiltMax:Math.max(...samples.map(p=>p.ParamAngleZ)),maxYaw:Math.max(...samples.map(p=>Math.abs(p.ParamAngleX))),manualEndpointsPass:true};
 await page.evaluate(r=>window.tiltRangeVerification=r,report);return report;
}
