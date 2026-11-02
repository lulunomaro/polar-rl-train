"""Independent443 collection of original443 closed final; no GO/writer/optimizer."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
from normal443_common import *
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def read(p):return json.loads(Path(p).read_bytes())
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
COLLECT_NODE="""from pathlib import Path
import fcntl,hashlib,json,psutil,time
B=Path(v['spec']['job_root']);C=B/'control443';end=time.time()+180
import sys;sys.path.insert(0,str(C));from report_classification312 import classify_error_reports
while time.time()<end and not (C/'NODE_EXIT_ACTUAL.json').is_file():time.sleep(2)
t=json.loads((C/'NODE_TERMINAL_ACTUAL.json').read_bytes());e=json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes());assert e['all_own_children_waited'] and e['private_EX_released']
identity=json.loads((C/'NODE_IDENTITY.json').read_bytes())
def running(x):
 try:p=psutil.Process(x['pid']);return p.create_time()==x['creation'] and p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
while time.time()<end and running(identity):time.sleep(.5)
assert not running(identity)
with Path(v['spec']['private_lock']).open('rb+') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_UN)
texts=[];models=[]
for root in (C,B/'production'):
 for p in sorted(root.rglob('*')):
  if not p.is_file() or 'kit_isolation' in p.relative_to(root).parts:continue
  if p.suffix=='.pt':models.append(dict(path=str(p),bytes=p.stat().st_size,SHA='producer index only, no extra hash'));continue
  if p.suffix in ('.npz','.npy','.jsonl','.usd','.usdc','.png','.mp4'):
   models.append(dict(path=str(p),bytes=p.stat().st_size,SHA='existing producer or unknown; no binary/raw read'));continue
  if p.suffix not in ('.json','.log'):continue
  raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
f=B/'production/FINAL.json';final=json.loads(f.read_bytes()) if f.is_file() else None
errors,diagnostic_reports=classify_error_reports(B/'production')
material_errors=[line for textrow in texts for line in textrow['UTF8'].splitlines() if 'PxPhysics::createMaterial' in line and '64K' in line]
actual_go=json.loads((B/'GO_PRODUCTION.json').read_bytes())
qualified=bool(not material_errors and t['row']['returncode']==0 and not t['row']['original_error'] and final and final.get('passed') and final.get('actual_new_WM_updates',0)>0 and final.get('actual_new_PPO_updates')==final.get('actual_new_Pi_updates') and final.get('actual_new_Pi_updates',0)>0 and final.get('actual_new_critic_updates',0)>0 and not errors and final['final']['save_epoch']>=actual_go['save_deadline'])
counts=None
if qualified:
 counts=json.loads(next(x['UTF8'] for x in texts if Path(x['path']).name=='ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json'))
 assert counts['source_SHA']==v['spec']['source_SHA'] and counts['source_byte_reads']==counts['source_GPU_decodes']==1
 assert final['final']['teacher_source_SHA']==v['spec']['teacher_SHA']
 u=final['actual_new_WM_updates'];assert u>0
 assert final['total_WM_updates']==30731+u and final['final']['WM_Adam_step_min']==final['final']['WM_Adam_step_max']==30731+u
 assert final['final']['teacher_iteration']==2135 and final['final']['teacher_Adam_step']==42940
 import sys;sys.path.insert(0,str(C));from teacher_task443 import validate_final;validate_final(final,json.loads((B/'TASK443.json').read_bytes()),actual_go)
 assert final['final']['full_Adam_norm_RNG_DR_reward_memory_saved']
formal=None
if qualified:
 formal=final['final'];p=Path(formal['path']);assert p.resolve().is_relative_to((B/'production').resolve()) and p.stat().st_size==formal['bytes']
 with p.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
 assert sha==formal['SHA'];formal=dict(formal,actual_source_host_SHA=sha)
