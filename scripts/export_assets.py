import sys,json,bmesh,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from validation import production_objects
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'resin_printer_master.blend'))
s=bpy.context.scene;s.frame_set(1)
obs=production_objects();names={o.name for o in obs}
# All mesh conversion is confined to this disposable export process.
for c in bpy.data.collections:c.hide_viewport=False
for o in obs:o.hide_viewport=False;o.hide_set(False)
dg=bpy.context.evaluated_depsgraph_get()
curves=[o for o in obs if o.type in {'CURVE','FONT'}]
for o in curves:
    oldname=o.name;mx=o.matrix_world.copy();pa=o.parent;children={c:c.matrix_world.copy() for c in o.children}
    e=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    new=bpy.data.objects.new(oldname+'_Baked',me)
    for c in o.users_collection:c.objects.link(new)
    for k in o.keys():new[k]=o[k]
    new.parent=pa;new.matrix_world=mx
    if o.animation_data and o.animation_data.action:
        new.animation_data_create();new.animation_data.action=o.animation_data.action
        try:new.animation_data.action_slot=o.animation_data.action_slot
        except Exception:pass
    for c,m in children.items():c.parent=new;c.matrix_world=m
    bpy.data.objects.remove(o,do_unlink=True);new.name=oldname
    dg=bpy.context.evaluated_depsgraph_get()
obs=[bpy.data.objects[n] for n in sorted(names)]
cleanup=[]
# Bake evaluated mesh geometry and remove zero-area triangulation slivers around hex drives.
# The Blender master retains its modifiers and quad/ngon modeling topology.
dg=bpy.context.evaluated_depsgraph_get()
for o in obs:
    if o.type!='MESH':continue
    e=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg);me.calc_loop_triangles()
    bad=0
    for t in me.loop_triangles:
        a,b,c=[me.vertices[i].co for i in t.vertices]
        if (b-a).cross(c-a).length*.5<1e-13:bad+=1
    if bad:
        bm=bmesh.new();bm.from_mesh(me)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
        cleanup.append({'object':o.name,'degenerate_triangles_before':bad})
    o.data=me;o.modifiers.clear()
print('EXPORT_SLIVER_CLEANUP',len(cleanup),flush=True)
(ROOT/'reports'/'export_mesh_cleanup.json').write_text(json.dumps(cleanup,indent=2))
def snapshot():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out={}
    for o in obs:
        item={'parent':o.parent.name if o.parent else None,'matrix_world':[v for row in o.matrix_world for v in row],'materials':[sl.material.name for sl in o.material_slots if sl.material] if hasattr(o,'material_slots') else []}
        if o.type=='MESH':
            e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();pts=[o.matrix_world@v.co for v in me.vertices]
            area=0.;volume=0.
            for t in me.loop_triangles:
                a,b,c=[me.vertices[i].co for i in t.vertices];area+=(b-a).cross(c-a).length*.5;volume+=a.dot(b.cross(c))/6
            used={p.material_index for p in me.polygons}
            item['materials']=[me.materials[i].name for i in used if i<len(me.materials) and me.materials[i]]
            item.update(triangles=len(me.loop_triangles),bounds_min=[min(p[i] for p in pts) for i in range(3)],bounds_max=[max(p[i] for p in pts) for i in range(3)],surface_area=area,signed_volume=volume)
            e.to_mesh_clear()
        out[o.name]=item
    return out
snap={'assembled':snapshot()};s.frame_set(100);snap['exploded']=snapshot();s.frame_set(1)
(ROOT/'reports'/'export_expected.json').write_text(json.dumps(snap,indent=2))
rna=bpy.ops.export_scene.gltf.get_rna_type()
import io_scene_gltf2
formats=[v[0] for v in io_scene_gltf2.get_format_items(None,bpy.context)]
print('EXPORT_FORMATS',formats,flush=True)
if 'GLB' not in formats:raise RuntimeError('Binary glTF unavailable')
def export(name,chosen,animated=False,extras=True):
    bpy.ops.object.select_all(action='DESELECT')
    for o in chosen:o.select_set(True)
    kwargs={'filepath':str(ROOT/'exports'/name),'export_format':'GLB','use_selection':True,'export_apply':True,'export_animations':animated,'export_extras':extras,'export_normals':True,'export_yup':True}
    if animated:
        if 'SCENE' not in [i.identifier for i in rna.properties['export_animation_mode'].enum_items]:raise RuntimeError('SCENE animation export unavailable')
        kwargs['export_animation_mode']='SCENE';kwargs['export_frame_range']=True;kwargs['export_anim_scene_split_object']=False;kwargs['export_nla_strips_merged_animation_name']='EXPLODED_VALIDATION'
    bpy.ops.export_scene.gltf(**kwargs)
    print('EXPORTED',name,flush=True)
export('resin_printer_complete.glb',obs,False,False)
export('resin_printer_explodable.glb',obs,True,True)
for filename,group in [('build_plate.glb','03_BUILD_PLATFORM'),('resin_vat.glb','04_RESIN_VAT'),('lcd_stack.glb','05_LCD_STACK'),('z_axis.glb','06_Z_AXIS'),('uv_light_engine.glb','07_LIGHT_ENGINE'),('electronics.glb','10_ELECTRONICS')]:
    chosen=[o for o in obs if o in set(coll(group).all_objects)]
    # Keep the root and ancestor nodes so subsystem coordinates match the complete model.
    expanded=set(chosen)
    for o in chosen:
        p=o.parent
        while p:expanded.add(p);p=p.parent
    export(filename,list(expanded))
print('ALL_EXPORTS_DONE',flush=True)
