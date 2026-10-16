from pathlib import Path
import sys,os,json,time,hashlib,shutil,ast,traceback
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';R=P/'reports';Q=P/'short_tmp_v2_payload';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import code,H,t,ROOTS
from deploy_bridge275_deferred_existing_owner_native_finite_once import CPU
ROOT='/mnt/mod4_linux_durable_20261013/C275_1610v2';PREV=ROOTS['curb']+'/curb275_bridge_case_v1'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,hashlib,shutil,psutil,subprocess
A=Path(sys.argv[1]);B=Path(sys.argv[2]);assert B.parent==Path('/mnt/mod4_linux_durable_20261013') and B.name=='C275_1610v2' and not B.exists() and len(str(B/'job0/tmp'))<100;error=json.loads((A/'job0/native20k_then_production/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes());assert 'name of directory for temporary files is too long' in error['error'];assert not (A/'job0/native20k_then_production/NATIVE144_COMPLETE.json').exists();wait=json.loads((A/'job0/native_WAITED_EXIT_ACTUAL.json').read_bytes());assert wait['actual_waited'];processes=[]
for p in psutil.process_iter(['pid','cmdline']):
 try:
  if any(str(A)+'/' in s for s in p.info['cmdline'] or []):processes.append(p.info)
 except psutil.Error:pass
assert not processes;gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(s for s in gpu.splitlines() if sys.argv[3] in s);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3;B.mkdir();(B/'job0').mkdir()
for n in ('runtime','source','assets'):shutil.copytree(A/'job0'/n,B/'job0'/n)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');print(json.dumps(dict(epoch=time.time(),root=str(B),old_original_NVRTC_error_retained=True,old_scope_all_processes_actual_out=True,old_native_or_PPO_not_complete=True,new_owned_TMP_path=str(B/'job0/tmp'),actual_GPU_line=line,no_oldroot_or_SDK_or_driver_changes=True)))
'''
def main():
 v=json.loads((R/'BRIDGE275_ACTUAL_NATIVE_OR_PENDING_OWNER_BOUND_COLLECTION.json').read_bytes());assert v['last_wait_actual']['original_error'] and not v['case']['actual_own_processes'];put('SHORT_TMP_V2_ORIGINAL_NATIVE_CONSTRUCTION_ERROR_DISCLOSURE.json',dict(epoch=time.time(),old_native_CPU_and_PPO_pass=False,own_native_constructor_NVRTC_private_TMP_path_too_long=True,new_root=ROOT,only_new_owned_short_directory_not_SDK_driver_or_physics_fix=True,oldworker_exit0_not_success=True,original_error_files=[r for r in v['case']['files'] if 'ORIGINAL_ERROR' in r['path']],current_E2_E3_untouched=True,new_CURB_learning_waits_actual_original_cohort_completion_and_twofcntl_handoff=True,no_new_budget_or_automatic_extra_window=True));shutil.copytree(P/'payload',Q);p=Q/'production_worker.py';s=p.read_text('utf8');needle="assert B.name=='curb275_bridge_case_v1' and B.parent.name=='curb';go=json.loads((B.parent/'GO_PRODUCTION_ACTUAL.json').read_bytes())";assert needle in s;p.write_text(s.replace(needle,"go=json.loads((B/'GO_PRODUCTION_ACTUAL.json').read_bytes())"),encoding='utf8');shutil.copy2(P/'bridge275_native_then_original_lock_handoff_parent_v2.py',Q/'bridge275_native_then_original_lock_handoff_parent_v2.py');m=json.loads((Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());files=[]
 for p in sorted(Q.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 m['files']=files;mf=Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(m,indent=2),encoding='utf8');cfg={k:v for k,v in m.items() if k!='files'};cfg.update(manifest_SHA=H(mf),python=t.PY,root=ROOT,previous_case=PREV);assert len(ROOT+'/job0/tmp')<100 and cfg['max_parent_seconds']==1800;put('SHORT_TMP_V2_CPU_MANIFEST_ORIGINAL_CANONICAL_HANDOFF_PREPARED.json',dict(epoch=time.time(),passed_CPU_static=True,manifest_SHA=H(mf),files=len(files),cfg=cfg,source_and_geometry_reward_DR_assets_byteexact_v1=True,only_owned_TMP_namespace_and_parent_finite_handoff_changed=True,native_and_CPU_required_before_any_accounted_learning=True));put('SHORT_TMP_V2_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True));c=None
 try:
  c=t.connect();put('SHORT_TMP_V2_TARGET_COPY_RESOURCES_ACTUAL.json',code(c,t.PY,CREATE,PREV,ROOT,cfg['GPU_UUID']));sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   sf.put(str(mf),ROOT+'/CONTINUATION_COMPLETE_MANIFEST_V2.json');missing=code(c,t.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());print(json.dumps(dict(missing=[r for r in m['files'] if not (B/r['relative']).is_file() or (B/r['relative']).stat().st_size!=r['bytes'] or hashlib.sha256((B/r['relative']).read_bytes()).hexdigest()!=r['SHA']])))",ROOT);put('SHORT_TMP_V2_MISSING_ONLY_UPLOAD_ACTUAL.json',missing)
   for r in missing['missing']:
    folder=ROOT
    for piece in r['relative'].split('/')[:-1]:
     folder+='/'+piece
     try:sf.stat(folder)
     except FileNotFoundError:sf.mkdir(folder)
    sf.put(str(Q/r['relative']),ROOT+'/'+r['relative'])
  finally:sf.close()
  put('SHORT_TMP_V2_ALL_TARGET_SOURCE_CPU_ACTUAL.json',code(c,t.PY,CPU,ROOT,timeout=180));source="from pathlib import Path;import sys,json,subprocess,os;B=Path(sys.argv[1]);assert not (B/'PARENT_CONSOLE.log').exists();p=subprocess.run([sys.argv[2],'-u','-B',str(B/'bridge275_native_then_original_lock_handoff_parent_v2.py')],input=sys.argv[3]+'\\n',text=True,capture_output=True,cwd=B,timeout=30);assert p.returncode==0,p.stderr;print(p.stdout)";owner=code(c,t.PY,source,ROOT,t.PY,json.dumps(cfg));put('SHORT_TMP_V2_NEW_NATIVE_ONLY_UNTIL_ORIGINAL_LOCK_HANDOFF_ACTUAL_DISPATCH.json',dict(epoch=time.time(),parent=owner,root=ROOT,source_SHA=cfg['source_SHA'],new_native_only_until_original_account_handoff=True,no_native_or_PPO_pass_inferred=True));print(json.dumps(owner),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('SHORT_TMP_V2_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_replay=True));raise
