"""Read approved central plan, RM revisions and own G3 final review context."""
from pathlib import Path
import os,sys,json,time,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
NAMES=('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','MOD4_MOE_MASTER_PLAN.md','E1_G3_FORMAL_FINAL_ACTUAL_REVIEW.json','E1_G3_OWN_FORMAL_CPU_SOURCE_VERIFIED.json','E1_G3_FORMAL_FINAL_CURRENT_ACTUAL.json','E1_G3_127_CANDIDATE_CURRENT_COLLECTION.json','E1_G3_FORMAL_CLOSEOUT_METADATA_SYNCED.json','MOD4_RM_TERRAIN_TRAINING_REVISION.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.md','NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.json','NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.md','NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.json','RM_TERRAIN_CURRICULUM_METADATA_SYNCED.json','RM_CURB_CLARIFICATION_METADATA_SYNCED.json')

def main():
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect();files={}
 try:
  with c.open_sftp() as f:
   for n in NAMES:
    try:b=f.open(ROOT+'/'+n).read()
    except FileNotFoundError:files[n]=dict(expected_context_missing_at_read=True);continue
    files[n]=dict(source=ROOT+'/'+n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),content=json.loads(b) if n.endswith('.json') else b.decode('utf8'))
  assert files['MOD4_MOE_MASTER_PLAN.md']['sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
  v=dict(epoch=time.time(),trial_id='E1-G3-127-MATCHED-CENTRAL-CONTEXT-READ-01',files=files,read_only=True,no_PPO_or_budget_or_queue_mutation=True,cached127_pending_not_actual_final_result=True)
  p=R/('CENTRAL_CONTEXT_ACTUAL_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
  print(json.dumps(dict(report=str(p),master_SHA_verified=True,read_files=len(files),missing=[n for n,x in files.items() if x.get('expected_context_missing_at_read')],no_mutation=True)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':main()
