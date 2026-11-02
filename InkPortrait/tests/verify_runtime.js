async (page) => {
  const root='workspace';
  await page.bringToFront();
  await page.reload();
  await page.waitForFunction(()=>window.live2dQA?.model?.getParameterCount()===18);
  const step=async(p)=>{await page.evaluate(async(p)=>{window.live2dQA.freeze=true;window.live2dQA.parameters=p;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))},p)};
  await step({});
  const meta=await page.evaluate(()=>{
    const m=window.live2dQA.model,d=m.getModel().drawables;
    window.portraitBaseline={vertices:d.vertexPositions.map(p=>Array.from(p)),opacity:Array.from(d.opacities)};
    const ids=Array.from(d.ids);
    for(const side of ['R','L']){
      const iris=ids.indexOf('ArtMeshIrides'+side),white=ids.indexOf('ArtMeshEyewhite'+side);
      if(iris<0||white<0||!Array.from(d.masks[iris]).includes(white))throw Error('Missing iris clipping: '+side);
    }
    return {drawables:d.count,vertices:Array.from(d.vertexCounts).reduce((a,b)=>a+b,0),parameters:Array.from({length:m.getParameterCount()},(_,i)=>({id:m.getParameterId(i).getString(),min:m.getParameterMinimumValue(i),max:m.getParameterMaximumValue(i)})),irisClipping:true};
  });
  const results=[];
  for(const p of meta.parameters){
    for(const v of [p.min,p.max]){
      await step({[p.id]:v});
      const check=await page.evaluate(()=>{
        const d=window.live2dQA.model.getModel().drawables,b=window.portraitBaseline;
        const changed=[];let maxDelta=0;
        for(let i=0;i<d.count;i++){
          let delta=0;
          for(let j=0;j<d.vertexPositions[i].length;j++){
            const x=d.vertexPositions[i][j];if(!Number.isFinite(x))throw Error('Nonfinite geometry');
            delta=Math.max(delta,Math.abs(x-b.vertices[i][j]));
          }
          if(delta>1e-6||Math.abs(d.opacities[i]-b.opacity[i])>1e-5)changed.push(d.ids[i]);
          maxDelta=Math.max(delta,maxDelta);
        }
        return {changed,maxDelta,finite:true};
      });
      results.push({parameter:p.id,value:v,...check});
    }
  }
  for(const p of meta.parameters){if(!results.some(r=>r.parameter===p.id&&r.changed.length))throw Error('Inert parameter: '+p.id)}
  const poses={neutral:{},blink:{ParamEyeLOpen:0,ParamEyeROpen:0},mouth:{ParamMouthOpenY:.85},left:{ParamAngleX:-25},right:{ParamAngleX:25},up:{ParamAngleY:18},down:{ParamAngleY:-18},tilt:{ParamAngleZ:12},gaze:{ParamEyeBallX:.8,ParamEyeBallY:.35}};
  for(const [name,p] of Object.entries(poses)){await step(p);await page.screenshot({path:`${root}/runtime-${name}.png`})}
  await step({ParamMouthOpenY:1});
  const mouthCloseHidden=await page.evaluate(()=>{const d=window.live2dQA.model.getModel().drawables;return d.opacities[Array.from(d.ids).indexOf('ArtMeshMouthClose')]<.001});
  if(!mouthCloseHidden)throw Error('Closed mouth persists during speech');
  const physics=await page.evaluate(async()=>{
    const q=window.live2dQA,m=q.model,values=[];q.freeze=false;
    const ids=Array.from({length:m.getParameterCount()},(_,i)=>m.getParameterId(i).getString());
    for(let f=0;f<180;f++){
      q.parameters={ParamAngleX:15*Math.sin(f/18),ParamAngleZ:8*Math.sin(f/25)};
      await new Promise(r=>requestAnimationFrame(r));
      values.push(['ParamHairFront','ParamHairBack'].map(id=>m.getParameterValueByIndex(ids.indexOf(id))));
    }
    q.parameters={};
    return ['front','back'].map((part,i)=>({part,min:Math.min(...values.map(v=>v[i])),max:Math.max(...values.map(v=>v[i]))}));
  });
  if(physics.some(p=>!Number.isFinite(p.min)||p.max-p.min<1e-4))throw Error('Hair physics inactive');
  const report={model:'InkPortrait',runtime:'Official Cubism SDK for Web 5-r.5',...meta,parameterTests:results,mouthCloseHidden,physics,visualPoses:Object.keys(poses),pass:true};
  await page.evaluate(report=>{window.portraitVerification=report},report);
  return {pass:report.pass,drawables:meta.drawables,parameters:meta.parameters.length,parameterExtremesTested:results.length,mouthCloseHidden,physics};
}
