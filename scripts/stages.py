from common import *

def stage1():
    setup()
    box('BLOCK_Base',(.36,.35,.163),(0,0,.1035),'09_HOUSING','Powdercoat_Black',.004)
    box('BLOCK_Deck',(.355,.345,.006),(0,0,.188),'09_HOUSING','Anodized_Aluminum_Black',.002)
    for x in [-.145,.145]:
        for y in [-.135,.135]:cyl(f'PRT_Foot_{x}_{y}',.016,.018,(x,y,.010),'08_FRAME','Rubber')
    box('BLOCK_Tower',(.10,.050,.344),(0,.125,.362),'06_Z_AXIS','Anodized_Aluminum_Black',.002)
    box('BLOCK_Plate',(.220,.124,.010),(0,-.024,.38),'03_BUILD_PLATFORM','Anodized_Aluminum_Silver',.001)
    box('BLOCK_Arm',(.07,.16,.022),(0,.053,.422),'03_BUILD_PLATFORM','Anodized_Aluminum_Black')
    cyl('BLOCK_PlateJoint',.018,.037,(0,-.024,.402),'03_BUILD_PLATFORM')
    ring('BLOCK_Vat',(.278,.182),(.243,.147),.035,(0,-.025,.211),'04_RESIN_VAT',r=.012,bevel=.0015)
    # Molded hollow shell: connected outer/inner walls and top, open at the bottom.
    a=outline(.356,.346,.018,16);b=outline(.350,.340,.015,16);n=len(a)
    verts=[(x,y,z) for pts,z in [(a,.193),(a,.665),(b,.193),(b,.662)] for x,y in pts]
    faces=[]
    for i in range(n):
        j=(i+1)%n;faces +=[(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j)]
    faces +=[tuple(range(n,2*n)),tuple(reversed(range(3*n,4*n)))]
    cover=mesh('PRT_UV_Cover',verts,faces,'02_UV_COVER','UV_Cover_Amber',bevel=.0012)
    set_origin(cover,(0,0,.193));cover['wall_thickness_m']=.003
    ring('PRT_UV_Cover_Lower_Lip',(.353,.343),(.343,.333),.006,(0,0,.195),'02_UV_COVER',r=.016)
    ring('PRT_UV_Cover_Gasket',(.354,.344),(.348,.338),.002,(0,0,.1915),'02_UV_COVER','Rubber',r=.016,bevel=.0002)
    # Small functional grip on roof; no large opaque ornamental panels.
    for x in [-.035,.035]:box('PRT_Cover_HandleFoot_'+str(x),(.012,.022,.006),(x,0,.669),'02_UV_COVER','Plastic_Black',.001)
    box('PRT_UV_Cover_Handle',(.086,.022,.011),(0,0,.677),'02_UV_COVER','Plastic_Black',.003)
    bpy.context.scene['design_envelope_m']=[.360,.350,.6825]
    bpy.context.scene['design_note']='Fictional MSLA printer; engineering dimensions estimated. Front -Y, up +Z. Hood is removable.'
    save(1);render('milestones/01_blockout.png')

def rail_profile(name,x):
    # Extruded profile with ground running shoulders and a reduced web.
    pts=[(-.008,-.005),(.008,-.005),(.008,-.0025),(.006,-.001),(.006,.001),(.008,.0025),(.008,.005),(-.008,.005),(-.008,.0025),(-.006,.001),(-.006,-.001),(-.008,-.0025)]
    n=len(pts);vv=[(px,py,z) for z in [-.147,.147] for px,py in pts]
    ff=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,vv,ff,'06_Z_AXIS','Stainless_Steel',loc=(x,.094,.364),bevel=.00022)
    for z in [.232,.276,.320,.364,.408,.452,.496]:
        cut=cyl('TOOL_RailHole',.002,.025,(x,.094,z),'00_REFERENCE',axis='Y',bevel=0,vertices=20);boolean(o,cut)
        screw(f'SCR_Rail_{x}_{z}',(x,.0885,z),'06_Z_AXIS','Y',3,.009)
    return o

def helix(name,r,pitch,height,loc,group,ma='Steel',wire=.0006):
    turns=height/pitch;steps=int(turns*48)
    pts=[(loc[0]+r*math.cos(i/steps*turns*math.tau),loc[1]+r*math.sin(i/steps*turns*math.tau),loc[2]-height/2+i/steps*height) for i in range(steps+1)]
    o=path(name,pts,wire,group,ma,smooth=False);o.data.bevel_resolution=2
    return o

