"""Import each main GLB into an empty Blender scene and compare production evidence."""
import bpy,sys,json,bmesh,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
expected=json.loads((ROOT/'reports'/'export_expected.json').read_text())
def glb_json(path):
    data=path.read_bytes();magic,version,length=struct.unpack_from('<III',data)
    if magic!=0x46546c67 or version!=2 or length!=len(data):raise RuntimeError('Invalid GLB header')
    size,kind=struct.unpack_from('<II',data,12)
    if kind!=0x4e4f534a:raise RuntimeError('No JSON chunk')
    return json.loads(data[20:20+size])
reports=[]
for filename in ['resin_printer_complete.glb','resin_printer_explodable.glb']:
    path=ROOT/'exports'/filename;j=glb_json(path)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
    report={'file':filename,'bytes':path.stat().st_size,'nodes':len(j.get('nodes',[])),'meshes':len(j.get('meshes',[])),'materials':len(j.get('materials',[])),'animations':len(j.get('animations',[])),'checks':{},'errors':[],'max_world_matrix_error':0,'max_bounds_error_m':0,'normal_checks':{'nonfinite':0,'nonunit':0},'triangle_count':0}
    required=set(expected['assembled']);found=set(bpy.data.objects.keys())
    if required-found:report['errors'].append({'missing_nodes':sorted(required-found)})
    if any(o.type in {'CAMERA','LIGHT'} for o in bpy.data.objects):report['errors'].append('Studio object leaked into export')
    for name,item in expected['assembled'].items():
        o=bpy.data.objects.get(name)
        if not o:continue
        parent=o.parent.name if o.parent else None
        if parent!=item['parent']:report['errors'].append({'parent':name,'expected':item['parent'],'actual':parent})
        flat=[v for row in o.matrix_world for v in row]
        err=max(abs(a-b) for a,b in zip(flat,item['matrix_world']));report['max_world_matrix_error']=max(err,report['max_world_matrix_error'])
        if err>2e-5:report['errors'].append({'transform':name,'error':err})
        if 'triangles' in item:
            if o.type!='MESH':report['errors'].append({'not_mesh':name});continue
            me=o.data;me.calc_loop_triangles();tri=len(me.loop_triangles);report['triangle_count']+=tri
            if tri!=item['triangles']:report['errors'].append({'triangles':name,'expected':item['triangles'],'actual':tri})
            pts=[o.matrix_world@v.co for v in me.vertices]
            lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
            berr=max(abs(a-b) for a,b in zip(lo+hi,item['bounds_min']+item['bounds_max']));report['max_bounds_error_m']=max(berr,report['max_bounds_error_m'])
            if berr>2e-5:report['errors'].append({'bounds':name,'error_m':berr})
            mats=[m.name for m in me.materials if m]
            if set(mats)!=set(item['materials']):report['errors'].append({'materials':name,'expected':item['materials'],'actual':mats})
            area=0.;vol=0.
            for t in me.loop_triangles:
                a,b,c=[me.vertices[i].co for i in t.vertices];area+=(b-a).cross(c-a).length*.5;vol+=a.dot(b.cross(c))/6
            if abs(area-item['surface_area'])>max(1e-9,item['surface_area']*.0001):report['errors'].append({'surface_area':name})
            if abs(vol-item['signed_volume'])>max(1e-12,abs(item['signed_volume'])*.001):report['errors'].append({'signed_volume':name,'expected':item['signed_volume'],'actual':vol})
            for no in me.corner_normals:
                l=no.vector.length
                if not math.isfinite(l):report['normal_checks']['nonfinite']+=1
                elif abs(l-1)>1e-4:report['normal_checks']['nonunit']+=1
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
            nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
            if nonmanifold:report['errors'].append({'non_manifold_after_weld':name,'edges':nonmanifold})
    if filename.endswith('explodable.glb'):
        if not j.get('animations'):report['errors'].append('Missing validation animation')
        s.frame_set(100);bpy.context.view_layer.update();maxerr=0
        for name,item in expected['exploded'].items():
            if name not in bpy.data.objects:continue
            ob=bpy.data.objects[name];flat=[v for row in ob.matrix_world for v in row]
            err=max(abs(a-b) for a,b in zip(flat,item['matrix_world']));maxerr=max(maxerr,err)
            if err>3e-5:report['errors'].append({'exploded_transform':name,'error':err})
        report['max_exploded_matrix_error']=maxerr
    # Verify glTF PBR values and glass transmission are genuinely present.
    for name in ['MAT_UV_Cover_Amber','MAT_Glass','MAT_Anodized_Aluminum_Silver','MAT_PCB_Green_or_Black']:
        materials=[m for m in j.get('materials',[]) if m.get('name')==name]
        if not materials:report['errors'].append({'missing_material':name})
        elif name in ['MAT_UV_Cover_Amber','MAT_Glass'] and materials[0].get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)<.95:report['errors'].append({'missing_transmission':name})
    report['passed']=not report['errors'] and not any(report['normal_checks'].values())
    reports.append(report)
    print('ROUNDTRIP',filename,'PASS' if report['passed'] else 'FAIL','errors',len(report['errors']),flush=True)
    (ROOT/'reports'/'roundtrip_validation.json').write_text(json.dumps(reports,indent=2))
if not all(r['passed'] for r in reports):raise RuntimeError('GLB round-trip validation failed; see reports/roundtrip_validation.json')
