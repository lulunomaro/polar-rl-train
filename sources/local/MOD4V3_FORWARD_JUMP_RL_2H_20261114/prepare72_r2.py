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
plan = json.loads((T/'PLAN.json').read_bytes())
root = plan['root']
client = connect()
try:
    sftp = client.open_sftp()
    with sftp.open(root+'/train120m_r1/SAFE_CLOSED.json','rb') as stream:
        closed = json.loads(stream.read())
    assert closed['outcome'] == 'complete'
    with sftp.open(root+'/train120m_r1/FINAL.json','rb') as stream:
        final = json.loads(stream.read())
    checkpoint = final['checkpoint']
    target = T/'weights/train120m_r1__model_final.pt'
    if not target.exists():
        sftp.get(checkpoint['path'],str(target))
    assert hashlib.sha256(target.read_bytes()).hexdigest() == checkpoint['sha256']
    with sftp.open(root+'/train120m_r1/TRAINING_STARTED.json','rb') as stream:
        first = json.loads(stream.read())
    plan.update(parent=checkpoint['path'],parent_sha256=checkpoint['sha256'],
        parent_iteration=checkpoint['iteration'],teacher_parent=plan['parent'],teacher_sha256=plan['parent_sha256'],
        root_parent_sha256=plan['parent_sha256'],support=root+'/support_r2',
        original_training_start_epoch=first['epoch'],prior_phase_elapsed_seconds=final['elapsed_seconds'],
        revision='R2 phase commands and finite push attempt; original wall window retained',
        cumulative_training_seconds_before=final['elapsed_seconds'])
    plan['jump'].update(policy_slots_28_35=['base_mode','jump_request','measured_air','landed','crouch_command','push_command',0],
        push_attempt_timeout_s=.8,phase_commands_explicit=True,
        controller_execution='Learned action only; environment supplies high-level phase commands')
    (T/'PLAN_R2.json').write_text(json.dumps(plan,indent=2)+'\n')
    decision = dict(epoch=time.time(),first_fixed_eval='eval_model_005m',result='0/256 complete success and0takeoff',
        reason=['Crouch/push are identical policy mode observations for a feedforward MLP',
                'Push could persist without takeoff and retain extension reward'],
        fixes=['Explicit crouch/push input commands in previously unused mode slots',
               'A push with no takeoff within0.8s is an unsuccessful task episode'],
        R1_final=final,R1_closed=closed,original_start_epoch=first['epoch'],deadline_epoch=first['epoch']+7200.,
        root_parent_sha256=plan['root_parent_sha256'],full_PPO_continuation=True,extra_budget_seconds=0,
        stop_marker_note='SFTP x created the empty REQUEST_STOP marker; subsequent text write raised File not open for writing. The existing marker correctly requested a complete save.')
    (T/'evidence/REVISION_R2_DECISION.json').write_text(json.dumps(decision,indent=2)+'\n')
    manifest = []
    with tarfile.open(args.archive,'w:gz') as archive:
        for source in (T/'support_r2',T/'PLAN_R2.json'):
            for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
                if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                    continue
                if path.suffix == '.py':
                    ast.parse(path.read_text(encoding='utf8'))
                rel = path.relative_to(T).as_posix()
                archive.add(path,arcname=rel,recursive=False)
                manifest.append(dict(path=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (T/'evidence/REMOTE_INPUTS_R2.json').write_text(json.dumps(dict(epoch=time.time(),files=manifest,
        original_deadline_epoch=first['epoch']+7200.,parent_sha256=plan['parent_sha256']),indent=2)+'\n')
    sftp.put(args.archive,root+'/revision_r2_inputs.tar.gz')
    sftp.close()
    status,out,err = execute(client,'cd '+shlex.quote(root)+' && test ! -e support_r2 && tar -xzf revision_r2_inputs.tar.gz',30)
    assert status == 0,out+err
finally:
    client.close()
print(json.dumps(dict(root=root,prior_phase_seconds=final['elapsed_seconds'],
    original_deadline_epoch=first['epoch']+7200.,remaining_wall_seconds=first['epoch']+7200.-time.time())),flush=True)
