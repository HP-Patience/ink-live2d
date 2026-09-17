async(page)=>{
 await page.bringToFront();const results=[];
 for(const x of [-45,45])for(const y of [-30,0,30])for(const z of [-30,30]){
  const params={ParamAngleX:x,ParamAngleY:y,ParamAngleZ:z};
  await page.evaluate(async p=>{const q=window.live2dQA;q.freeze=true;q.parameters=p;for(let i=0;i<3;i++)await new Promise(r=>requestAnimationFrame(r));if(q.model.getModel().drawables.vertexPositions.some(v=>Array.from(v).some(n=>!Number.isFinite(n))))throw Error('Invalid combined pose')},params);
  const name=`v3-combo-${x}-${y}-${z}`;await page.screenshot({path:`workspace/${name}.png`});results.push({params,name,finite:true});
 }
 await page.evaluate(r=>window.portraitV3Verification={pass:true,combinedPoses:r},results);
 return {pass:true,combinedPoses:results.length};
}
