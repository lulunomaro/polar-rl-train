"""New D AST/source contract check only, never imports lifecycle callers."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback

N=Path(__file__).resolve().parent


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 purpose=json.loads((N/'reports/CPU227D_PURPOSE_FROZEN.json').read_bytes())
 put(N/'reports/CPU227D_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=purpose['ID']))
 trees={};texts={}
 for r in purpose['sources']:
  b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']
  trees[Path(r['path']).name]=ast.parse(b);texts[Path(r['path']).name]=b.decode()
 count=0;payload={}
 for name in ('remote227D_payloads.py','remote227D_additions.py'):
  payload[name]={}
  for n in trees[name].body:
   if isinstance(n,ast.Assign):
    code=ast.literal_eval(n.value);ast.parse(code);payload[name][n.targets[0].id]=code;count+=1
 normal=trees['collect227D_original_W35_formal_cost_normal900_UNUSED_once.py']
 for n in ast.walk(normal):
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('COLLECT_NODE','code') for t in n.targets) and isinstance(n.value,ast.Constant):
   ast.parse(n.value.value);count+=1
 spawn=payload['remote227D_payloads.py']['SPAWN']
 assert 'os.chdir(' not in spawn and "Path.cwd().resolve()==Path(v['expected_control_cwd']).resolve()" in spawn
 assert spawn.index('Path.cwd().resolve()')<spawn.index('pid=os.fork()')
 assert "v['expected_control_cwd']=='/home/lc01/Zonglin Li/zonglin2'" in spawn
 launcher=texts['launch227D_install_original_solo_W35_FIRST_UNUSED_once.py']
 for name in ('launch227D_install_original_solo_W35_FIRST_UNUSED_once.py','collect227D_original_W35_formal_cost_normal900_UNUSED_once.py','review227D_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py'):
  assert '227C' not in texts[name] and 'INDEX227D_FROZEN.json' in texts[name]
 assert 'ROOT227D_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json' in texts['collect227D_original_W35_formal_cost_normal900_UNUSED_once.py']
 assert 'ROOT227D_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json' in texts['review227D_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py']
 assert launcher.count('expected_control_cwd=CONTROL_CWD')==2
 assert "owner['cwd']==CONTROL_CWD and owner['root']==O" in launcher
 assert "node['cwd']==CONTROL_CWD and node['root']==J+'/control227'" in launcher
 assert "sf.file(remote,'wx')" in launcher and 'target.POSTCOPY_NO_MODEL' in launcher
 assert 'admission_probe_locks_released_before_return' in launcher
 resource=payload['remote227D_additions.py']['RESOURCE']
 assert 'fcntl.LOCK_UN' in resource and 'admission_probe_only=True' in resource and 'admission_probe_locks_released_before_return=True' in resource
 assert "v['source']" not in payload['remote227D_payloads.py']['POSTCOPY_NO_MODEL']
 assert 'time.time()+850' in payload['remote227D_payloads.py']['FIRST'] and '649740' in payload['remote227D_payloads.py']['FIRST']
 normal_text=texts['collect227D_original_W35_formal_cost_normal900_UNUSED_once.py']
 assert 'nominal-time.time()<=900' in normal_text and 'end=time.time()+850' in normal_text and 'end=time.time()+180' in normal_text
 assert 'rawsum=sum(fees.values())' in normal_text
 cpu=texts['review227D_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py']
 assert '649720+20*updates' in cpu and "ck['iter']==32404+updates" in cpu and 'weights_only=False' in cpu
 put(N/'reports/CPU227D_SOURCE_AST_INTERFACE_ACTUAL.json',dict(passed=True,ID=purpose['ID'],
  source_AST_count=len(trees),embedded_remote_AST_count=count,cwd_conformance='Source guards bound to original219V3 actual owner+node receipts;actual D runtime still pending',
  source_A_B_C_and_indices_unchanged=True,old_fixtures_replayed=0,
  temporary_probe_held_as_production_lease=False,original_node_private_and_owner_shared_handoff_preserved=True,
  physical_reward_guard_270_changes=0,PT_NPZ_USD_actualraw_Torch_SDK_GPU_SSH_Git_calls=0,
  actual_admission_GO_FIRST_normal_NEWformalCPU='PENDING_ROOT_ONLY'))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/CPU227D_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