def stage2():
    for p in ['BLOCK_Tower','BLOCK_Plate','BLOCK_Arm','BLOCK_Vat']:remove_prefix(p)
    g='06_Z_AXIS'
    # Backbone, milled reliefs and a pair of precision guides.
    box('PRT_Vertical_Extrusion',(.108,.034,.340),(0,.124,.36),g,bevel=.001)
    for x in [-.046,.046]:
        box('PRT_Backbone_Tslot_'+str(x),(.004,.002,.318),(x,.1059,.362),g,'Rubber',.0002)
        rail_profile('PRT_LinearRail_'+('Left' if x<0 else 'Right'),x)
        block=box('PRT_LinearBlock_'+str(x),(.033,.024,.053),(x,.077,.423),g,'Anodized_Aluminum_Silver',.001)
        for z in [.400,.446]:box('PRT_RailBlock_EndSeal',(.034,.025,.004),(x,.076,z),g,'Plastic_Black',.0005)
        for xx in [x-.011,x+.011]:
            for zz in [.407,.439]:screw(f'SCR_LinearBlock_{xx}_{zz}',(xx,.064,zz),g,'Y')
    cyl('PRT_LeadScrew_Core',.0034,.310,(0,.085,.362),g,bevel=.0001)
    helix('PRT_LeadScrew_HelicalThread',.0041,.003,.306,(0,.085,.362),g,wire=.00065)
    tube('PRT_LeadScrew_Nut',.009,.0046,.018,(0,.085,.423),g,'Copper')
    ring('PRT_AntiBacklash_NutFlange',(.029,.027),(.010,.010),.004,(0,.085,.436),g,'Copper',r=.002)
    box('PRT_ZCarriage',(.126,.015,.069),(0,.057,.423),g,bevel=.0012)
    for z in [.208,.520]:
        box('PRT_BearingSupport_'+str(z),(.038,.043,.012),(0,.084,z),g,'Anodized_Aluminum_Silver',.0008)
        tube('PRT_Bearing_'+str(z),.011,.0048,.008,(0,.084,z+.007),g,'Steel')
        for x in [-.014,.014]:screw('SCR_Bearing_'+str((x,z)),(x,.084,z+.006),g)
    box('PRT_Top_BearingBridge',(.118,.050,.010),(0,.120,.530),g,'Anodized_Aluminum_Black',.001)
    # Stepper is below the deck behind the exposure area.
    box('PRT_StepperMotor_Body',(.042,.042,.038),(0,.084,.159),g,'Plastic_Black',.003)
    for z in [.138,.180]:box('PRT_StepperMotor_Endcap',(.042,.042,.005),(0,.084,z),g,'Anodized_Aluminum_Silver',.002)
    cyl('PRT_MotorShaft',.0025,.018,(0,.084,.189),g)
    tube('PRT_MotorCoupler',.009,.003,.019,(0,.084,.197),g,'Anodized_Aluminum_Silver')
    for z in [.191,.194,.197,.200]:
        # Shallow split lines imply flexible slits without destroying the shaft sleeve.
        tube('PRT_Coupler_Slit',.00905,.0087,.00045,(0,.084,z),g,'Rubber',n=48)
    box('PRT_MotorMount_Bracket',(.074,.058,.004),(0,.084,.1835),g,'Steel')
    box('PCB_LimitSensor',(.018,.012,.0016),(.054,.098,.235),g,'PCB_Green_or_Black')
    box('PRT_LimitSensor_OpticalFork',(.008,.010,.010),(.055,.090,.240),g,'Plastic_Black')
    box('PRT_LimitSensor_Flag',(.002,.012,.020),(.055,.057,.389),g,'Steel')
    # Carriage arm bridges the center of the plate, never a loose floating post.
    g='03_BUILD_PLATFORM'
    box('PRT_MountingArm',(.066,.125,.018),(0,-.009,.423),g,bevel=.0015)
    for x in [-.032,.032]:box('PRT_Arm_Rib',(.006,.120,.032),(x,-.008,.411),g,bevel=.0007)
    box('PRT_ZCarriage_Interface',(.108,.012,.052),(0,.043,.423),g,bevel=.001)
    for x in [-.043,.043]:
        for z in [.408,.438]:screw('SCR_ArmMount_'+str((x,z)),(x,.036,z),g,'Y',4,.012)
    plate=box('PRT_BuildPlate',(.220,.124,.008),(0,-.025,.377),g,'Anodized_Aluminum_Silver',.0007)
    set_origin(plate,(0,-.025,.4))
    plate['surface_finish']='Fine machined underside; modeled perimeter relief, procedural micro finish.'
    box('PRT_BuildPlate_Carrier',(.216,.120,.008),(0,-.025,.391),g,'Anodized_Aluminum_Black',.002)
    for x in [-.089,.089]:
        for y in [-.067,.017]:
            cyl('PRT_Leveling_GuidePin',.003,.010,(x,y,.384),g,'Stainless_Steel')
            tube('PRT_Leveling_SpringSeat',.0055,.0032,.002,(x,y,.384),g,'Steel')
            screw('SCR_Leveling_'+str((x,y)),(x,y,.395),g,'Z',4,.018)
    # Captured spherical leveling joint plus split clamp and a quick-release cam lever.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.012,location=(0,-.025,.404))
    ball=register(bpy.context.object,'PRT_Leveling_BallJoint',g,'Steel')
    box('PRT_BuildPlate_Mount',(.042,.042,.016),(0,-.025,.402),g,'Anodized_Aluminum_Black',.0015)
    for x in [-.018,.018]:box('PRT_Clamp_Jaw',(.012,.047,.021),(x,-.025,.414),g,'Anodized_Aluminum_Silver',.0007)
    cyl('PRT_Clamp_CamShaft',.004,.057,(0,-.025,.417),g,'Steel',axis='X')
    cyl('PRT_Clamp_Cam',.009,.010,(.031,-.025,.417),g,'Anodized_Aluminum_Black',axis='X')
    box('PRT_ClampLever',(.010,.052,.009),(.032,-.047,.424),g,'Anodized_Aluminum_Black',.003)
    box('PRT_ClampLever_Grip',(.014,.019,.012),(.032,-.066,.424),g,'Rubber',.003)
    for x in [-.10,.10]:
        for y in [-.073,.023]:screw('SCR_PlateCarrier_'+str((x,y)),(x,y,.3955),g)
    # Reservoir walls, retention rings and film are independent watertight solids.
    g='04_RESIN_VAT'
    vat=ring('PRT_Vat_Frame',(.280,.184),(.248,.152),.028,(0,-.025,.210),g,r=.013,bevel=.0011)
    ring('PRT_Inner_Reservoir',(.250,.154),(.246,.150),.023,(0,-.025,.209),g,'Anodized_Aluminum_Silver',r=.011,bevel=.0002)
    ring('PRT_Film_Frame',(.279,.183),(.242,.146),.004,(0,-.025,.193),g,'Anodized_Aluminum_Silver',r=.012,bevel=.00035)
    ring('PRT_Film_Clamp',(.275,.179),(.240,.144),.002,(0,-.025,.1895),g,r=.012,bevel=.00025)
    film=box('PRT_FEP_Film',(.247,.151,.00015),(0,-.025,.19515),g,'FEP',.00003)
    film['thickness_m']=.00015
    for x in [-.151,.151]:
        tab=box('PRT_Vat_MountingTab',(.026,.052,.010),(x,-.025,.218),g,bevel=.002)
        hole=cyl('TOOL_VatBoltHole',.0034,.02,(x,-.025,.218),'00_REFERENCE',bevel=0,vertices=32);boolean(tab,hole)
        cyl('PRT_Vat_LockShaft',.003,.026,(x,-.025,.213),g)
        cyl('PRT_Vat_LockKnob',.009,.012,(x,-.025,.230),g,'Plastic_Black',vertices=48,bevel=.001)
        for i in range(24):
            a=i*math.tau/24;cyl('PRT_Knob_Knurl',.0006,.010,(x+.0088*math.cos(a),-.025+.0088*math.sin(a),.230),g,'Plastic_Black',vertices=8,bevel=0)
    # Corner pour notch actually cuts through the rim, with a separate projecting spout floor.
    cut=box('TOOL_PourNotch',(.021,.020,.013),(.120,-.109,.223),'00_REFERENCE',bevel=0);boolean(vat,cut)
    box('PRT_Vat_PourSpout',(.021,.026,.003),(.120,-.113,.216),g,bevel=.0009)
    for x in [-.13,.13]:
        for y in [-.09,-.057,-.024,.009,.042]:screw('SCR_FilmRetention_'+str((x,y)),(x,y,.2242),g,'Z',3,.033)
    for y in [-.106,.056]:
        for x in [-.09,-.045,0,.045,.09]:screw('SCR_FilmRetention_'+str((x,y)),(x,y,.2242),g,'Z',3,.033)
    resin=box('PRT_Optional_Resin',(.244,.148,.018),(0,-.025,.2046),g,'Resin',.001)
    resin.hide_render=True;resin.hide_viewport=True;resin['optional']=True
    hide_groups(['02_UV_COVER'])
    save(2);render('milestones/02_core_mechanics.png','CAM_Internal')

