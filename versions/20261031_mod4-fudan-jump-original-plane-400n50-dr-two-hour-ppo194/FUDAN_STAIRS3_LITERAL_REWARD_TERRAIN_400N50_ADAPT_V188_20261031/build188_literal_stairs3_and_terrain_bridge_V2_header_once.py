"""Keep selected original reward/config/Terrain methods verbatim.
Only the SDK measured-field and heightfield/triangle bridge lives outside them.
"""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;P=N/'package_v2';P.mkdir()
S=N/'upstream/plane/logs/wheel_legged/上台阶3'
def H(b):return hashlib.sha256(b).hexdigest()
def put(name,v):
 with (N/'reports'/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def source(p):
 b=p.read_bytes();return b,b.decode('utf8'),ast.parse(b)
rb,rt,ra=source(S/'legged_robot.py');cb,ct,ca=source(S/'legged_robot_config.py')
cls=next(x for x in ra.body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobot')
methods=[x for x in cls.body if isinstance(x,ast.FunctionDef) and (x.name.startswith('_reward_') or x.name in ('compute_reward','_prepare_reward_function','_update_terrain_curriculum','_get_heights'))]
first_import=min(x.lineno for x in ra.body if isinstance(x,(ast.Import,ast.ImportFrom)));license=''.join(rt.splitlines(keepends=True)[:first_import-1])
chunks=[ast.get_source_segment(rt,x) for x in methods]
# get_source_segment omits indentation on the first line only; restore those
# four spaces, leaving every character inside each original method unchanged.
original_methods='\n\n'.join('    '+x for x in chunks)
(P/'literal_stairs3_original_methods.py').write_text(license+'\nfrom __future__ import annotations\nimport torch\n\nclass OriginalStairs3Methods:\n'+original_methods+'\n',encoding='utf8')
cfg=next(x for x in ca.body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobotCfg')
parts=[x for x in cfg.body if isinstance(x,ast.ClassDef) and x.name in ('terrain','commands','rewards','normalization')]
old=T/'ORIGINAL_FUDAN_JUMP_UPSTREAM_SOURCE_REVIEW_20261031_V1/literal_harness_v1/literal_original_config.py'
ob,ot,oa=source(old);fn=next(x for x in oa.body if isinstance(x,ast.FunctionDef) and x.name=='class_to_dict')
config=license+'\nclass OriginalStairs3Cfg:\n'+'\n\n'.join('    '+ast.get_source_segment(ct,x) for x in parts)+'\n\n'+ast.get_source_segment(ot,fn)+'\n'
(P/'literal_stairs3_original_config.py').write_text(config,encoding='utf8')
tb,tt,ta=source(N/'upstream/plane/wheel_legged_gym/utils/terrain.py')
terrain_cls=next(x for x in ta.body if isinstance(x,ast.ClassDef) and x.name=='Terrain')
terrain_source=tt[:tt.index('import numpy')]
terrain_source+='\nfrom __future__ import annotations\nimport numpy as np\nfrom numpy.random import choice\nfrom types import SimpleNamespace\nfrom literal_stairs3_original_config import OriginalStairs3Cfg as LeggedRobotCfg\n'
terrain_source+='from stairs3_heightfield_sdk_bridge188 import terrain_utils\n\n'+ast.get_source_segment(tt,terrain_cls)+'\n'
(P/'literal_stairs3_original_terrain.py').write_text(terrain_source,encoding='utf8')
api=json.loads((N/'reports/ROOT188API_ORIGINAL_FORWARD210_MODEL_FILENAME_INVENTORY_ACTUAL.json').read_bytes())
hf=next(x for x in api['files'] if x['path'].endswith('/hf_terrains.py'))
ht=hf['UTF8'];ha=ast.parse(ht);stairs=next(x for x in ha.body if isinstance(x,ast.FunctionDef) and x.name=='pyramid_stairs_terrain')
body=ast.get_source_segment(ht,stairs)
(P/'installed_original_raw_pyramid_stairs188.py').write_text(ht[:ht.index('from __future__')]+'\nfrom __future__ import annotations\nimport numpy as np\n\ndef height_field_to_mesh(f):return f\n\n@height_field_to_mesh\n'+body+'\n',encoding='utf8')
new=ast.parse((P/'literal_stairs3_original_methods.py').read_bytes());nc=next(x for x in new.body if isinstance(x,ast.ClassDef))
assert len(nc.body)==len(methods)
for x,y in zip(methods,nc.body):assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False),x.name
put('ROOT188_LITERAL_REWARD_TERRAIN_EXTRACTION_V2_FROZEN_SOURCE.json',dict(epoch=time.time(),passed_text_AST=True,original_reward_file_SHA=H(rb),original_cfg_SHA=H(cb),original_terrain_SHA=H(tb),unchanged_reward_and_state_methods=[x.name for x in methods],reward_formula_or_weight_edits=0,Terrain_class_AST_literal=True,SDK_hf_pyramid_source=hf['path'],SDK_hf_pyramid_source_SHA=hf['SHA'],original_class_to_dict_reused=True,models_SDK_GPU_or_training=0,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes())) for p in sorted(P.glob('*.py'))]))
print(json.dumps(dict(original_methods=len(methods),source_AST_passed=True,original_reward_edits=0)))
