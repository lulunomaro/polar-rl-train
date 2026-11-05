"""Small changed overlay after preserved20k failure; same complete PPO source."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut'
read=lambda p:json.loads(Path(p).read_bytes())
old=N/'supermimic_final881_1h';new=N/'supermimic_final881_host_replay02_1h'
failed=read(old/'reports/FAILED_FORMAL_RETURNED.json')
owner=failed['files']['OWNER_EXIT.json']
assert owner['all_own_waited']and owner['original_leases_released']and owner['error']
assert read(N/'supermimic_host_replay08/RESULT.json')['passed']
assert read(N/'reports/HOST_REPLAY_PARITY.json')['passed']
plan=read(old/'PLAN.json')
plan.update(remote_root=plan['remote_root'].rsplit('/',1)[0]+'/'+new.name,
    run_id='newton_supermimic_host_replay_'+str(time.time_ns()),
    previous_overlay_paths=[plan['remote_root']+'/overlay',*plan['previous_overlay_paths']],
    cumulative_authorized_seconds_before_this_segment=plan['cumulative_authorized_seconds_before_this_segment']+owner['actual_elapsed_seconds'],
    prior_failed_attempt=plan['remote_root'],source_optimizer_step=17620,
    source_learning_rate=.0008649755859375004,replay_storage='cpu',replay_sample_device='cuda:0',
    specific_repair='Full-precision CPU replay, GPU sampled batches, unused PPO runner storage released before collision workspace; unchanged20k/physics/Fudan/H32')
plan.pop('GPU_UUID',None)
assert plan['cumulative_authorized_seconds_before_this_segment']+3900<=360000
new.mkdir(exist_ok=False);(new/'reports').mkdir()
files=[]
def add(p,name):
    raw=p.read_bytes();files.append(dict(path=str(p),relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for name in ('supermimic_newton.py','supermimic_train.py'):add(CODE/name,'overlay/'+name)
binding=new/'SUPERMIMIC_BINDINGS.json';binding.write_bytes((old/'SUPERMIMIC_BINDINGS.json').read_bytes());add(binding,binding.name)
add(N/'newton_entry.py','entry.py');add(N/'newton_owner.py','owner.py')
add(N/'newton_fudan_final620_1h/run-newton.sh','run-newton.sh')
(new/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
(new/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,
    shared_text=read(old/'SOURCE_PREPARED.json')['shared_text'],whole_tree_copies=0,
    checkpoint_copies=0,asset_copies=0,learner_source_reference=str(old/'SUPERMIMIC_BINDINGS.json')),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(new),files=len(files),source=plan['source_checkpoint'],cumulative_seconds=plan['cumulative_authorized_seconds_before_this_segment'])))
