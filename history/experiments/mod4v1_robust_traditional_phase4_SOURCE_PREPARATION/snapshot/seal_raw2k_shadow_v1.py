"""Seal existing R38 shadow contract evidence, no tests/physics/raw rehash.
This is a simulation information-enhancement branch, never control qualification.
"""
from pathlib import Path
import hashlib
import json
R=Path(__file__).resolve().parent
D=R/'RAW2K_SHADOW_V1'
primary=['publisher.py','unit_publisher.py','attempts/001/SOURCE_PREEXEC.json','attempts/001/RESULT.json','admission.py','admission001/RESULT.json','BRIDGE_PRECHECK.json','SENSOR_ONLY_MANIFEST.json','validate_r38_capture.py','capture_qa001/RESULT.json','README.md']
links=[]
for relative in primary:
    p=D/relative;raw=p.read_bytes();links.append(dict(path=str(p),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for relative in ('prepare_raw2k_shadow_v1.py','physics_bridge_raw2k_v1.py','physics_bridge_raw2k_grade_v1.py','run_raw2k_shadow_case_v1.py','launch_r38_raw2k_shadow.py',Path(__file__).name,'batches/r38_raw2k_shadow6/PROTOCOL.json','batches/r38_raw2k_shadow6/ADMISSION.log','batches/r38_raw2k_shadow6/BATCH_RESULT.json','reports/R38_RAW2K_SHADOW_FACTS.json'):
    p=R/relative;raw=p.read_bytes();links.append(dict(path=str(p),relative='../'+relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
batch=json.loads((R/'batches/r38_raw2k_shadow6/BATCH_RESULT.json').read_bytes())
for case in batch['rows']:
    for relative in ('config.json','SOURCE_MANIFEST.json','result.json'):
        p=R/'results'/case['case']/relative;raw=p.read_bytes();links.append(dict(path=str(p),relative='../results/'+case['case']+'/'+relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
raws=[]
for case in batch['rows']:
    for kind in ('shadow','original_trace'):
        artifact=case[kind]
        raws.append(dict(kind=kind,path=artifact['path'],bytes=artifact['bytes'],producer_SHA=artifact['SHA'],only_metadata_in_seal=True,raw_rehashed=False))
qa=json.loads((D/'capture_qa001/RESULT.json').read_bytes())
index=dict(status='SEALED_SIMULATION_SHADOW_CAPTURE_CONTRACT_ONLY',information_enhancement_not_old_benchmark=True,hardware_binding=False,actuation_used=False,control_qualification=False,raw_schema_checks=qa['checks'],failures=qa['failures'],new_physics_cases=6,new_physics_steps=64000,frames=3200,published_samples=qa['published_samples'],source_unique_samples=qa['unique_source_samples'],old_confidence_caps_unchanged=True,all_new_R38_control_cases_complete=True,no_new_physics_tests_during_seal=True,links=links,raw_metadata=raws,git_status='PH4_PENDING_NOT_IN_PH3_CUTOFF')
with(D/'INDEX.json').open('x',encoding='utf-8')as f:json.dump(index,f,indent=2)
print(json.dumps(dict(status=index['status'],files=len(links),raw_metadata=len(raws),physics_steps_during_seal=0,INDEX_SHA=hashlib.sha256((D/'INDEX.json').read_bytes()).hexdigest()),indent=2))
