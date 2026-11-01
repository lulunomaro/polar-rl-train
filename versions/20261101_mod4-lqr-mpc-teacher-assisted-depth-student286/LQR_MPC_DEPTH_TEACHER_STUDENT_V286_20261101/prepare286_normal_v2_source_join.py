"""Correct unused collector's inherited receipt name; never alter its old index."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;R=N/'reports';OLD=N/'normal286';D=N/'normal286_v2';D.mkdir(exist_ok=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
source=OLD/'collect286_teacher_student_formal_cost_normal900_UNUSED_once.py'
text=source.read_text('utf8').replace('normal286_common','normal286v2_common')
text=text.replace('ACTUAL286_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json',
                  'ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json')
target=D/source.name;target.write_text(text,encoding='utf8');ast.parse(text)
common=(OLD/'normal286_common.py').read_text('utf8')
lines=common.splitlines();lines=["SHA='cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b'"if line.startswith('SHA=')else line for line in lines]
common='\n'.join(lines)+'\n';common=common.replace('INDEX286_NORMAL_SOURCE_FROZEN.json','INDEX286_NORMAL_V2_SOURCE_FROZEN.json')
p=D/'normal286v2_common.py';p.write_text(common,encoding='utf8');ast.parse(common)
spec=importlib.util.spec_from_file_location('normal286v2_test',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
current=json.loads((R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER.json').read_bytes())
binding=json.loads((R/'ROOT286_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json').read_bytes());g=binding['current']['go']['jump_72']
assert module.validate_original_go(g,current['run_id'])
assert not module.normal900_eligible(g,g['nominal_end_epoch']-901,False)
assert module.normal900_eligible(g,g['nominal_end_epoch']-900,False)
assert module.normal900_eligible(g,g['learning_started_epoch'],True)
# A typed final-receipt metadata check does not open any model or replay data.
from teacher_task286 import validate_final,FINAL_KIND
fake=json.loads(json.dumps(binding['first']));fake['kind']=FINAL_KIND;fake['final']=fake.pop('first_complete')
fake['final']['save_epoch']=g['save_deadline'];assert validate_final(fake,json.loads((N/'TASK286_FROZEN.json').read_bytes()),g)
fake['final']['save_epoch']=g['save_deadline']-1
try:validate_final(fake,json.loads((N/'TASK286_FROZEN.json').read_bytes()),g)
except AssertionError:pass
else:raise AssertionError('early final metadata must reject')
report=R/'NORMAL286_V2_SOURCE_METADATA_JOIN.json'
put(report,dict(epoch=time.time(),passed=True,trial_id='teacher286-unused-normal-reader-source-join-v2',
 old_unused_reader_preserved=True,old_descriptive_SHA_substitution_typo_unused=True,
 reason='actual inherited production receipt is ACTUAL276, not renamedACTUAL286; preserve full original UTF8',
 signed_normal900_boundary_and_closed_cases=True,typed_final_positive_and_early_save_reject=True,
 model_raw_SDK_GPU_network_reads=0,old_once_not_executed=True))
index=D/'INDEX286_NORMAL_V2_SOURCE_FROZEN.json';put(index,dict(epoch=time.time(),kind='UNUSED286_NORMAL_V2_SOURCE_JOIN',files=[dict(path=str(q),bytes=q.stat().st_size,SHA=H(q))for q in (target,p,N/'teacher_task286.py',report,Path(__file__))]))
current['next']['normal_collector']=str(target);current['next']['caller_index_SHA']=H(index)
current['next']['retired_normal_v1_unused']=str(source)
current['next']['new_normal_v2_metadata_join']=str(report)
current['epoch']=time.time();current['status']='ACTUAL286_FIRST_PASS_CURRENT_NORMAL_V2_SOURCE_SELECTED'
put(R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER_V2.json',current)
print(json.dumps(dict(passed=True,normal_index_SHA=H(index),collector=str(target))))
