"""Fill the restored210 GPU with its required original fullstate native while H1 learns."""
from pathlib import Path
import os,sys,json,time,traceback,hashlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';S=W/'MOD4_THREE_GPU_UTILIZATION_STORAGE_RECOVERY_20261018';sys.path.insert(0,str(S));import deploy_two_idle_4090_linux_reward_frame_observations_once as d
a=d.a;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();TARGET='/mnt/mod4_linux_durable_20261013/T3h_1810v1/e2'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
INSTALL=r'''
from pathlib import Path
import sys,json,hashlib,zipfile,ast,os,time,importlib.util
B=Path(sys.argv[1]);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert H(B/'payload.zip')==sys.argv[2]
with zipfile.ZipFile(B/'payload.zip') as z:
 for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts and (B/n).resolve().is_relative_to(B.resolve())
 z.extractall(B)
m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==sys.argv[3]
for row in m['files']:
 p=B/row['relative'];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
os.environ['CUDA_VISIBLE_DEVICES']='';import torch
ck=torch.load(B/'job0/source/E2_final58.pt',map_location='cpu',weights_only=False);assert ck['owned_phase_complete_updates']==112 and {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={666780};counts=[0,0]
def finite(x):
 if torch.is_tensor(x):
  counts[0]+=1
  if x.is_floating_point():counts[1]+=1;assert torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(list,tuple)):
  for v in x:finite(v)
finite(ck);assert counts==m['source_schema_counts'] and not torch.cuda.is_initialized();root=Path(importlib.util.find_spec('rsl_rl').submodule_search_locations[0]);rsl=[]
for row in m['expected_actual_RSL_sources']:
 p=root/row['relative'];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];rsl.append(dict(path=str(p),SHA=H(p)))
sdk=Path(importlib.util.find_spec('isaaclab').submodule_search_locations[0])/'utils/math.py';assert H(sdk)==m['expected_actual_SDK_math_SHA'];print(json.dumps(dict(epoch=time.time(),passed=True,full_source_counts=counts,source_Adam666780=True,source_SHA=m['source_SHA'],RSL_files=rsl,SDK_math=dict(path=str(sdk),SHA=H(sdk)),no_GPU_or_optimizer=True)))
'''
def main():
 prep=json.loads((R/'E2_SOURCE210_EXISTING_FULLSTATE_ONE_HOUR_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());put('E2_210_NATIVE_THREE_LEARNING_HANDOFF_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_transport=True,latest_human_requires_all_three_actual_training=True));c=None
 try:
  c=a.t.connect();out=a.code(c,a.t.PY,"from pathlib import Path;import json,psutil,os;P=Path('/mnt/mod4_linux_durable_20261013/T3h_1810v1');P.mkdir(exist_ok=True);A=Path('/mnt/mod4_linux_durable_20261013/H1f7_1810ev1f');e=json.loads((A/'full1500/PARENT_EXIT_RECEIPT.json').read_bytes());assert e['actual_child_returncode']==0 and e['all_actual_own_children_waited'];alive=[p.info for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or [])];assert not alive;print(json.dumps(dict(previous_frozen_actualout=True,static_parent_ready=True)))",timeout=60);put('E2_210_PREVIOUS_FROZEN_OUT_ROOT_PARENT_ACTUAL.json',out)
  cfg=dict(d.S['E2'],root=TARGET);put('E2_210_NATIVE_FRESH_GPU_RAM_D25G_REAL_PRIVATE_FCNTL_ACTUAL.json',a.code(c,a.t.PY,d.codefmt(d.ADMIT,cfg),timeout=60));sf=c.open_sftp()
  try:sf.get_channel().settimeout(120);sf.put(prep['package']['path'],TARGET+'/payload.zip')
  finally:sf.close()
  put('E2_210_NATIVE_TARGET_FULL_SOURCE_ACTUAL_RSL_SDK_CPU.json',a.code(c,a.t.PY,INSTALL,TARGET,prep['package']['SHA'],prep['manifest']['SHA'],timeout=180))
  cfg=dict(root=TARGET,GPU_UUID=d.S['E2']['GPU_UUID'],private_lock=d.S['E2']['actual_existing_private_lock'],python=a.t.PY,source_SHA=prep['source_SHA'],manifest_SHA=prep['manifest']['SHA'])
  from dispatch_new_fe778_frozen210_native120_after_E2_full_out_once import old
  parent=old.d.launch(a.code,c,a.t.PY,TARGET,'fullstate_native_only_finite_parent_v1.py',cfg);put('E2_SOURCE210_NEW_FULLSTATE_NATIVE144_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=TARGET,cfg=cfg,H1_current_production_not_signalled_or_changed=True,no_new_canonical_writer_GO_or_charge=True,native_not_PPO_yet=True));print(json.dumps(dict(E2_new_fullstate_native_dispatched=True,parent=parent,H1_training_untouched=True)),flush=True)
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_210_NATIVE_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_before_any_new_attempt=True));raise
