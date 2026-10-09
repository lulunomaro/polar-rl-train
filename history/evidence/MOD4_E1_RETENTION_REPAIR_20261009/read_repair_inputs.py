"""Read repair inputs and natural closeout; no GPU, queue or budget writes."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_REVIEWED_STABLE_20261009'
CENTRAL='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,('Keep earlier evidence',str(p))
 else:p.write_bytes(b)
def main():
 assert not (R/'INPUTS.json').exists()
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret
 c=connect();index=[]
 try:
  with c.open_sftp() as sf:
   def get(source,target):
    b=sf.open(source).read();save(R/target,b)
    index.append(dict(source=source,local=target,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    return b
   for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.json'):
    get(CENTRAL+'/'+n,'central/'+n)
   f=json.loads(get(ROOT+'/reports/SOURCE_FREEZE.json','predecessor/SOURCE_FREEZE.json'))['sha256'];assert len(f)==313
   names=('e1_rough_recipe.py','e1_terrain_runtime.py','e1_terrain_training_env.py','e1_terrain_checkpoint.py','e1_terrain_state.py','e1_full_pose_reset.py','e1_scene_query_resource.py','e1_reset_evidence_training_env.py','train_e1_resource_fresh_preflight_ppo.py','train_e1_route_health_resume_ppo.py','e1_chunked_terrain.py','e1_rough_ground.py')
   for n in names:
    b=get(ROOT+'/isaac/mod4/'+n,'source/'+n);assert hashlib.sha256(b).hexdigest()==f['isaac/mod4/'+n]
   for n in ('E1_STATE.json','E1_REVIEW_READY.json','E1_GUARDIAN_STARTED.json','e1_gentle_stable_block2_PASSED.json','e1_gentle_stable_block2_SAVED_EXIT.json','E1_116-e1-gentle-b2_ASYNC_PUBLISHED.json','E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json'):
    get(ROOT+'/reports/'+n,'predecessor/'+n)
  code="""from pathlib import Path
import json,os,time
D=Path(ROOT);j=lambda p:json.loads(p.read_text());s=j(D/'reports/E1_STATE.json');g=j(D/'reports/E1_GUARDIAN_STARTED.json');p=j(D/'reports/e1_gentle_stable_block2_PASSED.json')
def actual(pid):
 q=Path('/proc')/str(pid)
 if not q.exists():return None
 try:return dict(pid=pid,stat=(q/'stat').read_text(),argv=(q/'cmdline').read_bytes().decode().split('\\0'),cwd=os.readlink(q/'cwd'))
 except OSError:return None
b=j(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
assert s['child'] is None and s['phase']=='E1_gentle_stable_saved_review_ready' and b['active_segment'] is None
identities={str(pid):actual(pid) for pid in (s['owner']['pid'],g['pid'],p['own_PID_bound_receipt']['pid'])}
assert all(v is None or v['stat'].split(') ',1)[1].split()[0]=='Z' for v in identities.values())
print(json.dumps(dict(epoch=time.time(),identities=identities,phase=s['phase'],active_segment=None,block2_unique_segments=[x for x in b['completed_segments'] if x['pid']==p['own_PID_bound_receipt']['pid']],canonical_authorized_seconds=b['authorized_training_seconds'],remaining_seconds=b['authorized_training_seconds']-b['charged_training_seconds'],read_only=True)))
""".replace('ROOT',repr(ROOT))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
  proof=json.loads(raw);assert len(proof['block2_unique_segments'])==1
  save(R/'NATURAL_BOUNDARY.json',json.dumps(proof,indent=2).encode())
  save(R/'INPUTS.json',json.dumps(dict(epoch=time.time(),files=index,source313_exact=True,no_GPU_PPO_queue_or_budget_write=True),indent=2).encode())
  print(json.dumps(proof,ensure_ascii=True))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save(R/'INPUT_01_ERROR.json',json.dumps(dict(epoch=time.time(),trial_id='E1-REPAIR-INPUT-01',error=traceback.format_exc(),no_training_change=True),indent=2).encode());raise