def fan(name,loc,size=.070,axis='Z'):
    g='12_COOLING';x,y,z=loc
    root=empty('ASM_'+name,g,loc,parent=bpy.data.objects['ASM_Cooling'])
    # Model around origin and then bake orientation/translation for a clean rotational pivot.
    before=set(bpy.data.objects)
    frame=box('PRT_'+name+'_Housing',(size,size,.014),(0,0,0),g,'Plastic_Black',.003)
    cut=cyl('TOOL_Fan_Aperture',size*.435,.022,(0,0,0),'00_REFERENCE',vertices=96,bevel=0);boolean(frame,cut)
    for xx in [-size*.41,size*.41]:
        for yy in [-size*.41,size*.41]:
            cut=cyl('TOOL_Fan_MountHole',.002,.023,(xx,yy,0),'00_REFERENCE',vertices=24,bevel=0);boolean(frame,cut)
            screw('SCR_'+name,(xx,yy,.0075),g,length=.018)
    cyl('PRT_'+name+'_Hub',size*.17,.011,(0,0,0),g,'Plastic_Black',vertices=64,bevel=.001)
    cyl('PRT_'+name+'_MotorLabel',size*.12,.0004,(0,0,.006),g,'Marking',vertices=48,bevel=0)
    # Seven swept, pitched blades, each a solid surface with six radial segments.
    for k in range(7):
        vs=[]
        for side in [-.0005,.0005]:
            for t in range(7):
                r=size*(.16+.255*t/6);a=k*math.tau/7 + .50*t/6
                for width in [-.22,.22]:
                    aa=a+width;vs.append((r*math.cos(aa),r*math.sin(aa),side+width*.008+t*.00025))
        fs=[]
        for i in range(6):
            j=i*2;fs +=[(j,j+2,j+3,j+1),(14+j+1,14+j+3,14+j+2,14+j),(j,14+j,14+j+2,j+2),(j+1,j+3,14+j+3,14+j+1)]
        fs +=[(0,1,15,14),(12,26,27,13)]
        mesh('PRT_'+name+'_Blade_'+str(k),vs,[tuple(reversed(f)) for f in fs],g,'Plastic_Black',bevel=.0002)
    for a in [0,math.pi/2,math.pi,3*math.pi/2]:
        path('PRT_'+name+'_MotorStrut',[(0,0,-.005),(size*.20*math.cos(a),size*.20*math.sin(a),-.005),(size*.45*math.cos(a+.1),size*.45*math.sin(a+.1),-.005)],.0014,g,'Plastic_Black')
    objs=set(bpy.data.objects)-before
    rotation=Matrix.Rotation(math.pi/2,4,'Y') if axis=='X' else Matrix.Rotation(math.pi/2,4,'X') if axis=='Y' else Matrix.Identity(4)
    for o in objs:
        bpy.context.view_layer.update();mx=Matrix.Translation(Vector(loc))@rotation@o.matrix_world
        o.parent=root;o.matrix_world=mx
    root['pivot_role']='Fan rotation center';return root

def stage3():
    remove_prefix('BLOCK_Deck')
    ring('PRT_Top_Frame',(.355,.345),(.246,.151),.005,(0,0,.188),'09_HOUSING',r=.012,bevel=.0007)
    # Correct aperture centered on exposure datum; remake asymmetric deck with boolean.
    remove_prefix('PRT_Top_Frame')
    deck=box('PRT_Top_Frame',(.355,.345,.005),(0,0,.188),'09_HOUSING',bevel=.0012)
    boolean(deck,box('TOOL_DeckAperture',(.248,.153,.02),(0,-.025,.188),'00_REFERENCE',bevel=0))
    for x in [-.046,0,.046]:boolean(deck,box('TOOL_TowerPassage',(.026,.044,.02),(x,.092,.188),'00_REFERENCE',bevel=0))
    g='05_LCD_STACK'
    specs=[('PRT_Protective_Glass',(.230,.134,.0012),.19405,'Glass'),('PRT_Screen_Protector',(.230,.134,.00010),.19475,'FEP'),('PRT_Polarizer_Top',(.224,.128,.00020),.19325,'Polarizer'),('PRT_LCDPanel',(.224,.128,.0008),.1927,'LCD'),('PRT_Polarizer_Bottom',(.224,.128,.0002),.19215,'Polarizer')]
    for i,(n,sz,z,ma) in enumerate(specs):
        o=box(n,sz,(0,-.025,z),g,ma,.00004);o['explode_delta']=[0,0,.018*(len(specs)-i)];o['layer_index']=i
    for n,outer,inner,h,z,ma in [('PRT_LCD_Frame',(.242,.146),(.221,.125),.002,.192,'Anodized_Aluminum_Black'),('PRT_Optical_Gasket',(.246,.150),(.229,.133),.0006,.1938,'Rubber'),('PRT_Heat_Spreader',(.252,.156),(.224,.128),.0015,.1902,'Copper'),('PRT_LCD_Mounting_Frame',(.264,.168),(.236,.140),.004,.1874,'Anodized_Aluminum_Silver')]:
        o=ring(n,outer,inner,h,(0,-.025,z),g,ma,r=.003,bevel=.0001);o['explode_delta']=[0,0,-.014*(1+len([x for x in bpy.data.objects if x.name.startswith('PRT_LCD_')]))]
    for x in [-.126,.126]:
        for y in [-.099,.049]:
            tab=box('PRT_LCD_MountTab',(.017,.018,.003),(x,y,.186),g,'Anodized_Aluminum_Silver',.0005)
            boolean(tab,cyl('TOOL_LCDHole',.002,.015,(x,y,.186),'00_REFERENCE',bevel=0,vertices=24))
            screw('SCR_LCD_Mount',(x,y,.188),g)
    # Thin ribbon composed of substrate and parallel conductor traces.
    box('CBL_LCD_FPC',(.033,.060,.00035),(.090,.062,.1925),g,'Copper',.00008)
    for i in range(22):box('PRT_LCD_FPC_Trace',(.00045,.054,.00008),(.075+i*.0014,.062,.19273),g,'Marking',0)
    box('PRT_LCD_FPC_Connector',(.037,.007,.003),(.090,.090,.191),g,'Plastic_Black',.0004)
    g='07_LIGHT_ENGINE'
    box('PRT_ThermalInterface',(.228,.132,.0007),(0,-.025,.0898),g,'Ceramic',.0001)
    box('PRT_HeatSink_Base',(.246,.146,.006),(0,-.025,.086),g,'Anodized_Aluminum_Silver',.0005)
    for i in range(43):box('PRT_HeatSink_Fin_'+str(i),(.0013,.138,.027),(-.117+i*.00557,-.025,.0695),g,'Anodized_Aluminum_Silver',.00025)
    pcb=box('PCB_UV_LED_Array',(.226,.130,.0016),(0,-.025,.091),g,'PCB_Blue',.0004)
    pcb['emitter_layout']='12 columns × 7 rows; 84 individual emitter packages and collimators'
    for row in range(7):
        y=-.079+row*.018
        box('PRT_LED_CopperBus',(.217,.0012,.00007),(0,y,.09185),g,'Copper',0)
        for col in range(12):
            x=-.099+col*.018
            box('PRT_UV_LED_Package',(.006,.006,.0014),(x,y,.0927),g,'Ceramic',.0004)
            for dx in [-.004,.004]:box('PRT_LED_SolderPad',(.002,.003,.00015),(x+dx,y,.0919),g,'Stainless_Steel',.0002)
            cyl('PRT_UV_LED_Emitter',.0018,.0007,(x,y,.0937),g,'LED_Lens',vertices=32,bevel=.0003)
            # Reflective collimator with open light path and a curved clear lens.
            tube('PRT_LED_Reflector',.0076,.0069,.010,(x,y,.100),g,'Anodized_Aluminum_Silver',n=32)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=(x,y,.106))
            o=register(bpy.context.object,'PRT_Collimating_Lens',g,'Glass');o.data.transform(Matrix.Diagonal((.0068,.0068,.0032,1)))
            for p in o.data.polygons:p.use_smooth=True
    for x in [-.105,.105]:
        for y in [-.084,.034]:screw('SCR_LED_PCB',(x,y,.092),g)
    box('PRT_LED_ElectricalConnector',(.014,.008,.007),(.104,.033,.096),g,'Ceramic',.0005)
    housing=ring('PRT_Light_Housing',(.258,.164),(.244,.150),.063,(0,-.025,.139),g,'Anodized_Aluminum_Black',r=.006)
    housing['explode_delta']=[0,0,-.035]
    ring('PRT_Reflector',(.244,.150),(.239,.145),.054,(0,-.025,.138),g,'Anodized_Aluminum_Silver',r=.005,bevel=.0001)
    diffusion=box('PRT_Diffuser',(.238,.144,.0010),(0,-.025,.173),g,'Glass',.0001);diffusion['explode_delta']=[0,0,.035]
    lens=box('PRT_Collimating_Plate',(.238,.144,.002),(0,-.025,.177),g,'Glass',.0002);lens['explode_delta']=[0,0,.067]
    ring('PRT_Optical_Frame',(.256,.162),(.233,.139),.003,(0,-.025,.180),g,'Anodized_Aluminum_Black',r=.004,bevel=.0003)['explode_delta']=[0,0,.088]
    for x in [-.122,.122]:
        for y in [-.1,.05]:
            tube('PRT_Optics_Standoff',.0035,.0017,.066,(x,y,.138),g,'Steel')
            screw('SCR_Optical_Frame',(x,y,.182),g)
    fan('UV_IntakeFan',(-.065,-.025,.043))
    fan('UV_ExhaustFan',(.065,-.025,.043))
    for x in [-.065,.065]:
        ring('PRT_Fan_Duct',(.074,.074),(.066,.066),.006,(x,-.025,.053),'12_COOLING','Rubber',r=.005)
    save(3)
    state=isolate(['05_LCD_STACK','07_LIGHT_ENGINE','12_COOLING'])
    moved={}
    for o in bpy.data.objects:
        if 'explode_delta' in o:
            moved[o.name]=o.location.copy();o.location+=Vector(o['explode_delta'])
    render('milestones/03_exposure_review.png','CAM_LCD',1200,48)
    for n,p in moved.items():bpy.data.objects[n].location=p
    restore_visibility(state)

