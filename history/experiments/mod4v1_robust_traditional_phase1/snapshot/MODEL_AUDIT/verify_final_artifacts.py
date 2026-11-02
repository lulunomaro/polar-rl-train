"""Final static integrity QA only; no simulator import and no source mutations."""
from pathlib import Path
import ast, hashlib, json, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def invalid_constant(x):raise ValueError('Non-RFC8259 constant '+x)
p=HERE/'MODEL_ALIGNMENT_INDEX.json';idx=json.loads(p.read_text(encoding='utf-8'),parse_constant=invalid_constant)
# Refresh only hashes of the reviewed wording correction and its generator source.
idx['report']=meta(HERE/'MODEL_ALIGNMENT.md')
for a in idx['artifacts']:
    if Path(a['path']).name=='build_alignment_report.py':a.update(meta(HERE/'build_alignment_report.py'))
idx['artifacts'].append(meta(Path(__file__)))
p.write_text(json.dumps(idx,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
assert all(not a['exists'] or sha(a['path'])==a['sha256'] for a in idx['checked_source_files'])
assert sha(idx['primary']['path'])==idx['primary']['sha256']
assert sha(idx['report']['path'])==idx['report']['sha256']
assert all(sha(a['path'])==a['sha256'] for a in idx['artifacts'])
receipt=json.loads((HERE/'USD_SOURCE_DERIVATION_RECEIPT.json').read_text(encoding='utf-8'))
assert all(sha(a['path'])==a['sha256'] for a in receipt['mesh_dependencies']['files'])
old=ET.parse(r'F:\RMPOLAR-RL\traditional_control_20261101\model\mod4_400N.xml').getroot()
new=ET.parse(idx['primary']['path']).getroot()
for tag in ['equality','actuator','contact','sensor','option','default']:
    assert ET.tostring(old.find(tag))==ET.tostring(new.find(tag)),tag
assert len(new.findall('.//body'))==31
assert len(new.findall('.//body/geom'))==311
assert len(new.findall('equality/connect'))==6 and len(new.findall('equality/joint'))==4
assert len(new.findall('asset/mesh'))==279
for name in ['inspect_sources.py','analyze_alignment.py','generate_mjcf.py','finalize_geometry_candidate.py','verify_geometry.py','build_alignment_report.py','verify_final_artifacts.py']:
    ast.parse((HERE/name).read_text(encoding='utf-8'),filename=name)
result={'status':'PASS_FINAL_STATIC_INTEGRITY','strict_JSON_index':True,'all_indexed_artifact_hashes_match':True,'all_checked_source_hashes_unchanged':True,'all_279_mesh_dependencies_exist_and_match_hashes':True,'unchanged_XML_sections':['equality','actuator','contact','sensor','option','default'],'script_AST_parse_all_pass':True,'primary':meta(idx['primary']['path']),'report':meta(HERE/'MODEL_ALIGNMENT.md'),'index':meta(p),'full_DR_episodes':0,'time_advanced_s':0}
(HERE/'FINAL_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
