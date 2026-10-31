"""New source namespace only; preserve the rejected-unused C bytes and index."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback

N=Path(__file__).resolve().parent
P=N.parent
C=P/'C_ROOT_CALLERS_SOURCE'
A=P/'A_PPO_SOURCE'
OLD=P.parent/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101'
GLOBAL='/home/lc01/Zonglin Li/zonglin2'


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,b):
 with p.open('xb') as f:f.write(b)
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)


def main():
 purpose=json.loads((N/'reports/DERIVE227D_PURPOSE_FROZEN.json').read_bytes())
 for r in purpose['inputs']:assert ref(Path(r['path']))==r
 assert ref(C/'INDEX227C_FROZEN.json')['SHA']=='b357231567885b2df36d7ac1d506a4897f419d9d1f7d8dd78726499466b9419f'
 receipts=[]
 for name,key in [('ROOT219V3_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json','owner'),('ROOT219V3_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json','node')]:
  path=OLD/'reports'/name;value=json.loads(path.read_bytes());x=value[key]
  assert x['cwd']==GLOBAL and x['role']==key and x['root']!=x['cwd']
  receipts.append(dict(report=ref(path),run_id=value['run_id'],role=key,selected_receipt={k:x[k] for k in ('pid','creation','exe','argv','cwd','root','role')}))
 def literal_payload(path):
  return {n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.Assign)}
 old=literal_payload(OLD/'source/remote219_payloads.py')
 payload=literal_payload(C/'remote227C_payloads.py')
 assert payload['SPAWN']=="import os\nos.chdir(v['root'])\n"+old['SPAWN']
 payload['SPAWN']="from pathlib import Path\nassert v['expected_control_cwd']=='"+GLOBAL+"'\nassert Path.cwd().resolve()==Path(v['expected_control_cwd']).resolve()\n"+old['SPAWN']
 write(N/'remote227D_payloads.py',('"""ROOT-only227D source; original219V3 SPAWN inherits actual global cwd."""\n'+\
      '\n\n'.join(k+' = '+repr(v) for k,v in payload.items())+'\n').encode())
 additions=(C/'remote227C_additions.py').read_text(encoding='utf8')
 additions=once(additions,'private_EX_probe_free=True,shared_EX_probe_free=True,',
   "private_EX_probe_free=True,shared_EX_probe_free=True,admission_probe_only=True,admission_probe_locks_released_before_return=True,execution_lock_handoff='Original node holds selectedGPU private EX before READY;original owner holds two shared EX before GO',")
 write(N/'remote227D_additions.py',additions.encode())
 names=['launch227C_install_original_solo_W35_FIRST_UNUSED_once.py',
        'collect227C_original_W35_formal_cost_normal900_UNUSED_once.py',
        'review227C_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py']
 for name in names:
  text=(C/name).read_text(encoding='utf8').replace('227C','227D')
  if name.startswith('launch'):
   text=once(text,"R=N/'reports'","R=N/'reports'\nCONTROL_CWD='/home/lc01/Zonglin Li/zonglin2'")
   text=once(text,"console='owner_CONSOLE.log',role='owner',config=cfg)","console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=CONTROL_CWD)")
   text=once(text,"console='node_CONSOLE.log',role='node',config=private_spec)","console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd=CONTROL_CWD)")
   text=once(text,"  put('ROOT227D_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json'", "  assert owner['cwd']==CONTROL_CWD and owner['root']==O\n  put('ROOT227D_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json'")
   text=once(text,"  put('ROOT227D_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json'", "  assert node['cwd']==CONTROL_CWD and node['root']==J+'/control227'\n  put('ROOT227D_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json'")
   text=once(text,"  authority=d.code(client,d.PY72,target.AUTH,{},timeout=45)","  assert resource['admission_probe_only'] and resource['admission_probe_locks_released_before_return']\n  authority=d.code(client,d.PY72,target.AUTH,{},timeout=45)")
  write(N/name.replace('227C','227D'),text.encode())
 controls=json.loads((C/'reports/CONTROL227C_A_FROZEN_BINDINGS.json').read_bytes())
 put(N/'reports/CONTROL227D_A_FROZEN_BINDINGS.json',controls)
 put(N/'reports/BEFORE_USE227D_ORIGINAL_C_CWD_REJECT_AND_REPAIR.json',dict(epoch=time.time(),
  status='C_UNUSED_BEFORE_USE_REFUSAL_PRESERVED_NEW_D_SOURCE_ONLY',C_INDEX=ref(C/'INDEX227C_FROZEN.json'),
  old_C_incorrect_change="SPAWN prefix os.chdir(v['root']) chose owner72/node control cwd",
  original_AST_pass_scope='Syntax/interface-only;did not establish global owner cwd conformance',
  old_C_executed=False,original_actual219V3_selected_receipts=receipts,
  correction='Original219V3 SPAWN byte body retained;before-fork inherited cwd assert from actual receipts;never chdir(taskroot)',
  exact_global_owner_and_actual_node_cwd=GLOBAL,
  node_module_root='J/control227',owner_module_root='O',original_worker_Popen_cwd='J',
  source_or_index_C_overwritten=False,physical_reward_guard_270_changes=0))
 owner=(A/'control227/solo227_finite_owner_authority72.py').read_text(encoding='utf8')
 node=(A/'control227/solo227_fullstate_slot_node.py').read_text(encoding='utf8')
 assert "for path in b.LOCKS" in owner and 'fcntl.LOCK_EX|fcntl.LOCK_NB' in owner
 assert node.index('lock=Path(spec["private_lock"])')<node.index('phase="ready"')<node.index('subprocess.Popen(args,cwd=J')
 put(N/'reports/JOIN227D_SOURCE_CONTRACT_REVIEW.json',dict(
  status='SOURCE_REVIEW_ONLY_ACTUAL_ADMISSION_PENDING',
  owner_cfg='role=owner;new run_id/token;onlyw35_72;original scheduling authority/HMAC/accounting;no active owner hotadd',
  spec='A generated w35_72,target72,c27,20000env,source343e/32404/649720/LR.00017085937500000009;new manifest and Ready;worker227.py',
  job='J=new root/w35_72;O=new root/owner72;control module root J/control227;control cwd global for both;worker cwd J',
  source_install='A INSTALL sources/runtime/assets only;343e path constant outsideJ;no source PT stat/hash/copy/open/decode in installer',
  fresh_probe='Temporary selected private and shared availability EX probes explicitly unlock/close before return;not a held production lease',
  execution_handoff='Original node acquires and holds selected private EX before READY;original owner acquires/holds its two shared locks before original GO;finally release/wait/terminalACK unchanged',
  source_production_read='Only pinned worker one physical byte/hash and one decode;logical original full restores cached;source unchanged',
  controls=[ref(A/'control227/solo227_finite_owner_authority72.py'),ref(A/'control227/solo227_fullstate_slot_node.py')],
  no_guard_reward_physics_270_or_budget_change=True,actual_GO_model_SDK_network_calls=0))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/DERIVE227D_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
