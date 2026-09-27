"""Real-scale hard-surface helpers. Run with Blender's bundled Python."""
import bpy, math, os, json
from mathutils import Vector, Matrix
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MM = .001
GROUPS = ['00_REFERENCE','01_COMPLETE','02_UV_COVER','03_BUILD_PLATFORM','04_RESIN_VAT','05_LCD_STACK','06_Z_AXIS','07_LIGHT_ENGINE','08_FRAME','09_HOUSING','10_ELECTRONICS','11_POWER','12_COOLING','13_UI','14_CABLES','15_FASTENERS','16_PRINT_SAMPLE','17_CUTAWAY']
ASMS = {'02_UV_COVER':'Cover','03_BUILD_PLATFORM':'BuildPlate','04_RESIN_VAT':'Vat','05_LCD_STACK':'LCDStack','06_Z_AXIS':'ZAxis','07_LIGHT_ENGINE':'LightEngine','08_FRAME':'Frame','09_HOUSING':'Housing','10_ELECTRONICS':'Electronics','11_POWER':'Power','12_COOLING':'Cooling','13_UI':'UI','14_CABLES':'Cables','15_FASTENERS':'Fasteners','16_PRINT_SAMPLE':'PrintSample'}

def enum_set(obj, attr, value):
    prop = obj.bl_rna.properties[attr]
    vals = [i.identifier for i in prop.enum_items]
    if value not in vals: raise RuntimeError(f'{attr}: {value} unavailable; {vals}')
    setattr(obj, attr, value)

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene
    s.name='Resin_Printer_Studio'
    enum_set(s.unit_settings,'system','METRIC'); s.unit_settings.scale_length=1
    root=coll('Resin_Printer')
    for g in GROUPS: coll(g,root)
    root_obj=empty('CTRL_Printer','01_COMPLETE')
    for g,a in ASMS.items(): empty('ASM_'+a,g,parent=root_obj)
    for d in ['checkpoints','renders/milestones','exports','reports']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    materials(); studio()

def mat(name,color,metal=0,rough=.35,trans=0,ior=1.45):
    m=bpy.data.materials.get('MAT_'+name) or bpy.data.materials.new('MAT_'+name)
    m.use_fake_user=True
    m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=rough
    n.inputs['Transmission Weight'].default_value=trans
    n.inputs['IOR'].default_value=ior
    m.diffuse_color=(*color,1)
    return m

def materials():
    mat('Anodized_Aluminum_Black',(.025,.032,.041),.8,.27)
    mat('Anodized_Aluminum_Silver',(.48,.53,.58),.85,.27)
    mat('Powdercoat_Black',(.032,.041,.053),.6,.38)
    mat('Steel',(.26,.29,.33),.9,.24)
    mat('Stainless_Steel',(.63,.69,.74),.95,.2)
    mat('Plastic_Black',(.012,.017,.022),.05,.31)
    mat('Rubber',(.009,.012,.014),0,.62)
    mat('UV_Cover_Amber',(.42,.12,.027),0,.13,.86)
    mat('Glass',(.85,.94,.98),0,.07,.98)
    mat('FEP',(.88,.94,.99),0,.09,.99,1.34)
    mat('LCD',(.013,.02,.038),.22,.19)
    mat('Polarizer',(.085,.10,.16),0,.2,.25)
    mat('PCB_Green_or_Black',(.018,.11,.074),.12,.39)
    mat('PCB_Blue',(.018,.053,.10),.2,.34)
    mat('Copper',(.6,.28,.065),.85,.25)
    mat('Resin',(.10,.22,.25),0,.17,.28,1.47)
    mat('Print_Resin',(.17,.31,.35),.05,.3)
    mat('Ceramic',(.75,.77,.7),.0,.36)
    mat('LED_Lens',(.65,.55,.86),.1,.12,.65)
    mat('Wire_Red',(.32,.022,.013),.05,.38)
    mat('Wire_Blue',(.018,.08,.24),.05,.38)
    mat('Wire_Yellow',(.55,.35,.015),0,.42)
    mat('Marking',(.62,.69,.72),.2,.42)
    mat('Accent',(.82,.28,.065),.65,.3)
    mat('Studio',(.14,.18,.22),0,.65)

