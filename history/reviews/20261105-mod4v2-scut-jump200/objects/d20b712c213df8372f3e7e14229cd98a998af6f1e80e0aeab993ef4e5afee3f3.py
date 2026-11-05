from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;P=N/'newton_fudan_final620_1h/authored_gap03';A=P.parent/'episode_reset04'
CODE=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut')
read=lambda p:json.loads(Path(p).read_bytes())
f=read(P/'reports/FIRST_ACTUAL_RETURNED.json')['files'];old=read(P/'PLAN.json')
assert f['OWNER_EXIT.json']['all_own_waited']and f['OWNER_EXIT.json']['original_leases_released']
assert 'Nonfinite real sensor input'in f['production/ERROR.json']['error']
assert read(N/'reports/NEWTON_EPISODE_RESET08.json')['passed']
A.mkdir(exist_ok=False);(A/'reports').mkdir();plan=dict(old)
plan['previous_overlay_paths']=[old['remote_root']+'/overlay',*old['previous_overlay_paths']]
plan['remote_root']=old['remote_root'].rsplit('/',1)[0]+'/episode_reset04'
plan['run_id']='newton_episode_reset04_'+str(time.time_ns())
plan['cumulative_authorized_seconds_before_this_segment']+=f['OWNER_EXIT.json']['actual_elapsed_seconds']
digest=hashlib.sha256(old['remote_root'].encode()).hexdigest()[:12]
plan['warp_cache_reference']='/tmp/mod4n_'+digest+'/cache/warp'
plan['specific_repair']='Apply existing per-environment numerical episode reset before sensor corruption; clear MuJoCo warmstart and both buffers; count every actual reset'
plan.pop('GPU_UUID',None)
(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
files=[]
for path,rel in [(CODE/'newton_env.py','overlay/newton_env.py'),(CODE/'newton_train.py','overlay/newton_train.py'),
                 (N/'newton_entry.py','entry.py'),(N/'newton_owner.py','owner.py'),(P.parent/'run-newton.sh','run-newton.sh')]:
 raw=path.read_bytes();files.append(dict(path=str(path),relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(A/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,shared_text=read(P/'SOURCE_PREPARED.json')['shared_text'],
    original_failed_attempts_preserved=True,only_changed_source=True,old_kernel_cache_referenced=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(A),files=len(files))))