print(json.dumps(dict(epoch=time.time(),passed_collection=True,key=v['spec']['key'],qualified_formal=qualified,formal=formal,final=final,errors=errors,actual_material_limit_error_count=len(material_errors),original_material_error_lines=material_errors,
 source_readcounts_before_Appclose=counts,original_node_terminal=t,original_node_exit=e,node_out_or_nonexecuting_original_zombie=True,private_EX_free=True,full_UTF8=texts,other_models_metadata_only=models)))"""
def main():
 assert sys.version_info[:2] == (3,14), 'Control transport requires existing Python314 compression.zstd'
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);parser.add_argument('--auth-provider',type=Path,required=True);parser.add_argument('--additional-control-pattern',required=True);parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
 assert args.root_lease_label.startswith('ROOT443_EXCLUSIVE_NORMAL900_RECOVERY_') and args.additional_control_pattern
 from normal443_common import verify_index,INDEX,validate_original_go,normal900_eligible
 verify_index(D/INDEX,args.caller_index_SHA)
 launch=read(R/'ROOT443_ORIGINAL_OWNER_LAUNCH_ACTUAL.json');owner=launch['owner'];specs=launch['specs']
 state=read(R/'ROOT443_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json');go=state['current']['go'];assert set(go)==set(specs)=={'jump_72'};validate_original_go(go['jump_72'],launch['run_id'])
 nominal=max(g['nominal_end_epoch'] for g in go.values());already_closed=bool(state['canonical_None'] and state['files'].get('COHORT_FINAL.json') and state['files'].get('OWNER_EXIT_ACTUAL.json'))
 assert normal900_eligible(go['jump_72'],time.time(),already_closed),'Original signed local900 gate not yet eligible'
 pattern='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|run_once_after_resume|continue_clean_sequential|watch_|prepare_archive|single_gpu|collect_nine|deploy_nine|collect_e1|E1_actual|snapshot_adaptation|deploy_w35|launch_w35|collect_attempt2_wait_and_sdk|postround|run_ROOT|PAIR1|PAIR2|PAIR3|PAIR4|RMPOLAR|watch_|run339_|run342_|run_once_after_resume|launch283_|collect283_|launch285_|collect285_|launch443_|collect443_|run_ROOT274_|run_ROOT272_|collect240_|start240_|install240_|read240_|transfer240_|collect_e2_solo_|launch_e2_solo_|review_e2_solo_|collect227D_|launch227D_|review227D_|collect219V3_|launch219_|launch210_|prepare212_|install211_|install209_|launch209_|human196_194_one_saved|collect194_original|start195_literal|collect195_original|install195_literal|'+args.additional_control_pattern
 query='Get-CimInstance Win32_Process -Filter "Name=\'python.exe\' OR Name=\'ssh.exe\'" | Where-Object { $_.CommandLine -match \'CONTROL_PATTERN\' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'.replace('CONTROL_PATTERN',pattern.replace("'","''"))
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[v for v in rows if v['ProcessId']==os.getpid()];other=[v for v in rows if v['ProcessId']!=os.getpid()]
 put('ROOT443_LOCAL_EXACT_CIM_BEFORE_ASSERT_'+str(time.time_ns())+'.json',dict(epoch=time.time(),rows=rows,PID=os.getpid(),exe=sys.executable))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower() and not other
 assert any(str(path).replace(chr(92),'/').lower() in own[0]['CommandLine'].replace(chr(92),'/').lower()for path in(Path(__file__).resolve(),Path('C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\RL443_SINGLE_PROCESS_POSTROUND_V444_20261102\\postround444_close_actual443_eval_once.py')))
 put('ROOT443_NORMAL900_RECOVERY_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,exact_CIM=rows))
 put('ROOT443_NORMAL900_RECOVERY_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=launch['run_id'],original_owner=owner,original_go=go,
  one_original_fee_sum_once=True,one_NEW_formal_transfer_per_qualified_role=True,old_E2_source_inputs_read=0,no_new_GO_or_extra_learning=True))
 wrapper=module('normal210_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None;results={};transfers={}
 try:
  transport,previous=wrapper.install();sec=module('normal_e2_solo_auth',args.auth_provider);secret=sec.recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import json,time,fcntl,psutil,hashlib
O=Path(v['owner']['root']);go=v['go'];nominal=max(g['nominal_end_epoch'] for g in go.values())
current=json.loads((O/'OWNER_CURRENT.json').read_bytes());assert current['go']==go and set(go)=={'jump_72'}
closed=(O/'COHORT_FINAL.json').is_file() and (O/'OWNER_EXIT_ACTUAL.json').is_file()
assert nominal-time.time()<=900 or closed,'Original signed remote900 gate not eligible'
identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());assert identity['pid']==v['owner']['pid'] and identity['creation']==v['owner']['creation']
end=time.time()+850
while time.time()<end and not (O/'OWNER_EXIT_ACTUAL.json').is_file():time.sleep(2)
final=json.loads((O/'COHORT_FINAL.json').read_bytes());exit=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes());assert final['original_cost_settled'] and exit['original_cost_settled'] and final['go']==go
def running(x):
 try:p=psutil.Process(x['pid']);return p.create_time()==x['creation'] and p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
while time.time()<end and running(v['owner']):time.sleep(.5)
assert not running(v['owner'])
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(P.read_bytes());assert c['active_segment'] is None
segments=[s for s in c['completed_segments'] if s.get('owner_parent_pid')==v['owner']['pid']];assert len(segments)==1
s=segments[0];fees={}
for key,g in go.items():
 x=s['experts'][key];assert x['started_epoch']==g['learning_started_epoch'] and x['ended_epoch']>=x['started_epoch'] and x['duration_bound_passed']
 assert final['rows'][key]['terminal_all_own_children_waited'];fees[key]=x['charged_seconds']
rawsum=sum(fees.values());assert abs(s['charged_expert_seconds']-rawsum)<1e-5
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (P.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[]
for p in sorted(O.iterdir()):
 if not p.is_file() or p.suffix not in ('.json','.log'):continue
 raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed=True,canonical_None=True,original_owner_out_or_original_nonexecuting_zombie=True,shared_locks_free=True,
 original_one_owner_segment=s,original_independent_raw_fees=fees,raw_fee_sum_once=rawsum,closing_balance_snapshot=c['remaining_training_seconds'],cohort_final=final,owner_exit=exit,full_UTF8=texts,no_account_write=True)))"""
  ownerclosed=d.code(client,d.PY72,code,dict(owner=owner,go=go,already_closed=already_closed),timeout=900)
  put('ROOT443_NORMAL900_RECOVERY_ORIGINAL_SOLO_OWNER_ONE_RAW_FEE_CLOSED_ACTUAL.json',ownerclosed)
  result=d.code(client,d.PY72,COLLECT_NODE,dict(spec=specs['jump_72']),timeout=210);results['jump_72']=result
  put('ROOT443_NORMAL900_RECOVERY_JUMP_FULL_UTF8_AND_FORMAL_ACTUAL.json',result)
  if result['qualified_formal']:
   formal=result['formal'];dest=N/'current_closed443_models/jump_72/formal/model_final.pt';dest.parent.mkdir(parents=True,exist_ok=False)
   sf=client.open_sftp()
   try:sf.get(formal['path'],str(dest))
   finally:sf.close()
   with dest.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
   assert dest.stat().st_size==formal['bytes'] and sha==formal['SHA']
   transfers['jump_72']=dict(path=str(dest),source=formal['path'],bytes=formal['bytes'],SHA=sha,transfers=1,two_host_SHA_equal=True)
  put('ROOT443_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed_collection=True,run_id=launch['run_id'],owner_closed=ownerclosed,roles=results,formals=transfers,skill_not_inferred=True,actualPPO443=True))
  print(json.dumps(dict(qualified_roles=list(transfers),raw_fee_sum_once=ownerclosed['raw_fee_sum_once'],closing_balance_snapshot=ownerclosed['closing_balance_snapshot'])),flush=True)
 finally:
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT443_NORMAL900_RECOVERY_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT443_NORMAL900_RECOVERY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