def material(name): return bpy.data.materials['MAT_'+name]

def register(o,name,group,ma=None,parent=None,origin=None):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    coll(group).objects.link(o)
    if o.data: o.data.name=name+'_Geometry'
    if ma and hasattr(o.data,'materials'): o.data.materials.append(material(ma))
    if parent is None and group in ASMS: parent=bpy.data.objects.get('ASM_'+ASMS[group])
    if isinstance(parent,str): parent=bpy.data.objects[parent]
    if parent:
        mx=o.matrix_basis.copy(); o.parent=parent; o.matrix_parent_inverse=parent.matrix_world.inverted(); o.matrix_basis=mx
    if origin is not None: set_origin(o,origin)
    if group in ASMS: o['assembly']=ASMS[group]; o['dimension_source']='Original design estimate; meters'
    return o

def set_origin(o,p):
    bpy.context.view_layer.update()
    p=Vector(p); delta=o.matrix_world.inverted()@p
    if o.data and hasattr(o.data,'transform'): o.data.transform(Matrix.Translation(-delta))
    mx=o.matrix_world.copy(); mx.translation=p; o.matrix_world=mx

def empty(name,group,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None); coll(group).objects.link(o)
    o.location=loc; o.empty_display_size=.025
    if parent:o.parent=parent
    bpy.context.view_layer.update()
    return o

def mesh(name,verts,faces,group,ma,parent=None,loc=(0,0,0),bevel=0):
    d=bpy.data.meshes.new(name+'_Geometry'); d.from_pydata(verts,[],faces); d.update()
    o=bpy.data.objects.new(name,d); coll(group).objects.link(o); o.location=loc
    register(o,name,group,ma,parent)
    if bevel: edge(o,bevel)
    return o

def edge(o,width=.0005,segments=3):
    mod=o.modifiers.new('Manufactured edge radii','BEVEL'); mod.width=width; mod.segments=segments
    enum_set(mod,'limit_method','ANGLE')
    mod=o.modifiers.new('Face weighted normals','WEIGHTED_NORMAL'); mod.keep_sharp=True; mod.weight=50
    return o

def box(name,size,loc,group,ma='Anodized_Aluminum_Black',bevel=.0006,parent=None):
    x,y,z=[v/2 for v in size]
    v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    f=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    return mesh(name,v,f,group,ma,parent,loc,bevel)

