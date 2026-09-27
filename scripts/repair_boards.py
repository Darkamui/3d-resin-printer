import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from stages import board
from validation import geometry_audit,manifest,production_objects
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'resin_printer_master.blend'))
bpy.context.scene.frame_set(1)
for name,center,size,rotate in [('LCD_Controller',(.139,-.042,.137),(.090,.030),True),('USB_Data_Board',(-.102,-.144,.132),(.056,.030),False)]:
    old=bpy.data.objects['ASM_'+name]
    for o in list(old.children_recursive):
        if bpy.data.objects.get('CUT_'+o.name):bpy.data.objects.remove(bpy.data.objects['CUT_'+o.name],do_unlink=True)
        bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.objects.remove(old,do_unlink=True)
    new=board(name,center,size)
    bpy.context.view_layer.update()
    if rotate:
        turn=Matrix.Translation(Vector(center))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-Vector(center))
        children={o:turn@o.matrix_world for o in new.children}
        for o,mx in children.items():o.matrix_world=mx
    bpy.context.view_layer.update()
    for o in list(new.children):
        if o.type not in {'MESH','CURVE','FONT'}:continue
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg)
        dupe=bpy.data.objects.new('CUT_'+o.name,me);coll('17_CUTAWAY').objects.link(dupe);dupe.parent=bpy.data.objects['ASM_Cutaway'];dupe.matrix_world=o.matrix_world.copy();dupe['source_part']=o.name
for o in production_objects():
    if o.name not in coll('EXPORT').objects:coll('EXPORT').objects.link(o)
geometry_audit();manifest()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'resin_printer_master.blend'))
