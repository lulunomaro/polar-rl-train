"""Freeze a new height task and reuse the previous immutable plant inputs."""
import ast
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T=Path(__file__).resolve().parent
P=T.parent/'MOD4V3_FORWARD_JUMP_REPAIR_2H_20261114'
sys.path.insert(0,sys.argv[1])
from ssh72 import connect,execute
root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114_R1'
plan=json.loads((P/'PLAN.json').read_bytes())
old_root=plan['root']
plan.update(schema='MOD4V3_FORWARD_JUMP_HEIGHT_V1',root=root,support=root+'/support',
            parent=old_root+'/train7200/model_085m.pt',
            parent_sha256='c4d0328472e8642c497f113e37fb8940d92435cd8d96f547b8f1f4aa15cc1dfe',
            parent_iteration=27116,cumulative_training_seconds_before=0,
            budget_total_training_seconds=7200,prior_phase_elapsed_seconds=0,
            revision='Measured height rewards and unconstrained push/flight PPO',
            parent_selection='Best survived complete-jump checkpoint of the completed prior two-hour run',
            user_authorization='Repair and start jumping training; retain prior two-hour duration',
            input_reuse='Previous frozen dependencies/native package/reset bank are read-only')
plan['height']=dict(initial_clearance_m=.25,final_clearance_m=.35,
                    initial_body_rise_m=.25,final_body_rise_m=.32,curriculum_seconds=3600.,
                    reference='Body root height immediately before crouch; wheel lower rim above flat ground',
                    evaluation='Fixed final targets at all checkpoints, seed10066, 51nominal/205fullDR',
                    measured_height_reward='Monotone airborne peak increments, orientation weighted; body45, rim20',
                    push_reward='Ballistic remaining-height speed tracking plus predicted apex progress',
                    external_takeoff_assistance=False)
plan['jump_bc']=dict(initial=.1,final=.02,decay_seconds=3600.,demo_coefficient=0.,
                     phase_weights=[1.,0.,0.,0.,1.],
                     type='Weak training-only frozen cruise labels for approach and landed phases',
                     execution='Sampled learned actor only',teacher_execution_in_PPO=False,
                     standalone_BC_optimizer=False,old_jump_demo_replay=False)
plan['jump'].update(min_wheel_lower_rim_peak_m=.35,min_body_rise_peak_m=.32,
                    initial_curriculum_clearance_m=.25,legacy_sequence_clearance_m=.12,
                    actual_extension_required_before_takeoff=True,
                    selection='Survived fixed-final-height successes, then complete sequences and measured clearance')
plan['repair']=dict(old_trial_immutable=True,plant_motor_timing_unchanged=True,
                    root_parent_sha256=plan['root_parent_sha256'],
                    continuation_parent_sha256=plan['parent_sha256'],
                    old_1_5_m_s_reward_cap_removed=True,actual_body_rise_and_clearance_required=True,
                    old_small_jump_demonstrations_disabled=True,
                    weak_guidance_phases=['approach','landed'],
                    policy_observation_semantics_unchanged=True)
assert hashlib.sha256((P/'weights/train7200__model_085m.pt').read_bytes()).hexdigest()==plan['parent_sha256']
assert json.loads((T/'evidence/OBJECTIVE_CHECK.json').read_bytes())['passed']
(T/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8')
archive=T/'inputs.tar.gz'
files=[]
with tarfile.open(archive,'w:gz') as bundle:
    for path in sorted((T/'support').rglob('*'))+[T/'PLAN.json']:
        if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':continue
        if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8-sig'))
        name=path.relative_to(T).as_posix()
        bundle.add(path,arcname=name,recursive=False)
        files.append(dict(path=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
receipt=dict(epoch=time.time(),root=root,files=files,reused_input_root=old_root,
             parent_sha256=plan['parent_sha256'],source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
(T/'evidence/INPUTS.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
client=connect()
try:
    script='from pathlib import Path; Path('+repr(root)+').mkdir()'
    code,out,err=execute(client,'python3 -c '+shlex.quote(script),20)
    assert code==0,out+err
    sftp=client.open_sftp()
    sftp.put(str(archive),root+'/inputs.tar.gz')
    sftp.close()
    script='''
import hashlib,json,subprocess
from pathlib import Path
r=Path(ROOT)
subprocess.run(['tar','-xzf',str(r/'inputs.tar.gz'),'-C',str(r)],check=True)
p=json.loads((r/'PLAN.json').read_text())
assert hashlib.sha256(Path(p['parent']).read_bytes()).hexdigest()==p['parent_sha256']
for f in FILES:
 assert hashlib.sha256((r/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
print(json.dumps(dict(root=str(r),parent_sha256=p['parent_sha256'],files_verified=len(FILES),optimizer_updates=0)))
'''.replace('ROOT',repr(root)).replace('FILES',repr(files))
    code,out,err=execute(client,'python3 -c '+shlex.quote(script),60)
    assert code==0,out+err
    remote=json.loads(out)
    (T/'evidence/REMOTE_INPUT_CHECK.json').write_text(json.dumps(remote,indent=2)+'\n',encoding='utf8')
    print(json.dumps(remote,indent=2))
finally:client.close()