def cyl(name,radius,depth,loc,group,ma='Steel',axis='Z',vertices=64,bevel=.0003,parent=None):
    # Bake orientation into vertices: every manufactured part keeps unit transforms.
    vv=[]
    for z in [-depth/2,depth/2]:
        for i in range(vertices):
            a=i*math.tau/vertices; p=(radius*math.cos(a),radius*math.sin(a),z)
            vv.append((p[2],p[0],p[1]) if axis=='X' else (p[0],p[2],-p[1]) if axis=='Y' else p)
    ff=[tuple(reversed(range(vertices))),tuple(range(vertices,2*vertices))]
    ff +=[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    o=mesh(name,vv,ff,group,ma,parent,loc,bevel)
    for p in o.data.polygons[2:]:p.use_smooth=True
    return o

def outline(w,d,r,n=10):
    pts=[]
    for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for j in range(n+1):
            a=math.radians(start+90*j/n); pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts

def ring(name,outer,inner,height,loc,group,ma='Anodized_Aluminum_Black',r=.004,bevel=.0003,parent=None):
    # Closed rounded rectangular annulus, no stacked solid rectangles in optical apertures.
    a=outline(*outer,r); b=outline(*inner,min(r,min(inner)/4)); n=len(a)
    verts=[(x,y,z) for z,pts in [(-height/2,a),(height/2,a),(-height/2,b),(height/2,b)] for x,y in pts]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces += [(i,j,n+j,n+i),(n+i,n+j,3*n+j,3*n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j)]
    return mesh(name,verts,faces,group,ma,parent,loc,bevel)

def tube(name,ro,ri,depth,loc,group,ma='Steel',axis='Z',n=64,parent=None):
    verts=[]
    for z,r in [(-depth/2,ro),(depth/2,ro),(-depth/2,ri),(depth/2,ri)]:
        for i in range(n):
            a=math.tau*i/n;p=(r*math.cos(a),r*math.sin(a),z)
            verts.append((p[2],p[0],p[1]) if axis=='X' else (p[0],p[2],-p[1]) if axis=='Y' else p)
    faces=[]
    for i in range(n):
        j=(i+1)%n; faces +=[(i,j,n+j,n+i),(n+i,n+j,3*n+j,3*n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j)]
    o=mesh(name,verts,faces,group,ma,parent,loc,.00015)
    return o

def path(name,points,r,group='14_CABLES',ma='Plastic_Black',parent=None,smooth=True):
    d=bpy.data.curves.new(name+'_Geometry','CURVE'); d.dimensions='3D'; d.resolution_u=8
    d.bevel_depth=r; d.bevel_resolution=3; d.use_fill_caps=True
    sp=d.splines.new('BEZIER' if smooth else 'POLY')
    if smooth:
        sp.bezier_points.add(len(points)-1)
        for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    else:
        sp.points.add(len(points)-1)
        for p,co in zip(sp.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,d);coll(group).objects.link(o);register(o,name,group,ma,parent)
    set_origin(o,points[0]);return o

def screw(name,loc,group='15_FASTENERS',axis='Z',size=3,length=.008,parent=None):
    # Socket head with a real recessed hex drive, unified closed mesh and shared datablock.
    key=f'SHARED_M{size}x{length*1000:g}_{axis}'
    existing=bpy.data.meshes.get(key)
    if existing:
        o=bpy.data.objects.new(name,existing);coll(group).objects.link(o);o.location=loc
        register(o,name,group,parent=parent);o.data.name=key;edge(o,.00010,2);return o
    r=size*.001/2; head=r*1.65; h=size*.001*.85;n=48
    rings=[(-length,r*.84),(-.0002,r*.84),(0,head), (h,head),(h,r*.83),(h*.40,r*.83)]
    vv=[]
    for k,(z,rr) in enumerate(rings):
        for i in range(n):
            a=math.tau*i/n
            rad=rr if k<4 else rr*math.cos(math.pi/6)/math.cos((a%(math.pi/3))-math.pi/6)
            p=(rad*math.cos(a),rad*math.sin(a),z)
            vv.append((p[2],p[0],p[1]) if axis=='X' else (p[0],-p[2],p[1]) if axis=='Y' else p)
    ff=[tuple(reversed(range(n))),tuple(range(5*n,6*n))]
    for k in range(5):
        ff +=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
    o=mesh(name,vv,ff,group,'Stainless_Steel',parent,loc,.0001);o.data.name=key
    return o

def boolean(target,cutter):
    mod=target.modifiers.new('Machined opening','BOOLEAN');enum_set(mod,'operation','DIFFERENCE');mod.object=cutter
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

def label(name,text,loc,size,group,ma='Marking',rot=(math.pi/2,0,0),parent=None):
    d=bpy.data.curves.new(name+'_Geometry','FONT');d.body=text;d.size=size;d.extrude=.000035;d.space_character=1.12
    o=bpy.data.objects.new(name,d);coll(group).objects.link(o);o.location=loc;o.rotation_euler=rot
    register(o,name,group,ma,parent)
    return o

def remove_prefix(prefix):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def camera(name,pos,target,lens=65):
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.001;d.clip_end=100
    o=bpy.data.objects.new(name,d);coll('STUDIO').objects.link(o);o.location=pos;aim(o,target);return o

def studio():
    s=bpy.context.scene
    try:s.render.engine='CYCLES'
    except TypeError:pass
    s.cycles.samples=32;s.cycles.use_denoising=True
    s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
    try:
        p=bpy.context.preferences.addons['cycles'].preferences
        for backend in ['OPTIX','CUDA','HIP']:
            try:
                p.compute_device_type=backend;p.get_devices()
                gpu=[d for d in p.devices if d.type!='CPU']
                if gpu:
                    for d in p.devices:d.use=d.type!='CPU'
                    s.cycles.device='GPU';print('RENDER_GPU',[(d.name,d.type) for d in gpu]);break
            except Exception:pass
    except Exception:pass
    s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100
    enum_set(s.render.image_settings,'file_format','PNG')
    s.world=bpy.data.worlds.new('Studio_World');s.world.use_nodes=True
    bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.17,.21,.27,1);bg.inputs[1].default_value=.35
    for name,pos,power,size,color in [('Key',(.1,-.75,1.3),90,.8,(.83,.9,1)),('Fill',(-.8,-.15,.7),65,.7,(.7,.83,1)),('Rim',(.6,.7,.95),120,.65,(1,.74,.5))]:
        d=bpy.data.lights.new('LIGHT_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
        o=bpy.data.objects.new('LIGHT_'+name,d);coll('STUDIO').objects.link(o);o.location=pos;aim(o,(0,0,.3))
    box('STUDIO_Ground',(200,200,.02),(0,0,-.011),'STUDIO','Studio',0)
    camera('CAM_Hero_3Quarter',(.96,-1.38,.89),(0,0,.32))
    camera('CAM_Front',(0,-1.65,.39),(0,0,.32))
    camera('CAM_Side',(1.65,0,.43),(0,0,.32))
    camera('CAM_Back',(-.94,1.35,.82),(0,0,.3))
    camera('CAM_Top',(.001,0,1.75),(0,0,.2))
    camera('CAM_Internal',(.80,-1.02,.74),(0,0,.28))
    camera('CAM_LCD',(.47,-.61,.6),(0,-.025,.2))
    camera('CAM_LightEngine',(.44,-.6,.5),(0,-.025,.11))
    camera('CAM_ZAxis',(.5,-.75,.52),(0,.11,.34))
    camera('CAM_BuildPlate',(.38,-.52,.63),(0,-.005,.412))
    camera('CAM_Vat',(.37,-.49,.57),(0,-.026,.212))
    camera('CAM_Electronics',(.59,.65,.65),(.0,.04,.065))
    s.camera=bpy.data.objects['CAM_Hero_3Quarter']

def render(name,camera_name='CAM_Hero_3Quarter',size=1100,samples=32):
    s=bpy.context.scene;s.camera=bpy.data.objects[camera_name]
    # Device preferences do not persist inside .blend files between isolated processes.
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='OPTIX';prefs.get_devices()
        if any(d.type=='OPTIX' for d in prefs.devices):
            for d in prefs.devices:d.use=d.type=='OPTIX'
            s.cycles.device='GPU'
    except Exception:pass
    s.render.resolution_x=size;s.render.resolution_y=size;s.cycles.samples=samples
    output=ROOT/'renders'/name
    output.parent.mkdir(parents=True,exist_ok=True)
    s.render.filepath=str(output)
    bpy.ops.render.render(write_still=True)

def cyclorama():
    if bpy.data.objects.get('STUDIO_Cyclorama'):return
    remove_prefix('STUDIO_Ground')
    profile=[(0,-.001),(2,-.001)]
    for j in range(1,33):
        a=j*math.pi/64;profile.append((2+2*math.sin(a),-.001+2*(1-math.cos(a))))
    profile.append((4,10));n=128
    verts=[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for r,z in profile for i in range(n)]
    faces=[]
    for k in range(len(profile)-1):
        for i in range(n):j=(i+1)%n;faces.append(((k+1)*n+i,(k+1)*n+j,k*n+j,k*n+i))
    o=mesh('STUDIO_Cyclorama',verts,faces,'STUDIO','Studio')
    for p in o.data.polygons:p.use_smooth=True

def hide_groups(names,hide=True):
    for name in names:coll(name).hide_render=hide

def isolate(groups):
    state={g:coll(g).hide_render for g in GROUPS}
    for g in GROUPS:coll(g).hide_render=g not in groups
    return state

def restore_visibility(state):
    for g,v in state.items():coll(g).hide_render=v

def save(stage):
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'checkpoints'/f'm{stage:02d}.blend'))
    print('MILESTONE_SAVED',stage, 'OBJECTS',len(bpy.data.objects),flush=True)
