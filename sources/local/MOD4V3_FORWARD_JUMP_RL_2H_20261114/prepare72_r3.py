"""Stage a task fix from the safe R1 save, retaining the original deadline."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
parser.add_argument('--archive',required=True)
args = parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect,execute
plan = json.loads((T/'PLAN_R2.json').read_bytes())
root = plan['root']
client = connect()
try:
    sftp = client.open_sftp()
    with sftp.open(root+'/train_cont_r2/SAFE_CLOSED.json','rb') as stream:
        closed = json.loads(stream.read())
    assert closed['outcome'] == 'complete'
    with sftp.open(root+'/train_cont_r2/FINAL.json','rb') as stream:
        final = json.loads(stream.read())
    checkpoint = final['checkpoint']
    target = T/'weights/train_cont_r2__model_final.pt'
    if not target.exists():
        sftp.get(checkpoint['path'],str(target))
    assert hashlib.sha256(target.read_bytes()).hexdigest() == checkpoint['sha256']
    with sftp.open(root+'/train120m_r1/TRAINING_STARTED.json','rb') as stream:
        first = json.loads(stream.read())
    with sftp.open(root+'/teacher_demos_r1/RESULT.json','rb') as stream:
        demos=json.loads(stream.read())
    plan.update(parent=checkpoint['path'],parent_sha256=checkpoint['sha256'],
        parent_iteration=checkpoint['iteration'],support=root+'/support_r3',
        prior_phase_elapsed_seconds=plan['prior_phase_elapsed_seconds']+final['elapsed_seconds'],
        revision='R3 phase-balanced native successful demonstrations inside the same PPO loss',
        cumulative_training_seconds_before=time.time()-first['epoch'])
    plan['jump_bc'].update(dataset=root+'/teacher_demos_r1/successful_demos.pt',
        dataset_sha256=demos['dataset_sha256'],demo_coefficient=2.,demo_minibatch=1025,
        demo_sampling='Equal samples from approach/crouch/push/flight/recovery',
        teacher_execution_in_PPO=False,standalone_BC_optimizer=False)
    plan['jump'].update(policy_slots_28_35=['base_mode','jump_request','measured_air','landed','crouch_command','push_command','phase_progress'],
        phase_progress_normalization_s=dict(crouch=.32,push=.8,flight=.4),
        critic_slots_32_39='Five phase bits plus reserved bit and normalized phase progress',
        phase_clock_observed=True)
    (T/'PLAN_R3.json').write_text(json.dumps(plan,indent=2)+'\n')
    decision=dict(epoch=time.time(),reason='On-policy sampling has almost no successful crouch/air states; phase-balanced successful native demonstration guidance',
        R2_final=final,R2_closed=closed,dataset=demos,original_start_epoch=first['epoch'],
        deadline_epoch=first['epoch']+7200.,full_PPO_continuation=True,extra_budget_seconds=0,
        reward_guards_assets_unchanged_from_R2=True,
        input_change='One unused mode slot now observes normalized phase progress, so the MLP can represent the time-varying labels',
        runtime_admission='Native successful demonstration collection under R3 input schema, plus inherited exact assets/timing/guards',
        root_parent_sha256=plan['root_parent_sha256'])
    (T/'evidence/REVISION_R3_DECISION.json').write_text(json.dumps(decision,indent=2)+'\n')
    manifest = []
    with tarfile.open(args.archive,'w:gz') as archive:
        for source in (T/'support_r3',T/'PLAN_R3.json'):
            for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
                if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                    continue
                if path.suffix == '.py':
                    ast.parse(path.read_text(encoding='utf8'))
                rel = path.relative_to(T).as_posix()
                archive.add(path,arcname=rel,recursive=False)
                manifest.append(dict(path=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (T/'evidence/REMOTE_INPUTS_R3.json').write_text(json.dumps(dict(epoch=time.time(),files=manifest,
        original_deadline_epoch=first['epoch']+7200.,parent_sha256=plan['parent_sha256']),indent=2)+'\n')
    sftp.put(args.archive,root+'/revision_r3_inputs.tar.gz')
    sftp.close()
    status,out,err = execute(client,'cd '+shlex.quote(root)+' && test ! -e support_r3 && tar -xzf revision_r3_inputs.tar.gz',30)
    assert status == 0,out+err
finally:
    client.close()
print(json.dumps(dict(root=root,prior_phase_seconds=final['elapsed_seconds'],
    original_deadline_epoch=first['epoch']+7200.,remaining_wall_seconds=first['epoch']+7200.-time.time())),flush=True)