def board(name,center,size=(.115,.065),group='10_ELECTRONICS',controller=False):
    x,y,z=center;w,d=size
    root=empty('ASM_'+name,group,parent=bpy.data.objects['ASM_'+ASMS[group]])
    pcb=box('PCB_'+name,(w,d,.0016),center,group,'PCB_Green_or_Black',.0005,parent=root)
    for xx in [x-w/2+.006,x+w/2-.006]:
        for yy in [y-d/2+.006,y+d/2-.006]:
            boolean(pcb,cyl('TOOL_PCBHole',.0017,.01,(xx,yy,z),'00_REFERENCE',vertices=24,bevel=0))
            tube('PRT_'+name+'_Standoff',.003,.0015,.009,(xx,yy,z-.0055),group,'Copper',parent=root)
            screw('SCR_'+name,(xx,yy,z+.001),group,parent=root)
    box('PRT_'+name+'_MCU',(.016,.016,.0025),(x-.012,y,z+.0023),group,'Plastic_Black',.0005,parent=root)
    for side in [-1,1]:
        for i in range(12):
            box('PRT_'+name+'_ICLead',(.0018,.00035,.0004),(x-.012+side*.0088,y-.0066+i*.0012,z+.0013),group,'Stainless_Steel',.00008,parent=root)
            box('PRT_'+name+'_ICLead',(.00035,.0018,.0004),(x-.0186+i*.0012,y+side*.0088,z+.0013),group,'Stainless_Steel',.00008,parent=root)
    for i in range(10):
        xx=x-w*.37+i*w*.075
        box('PRT_'+name+'_SMD',(.0025,.0013,.0008),(xx,y-d*.32,z+.0012),group,'Ceramic',.00015,parent=root)
        box('PRT_'+name+'_Trace',(.0003,d*.22,.00005),(xx,y-d*.18,z+.00084),group,'Copper',0,parent=root)
        for s in [-1,1]:box('PRT_'+name+'_Solder',(.00055,.0014,.00035),(xx+s*.0011,y-d*.32,z+.0010),group,'Steel',.0001,parent=root)
    for i in range(min(4,max(1,int((w*.29-.003)/.009)+1))):
        xx=x+w*.21+i*.009
        cyl('PRT_'+name+'_Capacitor',.003,.009,(xx,y+d*.20,z+.0055),group,'Anodized_Aluminum_Silver',vertices=32,parent=root)
        cyl('PRT_'+name+'_CapSleeve',.00315,.006,(xx,y+d*.20,z+.004),group,'Plastic_Black',vertices=32,parent=root)
    box('PRT_'+name+'_Inductor',(.010,.009,.007),(x+w*.15,y-d*.18,z+.0045),group,'Plastic_Black',.001,parent=root)
    box('PRT_'+name+'_Driver',(.019,.015,.003),(x-w*.30,y+d*.18,z+.0025),group,'Plastic_Black',.0005,parent=root)
    for i in range(6):box('PRT_'+name+'_DriverFin',(.001,.014,.004),(x-w*.30-.007+i*.0028,y+d*.18,z+.006),group,'Anodized_Aluminum_Silver',.00015,parent=root)
    for i in range(min(4,max(1,int((w*.8-.005)/.014)+1))):
        xx=x-w*.30+i*.014
        box('PRT_'+name+'_Connector',(.010,.006,.006),(xx,y+d*.41,z+.004),group,'Ceramic',.0005,parent=root)
        for j in range(3):box('PRT_'+name+'_HeaderPin',(.00065,.00065,.004),(xx-.002+j*.002,y+d*.40,z+.006),group,'Copper',.00008,parent=root)
    # Test pads and silk markings remain real geometry/materials on export.
    for i in range(8):cyl('PRT_'+name+'_TestPad',.00065,.00004,(x-w*.35+i*.009,y-d*.40,z+.00085),group,'Copper',vertices=16,bevel=0,parent=root)
    label('PRT_'+name+'_Silkscreen',name.upper().replace('_',' ')+'  R2',(x-w*.38,y-d*.13,z+.00086),.0024,group,rot=(0,0,0),parent=root)
    return root

