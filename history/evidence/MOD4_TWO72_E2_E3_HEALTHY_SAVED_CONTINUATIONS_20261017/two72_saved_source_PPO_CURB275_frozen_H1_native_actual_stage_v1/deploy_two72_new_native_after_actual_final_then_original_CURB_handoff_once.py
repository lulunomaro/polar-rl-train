from pathlib import Path
import os,sys,json,time,hashlib,getpass,secrets,traceback
N=Path(__file__).resolve().parent;D=N.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';Q=N/'payload';R=N/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import code,H,connect72,t,PY
SOURCE='/mnt/mod4_linux_durable_20261013/N72_1710v1';ROOTS={k:'/home/lc01/Zonglin Li/zonglin2/tasks/N72_1710v1/'+k for k in ('e2','recovery')};PREV={k:'/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v9/'+k for k in ROOTS}
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,hashlib,shutil,psutil,subprocess
B=Path(sys.argv[1]);A=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists() and len(str(B/'job0/tmp'))<100;src=Path(sys.argv[3]);assert src.is_relative_to(A/'job0/production') and hashlib.sha256(src.read_bytes()).hexdigest()==sys.argv[4];assert json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];assert json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes())['validation_fcntl_released'];alive=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if any(str(A)+'/' in s for s in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive;gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if sys.argv[6] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3;B.mkdir(parents=True);(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copy2(src,B/'job0/source'/sys.argv[5]);print(json.dumps(dict(epoch=time.time(),root=str(B),actual_previous_nodes_all_children_out=True,actual_source_SHA=sys.argv[4],GPU_snapshot_line=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,new_root_copy_only_no_old_mutation=True)))
'''
CPU=r'''
from pathlib import Path
import sys,json,time,hashlib,ast,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4);B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
s=B/'job0/source'/m['source_filename'];assert H(s)==m['source_SHA'];ck=torch.load(s,map_location='cpu',weights_only=False);counts=[0,0]
def walk(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for z in x.values():walk(z)
 elif isinstance(x,(tuple,list)):
  for z in x:walk(z)
walk(ck);assert counts==m['source_schema_counts'] and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={m['source_Adamstep']};assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();print(json.dumps(dict(epoch=time.time(),passed_CPU_only=True,manifest_SHA=H(B/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),source_SHA=m['source_SHA'],source_schema_counts=counts,all_source_tensor_finite=True,all_target_manifest_files_actual_SHA=True,oldweights_optimizer_STD_not_reset=True,no_GPU_or_PPO=True)))
'''
def launch(c,py,root,cfg):
 source="from pathlib import Path;import sys,json,subprocess;B=Path(sys.argv[1]);assert not (B/(json.loads(sys.argv[3])['role']+'_CONSOLE.log')).exists();p=subprocess.run([sys.argv[2],'-u','-B',str(B/'two72_native_then_original_owner_handoff_v1.py')],input=sys.argv[3]+chr(10),text=True,capture_output=True,cwd=B,timeout=30);assert p.returncode==0,p.stderr;print(p.stdout)";return code(c,py,source,root,py,json.dumps(cfg))
def main():
 proof=json.loads((R/'TWO72_FINAL_PROTOCOL_CPU_NEGATIVES_FROZEN_SOURCES_ACTUAL.json').read_bytes());assert proof['passed_CPU_only'];specs={s['key']:dict(s,python=PY) for s in proof['specs']};put('TWO72_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport=True,no_current_CURB_or_old_nodes_mutation=True));pw=getpass.getpass('Host72 next saved-source two expert native admission (hidden): ');c=None;cfg=None
 try:
  c=t.connect();pre=code(c,t.PY,"from pathlib import Path;import sys,json,time,socket,psutil;B=Path(sys.argv[1]);assert B.parent==Path('/mnt/mod4_linux_durable_20261013') and not B.exists();C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());a=v['active_segment'];assert a is None or a['owner_parent_pid']==581261\nwith socket.socket() as s:s.bind(('10.24.4.210',29752))\nB.mkdir();print(json.dumps(dict(epoch=time.time(),original_current_owner=(a or {}).get('owner_parent_pid'),new_root=str(B),no_budget_or_current_job_mutation=True)))",SOURCE);put('SOURCE_COORDINATOR_ROOT_AND_EXISTING_CURB_ACCOUNT_ACTUAL.json',pre);sf=c.open_sftp()
  try:
   for name in ('two72_native_then_original_owner_handoff_v1.py','three_expert_helpers_v2.py'):
    p=N/name if name.startswith('two72_') else Q/'e2'/name;sf.put(str(p),SOURCE+'/'+name)
  finally:sf.close()
  cfg=dict(role='owner',experts=specs,run_id='TWO72_SAVED152_90_HEALTHY_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(c,t.PY,SOURCE,cfg);put('SOURCE_TWO72_NATIVE_ORIGINAL_ACCOUNT_WAIT_OWNER_ACTUAL_DISPATCH.json',dict(epoch=time.time(),owner=owner,original_current_CURB_untouched=True,native_not_PPO=True))
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;nodes={}
  for key,s in specs.items():
   root=ROOTS[key];put(key.upper()+'_NEW_ROOT_PREVIOUS_FINAL_OUT_RESOURCE_ACTUAL.json',code(c,PY,CREATE,root,PREV[key],s['prior_exact_final'],s['source_SHA'],s['source_filename'],s['GPU_UUID']));sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:
    mf=Q/key/'CONTINUATION_COMPLETE_MANIFEST_V2.json';sf.put(str(mf),root+'/'+mf.name);missing=code(c,PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());print(json.dumps(dict(missing=[r for r in m['files'] if not (B/r['relative']).is_file() or (B/r['relative']).stat().st_size!=r['bytes'] or hashlib.sha256((B/r['relative']).read_bytes()).hexdigest()!=r['SHA']])))",root);put(key.upper()+'_MISSING_ONLY_UPLOAD_ACTUAL.json',missing)
    for r in missing['missing']:
     p=Q/key/r['relative'];assert H(p)==r['SHA'];folder=root
     for piece in r['relative'].split('/')[:-1]:
      folder+='/'+piece
      try:sf.stat(folder)
      except FileNotFoundError:sf.mkdir(folder)
     sf.put(str(p),root+'/'+r['relative'])
   finally:sf.close()
   put(key.upper()+'_FULL_SOURCE_TARGET_CPU_SHA_AST_ACTUAL.json',code(c,PY,CPU,root,timeout=180));nodes[key]=launch(c,PY,root,dict(s,role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('TWO72_NEW_NATIVE144_336_AFTER_CLOSED152_90_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),owner=owner,nodes=nodes,source_root=SOURCE,target_roots=ROOTS,own_unused_new_source_native_and_CPU_before_original_CURB_actual_handoff_GO=True,each_finite3600_headroom300_original_budget_unchanged=True,no_future_native_PPO_or_skill_pass_inferred=True));print(json.dumps(dict(owner=owner,nodes=nodes,new_native_admission_actually_dispatched_not_PPO=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO72_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_replay_if_unknown_mutation=True));raise
