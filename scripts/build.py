import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from stages import STAGES

stage=int(sys.argv[sys.argv.index('--')+1])
if stage>1:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'checkpoints'/f'm{stage-1:02d}.blend'))
    if stage<7: materials()
STAGES[stage]()
