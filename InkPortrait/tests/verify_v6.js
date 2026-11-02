async(page)=>{
 await page.bringToFront();
 const result=await page.evaluate(async()=>{
  const q=window.live2dQA;const snapshot=async(p)=>{q.freeze=true;q.parameters=p;for(let i=0;i<3;i++)await new Promise(r=>requestAnimationFrame(r));const d=q.model.getModel().drawables;return Object.fromEntries(['ArtMeshTopwear2','ArtMeshNeck','ArtMeshTopwear'].map(id=>{const i=Array.from(d.ids).indexOf(id);if(i<0)throw Error('Missing collar/neck');return [id,{order:d.drawOrders[i],positions:Array.from(d.vertexPositions[i])}]}))};
  const base=await snapshot({});
  if(!(base.ArtMeshTopwear2.order<base.ArtMeshNeck.order && base.ArtMeshNeck.order<base.ArtMeshTopwear.order))throw Error('Incorrect rear collar occlusion');
  const yaw=await snapshot({ParamAngleX:45,ParamAngleZ:-12});
  const body=await snapshot({ParamBodyAngleX:10});
  const delta=(a,b)=>Math.max(...a.map((n,i)=>Math.abs(n-b[i])));
  const headDelta=delta(base.ArtMeshTopwear2.positions,yaw.ArtMeshTopwear2.positions);
  const bodyDelta=delta(base.ArtMeshTopwear2.positions,body.ArtMeshTopwear2.positions);
  if(headDelta>1e-5 || bodyDelta<1e-5)throw Error('Rear collar must follow clothing, not head');
  return {pass:true,rearCollarOrder:base.ArtMeshTopwear2.order,neckOrder:base.ArtMeshNeck.order,frontCollarOrder:base.ArtMeshTopwear.order,headDelta,bodyDelta};
 });
 await page.evaluate(r=>window.portraitV6Verification=r,result);
 return result;
}
