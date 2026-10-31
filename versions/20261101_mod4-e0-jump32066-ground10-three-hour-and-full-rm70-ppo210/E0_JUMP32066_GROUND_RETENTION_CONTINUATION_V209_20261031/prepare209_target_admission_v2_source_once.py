"""Retain unexecuted V1 label error; V2 corrects source counters and wording."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
remote=(N/'remote209_source_CPU_and_mixed_native80_admission.txt').read_text('utf8')
assert 'source_iteration=32094' in remote
remote=remote.replace('source_iteration=32094','source_iteration=32066')
remote=remote.replace('E0_82_LITERAL_JUMP72_400N50_NATIVE8_ACTUAL_SOURCE_ADMISSION','E0_JUMP32066_MIXED_GROUND10_JUMP90_NATIVE8_ACTUAL_SOURCE_ADMISSION')
local=(N/'install209_mixed_target80_admission_once.py').read_text('utf8')
local=local.replace('Adam17=641200,RSL=32094','Adam17=642840,RSL=32066')
local=local.replace('install209_mixed_target80_admission_once','install209_mixed_target80_admission_V2_once')
local=local.replace('remote209_source_CPU_and_mixed_native80_admission.txt','remote209_source_CPU_and_mixed_native80_admission_V2.txt')
local=local.replace('Only72 current194 authority check, new source stage, sourceCPU and64env0PT admission.','Fresh72 canonicalNone, new source stage, sourceCPU and80env mixed0PT admission.')
local=local.replace('ACTUAL209_FRESH72_CURRENT194_BINDING_BEFORE_STAGE','ACTUAL209_FRESH72_CNONE_BEFORE_STAGE')
local=local.replace("|install_evaluate191_'","|install_evaluate191_|install208_|launch208_|launch209_|collect209_|install207_|evaluate207_'" )
for name,src in [('remote209_source_CPU_and_mixed_native80_admission_V2.txt',remote),('install209_mixed_target80_admission_V2_once.py',local)]:
 ast.parse(src)
 with (N/name).open('x',encoding='utf8',newline='\n') as f:f.write(src)
with (R/'FROZEN209_TARGET_ADMISSION_V2_SOURCE_INDEX_AND_V1_REJECTION.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),selected='V2',original_V1='NOT_EXECUTED source metadata conversion changed31984 to32094; no model/SDK/GPU/network action',
  corrected_source_iteration=32066,corrected_Adam17=642840,actual_beforeuse_core_CPU_not_replayed=True,
  files={name:hashlib.sha256((N/name).read_bytes()).hexdigest() for name in ('remote209_source_CPU_and_mixed_native80_admission_V2.txt','install209_mixed_target80_admission_V2_once.py')},
  fresh_local_CIM_required=True,one_global_serial_SSH=True,source_only=True),f,indent=2)
print(json.dumps(dict(passed=True,selected='V2',source_only=True)))
