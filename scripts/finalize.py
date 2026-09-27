import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from validation import *
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'checkpoints'/'m07.blend'))
bpy.context.scene.frame_set(1)
# Fix blade winding discovered by signed-volume checks, including the independent cutaway.
import bmesh
seen=set()
for ob in bpy.data.objects:
    if ob.type=='MESH' and 'Blade_' in ob.name and ob.data not in seen:
        seen.add(ob.data);bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
# Tame Bezier overshoot at the cable's turn behind the left wall.
o=bpy.data.objects['CBL_USB_Data']
for sp in o.data.splines:
    for p in sp.bezier_points:
        left=p.handle_left.copy();right=p.handle_right.copy()
        enum_set(p,'handle_left_type','FREE');enum_set(p,'handle_right_type','FREE')
        for attr,co in [('handle_left',left),('handle_right',right)]:
            world=o.matrix_world@co;world.x=max(-.167,min(.166,world.x));world.y=max(-.163,min(.162,world.y))
            setattr(p,attr,o.matrix_world.inverted()@world)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg)
co=bpy.data.objects['CUT_CBL_USB_Data'];co.data=me;co.matrix_world=o.matrix_world.copy()
# Move every clamp-state key to a collision-free validation position.
for name,delta in [('ASM_Cover',(0,0,.62)),('ASM_BuildPlate',(0,-.015,.23)),('ASM_PrintSample',(0,-.015,.23))]:
    ob=bpy.data.objects[name];ob['explode_delta']=delta;ob.location=Vector(ob['assembled_location'])+Vector(delta);ob.keyframe_insert(data_path='location',frame=100,group='Validation pose')
bpy.context.scene.frame_set(1)
cam=bpy.data.objects['CAM_Exploded'];cam.location=(1.7,-2.65,2.0);aim(cam,(0,0,.78))
# Recess the IEC pins into a physically modeled inlet mouth.
iec=bpy.data.objects['PRT_IEC_Input']
boolean(iec,box('TOOL_IECSocket',(.024,.020,.017),(-.110,.180,.074),'00_REFERENCE',bevel=0))
for n in ['PRT_IEC_Pin','PRT_IEC_Pin.001','PRT_IEC_EarthPin']:
    ob=bpy.data.objects[n];ob.location.y-=.009
    if bpy.data.objects.get('CUT_'+n):bpy.data.objects['CUT_'+n].location.y-=.009
cutiec=bpy.data.objects['CUT_PRT_IEC_Input'];cutiec.data=bpy.data.meshes.new_from_object(iec.evaluated_get(bpy.context.evaluated_depsgraph_get()),depsgraph=bpy.context.evaluated_depsgraph_get())
audit=geometry_audit();manifest()
if audit['issues'] or audit['open_meshes'] or audit['zero_area_faces']:
    raise RuntimeError('Review geometry_audit.json before delivery')
# Save the assembled master, not the export working copy.
bpy.context.scene.camera=bpy.data.objects['CAM_Hero_3Quarter']
bpy.context.scene.render.resolution_x=1800;bpy.context.scene.render.resolution_y=1800;bpy.context.scene.cycles.samples=96
cyclorama()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'resin_printer_master.blend'))
print('MASTER_SAVED',flush=True)
bpy.context.scene.frame_set(100)
render('milestones/07_exploded_validation.png','CAM_Exploded',1400,64)
bpy.context.scene.frame_set(1)
render('milestones/08_export_ready_back.png','CAM_Back',1100,48)
