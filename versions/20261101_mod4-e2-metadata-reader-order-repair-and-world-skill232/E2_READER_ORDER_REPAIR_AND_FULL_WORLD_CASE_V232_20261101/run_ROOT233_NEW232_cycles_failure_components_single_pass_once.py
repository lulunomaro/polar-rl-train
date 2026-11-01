from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
PURPOSE='NEW233_SINGLE_PASS_NEW232_E2_ORIGINAL_BOUND_FAILURE_COMPONENTS'
RAW='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_FULL_WORLD_METADATA_CASE232_20261101/case/frozen_regression/E2_FULL_WORLD_SIGNED_UID_CYCLES_213_ACTUAL.jsonl'
SHA='0099ccd978ba122c4a47b7fc569198590f3804c8abbc7735d2f2cc41347232ef'
CODE=r'''from pathlib import Path
import collections,hashlib,json,math,statistics,struct,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment']is None
J=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_CYCLE_COMPONENTS233_20261101');J.mkdir(exist_ok=False)
def put(name,value):
 with(J/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
put('NEW233_ONCE_CONSUMED_BEFORE_RAW.json',dict(epoch=time.time(),purpose=v['purpose'],raw_path=v['path'],expected_bytes=93697936,expected_rows=64926,expected_SHA=v['SHA'],raw_physical_opens=1,same_forward_pass_hash_parse=True,oldotherraw_or_model_NPZ_GPU_reads=0,canonical_current_None=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),account_writes=0))
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
counts=collections.Counter();masks=collections.Counter();byprofile={};metrics={k:[]for k in('along_error','cross_error','yaw_error','reference_goal_error','actual_minus_reference')};examples={};rows=bytes_n=0;H=hashlib.sha256();disagree=0
with Path(v['path']).open('rb')as stream:
 for line in stream:
  H.update(line);bytes_n+=len(line);row=json.loads(line);rows+=1
  assert row['schema']=='mod4.E2.same_UID_world213.v1' and row['source_SHA']=='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
  if not row['complete_sampled_span']:counts['partial']+=1;continue
  counts['complete']+=1;p=str(row['original_E2_profile']);g=byprofile.setdefault(p,collections.Counter());g['complete']+=1
  along=float(row['along_speed_m_s']);cross=float(row['cross_speed_m_s']);yaw=float(row['signed_yaw_error_rad_s']);seconds=float(row['seconds']);assert seconds>0 and all(math.isfinite(x)for x in(along,cross,yaw,seconds))
  bad=[abs(f32(along-.5))>f32(.05),abs(cross)>f32(.05),abs(yaw)>f32(.2)]
  mask=''.join('1'if x else'0'for x in bad);masks[mask]+=1
  originalK=bool(row['original_kinematic_bounds_met']);valid=bool(row['valid_original_complete_skill_sample']);fact=bool(row['original_complete_cycle_fact']);assert fact==(originalK and valid)
  disagree+=int(originalK!=(not any(bad)));counts['original_false']+=not fact;counts['original_fact']+=fact;g['original_false']+=not fact;g['original_fact']+=fact
  for k,b in zip(('along_fail','cross_fail','yaw_fail'),bad):counts[k]+=b;g[k]+=b
  counts['original_nonterminal_and_nontimeout_false']+=not valid;counts['non_timeout_at_complete']+=bool(row['non_timeout_before_reset']);counts['timeout_at_complete']+=bool(row['timeout_before_reset'])
  counts['kinematic_false_from_original_flag']+=not originalK
  reference=float(row['sampled_original_BODY_reference_displacement_m'])/seconds
  for k,x in [('along_error',abs(along-.5)),('cross_error',abs(cross)),('yaw_error',abs(yaw)),('reference_goal_error',abs(reference-.5)),('actual_minus_reference',abs(along-reference))]:metrics[k].append(x)
  if mask not in examples:examples[mask]={k:row[k]for k in('env_id','episode_uid','command_uid','original_E2_profile','first_control','last_control','seconds','along_speed_m_s','cross_speed_m_s','signed_yaw_error_rad_s','nominal_world_goal_m_s','sampled_original_BODY_reference_displacement_m','valid_original_complete_skill_sample','original_complete_cycle_fact')}
assert bytes_n==93697936 and rows==64926 and H.hexdigest()==v['SHA'];assert counts['complete']==53140 and counts['original_false']==52588 and counts['original_fact']==552 and counts['partial']==11786
stats={k:dict(mean=sum(a)/len(a),median=statistics.median(a),max=max(a))for k,a in metrics.items()}
result=dict(epoch=time.time(),passed=True,purpose=v['purpose'],source=dict(path=v['path'],bytes=bytes_n,rows=rows,SHA=H.hexdigest(),physical_byte_opens=1,hash_and_parse_one_pass=True,raw_downloads=0),counts=dict(counts),failure_mask_order=['along','cross','yaw'],overlap_masks=dict(masks),by_original_profile={k:dict(x)for k,x in byprofile.items()},mean_absolute_errors_m_s_or_rad_s=stats,derived_F32_bounds_vs_original_flag_disagreements=disagree,first_example_per_mask=examples,
 original_bounds=dict(nominal_world_along_m_s=.5,along_and_cross_tolerance_m_s=.05,signed_yaw_error_tolerance_rad_s=.2),original_flags_authoritative=True,events_not_independent_robot_success_rate=True,no_new_graduation_gate=True,no_unique_policy_reward_mapping_or_DR_cause_claim=True,model_NPZ_SDK_GPU_or_optimizer_or_account_calls=0,canonical_current_None_snapshot=True)
put('ACTUAL233_ORIGINAL_FAILURE_COMPONENTS.json',result);print(json.dumps(result))
'''
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert read(R/'ROOT232_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 D=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/D_BEFORE_USE_CWD_REPAIR_SOURCE/reports'
 close=read(D/'ROOT227D_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');cpu=read(D/'ROOT227D_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert close['passed_collection']and close['owner_closed']['canonical_None']and cpu['passed']
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'run_ROOT233_|run_ROOT232_|run_ROOT231_|collect227|launch227|review227' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows];own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT233_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other=other));assert len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 ast.parse(CODE);put('ROOT233_NEW_NECESSARY_RAW_PURPOSE_FROZEN_BEFORE_NETWORK.json',dict(epoch=time.time(),purpose=PURPOSE,path=RAW,bytes=93697936,rows=64926,SHA=SHA,max_physical_opens=1,parse_hash_samepass=True,download=0,model_oldraw_NPZ_or_GPU=0,code_SHA=hashlib.sha256(CODE.encode()).hexdigest(),need='Actual232 full24s found52588 false completecycles;split original along/cross/yaw/terminal to choose concrete remedy,notforstatsorGit. Existing producer JSON hasonlyunion counts.',no_new_gate_or_graduation_rate=True))
 wrapper=module('case233_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();secret=module('case233_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  actual=d.code(client,d.PY72,CODE,dict(purpose=PURPOSE,path=RAW,SHA=SHA),timeout=240);put('ROOT233_ACTUAL_ORIGINAL_FAILURE_COMPONENTS_SINGLE_PASS_RETURNED.json',actual);print(json.dumps({k:actual[k]for k in('passed','counts','overlap_masks','mean_absolute_errors_m_s_or_rad_s','derived_F32_bounds_vs_original_flag_disagreements')}))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT233_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT233_LOCAL_OR_ORIGINAL_REMOTE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