def stage4():
    remove_prefix('BLOCK_Base')
    g='08_FRAME'
    ring('PRT_Base_Frame',(.338,.326),(.301,.289),.017,(0,0,.032),g,'Anodized_Aluminum_Silver',r=.007,bevel=.0008)
    for x in [-.156,.156]:
        for y in [-.146,.146]:
            box('PRT_Frame_Upright',(.017,.017,.141),(x,y,.112),g,'Anodized_Aluminum_Silver',.0007)
            for z in [.047,.173]:
                box('PRT_Frame_CornerBracket',(.032,.025,.003),(x-math.copysign(.007,x),y,z),g,'Steel')
                screw('SCR_FrameCorner',(x,y,z+.002),g,'Z',4,.014)
    for y in [-.118,.088]:box('PRT_Internal_Crossmember',(.314,.012,.015),(0,y,.045),g,'Anodized_Aluminum_Silver')
    for x in [-.146,.146]:box('PRT_LCD_SupportRail',(.014,.292,.013),(x,0,.176),g,'Anodized_Aluminum_Silver')
    box('PRT_ZAxis_Mount',(.134,.057,.008),(0,.126,.182),g,'Anodized_Aluminum_Silver')
    for x in [-.060,.060]:
        # Triangular gussets connect tower to rear deck, closed plate prisms.
        vv=[(xx,y,z) for xx in [x-.002,x+.002] for y,z in [(.106,.188),(.15,.188),(.106,.262)]]
        mesh('PRT_Backbone_Gusset',vv,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],g,'Anodized_Aluminum_Silver',bevel=.0005)
        for y in [.114,.144]:screw('SCR_BackboneMount',(x,y,.193),g,'Z',4,.014)
    for x in [-.128,.128]:
        for y in [-.11,.06]:
            box('PRT_LightEngine_MountBracket',(.024,.016,.031),(x,y,.065),g,'Steel')
            screw('SCR_LightEngine_Mount',(x,y,.082),g,'Z',4,.012)
    # Small rear shelf carries PSU and logic boards, with honest space around the optics.
    box('PRT_Electronics_Shelf',(.297,.076,.002),(0,.117,.038),g,'Steel')
    board('Mainboard',(.078,.115,.108),(.126,.067))
    lcd_board=board('LCD_Controller',(.139,-.042,.137),(.090,.030))
    bpy.context.view_layer.update()
    turn=Matrix.Translation(Vector((.139,-.042,.137)))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(Vector((-.139,.042,-.137)))
    for ob in lcd_board.children:ob.matrix_world=turn@ob.matrix_world
    board('USB_Data_Board',(-.102,-.144,.132),(.056,.030))
    box('PRT_USB_Receptacle',(.015,.015,.007),(-.102,-.163,.137),'10_ELECTRONICS','Stainless_Steel',.0006)
    box('PRT_USB_Tongue',(.010,.002,.003),(-.102,-.171,.136),'10_ELECTRONICS','Plastic_Black',.0002)
    box('PCB_Power_Distribution',(.040,.025,.0016),(.128,.118,.065),'10_ELECTRONICS','PCB_Green_or_Black',.0004)
    for i in range(4):
        box('PRT_ScrewTerminal',(.007,.011,.008),(.114+i*.008,.118,.070),'10_ELECTRONICS','PCB_Green_or_Black',.0005)
        screw('SCR_Terminal',(.114+i*.008,.118,.074),'10_ELECTRONICS','Z',3,.004)
    g='11_POWER'
    box('PRT_PSU_Base',(.130,.067,.002),(-.079,.116,.046),g,'Anodized_Aluminum_Silver')
    for x in [-.143,-.015]:box('PRT_PSU_Side',(.002,.067,.047),(x,.116,.070),g,'Anodized_Aluminum_Silver')
    for y in [.0835,.1485]:box('PRT_PSU_End',(.128,.002,.047),(-.079,y,.070),g,'Anodized_Aluminum_Silver')
    # Ventilated removable PSU top with modeled open slots.
    for i in range(20):box('PRT_PSU_VentSlat',(.0035,.065,.0015),(-.139+i*.0063,.116,.094),g,'Anodized_Aluminum_Silver',.0003)
    for y in [.085,.147]:box('PRT_PSU_TopFlange',(.128,.004,.002),(-.079,y,.094),g,'Anodized_Aluminum_Silver')
    box('PCB_PSU',(.122,.059,.0016),(-.079,.116,.049),g,'PCB_Green_or_Black')
    box('PRT_PSU_Transformer',(.031,.028,.027),(-.083,.116,.065),g,'Wire_Yellow',.0015)
    box('PRT_PSU_TransformerCore',(.019,.031,.030),(-.083,.116,.065),g,'Plastic_Black',.001)
    for x in [-.128,-.113]:cyl('PRT_PSU_Capacitor',.006,.024,(x,.118,.063),g,'Plastic_Black',vertices=48)
    for i in range(7):box('PRT_PSU_Terminal',(.011,.008,.009),(-.125+i*.014,.153,.054),g,'Plastic_Black',.0004)
    for x in [-.138,-.020]:
        for y in [.087,.144]:screw('SCR_PSU_Cover',(x,y,.095),g)
    box('PRT_IEC_Input',(.031,.021,.024),(-.110,.166,.074),g,'Plastic_Black',.001)
    for x in [-.118,-.102]:box('PRT_IEC_Pin',(.002,.009,.004),(x,.178,.074),g,'Copper',.0002)
    box('PRT_IEC_EarthPin',(.002,.009,.004),(-.110,.178,.081),g,'Copper',.0002)
    box('PRT_Main_Switch',(.018,.012,.024),(-.064,.173,.075),g,'Plastic_Black',.0018)
    box('PRT_Switch_Rocker',(.014,.004,.018),(-.064,.181,.075),g,'Wire_Red',.0015)
    cyl('PRT_FuseHolder',.006,.015,(-.034,.172,.074),g,'Plastic_Black',axis='Y')
    tube('PRT_Chassis_GroundLug',.005,.002,.001,(-.137,.131,.04),g,'Copper')
    screw('SCR_Chassis_Earth',(-.137,.131,.041),g,'Z',4,.009)
    fan('Electronics_Exhaust',(.160,.100,.130),.060,axis='X')
    # Major harnesses follow chassis perimeter channels, clear of the optical aperture.
    routes=[
        ('PSU_to_Distribution',[(-.022,.155,.058),(.006,.157,.052),(.10,.157,.056),(.125,.13,.071)],.0023,'Wire_Red'),
        ('Distribution_to_Mainboard',[(.131,.118,.074),(.143,.138,.085),(.118,.143,.113)],.002,'Plastic_Black'),
        ('Mainboard_to_Stepper',[(.045,.143,.113),(.018,.144,.117),(.018,.115,.139),(.016,.086,.149)],.002,'Plastic_Black'),
        ('Mainboard_to_UV',[(.060,.142,.112),(.151,.151,.10),(.154,.063,.10),(.130,.043,.096),(.104,.033,.098)],.002,'Wire_Red'),
        ('LCD_to_Controller',[(.090,.09,.190),(.118,.077,.178),(.142,.04,.167),(.140,-.001,.141)],.0016,'Plastic_Black'),
        ('Mainboard_to_LCD',[(.088,.143,.113),(.151,.142,.108),(.160,.044,.113),(.145,-.010,.143)],.0018,'Plastic_Black'),
        ('LimitSensor',[(.054,.098,.240),(.067,.114,.240),(.067,.144,.207),(.066,.153,.152),(.030,.143,.113)],.0012,'Wire_Blue'),
        ('USB_Data',[(-.102,-.144,.134),(-.153,-.133,.142),(-.156,.069,.135),(-.012,.156,.123),(.045,.143,.113)],.0018,'Plastic_Black'),
        ('Fan_Intake',[(-.094,-.05,.042),(-.138,-.06,.042),(-.142,.070,.047),(.115,.156,.066),(.127,.122,.074)],.0012,'Wire_Red'),
        ('Fan_Exhaust',[(.09,-.05,.042),(.144,-.053,.042),(.148,.05,.043),(.132,.112,.072)],.0012,'Plastic_Black'),
        ('Electronics_Fan',[(.15,.1,.13),(.141,.14,.133),(.102,.143,.113)],.0011,'Wire_Red'),
        ('Protective_Earth',[(-.110,.161,.081),(-.126,.156,.067),(-.143,.15,.05),(-.137,.131,.041)],.0015,'Wire_Yellow'),
        ('Mains_Live',[(-.104,.161,.074),(-.064,.158,.075),(-.050,.155,.058)],.0013,'Wire_Red'),
        ('Mains_Neutral',[(-.118,.161,.074),(-.115,.154,.065),(-.107,.153,.058)],.0013,'Wire_Blue')]
    for n,pts,r,ma in routes:
        cable=path('CBL_'+n,pts,r,ma=ma);cable['endpoints_m']=[v for p in [pts[0],pts[-1]] for v in p]
        for p in [pts[0],pts[-1]]:box('PRT_'+n+'_Plug',(.006,.007,.006),p,'14_CABLES','Plastic_Black',.0007)
    hide_groups(['02_UV_COVER','09_HOUSING','13_UI'])
    save(4);render('milestones/04_internal_hardware.png','CAM_Internal',1200,48)

