"""Previously unread failed21 three valid controls for its one actual boundary-miss environment."""
from pathlib import Path
import json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;N=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022';R=B/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,time,numpy as np
q=v['q'];root=Path(q['roots']['h1']);owner=Path(q['owner_root']);base=root/'job0/production/control_prefix_raw'
assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(a.startswith((str(root)+'/',str(owner)+'/')) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
idx=json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());row=idx['index'][72];assert row['controls']==3
p=Path(row['path']);s=p.stat();assert s.st_size==row['bytes'] and not p.is_symlink() and s.st_nlink==1
with np.load(p,allow_pickle=False) as z:
 data={k:z[k][:,11843].tolist() for k in ('root13','q30','done','episode','closure')}
assert np.isfinite(data['root13']).all() and np.isfinite(data['q30']).all()
print(json.dumps(dict(epoch=time.time(),source=dict(row,inode=s.st_ino,mtime_ns=s.st_mtime_ns,SHA_scope='Original producer SHA; selected NPZ arrays ZIP integrity, not new whole-file SHA'),env_id=11843,complete_control_numbers=[1729,1730,1731],selected_state=data,no_raw_download_or_new_hash_actor_optimizer_RNG_GPU_or_simulation=True)))
'''
try:
 proof=json.loads((R/'V110_FAILED21_DIAGNOSTIC_PREFIX_TWOHOST_SHA_AND_ALL_OUT_ACTUAL.json').read_bytes());assert proof['all_own_out'] and proof['canonical_none']
 q=json.loads((N/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());c=d.t.connect()
 try:r=d.code(c,d.t.PY,CODE,dict(q=q),timeout=120)
 finally:c.close()
 put('V110_ACTUAL_PRE_FAILURE_THREE_CONTROL_STATE_CPU_ACTUAL.json',r);print(json.dumps(r))
except BaseException:put('V110_PRE_FAILURE_STATE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
