import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'resin_printer_master.blend'))
cyclorama()
s=bpy.context.scene;s.frame_set(1)
def review(name,cam):
    if (ROOT/'renders'/name).exists():
        print('REVIEW_ALREADY_RENDERED',name,flush=True);return
    render(name,cam,2000,96);print('REVIEW_DONE',name,flush=True)
review('01_complete_hero.png','CAM_Hero_3Quarter')
review('02_front.png','CAM_Front')
review('03_back.png','CAM_Back')
hide_groups(['02_UV_COVER','09_HOUSING','13_UI'])
review('04_internal_no_panels.png','CAM_Internal')
hide_groups(['02_UV_COVER','09_HOUSING','13_UI'],False)
s.frame_set(100)
review('05_exploded_full.png','CAM_Exploded')
s.frame_set(1)
state=isolate(['03_BUILD_PLATFORM']);review('06_build_plate_closeup.png','CAM_BuildPlate');restore_visibility(state)
state=isolate(['04_RESIN_VAT']);review('07_vat_closeup.png','CAM_Vat');restore_visibility(state)
state=isolate(['05_LCD_STACK'])
names=['PRT_LCD_Mounting_Frame','PRT_Heat_Spreader','PRT_LCD_Frame','PRT_Polarizer_Bottom','PRT_LCDPanel','PRT_Polarizer_Top','PRT_Optical_Gasket','PRT_Protective_Glass','PRT_Screen_Protector']
saved={}
for i,n in enumerate(names):
    o=bpy.data.objects[n];saved[n]=o.location.copy();o.animation_data_clear();o.location.z+=i*.018
cam=bpy.data.objects['CAM_LCD'];cam.location=(.38,-.51,.54);aim(cam,(0,-.025,.265))
review('08_lcd_stack_exploded.png','CAM_LCD')
for n,p in saved.items():bpy.data.objects[n].location=p
restore_visibility(state)
state=isolate(['07_LIGHT_ENGINE']);saved={}
for o in coll('07_LIGHT_ENGINE').objects:
    d=None
    if o.name.startswith(('PRT_HeatSink_','PRT_ThermalInterface')):d=(0,0,-.045)
    elif o.name in ['PRT_Light_Housing','PRT_Reflector']:d=(.31,.05,.01)
    elif o.name=='PRT_Diffuser':d=(0,0,.04)
    elif o.name=='PRT_Collimating_Plate':d=(0,0,.080)
    elif o.name=='PRT_Optical_Frame':d=(0,0,.12)
    if d:saved[o.name]=o.location.copy();o.location+=Vector(d)
cam=bpy.data.objects['CAM_LightEngine'];cam.location=(.76,-1.09,.83);cam.data.lens=58;aim(cam,(.135,-.01,.17))
review('09_light_engine_exploded.png','CAM_LightEngine')
for n,p in saved.items():bpy.data.objects[n].location=p
restore_visibility(state)
state=isolate(['06_Z_AXIS']);review('10_z_axis_closeup.png','CAM_ZAxis');restore_visibility(state)
state=isolate(['10_ELECTRONICS','11_POWER'])
cam=bpy.data.objects['CAM_Electronics'];cam.location=(.48,.68,.59);cam.data.lens=58;aim(cam,(0,.015,.094))
review('11_electronics_closeup.png','CAM_Electronics');restore_visibility(state)
state=isolate(['17_CUTAWAY']);coll('17_CUTAWAY').hide_viewport=False
review('12_cutaway.png','CAM_Cutaway');restore_visibility(state);coll('17_CUTAWAY').hide_viewport=True
review('13_side.png','CAM_Side');review('14_top.png','CAM_Top')
print('ALL_REVIEWS_DONE',flush=True)
