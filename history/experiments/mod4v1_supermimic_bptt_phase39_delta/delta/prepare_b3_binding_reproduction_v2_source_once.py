"""Preserve the V1 pre-case fixture failure and create a NEW smaller reproduction."""
from pathlib import Path
import json,hashlib,ast,time
R=Path(__file__).resolve().parent;old=R/'verify_phase1_b3_binding_negative_reproduction_once.py';new=R/'verify_phase1_b3_binding_negative_reproduction_v2_once.py';out=R/'reports/PHASE1_B3_BINDING_REPRODUCTION_PRECASE_FAILURE_AND_V2_SOURCE_V1.json';assert not new.exists()and not out.exists();raw=old.read_bytes();text=raw.decode();assert (R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_STARTED_ONCE.json').exists()and not(R/'reports/PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V1.json').exists()
root=R/'source_phase1_passive_sensor_capture_v3';pins=json.loads((root/'CODEC_SOURCE_PINS.json').read_bytes());assert not any(type(v)is int for v in pins['codec_constants'].values())
for d in(root,R/'source_phase1_typed_capture_codec_v1'):
 for name,pin in json.loads((d/'SOURCE_SEAL.json').read_bytes())['files'].items():
  b=(d/name).read_bytes();assert len(b)==pin['bytes']and hashlib.sha256(b).hexdigest()==pin['sha256']
for a,b in [('PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V1.json','PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V2.json'),('PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_STARTED_ONCE.json','PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V2_STARTED_ONCE.json'),('ACTUAL_STDLIB_SOURCE_BINDING_NEGATIVE_REPRODUCTION_V1','ACTUAL_STDLIB_SOURCE_BINDING_NEGATIVE_REPRODUCTION_V2')]:
 assert text.count(a)==1;text=text.replace(a,b)
a=";constant_name=next(k for k,v in pins['codec_constants'].items()if type(v)is int);original_constant=vars(codec_module)[constant_name]";assert text.count(a)==1;text=text.replace(a,'')
start=text.index(' setattr(codec_module,constant_name,float(original_constant))');end=text.index(' q=contract.verify_typed_dependency(snapshot,ledger);assert len(q[\'checked_functions\'])==22 and fn.__defaults__ is original_defaults',start);text=text[:start]+text[end:];text=text.replace(" and type(vars(codec_module)[constant_name])is type(original_constant)",'').replace(';setattr(codec_module,constant_name,original_constant)','');assert 'constant_name'not in text
text=text.replace('Temporary function defaults/constants','Temporary function defaults').replace('temporary_defaults_and_constant_restored','temporary_defaults_restored');ast.parse(text)
with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
v=dict(kind='V1_PRECASE_SOURCE_FIXTURE_FAILURE_RETAINED_NEW_V2_NO_CONSTANT_ASSUMPTION',epoch=time.time(),original_runner=old.name,original_runner_SHA256=hashlib.sha256(raw).hexdigest(),actual_exit_code=1,actual_exception='StopIteration',actual_phase='next scalar-int codec_constants before cases list or any default mutation',actual_cases_reached=0,frozen_members_still_match_all_original_seals=True,persisted_module_mutation=False,module_mutation_claim_basis='failure occurs before mutating block; fresh process exited',old_sealed_sources_or_tests_changed=False,new_runner=new.name,new_runner_SHA256=hashlib.sha256(text.encode()).hexdigest(),new_scope='original two reviewed gaps only; no invented scalar-constant case',native_or_SDK_or_model_or_C_operations=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
