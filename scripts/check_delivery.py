"""File completeness, PNG dimensions, GLB containers and checksums; standard Python."""
from pathlib import Path
import struct,json,hashlib,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--verify',action='store_true',help='Check against the committed manifest without rewriting it')
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
required=['resin_printer_master.blend','exports/resin_printer_complete.glb','exports/resin_printer_explodable.glb']
render_names=['01_complete_hero','02_front','03_back','04_internal_no_panels','05_exploded_full','06_build_plate_closeup','07_vat_closeup','08_lcd_stack_exploded','09_light_engine_exploded','10_z_axis_closeup','11_electronics_closeup','12_cutaway','13_side','14_top']
required+=['renders/'+x+'.png' for x in render_names]
required+=['exports/'+x+'.glb' for x in ['build_plate','resin_vat','lcd_stack','z_axis','uv_light_engine','electronics']]
result={'files':[],'all_required_files_present':True}
for name in required:
    p=ROOT/name
    assert p.is_file(),name
    d=p.read_bytes();entry={'path':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
    if p.suffix=='.png':
        assert d[:8]==b'\x89PNG\r\n\x1a\n'
        w,h=struct.unpack_from('>II',d,16);assert (w,h)==(2000,2000);entry['dimensions']=[w,h]
    if p.suffix=='.glb':
        magic,ver,length=struct.unpack_from('<III',d);assert magic==0x46546c67 and ver==2 and length==len(d)
        size,kind=struct.unpack_from('<II',d,12);assert kind==0x4e4f534a
        j=json.loads(d[20:20+size]);entry['nodes']=len(j['nodes']);entry['meshes']=len(j['meshes']);entry['animations']=len(j.get('animations',[]))
        assert not any('uri' in b for b in j.get('buffers',[]))
        assert not j.get('cameras')
    result['files'].append(entry)
roundtrip=json.loads((ROOT/'reports'/'roundtrip_validation.json').read_text())
assert len(roundtrip)==2 and all(r['passed'] for r in roundtrip)
result['roundtrip_passed']=True
manifest_path=ROOT/'reports'/'delivery_manifest.json'
if args.verify:
    if result != json.loads(manifest_path.read_text()):
        raise SystemExit('Delivery manifest mismatch: review changed assets and regenerate the manifest.')
else:
    manifest_path.write_text(json.dumps(result,indent=2))
print('DELIVERY_PASS',len(required),'files; fourteen 2000px renders; two validated primary GLBs')
