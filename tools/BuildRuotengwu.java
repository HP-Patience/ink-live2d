import io.github.psd2live.core.*;
import org.umamo.runtime.model.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;

/** Reuses PSD2Live's authoring/export API; no custom MOC3 encoder. */
class BuildRuotengwu {
  static final Set<String> INPUTS=Set.of("desktop","mouse","hand mouse","hand keyboard");
  static String id(Object o) throws Exception {
    if(o instanceof org.umamo.format.art.SourceLayer) return (String)org.umamo.format.art.SourceLayer.class.getMethod("getId-VrS5uwI").invoke(o);
    for(var m:o.getClass().getMethods())
      if((m.getName().startsWith("getId-")||m.getName().equals("getId"))&&m.getParameterCount()==0)
        return (String)m.invoke(o);
    throw new IllegalArgumentException("No ID accessor: "+o.getClass());
  }
  static PipelineConfig config(Map<String,LayerClassificationOverride> tags,Map<String,String> parents,RigEditOverlay edits) {
    var d=new PipelineConfig();
    return d.copy(4096,d.getTextureUpscale(),3,24,
      d.getMeshOuterMargin(),d.getMeshInnerMargin(),d.getMeshMaxEdgeDistance(),d.getMeshInteriorDensity(),d.getMeshOverrides(),d.getAlphaThreshold(),
      .28f,.20f,false,true,true,false,"flat",MouthCurve.Companion.preset("flat"),null,1f,
      true,true,true,true,true,true,true,true,false,true,true,true,
      tags,d.getLayerVisibility(),d.getDeletedLayerIds(),parents,d.getDrawOrderOverrides(),edits);
  }
  static RigEditOverlay parameter(RigEditOverlay edits,String name,float min,float max) {
    return edits.upsert(new RigParameterEdit(name,name,min,max,0f,ParameterKind.NORMAL,false,true));
  }
  static RigEditOverlay meshKey(RigEditOverlay edits,String mesh,Map<String,Float> pose,List<Float> deltas) {
    return edits.setKeyform(new RigKeyformSetEdit(new RigTargetRef(RigTargetKind.ART_MESH,mesh,null),pose,
      new RigKeyformGeometryEdit(null,null,null,null,null,deltas),null));
  }
  static float smooth(float v) {v=Math.max(0f,Math.min(1f,v));return v*v*(3f-2f*v);}
  public static void main(String[] args) throws Exception {
    if(args.length!=2)throw new IllegalArgumentException("input.psd output-directory");
    var pipeline=new PSD2LivePipeline();var defaults=new PipelineConfig();
    var analysis=pipeline.inspect(Path.of(args[0]),defaults);
    var tags=new HashMap<String,LayerClassificationOverride>();var parents=new HashMap<String,String>();
    var found=new HashSet<String>();
    for(var layer:analysis.getLayers()) {
      String name=layer.getSource().getName(),layerId=id(layer.getSource());
      System.out.println("LAYER ["+name+"] "+layerId+" "+layer.getSemantic());
      if(INPUTS.contains(name)) {
        tags.put(layerId,new LayerClassificationOverride(SemanticTag.OBJECTS,Side.NONE));
        parents.put(layerId,"DeformBodyXY");found.add(name);
      }
    }
    if(!found.equals(INPUTS))throw new AssertionError("Missing input art: "+found);
    var edits=new RigEditOverlay();
    // BongoCat's viewer gain is calibrated to +/-30 horizontal units; the
    // portrait exporter's +/-45 default made direction reversals too abrupt.
    // Keep the authored keys, exposing the normal desktop range and modest tilt.
    edits=edits.upsert(new RigParameterEdit("ParamAngleX","Head X",-30f,30f,0f,ParameterKind.NORMAL,false,false));
    edits=edits.upsert(new RigParameterEdit("ParamAngleZ","Head tilt",-12f,12f,0f,ParameterKind.NORMAL,false,false));
    edits=parameter(edits,"CatParamLeftHandDown",0f,1f);
    edits=parameter(edits,"ParamMouseX",-30f,30f);
    edits=parameter(edits,"ParamMouseY",-30f,30f);
    edits=parameter(edits,"ParamMouseLeftDown",0f,1f);
    edits=parameter(edits,"ParamMouseRightDown",0f,1f);
    var preview=pipeline.buildPreview(Path.of(args[0]),config(tags,parents,edits));
    var frame=preview.getAnalysis().getAnchors().getCharacter();
    Deformer.Warp root=null;
    for(var deformer:preview.getRig().getPuppet().getDeformers())
      if(id(deformer).equals("DeformBodyXY"))root=(Deformer.Warp)deformer;
    if(root==null)throw new AssertionError("Expected root body warp");
    // Seated desktop stays rigid. Breathing continues below this root in BodyZBreath.
    var points=new ArrayList<Float>();
    for(int row=0;row<=root.getRows();row++)for(int col=0;col<=root.getColumns();col++) {
      points.add(frame.getLeft()+col*frame.getWidth()/root.getColumns());
      points.add(frame.getTop()+row*frame.getHeight()/root.getRows());
    }
    for(float x:new float[]{-10,0,10})for(float y:new float[]{-10,0,10})
      edits=edits.setKeyform(new RigKeyformSetEdit(new RigTargetRef(RigTargetKind.WARP_DEFORMER,"DeformBodyXY",null),
        Map.of("ParamBodyAngleX",x,"ParamBodyAngleY",y),new RigKeyformGeometryEdit(points,null,null,null,null,null),null));
    int driven=0;
    for(var mesh:preview.getRig().getPuppet().getDrawables()) {
      String name=mesh.getName();if(!INPUTS.contains(name)||name.equals("desktop"))continue;
      float[] pos=mesh.getMesh().getPositions();if(pos.length<6)throw new AssertionError("Empty input mesh");
      boolean keyboard=name.equals("hand keyboard"),hand=name.startsWith("hand ");
      if(keyboard) {
        for(float down:new float[]{0,1}) {
          var delta=new ArrayList<Float>();
          for(int i=0;i<pos.length;i+=2) {
            float canvasY=frame.getTop()+pos[i+1]*frame.getHeight();
            float w=smooth((canvasY-835f)/165f);
            delta.add(0f);delta.add(7f*down*w/frame.getHeight());
          }
          // Native Bongo per-key overlays carry the corresponding hand pose.
          // Hide only this resting keyboard arm while any physical key is held.
          edits=edits.setKeyform(new RigKeyformSetEdit(new RigTargetRef(RigTargetKind.ART_MESH,id(mesh),null),
            Map.of("CatParamLeftHandDown",down),null,
            new RigKeyformChannelsEdit(1f-down,null,null,null,null,null,null)));
        }
      } else {
        // Explicit combined keys keep pointer movement and either/both buttons additive.
        for(float x:new float[]{-30,0,30})for(float y:new float[]{-30,0,30})
        for(float left:new float[]{0,1})for(float right:new float[]{0,1}) {
          var delta=new ArrayList<Float>();
          for(int i=0;i<pos.length;i+=2) {
            float canvasY=frame.getTop()+pos[i+1]*frame.getHeight();
            float w=hand?smooth((canvasY-830f)/155f):1f;
            float press=Math.min(1f,left+right);
            // The character faces the user across the desk. Rotate only the
            // desk-plane hand/mouse translation by 180 degrees; gaze still uses
            // ParamAngle/EyeBall screen coordinates. Button press stays downward.
            delta.add((-x*3.0f)*w/frame.getWidth());
            delta.add((y*1.20f+(hand?5f:.7f)*press)*w/frame.getHeight());
          }
          edits=meshKey(edits,id(mesh),Map.of("ParamMouseX",x,"ParamMouseY",y,"ParamMouseLeftDown",left,"ParamMouseRightDown",right),delta);
        }
      }
      driven++;System.out.println("DRIVEN "+name+" "+id(mesh)+" vertices="+pos.length/2);
    }
    if(driven!=3)throw new AssertionError("Must rig both hands and mouse, got "+driven);
    var result=pipeline.run(Path.of(args[0]),Path.of(args[1]),config(tags,parents,edits),
      (stage,fraction)->System.out.printf("%3.0f%% %s%n",fraction*100,stage));
    System.out.println("Exported "+result.getExportedFiles().size()+" files");
    result.getWarnings().forEach(System.out::println);
    System.out.println("PARAMETERS "+result.getPreviewModel().getRig().getPuppet().getParameters().size());
    System.out.println("DRAWABLES "+result.getPreviewModel().getRig().getPuppet().getDrawables().size());
  }
}



