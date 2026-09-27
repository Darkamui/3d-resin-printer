import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports'/'resin_printer_complete.glb'))
mat('Studio',(.14,.18,.22),0,.65)
studio();cyclorama()
render('milestones/08_glb_roundtrip_hero.png','CAM_Hero_3Quarter',1400,64)
