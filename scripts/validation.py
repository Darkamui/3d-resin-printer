from common import *
import bmesh

def production_objects():
    candidates=set()
    for g in GROUPS[1:17]:
        candidates.update(coll(g).all_objects)
    return sorted([o for o in candidates if not o.name.startswith(('BLOCK_','TOOL_')) and 'Print_10Percent' not in o.name and 'Print_50Percent' not in o.name and not o.get('optional',False)],key=lambda o:o.name)

def geometry_audit():
    dg=bpy.context.evaluated_depsgraph_get();obs=production_objects()
    report={'units':'meters','front_axis':'-Y','up_axis':'+Z','object_count':len(obs),'mesh_count':0,'triangles':0,'materials':len(bpy.data.materials),'issues':[], 'open_meshes':[], 'zero_area_faces':[], 'assemblies':{},'curve_text_cap_seams_welded':[]}
    bounds=[]
    for o in obs:
        report['assemblies'][o.get('assembly','Hierarchy / sample')]=report['assemblies'].get(o.get('assembly','Hierarchy / sample'),0)+1
        if any(abs(v-1)>1e-6 for v in o.scale):report['issues'].append({'object':o.name,'issue':'Non-unit object scale','scale':list(o.scale)})
        if o.type in {'MESH','CURVE','FONT'}:
            e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();report['triangles']+=len(m.loop_triangles);report['mesh_count']+=1
            bm=bmesh.new();bm.from_mesh(m)
            if o.type in {'CURVE','FONT'}:
                raw_bad=sum(not x.is_manifold for x in bm.edges)
                bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
                if raw_bad:report['curve_text_cap_seams_welded'].append(o.name)
            bad=sum(not x.is_manifold for x in bm.edges)
            zero=sum(f.calc_area()<1e-16 for f in bm.faces)
            if bad:report['open_meshes'].append({'object':o.name,'non_manifold_edges':bad})
            if zero:report['zero_area_faces'].append({'object':o.name,'faces':zero})
            if bm.calc_volume(signed=True)<-1e-13:report['issues'].append({'object':o.name,'issue':'Inward face winding'})
            bm.free()
            bounds += [tuple(o.matrix_world@Vector(v)) for v in o.bound_box]
            e.to_mesh_clear()
    if bounds:
        lo=[min(p[i] for p in bounds) for i in range(3)];hi=[max(p[i] for p in bounds) for i in range(3)]
        report['bounds_m']={'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]}
    report['critical_clearances_m']={'film_bottom_to_protector_top':.19515-.000075-(.19475+.00005),'lcd_active_width':.220,'lcd_active_depth':.124,'cover_wall':.003}
    report['notes']=['Fastener contact, bonded optical layers, shaft/thread overlap and press-fit joints intentionally overlap.','Topology is checked on evaluated meshes, with coincident curve/text cap seams welded at 1e-8 m exactly as in export preparation. The Blender master preserves editable curves and text.','Whole-scene collision-free assembly is not mechanically certified.','Print states other than complete and liquid resin are optional and excluded from production GLBs.']
    (ROOT/'reports'/'geometry_audit.json').write_text(json.dumps(report,indent=2))
    print('AUDIT',report['object_count'],report['triangles'],'triangles','open',len(report['open_meshes']),'issues',len(report['issues']),flush=True)
    return report

def manifest():
    bpy.context.view_layer.update()
    obs=production_objects();result={}
    for o in obs:
        result[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix_world':[v for row in o.matrix_world for v in row],'materials':[s.material.name for s in o.material_slots if s.material] if hasattr(o,'material_slots') else [],'explode_delta':list(o.get('explode_delta',[0,0,0]))}
    (ROOT/'reports'/'assembly_manifest.json').write_text(json.dumps(result,indent=2))
    return result

def make_cutaway():
    dg=bpy.context.evaluated_depsgraph_get();root=empty('ASM_Cutaway','17_CUTAWAY')
    # The front-right quadrant below the build volume is opened. Optical and vat solids are capped.
    cut_names={'04_RESIN_VAT','05_LCD_STACK','07_LIGHT_ENGINE','09_HOUSING'}
    obs=production_objects()
    for o in obs:
        groups={c.name for c in o.users_collection}
        if o.type not in {'MESH','CURVE','FONT'} or '02_UV_COVER' in groups:continue
        e=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg)
        ob=bpy.data.objects.new('CUT_'+o.name,me);coll('17_CUTAWAY').objects.link(ob);ob.matrix_world=o.matrix_world.copy()
        ob.parent=root
        ob['source_part']=o.name
        if groups&cut_names:
            bb=[ob.matrix_world@Vector(p) for p in ob.bound_box]
            # New bound boxes need an update before inclusion tests.
            bpy.context.view_layer.update();bb=[ob.matrix_world@Vector(p) for p in ob.bound_box]
            inside=[p.x>.004 and p.y<.012 and p.z<.285 for p in bb]
            if all(inside):bpy.data.objects.remove(ob,do_unlink=True);continue
            if max(p.x for p in bb)>.004 and min(p.y for p in bb)<.012 and min(p.z for p in bb)<.285:
                cutter=box('TOOL_Cutaway',(1.0,1.0,.6),(.504,-.488,-.015),'00_REFERENCE',bevel=0)
                boolean(ob,cutter)
    coll('17_CUTAWAY').hide_render=True;coll('17_CUTAWAY').hide_viewport=True

def setup_explosion():
    # A validation pose only. Frame 1 is assembly; frame 100 separates major systems.
    s=bpy.context.scene;s.frame_start=1;s.frame_end=100
    offsets={'CTRL_Printer':(0,0,.27),'ASM_Cover':(0,0,.62),'ASM_BuildPlate':(0,-.015,.23),'ASM_Vat':(0,-.025,.21),'ASM_LCDStack':(0,-.025,.105),'ASM_ZAxis':(0,.19,.025),'ASM_LightEngine':(0,-.055,-.105),'ASM_Cooling':(0,-.055,-.20),'ASM_Electronics':(.23,.15,.015),'ASM_Power':(-.24,.14,.01),'ASM_UI':(.035,-.26,0),'ASM_Cables':(.26,.12,0),'ASM_FrontPanel':(0,-.26,0),'ASM_RearPanel':(0,.26,0),'ASM_LeftPanel':(-.26,0,0),'ASM_RightPanel':(.26,0,0),'ASM_PrintSample':(0,-.015,.23)}
    # LCD components separate in their actual physical order.
    layer_order=['PRT_LCD_Mounting_Frame','PRT_Heat_Spreader','PRT_LCD_Frame','PRT_Polarizer_Bottom','PRT_LCDPanel','PRT_Polarizer_Top','PRT_Optical_Gasket','PRT_Protective_Glass','PRT_Screen_Protector']
    for i,name in enumerate(layer_order):offsets[name]=(0,0,.009*i)
    for o in production_objects():
        if o.name.startswith('PRT_LinearRail_'):offsets[o.name]=(-.04 if 'Left' in o.name else .04,0,0)
        if o.name in ['PRT_LeadScrew_Core','PRT_LeadScrew_HelicalThread']:offsets[o.name]=(.11,0,0)
    for name,delta in offsets.items():
        o=bpy.data.objects.get(name)
        if o is None:continue
        base=o.location.copy();o['assembled_location']=list(base);o['explode_delta']=list(delta)
        o.location=base;o.keyframe_insert(data_path='location',frame=1,group='Validation pose')
        o.location=base+Vector(delta);o.keyframe_insert(data_path='location',frame=100,group='Validation pose')
        if o.animation_data and o.animation_data.action:o.animation_data.action.name='VALIDATE_'+name
    s.timeline_markers.new('ASSEMBLED',frame=1);s.timeline_markers.new('EXPLODED VALIDATION',frame=100);s.frame_set(1)
    camera('CAM_Exploded', (1.7,-2.65,2.0),(0,0,.78),65)
    camera('CAM_Cutaway',(.72,-.96,.68),(0,0,.24),65)
