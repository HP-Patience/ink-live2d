import io.github.psd2live.core.*;
import java.nio.file.*;

// Use upstream authoring settings omitted from its CLI; no exporter/rig reimplementation.
class BuildPortrait {
  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("input.psd output-directory");
    var d = new PipelineConfig();
    var pipeline = new PSD2LivePipeline();
    var parents = new java.util.HashMap<String,String>();
    var sourceId = org.umamo.format.art.SourceLayer.class.getMethod("getId-VrS5uwI");
    for (var layer : pipeline.inspect(Path.of(args[0]),d).getLayers()) {
      var name=layer.getSource().getName();
      if (name.equals("facedetail-r") || name.equals("facedetail-l")) {
        var side=name.endsWith("-r") ? "R" : "L";
        parents.put((String)sourceId.invoke(layer.getSource()),"DeformEyeShape"+side);
      }
    }
    if(parents.size()!=2) throw new AssertionError("Both lower lashes must follow their own eye shape");
    System.out.println("Lower-lash parents: "+parents);
    var c = d.copy(4096,d.getTextureUpscale(),d.getTexturePadding(),24,
      d.getMeshOuterMargin(),d.getMeshInnerMargin(),d.getMeshMaxEdgeDistance(),d.getMeshInteriorDensity(),d.getMeshOverrides(),d.getAlphaThreshold(),
      .35f,.3f,false,true,true,false,"flat",MouthCurve.Companion.preset("flat"),null,1f,
      true,true,true,true,true,true,true,true,true,true,true,true,
      d.getLayerOverrides(),d.getLayerVisibility(),d.getDeletedLayerIds(),parents,d.getDrawOrderOverrides(),d.getRigEdits());
    if(c.getMouthOutlineEnabled() || !c.getMouthShape().equals("flat")) throw new AssertionError("Mouth must retain original closed expression");
    var r = pipeline.run(Path.of(args[0]),Path.of(args[1]),c,(stage,fraction)->System.out.printf("%3.0f%% %s%n",fraction*100,stage));
    System.out.println("Exported: "+r.getExportedFiles().size());
    r.getWarnings().forEach(System.out::println);
  }
}
