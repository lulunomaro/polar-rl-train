from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;P=N/'newton_fudan_final620_1h';A=P/'shorttmp02'
read=lambda p:json.loads(Path(p).read_bytes())
old=read(P/'PLAN.json');failure=read(P/'reports/FIRST_ACTUAL_RETURNED.json')['files']
assert failure['OWNER_EXIT.json']['all_own_waited']and failure['OWNER_EXIT.json']['original_leases_released']
assert 'directory for temporary files is too long'in failure['WORKER.log']['text']
A.mkdir(exist_ok=False);(A/'reports').mkdir()
plan=dict(old);plan['remote_root']=old['remote_root']+'/shorttmp02';plan['run_id']='newton_fudan_shorttmp02_'+str(time.time_ns())
plan['previous_overlay_paths']=[old['remote_root']+'/overlay',*old['previous_overlay_paths']]
plan['mjcf_remote']=old['remote_root']+'/model_source.xml'
plan['cumulative_authorized_seconds_before_this_segment']+=failure['OWNER_EXIT.json']['actual_elapsed_seconds']
plan['specific_repair']='NVRTC TMPDIR path length, unique private /tmp/mod4n_SHA prefix'
plan['prior_failed_attempt']=old['remote_root'];plan['asset_copies']=0;plan['whole_tree_copies']=0
plan.pop('GPU_UUID',None)
(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
files=[]
for path,relative in [(N/'newton_entry.py','entry.py'),(N/'newton_owner.py','owner.py'),(P/'run-newton.sh','run-newton.sh')]:
 raw=path.read_bytes();files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(A/'SOURCE_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),files=files,
    shared_text=read(P/'SOURCE_PREPARED.json')['shared_text'],changed_files_only=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(A),specific_repair=plan['specific_repair'])))