def stage5():
    g='09_HOUSING'
    front_root=empty('ASM_FrontPanel',g,parent=bpy.data.objects['ASM_Housing'])
    # Folded front sheet: flat fascia and a 25 mm deep lower kick, with real thickness.
    profile=[(-.161,.023),(-.175,.048),(-.175,.184),(-.1726,.184),(-.1726,.0488),(-.1586,.0242)]
    n=len(profile);vv=[(x,y,z) for x in [-.177,.177] for y,z in profile]
    ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    front=mesh('PRT_Front_Panel',vv,ff,g,'Powdercoat_Black',parent=front_root,bevel=.00065)
    boolean(front,box('TOOL_DisplayOpening',(.070,.04,.108),(.111,-.172,.119),'00_REFERENCE',bevel=0))
    boolean(front,box('TOOL_USBOpening',(.017,.04,.010),(-.102,-.172,.137),'00_REFERENCE',bevel=0))
    for i in range(30):
        boolean(front,box('TOOL_FrontVent',(.0025,.035,.022),(-.141+i*.0067,-.170,.063),'00_REFERENCE',bevel=0))
    box('PRT_Front_ReturnFlange',(.350,.011,.002),(0,-.167,.183),g,'Powdercoat_Black',.0005,parent=front_root)
    box('PRT_Front_Accent',(.349,.001,.002),(0,-.1754,.179),g,'Accent',.0003,parent=front_root)
    for x in [-.167,.167]:
        for z in [.052,.175]:screw('SCR_FrontPanel',(x,-.176,z),g,'Y',3,.008,parent=front_root)
    label('PRT_Front_ModelMark','MSLA / 10',(-.148,-.176,.155),.010,g,parent=front_root)
    label('PRT_Front_Subtitle','PRECISION RESIN SYSTEM',(-.148,-.176,.146),.0029,g,parent=front_root)
    label('PRT_USB_Label','USB',(-.109,-.176,.126),.0035,g,parent=front_root)
    label('PRT_Front_Serial','SERIES 01  /  405 nm',(-.148,-.176,.096),.004,g,parent=front_root)
    for side in [-1,1]:
        root=empty('ASM_'+('LeftPanel' if side<0 else 'RightPanel'),g,parent=bpy.data.objects['ASM_Housing'])
        panel=box('PRT_'+('Left_Panel' if side<0 else 'Right_Panel'),(.0022,.341,.159),(side*.179,0,.1045),g,'Powdercoat_Black',.00065,parent=root)
        for i in range(26):
            boolean(panel,box('TOOL_SideVent',(.014,.0030,.041),(side*.179,-.119+i*.0055,.077),'00_REFERENCE',bevel=0))
        if side>0:
            for i in range(12):boolean(panel,box('TOOL_ExhaustVent',(.014,.003,.049),(side*.179,.070+i*.0054,.132),'00_REFERENCE',bevel=0))
        for z in [.026,.183]:box('PRT_Side_ReturnFlange',(.011,.339,.002),(side*.173,0,z),g,'Powdercoat_Black',.0004,parent=root)
        for y in [-.158,.158]:
            for z in [.037,.171]:
                s=screw('SCR_SidePanel',(side*.1805,y,z),g,'X',3,.008,parent=root)
                if side<0:s.data=s.data.copy();s.data.transform(Matrix.Rotation(math.pi,4,'Z'))
        # Recess behind slots is open; narrow guard ribs protect the inlet.
        for z in [.059,.095]:box('PRT_IntakeGuard_Rib',(.003,.154,.002),(side*.175,-.050,z),g,'Plastic_Black',.0003,parent=root)
    root=empty('ASM_RearPanel',g,parent=bpy.data.objects['ASM_Housing'])
    rear=box('PRT_Rear_Panel',(.356,.0022,.159),(0,.173,.1045),g,'Powdercoat_Black',.0007,parent=root)
    for x,sz,z in [(-.110,(.032,.020,.026),.074),(-.064,(.019,.020,.026),.075),(-.034,(.014,.020,.014),.074)]:boolean(rear,box('TOOL_RearOpening',sz,(x,.173,z),'00_REFERENCE',bevel=0))
    for i in range(22):boolean(rear,box('TOOL_RearVent',(.003,.014,.034),(.01+i*.006,.173,.118),'00_REFERENCE',bevel=0))
    for x in [-.163,.163]:
        for z in [.036,.172]:
            s=screw('SCR_RearPanel',(x,.175,z),g,'Y',parent=root);s.data=s.data.copy();s.data.transform(Matrix.Rotation(math.pi,4,'Z'))
    # Rear text faces outward (+Y).
    label('PRT_Input_Rating','100-240 V~  50/60 Hz',(-.134,.1743,.047),.004,g,rot=(math.pi/2,0,math.pi),parent=root)
    label('PRT_Rear_Serial','MSLA-10   /   SERIAL 0001',(.128,.1743,.158),.004,g,rot=(math.pi/2,0,math.pi),parent=root)
    label('PRT_Power_Label','I / O',(-.055,.184,.059),.003,g,rot=(math.pi/2,0,math.pi),parent=root)
    base=box('PRT_Base_Cover',(.350,.339,.002),(0,0,.023),g,'Powdercoat_Black',.0005)
    for xx in [-.065,.065]:
        for i in range(9):boolean(base,box('TOOL_BaseInlet',(.003,.057,.01),(xx-.025+i*.006,-.025,.023),'00_REFERENCE',bevel=0))
    # Upper deck fasteners and vat locating pins.
    for x in [-.165,.165]:
        for y in [-.154,.14]:screw('SCR_Deck',(x,y,.191),'09_HOUSING')
    for x in [-.151,.151]:tube('PRT_Vat_ThreadedInsert',.005,.0032,.014,(x,-.025,.189),'08_FRAME','Copper')
    # Screen hardware, separated front glass, LCD, bezel, electronics and mounting ears.
    g='13_UI'
    bezel=box('PRT_UI_Bezel',(.074,.012,.114),(.111,-.174,.119),g,'Plastic_Black',.0025)
    boolean(bezel,box('TOOL_UIWindow',(.058,.024,.093),(.111,-.174,.120),'00_REFERENCE',bevel=0))
    box('PRT_UI_FrontGlass',(.059,.0012,.094),(.111,-.1808,.120),g,'Glass',.0006)
    box('PRT_UI_LCD',(.060,.002,.095),(.111,-.179,.120),g,'LCD',.0005)
    box('PCB_UI_Controller',(.063,.0016,.098),(.111,-.164,.120),g,'PCB_Green_or_Black',.0004)
    for x in [.075,.147]:
        box('PRT_UI_MountBracket',(.010,.018,.091),(x,-.158,.120),g,'Steel')
        for z in [.081,.159]:screw('SCR_UI_Mount',(x,-.179,z),g,'Y')
    box('PRT_UI_Processor',(.020,.004,.020),(.111,-.160,.124),g,'Plastic_Black')
    path('CBL_Touchscreen',[(.12,-.158,.15),(.154,-.137,.154),(.163,-.02,.157),(.16,.075,.148),(.105,.143,.115)],.0022)
    # Support trays fix the early review's visibly unsupported boards.
    g='08_FRAME'
    for name,c,sz in [('Mainboard',(.078,.115,.097),(.132,.073,.002)),('LCD',(.139,-.042,.126),(.035,.108,.002)),('USB',(-.102,-.144,.121),(.061,.033,.002)),('Distribution',(.128,.118,.053),(.047,.032,.002))]:
        box('PRT_'+name+'_MountingTray',sz,c,g,'Anodized_Aluminum_Silver')
    for x in [.021,.135]:
        for y in [.087,.143]:tube('PRT_Mainboard_TrayPillar',.0035,.0018,.057,(x,y,.0675),g,'Anodized_Aluminum_Silver')
    for y in [-.086,0]:box('PRT_LCD_TrayBracket',(.018,.012,.047),(.152,y,.150),g,'Steel')
    for x in [-.126,-.078]:box('PRT_USB_TrayBracket',(.009,.007,.060),(x,-.151,.151),g,'Steel')
    for x in [-.130,-.026]:
        for y in [.09,.14]:cyl('PRT_PSU_IsolatingMount',.004,.006,(x,y,.0425),g,'Rubber')
    for x in [.11,.144]:cyl('PRT_Distribution_Pillar',.003,.014,(x,.118,.046),g,'Anodized_Aluminum_Silver')
    for x,y,z in [(.16,-.09,.153),(.16,.035,.15),(-.156,-.060,.142),(-.155,.060,.14),(.09,.156,.124),(.02,.155,.12)]:
        clip=ring('PRT_CableClip',(.012,.008),(.007,.004),.004,(x,y,z),'14_CABLES','Plastic_Black',r=.001,bevel=.0003)
        box('PRT_CableTie',(.0018,.012,.001),(x,y,z+.003),'14_CABLES','Rubber',.0002)
    # Generic warnings and reservoir marks; no copied brand graphics.
    label('PRT_UV_Warning','UV 405 nm / KEEP COVER CLOSED',(-.080,-.1736,.211),.0034,'02_UV_COVER')
    label('PRT_ZAxis_Warning','Z AXIS / KEEP CLEAR',(-.041,.105,.504),.0033,'06_Z_AXIS')
    for i in range(3):
        box('PRT_Vat_LevelTick',(.009,.0002,.00045),(-.096,-.1172,.203+i*.007),'04_RESIN_VAT','Marking',0)
    label('PRT_Vat_LevelMark','MAX',(-.116,-.1174,.216),.0024,'04_RESIN_VAT')
    # Reusable extra fasteners: washers, hex nuts, countersunk screws and standoffs.
    for x in [-.060,.060]:
        for y in [.114,.144]:
            tube('PRT_M4_Washer',.0045,.0021,.0008,(x,y,.192),'15_FASTENERS','Stainless_Steel')
            tube('PRT_M4_HexNut',.004,.002,.0032,(x,y,.176),'15_FASTENERS','Steel',n=6)
    for x in [-.151,.151]:
        for y in [-.136,.136]:
            o=cyl('SCR_Countersunk_M4',.004,.0018,(x,y,.022),'15_FASTENERS','Steel',vertices=48)
            boolean(o,box('TOOL_DriveSlot',(.004,.0008,.002),(x,y,.021),'00_REFERENCE',bevel=0))
    # Optional calibration sculpture: an open, twisted lattice with actual support contacts.
    for state,fraction in [('Print_10Percent',.1),('Print_50Percent',.5),('Print_Complete',1.0)]:
        group=coll(state,coll('16_PRINT_SAMPLE'))
        root=empty('ASM_'+state,state,parent=bpy.data.objects['ASM_PrintSample'])
        root['optional_print_state']=fraction
        box('PRT_'+state+'_Raft',(.048,.048,.0014),(-.031,-.025,.3718),state,'Print_Resin',.002,parent=root)
        for x in [-.048,-.014]:
            for y in [-.042,-.008]:path('PRT_'+state+'_Support',[(x,y,.371),(x,y,.363),(x*.95,y,.3575)],.00075,state,'Print_Resin',parent=root)
        levels=6; total=.062*fraction
        for i in range(math.ceil(levels*fraction)):
            h0=i*.062/levels;h1=min((i+1)*.062/levels,total)
            for j in range(4):
                a=j*math.pi/2+i*.14;b=(j+1)*math.pi/2+(i+1)*.14
                p0=(-.031+.018*math.cos(a),-.025+.018*math.sin(a),.357-h0)
                p1=(-.031+.018*math.cos(a+.14),-.025+.018*math.sin(a+.14),.357-h1)
                p2=(-.031+.018*math.cos(b),-.025+.018*math.sin(b),.357-h1)
                path('PRT_'+state+'_Column',[p0,p1],.001,state,'Print_Resin',parent=root,smooth=False)
                path('PRT_'+state+'_Diagonal',[p0,p2],.00075,state,'Print_Resin',parent=root,smooth=False)
        group.hide_render=fraction<1;group.hide_viewport=fraction<1
    hide_groups(['09_HOUSING','13_UI'],False)
    save(5);render('milestones/05_product_details.png','CAM_Internal',1300,48)

