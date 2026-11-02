async (page) => {
  await page.bringToFront();
  const results=await page.evaluate(async()=>{
    const q=window.live2dQA;
    const step=async(params)=>{
      q.freeze=true;q.parameters=params;
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      const d=q.model.getModel().drawables;
      return Object.fromEntries(['R','L'].flatMap(side=>['ArtMeshEyelash','ArtMeshFaceDetail'].map(name=>{
        const v=d.vertexPositions[Array.from(d.ids).indexOf(name+side)];
        let sum=0;for(let i=1;i<v.length;i+=2)sum+=v[i];
        return[name+side,sum/(v.length/2)];
      })));
    };
    const baseline=await step({});const results=[];
    for(const pitch of [-30,-18,18,30]) {
      const pos=await step({ParamAngleY:pitch});
      for(const side of ['R','L']) {
        const upper=pos['ArtMeshEyelash'+side]-baseline['ArtMeshEyelash'+side];
        const lower=pos['ArtMeshFaceDetail'+side]-baseline['ArtMeshFaceDetail'+side];
        results.push({pitch,side,upper,lower,error:Math.abs(upper-lower),pass:Math.abs(upper-lower)<.003});
      }
    }
    return results;
  });
  if(results.some(r=>!r.pass))throw Error('Lower eyelid detached from eye: '+JSON.stringify(results));
  for(const x of [-45,45])for(const y of [-30,30]) {
    await page.evaluate(async({x,y})=>{
      const q=window.live2dQA;q.parameters={ParamAngleX:x,ParamAngleY:y};
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      const d=q.model.getModel().drawables;
      if(d.vertexPositions.some(v=>Array.from(v).some(n=>!Number.isFinite(n))))throw Error('Invalid corner geometry');
    },{x,y});
  }
  await page.evaluate(results=>window.portraitBugfixVerification={pass:true,lowerLashTests:results,combinedCornersTested:4},results);
  return {pass:true,lowerLashTests:results,combinedCornersTested:4};
}
