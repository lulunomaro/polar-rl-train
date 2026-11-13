"""Stage the missing descending-flight cue while R3 continues its owner window."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
parser.add_argument('--archive',required=True)
args=parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect,execute
plan=json.loads((T/'PLAN_R3.json').read_bytes())
candidates=[]
for path in (T/'evidence').glob('eval_r3_model_*/RESULT.json'):
    data=json.loads(path.read_bytes())
    good=[e for e in data['episodes'] if e['success'] and not e['terminated']]
    candidates.append((len(good),sum(e['nominal'] for e in good),data))
best=max(candidates,key=lambda item:(item[0],item[1]))[2]
parent=best['checkpoint']
filename=Path(parent).name
frozen=T/'weights'/('train_cont_r3__'+filename)
assert hashlib.sha256(frozen.read_bytes()).hexdigest()==best['checkpoint_sha256']
plan.update(parent=parent,parent_sha256=best['checkpoint_sha256'],parent_iteration=best['iteration'],
    support=plan['root']+'/support_r4',draft=True,revision='R4 descending flight is now an observable landing-preparation command',
    continuation_selection=dict(evaluation=best['checkpoint'],successes=max(candidates,key=lambda item:(item[0],item[1]))[0],
        reason='Best completed R3 fixed evaluation, not latest filename'))
plan['jump']['policy_slots_28_35'][3]='landing_preparation_or_landed'
plan['jump']['landing_preparation_command']='phase3 and world vertical velocity<-0.10m/s, or measured landing already occurred'
plan['jump_bc'].update(dataset=plan['root']+'/teacher_demos_r3/successful_demos.pt',dataset_sha256='pending_native_collection')
(T/'PLAN_R4.json').write_text(json.dumps(plan,indent=2)+'\n')
files=[]
with tarfile.open(args.archive,'w:gz') as archive:
    for source in (T/'support_r4',T/'PLAN_R4.json'):
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':continue
            if path.suffix=='.py':ast.parse(path.read_text(encoding='utf8'))
            rel=path.relative_to(T).as_posix()
            archive.add(path,arcname=rel,recursive=False)
            files.append(dict(path=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(T/'evidence/REMOTE_INPUTS_R4_DRAFT.json').write_text(json.dumps(dict(epoch=time.time(),files=files,
    original_deadline_epoch=plan['original_training_start_epoch']+7200.,R3_owner_continues=True),indent=2)+'\n')
client=connect()
try:
    s=client.open_sftp();s.put(args.archive,plan['root']+'/revision_r4_inputs.tar.gz');s.close()
    status,out,err=execute(client,'cd '+shlex.quote(plan['root'])+' && test ! -e support_r4 && tar -xzf revision_r4_inputs.tar.gz',30)
    assert status==0,out+err
finally:client.close()
print(json.dumps(dict(parent=parent,parent_sha256=plan['parent_sha256'],draft=True,optimizer_updates=0)),flush=True)