def stage6():
    # Clear amber, polished molded polymer: light tint and full transmission.
    mat('UV_Cover_Amber',(.95,.73,.40),0,.035,1.0,1.49)
    mat('Glass',(.97,.985,1),0,.035,1,1.45)
    mat('FEP',(.98,.99,1),0,.035,1,1.34)
    mat('LCD',(.010,.016,.023),.25,.15)
    # The diffuser retains enough haze to read in the optical close-up.
    diffuser=mat('Diffuser',(.85,.89,.94),0,.32,.82)
    o=bpy.data.objects['PRT_Diffuser'];o.data.materials.clear();o.data.materials.append(diffuser)
    # Geometric underside machining, only 40 micron relief, exported as geometry.
    for i in range(48):
        y=-.082+i*.0024
        path('PRT_BuildPlate_Machining', [(-.102,y,.37295),(.102,y,.37295)],.000025,'03_BUILD_PLATFORM','Steel',smooth=False)
    # Align support contacts to actual top lattice nodes.
    for state in ['Print_10Percent','Print_50Percent','Print_Complete']:
        remove_prefix('PRT_'+state+'_Support')
        for j in range(4):
            a=j*math.pi/2;x=-.031+.018*math.cos(a);y=-.025+.018*math.sin(a)
            path('PRT_'+state+'_Support',[(x,y,.3711),(x,y,.361),(x,y,.357)],.00075,state,'Print_Resin',parent='ASM_'+state)
    # UVs on exterior parts, large plastics, boards, glass, and the plate.
    selected=[]
    for o in bpy.data.objects:
        if o.type=='MESH' and (o.name.startswith('PCB_') or o.name in ['PRT_UV_Cover','PRT_Front_Panel','PRT_Left_Panel','PRT_Right_Panel','PRT_Rear_Panel','PRT_Base_Cover','PRT_Top_Frame','PRT_BuildPlate','PRT_UI_FrontGlass','PRT_UI_LCD','PRT_Vat_Frame']):selected.append(o)
    for o in selected:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    # Store assembly pivot datums while keeping every child in assembled world position.
    pivots={'Cover':(0,0,.193),'BuildPlate':(0,-.025,.404),'Vat':(0,-.025,.207),'LCDStack':(0,-.025,.192),'ZAxis':(0,.124,.36),'LightEngine':(0,-.025,.13),'Electronics':(.06,.115,.09),'Power':(-.079,.116,.07),'Cooling':(0,-.025,.043),'UI':(.111,-.174,.119)}
    for a,p in pivots.items():
        o=bpy.data.objects['ASM_'+a];bpy.context.view_layer.update();children={c:c.matrix_world.copy() for c in o.children};o.location=p
        bpy.context.view_layer.update()
        for c,mx in children.items():c.matrix_world=mx
        o['pivot_role']='Functional assembly datum';o['assembled_location']=list(o.location)
    hide_groups(['02_UV_COVER','09_HOUSING','13_UI'],False)
    save(6);render('milestones/06_materials_hero.png','CAM_Hero_3Quarter',1400,96)
    render('milestones/06_materials_back.png','CAM_Back',1200,64)

