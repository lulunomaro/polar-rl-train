from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;P=N/'newton_fudan_final620_1h/shorttmp02';A=P.parent/'authored_gap03'
CODE=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut')
read=lambda p:json.loads(Path(p).read_bytes())
f=read(P/'reports/FIRST_ACTUAL_RETURNED.json')['files']
assert f['OWNER_EXIT.json']['all_own_waited']and f['OWNER_EXIT.json']['original_leases_released']
assert 'Failed to allocate 7688880000 bytes'in f['production/ERROR.json']['error']
assert read(N/'reports/NEWTON_AUTHORED_GAP07.json')['passed']
A.mkdir(exist_ok=False);(A/'reports').mkdir();plan=read(P/'PLAN.json')
plan['previous_overlay_paths']=[P.parent.as_posix()+'/unused']if False else plan['previous_overlay_paths']
plan['remote_root']=plan['remote_root'].rsplit('/',1)[0]+'/authored_gap03'
plan['run_id']='newton_authored_gap03_'+str(time.time_ns())
plan['cumulative_authorized_seconds_before_this_segment']+=f['OWNER_EXIT.json']['actual_elapsed_seconds']
plan['specific_repair']='Preserve original MJCF gap0 explicitly instead of Newton generic .1m collisiongap; valid resetpose allocation; old driver graph_conditional false'
plan.pop('GPU_UUID',None)
(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
files=[]
for path,rel in [(CODE/'newton_model.py','overlay/newton_model.py'),(N/'newton_entry.py','entry.py'),(N/'newton_owner.py','owner.py'),(P.parent/'run-newton.sh','run-newton.sh')]:
 raw=path.read_bytes();files.append(dict(path=str(path),relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(A/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,shared_text=read(P/'SOURCE_PREPARED.json')['shared_text'],
    original_failed_attempts_preserved=True,only_changed_source=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(A),files=len(files))))
