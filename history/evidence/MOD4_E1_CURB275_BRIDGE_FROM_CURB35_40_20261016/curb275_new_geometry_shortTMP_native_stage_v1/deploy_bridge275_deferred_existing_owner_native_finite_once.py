from pathlib import Path
import os,sys,json,time,hashlib,ast,traceback,shutil
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';Q=P/'payload';R=P/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import code,H,t,ROOTS
COORD=ROOTS['curb'];CASE=COORD+'/curb275_bridge_case_v1'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,psutil,hashlib,shutil,subprocess
A=Path(sys.argv[1]);B=Path(sys.argv[2]);assert B.parent==A and B.name=='curb275_bridge_case_v1' and not B.exists() and A.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013'));v=json.loads((A/'OWNER_CURRENT.json').read_bytes());id=json.loads((A/'OWNER_IDENTITY.json').read_bytes());p=psutil.Process(id['pid']);assert p.create_time()==id['creation'] and p.cmdline()==id['argv'];assert v['rows']['curb']['phase']=='waiting_reviewed_CURB_case' and not v['stop'] and 'curb' not in v['go'];assert time.time()-id['creation']<1800;assert not (A/'CURB_REPAIR_CASE_READY.json').exists();gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();assert int(next(x for x in gpu.splitlines() if sys.argv[3] in x).split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3
B.mkdir();(B/'job0').mkdir()
for n in ('runtime','source','assets'):shutil.copytree(A/'job0'/n,B/'job0'/n)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');print(json.dumps(dict(epoch=time.time(),case=str(B),actual_existing_owner_identity=id,actual_owner_current_epoch=v['epoch'],curb_no_grant_no_worker_before_new_case=True,only_new_case_copy_no_livefile_changes=True)))
'''
CPU=r'''
from pathlib import Path
import sys,json,time,ast,hashlib,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
ck=torch.load(B/'job0/source'/m['source_filename'],map_location='cpu',weights_only=False);assert H(B/'job0/source'/m['source_filename'])==m['source_SHA'];assert ck['E1_terrain_state']['CURB_height_m']==.035 and len(ck['optimizer_state_dict']['state'])==17 and {int(s['step']) for s in ck['optimizer_state_dict']['state'].values()}=={672200};counts=[0,0]
def walk(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():walk(v)
 elif isinstance(x,(list,tuple)):
  for v in x:walk(v)
walk(ck);assert counts==[181,102];rt=B/'job0/runtime/isaac/mod4';sys.path.insert(0,str(rt));from e1_terrain_state import validate as validate_base
tree=ast.parse((rt/'curb35_checkpoint.py').read_text('utf8'));functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('validate','validate_source35')];ns=dict(PROFILE='mod4_CURB_derived27p5mm_strip150_mirrored_entryreset_v1',validate_base=validate_base);exec(compile(ast.Module(body=functions,type_ignores=[]),'<actual_source_and_target_state>','exec'),ns);ns['validate_source35'](ck['E1_terrain_state'],20000);ns['validate'](dict(ck['E1_terrain_state'],profile=ns['PROFILE'],CURB_height_m=.0275,CURB_profile_sha256=H(rt/'curb35_profile.json')),20000);assert not torch.cuda.is_initialized() and torch.equal(rng,torch.get_rng_state());out=dict(epoch=time.time(),passed_CPU_only=True,source_SHA=m['source_SHA'],manifest_SHA=H(B/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),full_source_all_tensor_finite=True,all_target_manifest_files_actual_SHA=True,source_schema_counts=counts,no_GPU_or_PPO=True,original_source35_new27p5_separate_state_validation=True,own_new_native144_and_CPU_required_before_original_accounted_GO=True)
p=B/'TARGET_CPU_SOURCE_ADMISSION_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2));print(json.dumps(dict(**out,receipt_SHA=H(p))))
'''
PUBLISH=r'''
from pathlib import Path
import sys,json,time,hashlib,psutil
A=Path(sys.argv[1]);B=Path(sys.argv[2]);s=json.loads(sys.argv[3]);cpu=json.loads((B/'TARGET_CPU_SOURCE_ADMISSION_ACTUAL.json').read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();v=json.loads((A/'OWNER_CURRENT.json').read_bytes());ident=json.loads((A/'OWNER_IDENTITY.json').read_bytes());p=psutil.Process(ident['pid']);assert p.create_time()==ident['creation'];assert v['rows']['curb']['phase']=='waiting_reviewed_CURB_case' and not v['stop'] and time.time()-ident['creation']<1800
names=('three_expert_finite_owner_node_v9.py','three_expert_helpers_v2.py','native_CPU_status_bridge_v1.py','deferred_CURB_case_admission_v1.py');rows=[dict(relative=n,SHA=H(A/n)) for n in names];ready=dict(epoch=time.time(),case_root=str(B),spec=s,target_CPU_receipt_SHA=H(B/'TARGET_CPU_SOURCE_ADMISSION_ACTUAL.json'),existing_master_repair_axis_explicit=True,original_global_budget_unchanged=True,original_live_control_files=rows,scope='Only27.5mm intermediate height inside original20to35; no reward/command/DR/physics change',no_native_or_PPO_pass_inferred=True);path=A/'CURB_REPAIR_CASE_READY.json';assert not path.exists();path.write_text(json.dumps(ready,indent=2));print(json.dumps(dict(epoch=time.time(),ready=ready,ready_SHA=H(path),new_finite_case_published_not_native_or_PPO_pass=True)))
'''
def main():
 proof=json.loads((R/'BRIDGE27P5_GEOMETRY_FULL_SOURCE_DIFF_CPU_PREPARED_ACTUAL_V2.json').read_bytes());assert proof['passed_CPU_only'];p=Q/'production_worker.py';old=p.read_text('utf8');folder=P/'original_prepared_V2';folder.mkdir();shutil.copy2(p,folder/p.name);oldmf=Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json';shutil.copy2(oldmf,folder/oldmf.name);needle="go=json.loads((B/'GO_PRODUCTION_ACTUAL.json').read_bytes())";assert old.count(needle)==1;new=old.replace(needle,"assert B.name=='curb275_bridge_case_v1' and B.parent.name=='curb';go=json.loads((B.parent/'GO_PRODUCTION_ACTUAL.json').read_bytes())");ast.parse(new);p.write_text(new,encoding='utf8');m=json.loads(oldmf.read_bytes())
 for r in m['files']:
  q=Q/r['relative'];r.update(bytes=q.stat().st_size,SHA=H(q))
 oldmf.write_text(json.dumps(m,indent=2),encoding='utf8');spec=dict(proof['spec'],manifest_SHA=H(oldmf),root=CASE,python=t.PY);put('V3_CASE_PRODUCTION_READS_ACTUAL_COORDINATOR_GO_SOURCE_REVIEWED_CPU.json',dict(epoch=time.time(),old_production_source=str(folder/p.name),new_production_SHA=H(p),original_parent_creates_actual_GO_in_coordinator_root=True,new_case_reads_original_actual_GO_no_copy_or_fabrication=True,source_SHA_cap_exit_headroom_checks_original_exact=True,manifest_SHA=H(oldmf),spec=spec))
 put('BRIDGE275_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,new_case_no_second_coordinator_or_hotpatch=True));c=None
 try:
  c=t.connect();put('BRIDGE275_TARGET_NEW_ROOT_COPY_RESOURCE_ACTUAL.json',code(c,t.PY,CREATE,COORD,CASE,spec['GPU_UUID']));sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   sf.put(str(oldmf),CASE+'/CONTINUATION_COMPLETE_MANIFEST_V2.json');missing=code(c,t.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());print(json.dumps(dict(missing=[r for r in m['files'] if not (B/r['relative']).is_file() or (B/r['relative']).stat().st_size!=r['bytes'] or hashlib.sha256((B/r['relative']).read_bytes()).hexdigest()!=r['SHA']])))",CASE);put('BRIDGE275_MISSING_ONLY_UPLOAD_ACTUAL.json',missing)
   for r in missing['missing']:
    folder=CASE
    for piece in r['relative'].split('/')[:-1]:
     folder+='/'+piece
     try:sf.stat(folder)
     except FileNotFoundError:sf.mkdir(folder)
    sf.put(str(Q/r['relative']),CASE+'/'+r['relative'])
  finally:sf.close()
  put('BRIDGE275_ALL_TARGET_CPU_SOURCE_MANIFEST_ACTUAL.json',code(c,t.PY,CPU,CASE,timeout=180));put('BRIDGE275_EXISTING_OWNER_NEW_CASE_READY_ACTUAL.json',code(c,t.PY,PUBLISH,COORD,CASE,json.dumps(spec)));print(json.dumps(dict(new_case_ready_for_own_native=True,root=CASE,source_SHA=spec['source_SHA'],no_PPO_pass_inferred=True)),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('BRIDGE275_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_replay=True));raise