def stage7():
    from validation import geometry_audit,manifest,make_cutaway,setup_explosion,production_objects
    # Extend vat locking screws into the inserts, closing a 4 mm engagement gap.
    for o in list(bpy.data.objects):
        if o.name.startswith('PRT_Vat_LockShaft'):
            p=o.matrix_world.translation.copy();n=o.name;bpy.data.objects.remove(o,do_unlink=True)
            cyl(n,.003,.038,(p.x,p.y,.209),'04_RESIN_VAT')
    for name,p in [('PRT_LeadScrew_HelicalThread',(0,.085,.362)),('PRT_Front_Panel',(0,-.17,.104)),('PRT_Vat_Frame',(0,-.025,.21)),('PRT_BuildPlate',(0,-.025,.404))]:set_origin(bpy.data.objects[name],p)
    # Fasteners have linked source geometry. Consolidate identical package meshes as well.
    shared={}
    for o in bpy.data.objects:
        if o.type=='MESH' and o.name.startswith(('PRT_UV_LED_Package','PRT_UV_LED_Emitter','PRT_Collimating_Lens','PRT_HeatSink_Fin')):
            key=o.name.split('.')[0]
            if key in shared:o.data=shared[key]
            else:shared[key]=o.data
    bpy.context.scene['readme']='Frame 1: assembled. Frame 100: exploded validation, not final animation. Cutaway in 17_CUTAWAY is independent. EXPORT excludes studio and optional variants.'
    audit=geometry_audit()
    make_cutaway();setup_explosion()
    export=coll('EXPORT')
    for o in production_objects():
        if o.name not in export.objects:export.objects.link(o)
    export.hide_render=True;export.hide_viewport=True
    manifest()
    text=bpy.data.texts.new('README_Asset')
    text.write((ROOT/'README.md').read_text(encoding='utf-8')+ '\n\nFrame 1: assembled. Frame 100: exploded validation. Toggle 17_CUTAWAY separately from production collections. EXPORT links only approved production objects.\n')
    # Start in a useful material-preview modeling view.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=1.15
                area.spaces.active.region_3d.view_location=(0,0,.32)
                area.spaces.active.clip_start=.001
    save(7)
    bpy.context.scene.frame_set(100);render('milestones/07_exploded_validation.png','CAM_Exploded',1500,64)
    bpy.context.scene.frame_set(1)
    state=isolate(['17_CUTAWAY']);coll('17_CUTAWAY').hide_viewport=False
    render('milestones/07_cutaway.png','CAM_Cutaway',1200,48)
    restore_visibility(state);coll('17_CUTAWAY').hide_viewport=True

STAGES={1:stage1,2:stage2,3:stage3,4:stage4,5:stage5,6:stage6,7:stage7}
