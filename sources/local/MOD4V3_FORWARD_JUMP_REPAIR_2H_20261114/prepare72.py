"""Freeze repaired inputs in a new Host72 task; do not launch any learning."""
import ast
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T=Path(__file__).resolve().parent
P=T.parent/'MOD4V3_FORWARD_JUMP_RL_2H_20261114'
sys.path.insert(0,sys.argv[1])
from ssh72 import connect,execute
root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_REPAIR_2H_20261114_R1'
old=json.loads((P/'PLAN_R4.json').read_bytes())
plan=json.loads(json.dumps(old).replace(old['root'],root))
for key in ('original_training_start_epoch','prior_phase_elapsed_seconds','continuation_selection'):
    plan.pop(key,None)
plan.update(schema='MOD4V3_FORWARD_JUMP_REPAIR_V1',root=root,support=root+'/support',
    parent=root+'/weights/parent_r3_080m.pt',teacher_parent=root+'/weights/root_five_minute.pt',
    cumulative_training_seconds_before=0,revision='Measured tuck precedes landing extension',
    admission_before_training_window=True,prior_phase_elapsed_seconds=0)
plan['jump_bc'].update(initial=1.,final=.5,decay_seconds=5400.,phase_weights=[1.,1.,1.,4.,1.],
    dataset=root+'/teacher_demos/successful_demos.pt',dataset_sha256='pending_native_demonstration_collection',
    online_sampling='Phase-balanced means, flight weight4; empty phases omitted',
    demo_sampling='205 per phase; flight weight4',demo_coefficient=2.)
plan['jump'].update(landing_preparation_command='phase3 AND measured retraction already passed AND world vz<-0.10, or landed',
    teacher_tuck_ramp_s=.04,air_reward_switch='Only after measured tuck AND descent; .20rad before, 1.35rad after')
plan['jump']['policy_slots_28_35'][3]='measured_tuck_complete_and_descending_or_landed'
plan['repair']=dict(measured_threshold_unchanged_rad=.9,teacher_no_optimizer=True,
    inherited_PPO_and_Adam=True,old_experiment_immutable=True,
    root_parent_sha256=plan['root_parent_sha256'],continuation_parent_sha256=plan['parent_sha256'])
for name,expected in (('parent_r3_080m.pt',plan['parent_sha256']),('root_five_minute.pt',plan['teacher_sha256'])):
    assert hashlib.sha256((T/'weights'/name).read_bytes()).hexdigest()==expected
(T/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
paths=json.loads((T/'dependencies/SOURCE_PATHS.relative.json').read_bytes())
(T/'dependencies/SOURCE_PATHS.72.json').write_text(json.dumps({k:root+'/dependencies/'+v for k,v in paths.items()},indent=2)+'\n')
archive=T/'inputs.tar.gz'
files=[]
with tarfile.open(archive,'w:gz') as bundle:
    for name in ('support','dependencies','native_package','weights','PLAN.json'):
        source=T/name
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc': continue
            if path.suffix=='.py': ast.parse(path.read_text(encoding='utf-8-sig'))
            rel=path.relative_to(T).as_posix()
            bundle.add(path,arcname=rel,recursive=False)
            files.append(dict(path=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(T/'evidence/INPUTS.json').write_text(json.dumps(dict(epoch=time.time(),root=root,files=files),indent=2)+'\n')
client=connect()
try:
    status,out,err=execute(client,'mkdir '+shlex.quote(root),20)
    assert status==0,out+err
    s=client.open_sftp();s.put(str(archive),root+'/inputs.tar.gz');s.close()
    status,out,err=execute(client,'cd '+shlex.quote(root)+' && tar -xzf inputs.tar.gz && sha256sum weights/*.pt native_package/assets/robot.usd',60)
    assert status==0,out+err
    print(out,err)
finally: client.close()
print(json.dumps(dict(root=root,files=len(files),bytes=archive.stat().st_size,optimizer_updates=0)))
