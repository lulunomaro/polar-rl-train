"""User-requested original forwarded4090 training history, unseen log ranges only."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';R.mkdir(exist_ok=True)
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def read(p):return json.loads(Path(p).read_bytes())
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
    old_path=T/'FORWARDED210_EXISTING_FUDAN_JUMP_MODEL_REUSE_V185_20261031/reports/ROOT185DELIVERY_ORIGINAL_FORWARD210_MODEL_FILENAME_INVENTORY_ACTUAL.json'
    old=read(old_path);tail=next(x for x in old['texts'] if x['path'].endswith('/runs20k_tgs32_16/train.out.log'))
    a,z=tail['byte_range'];assert z==tail['original_file_bytes'] and 0<=a<=z
    cached=tail['UTF8'].encode('utf8');cached_exact=hashlib.sha256(cached).hexdigest()==tail['SHA']
    put('FROZEN206_USER_TRAIN_HISTORY_RANGE_REVIEW_PURPOSE.json',dict(epoch=time.time(),
        human='为什么端口转发4090训得能跳，现在E0不跳？看看端口训练记录；为什么都边跳边转圈',
        original_log=tail['path'],old185_tail_range=[a,z],old_tail_consumed_never_reread=True,
        new_range_budget=dict(prefix=[0,a],appended='[old185_end,currentstableEOF) if any'),maximum_log_file_opens=1,
        maximum_fresh_log_bytes=64*1024**2,maximum72_JSON_reads=1,
        checkpoint_metadata_stats_only=True,model_raw_NPZ_SDK_GPU_or_learning_calls=0,remote_writes=0,
        old_cached_tail_roundtrip_exact=cached_exact,maximum_seconds=180))
    query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'inspect206_original_training_unread_log_ranges_once|install_evaluate201_E0_final32066_same_plane_once|install_capture200_final197_literal_jump_plane_once|collect197_original_two_role_formals|launch197_unified_194_remaining|human199_main197_one_saved_status|run207_zero_yaw' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
    own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
    put('ROOT206_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,exact_CIM=rows))
    assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not others
    assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
    wrapper=module('history206_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    client=None;transport=None;previous=None;secret=None
    try:
        transport,previous=wrapper.install();sec=module('history206_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
        secret=sec.recover();client=d.connect72(secret);secret=None
        auth="""from pathlib import Path
import hashlib,json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
print(json.dumps(dict(epoch=time.time(),CNone=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),readonly=True,JSON_reads=1)))"""
        try:put('ROOT206_FRESH72_CNONE_READONLY.json',d.code(client,d.PY72,auth,{},timeout=45))
        finally:client.close();client=None
        client=route.connect()
        code="""from pathlib import Path
import hashlib,json,os,time
p=Path(v['log']);s=p.stat();a,z=v['old_tail_range'];assert 0<=a<=z<=s.st_size<=64*1024**2
ranges=[]
if a or s.st_size>z:
 with p.open('rb') as f:
  before=os.fstat(f.fileno())
  for lo,hi in ((0,a),(z,s.st_size)):
   if hi==lo:continue
   f.seek(lo);raw=f.read(hi-lo);assert len(raw)==hi-lo
   ranges.append(dict(byte_range=[lo,hi],bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace'),byte_passes=1))
  after=os.fstat(f.fileno())
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
m=Path('/mnt/mod4_linux_durable_20261013/rm2026_fudan_exact_20261031/runs20k_tgs32_16/2026-10-31_04-38-39_fudan_exact_mod4_plane_edge4090_20k_2p5ms_tgs32_16/model_4999.pt');ms=m.stat()
print(json.dumps(dict(epoch=time.time(),log=dict(path=str(p),bytes=s.st_size,mtime=s.st_mtime),new_ranges=ranges,old_tail_bytes_reread=0,accepted_log_opens=int(bool(a or s.st_size>z)),checkpoint_metadata_only=dict(path=str(m),bytes=ms.st_size,mtime=ms.st_mtime),model_content_reads_or_hashes=0,SDK_GPU_or_account_calls=0,no_remote_write=True)))"""
        actual=d.code(client,route.PY,code,dict(log=tail['path'],old_tail_range=[a,z]),timeout=90)
        put('ROOT206_ORIGINAL_FORWARD210_FRESH_UNREAD_LOG_RANGES_RETURNED_ACTUAL.json',actual)
        texts=[x['UTF8'] for x in actual['new_ranges'] if x['byte_range'][0]==0]+[tail['UTF8']]+[x['UTF8'] for x in actual['new_ranges'] if x['byte_range'][0]==z]
        text='\n'.join(texts);clean=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',text)
        iterations=[(int(x),int(y)) for x,y in re.findall(r'Learning iteration\s+(\d+)\s*/\s*(\d+)',clean)]
        steps=[int(x.replace(',','')) for x in re.findall(r'Total steps:\s*([\d,]+)',clean)]
        metric={}
        for name in ('Mean reward','Mean episode length','Mean action std','Time elapsed','Total time','Collection time','Learning time'):
            values=re.findall(re.escape(name)+r':\s*([^\r\n]+)',clean)
            if values:metric[name]=dict(first=values[0].strip(),last=values[-1].strip(),rows=len(values))
        view=read(T/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2/reports/ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')['result']
        primary=read(T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031_V2/reports/ROOT200V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')['result']
        comparison=read(T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031/reports/ACTUAL187_DELIVERY_VS_TOTALPLAN_400N50_DR_COMPARISON.json')
        summary=dict(epoch=time.time(),human_question='为何原forward4090能跳而现在E0弱；为何边跳边转圈',
            original_remote_history=dict(source=actual['log'],reused_old185_tail=[a,z],new_ranges=[dict(byte_range=x['byte_range'],bytes=x['bytes'],SHA=x['SHA']) for x in actual['new_ranges']],
                no_old_tail_content_reread=True,iteration_rows=len(iterations),first_iteration=iterations[0] if iterations else None,last_iteration=iterations[-1] if iterations else None,
                first_total_steps=steps[0] if steps else None,last_total_steps=steps[-1] if steps else None,metrics=metric),
            original_source_profile=comparison['source'],
            primary=dict(start='Already-jumping delivered4999',additional_updates=368,iteration=5367,actual20s=primary),
            E0_branch=dict(start='Frozen FLAT E0_82 originalRSL31984, separate trainable copy',jump_training_updates=82,iteration=32066,actual20s=view),
            key_fact='The primary5367 still jumps in actual200/user view; E0 branch is a different warmstart/history, not evidence that primary was overwritten or damaged',
            current_two_views_command=dict(vx_m_s=-.39,yaw_rad_s=1.66,yaw_deg_s=1.66*180/3.141592653589793,
                source='Actual200/205 screenshotHUD; original commands range+-2 rad/s; not a measured yaw-tracking error'),
            original_reward_explanation='tracking_ang_vel=exp(-(yaw_command-base_ang_vel_z)^2/.25); orientation uses gravityXY only, not absoluteyaw',
            no_unique_cause_claim='Prior jump training, number of new updates, task-mode domain and original3500/100Hz/noDR versus totalplan2000/50Hz/DR differ; no one-factor causal isolation',
            planned_test='New207 eval-only yaw command0 for both qualified models, original reward/weights/plant/guards unchanged',
            original_E0_reference_remains_frozen=True,no_training_restart_or_reward_change=True,
            log_ranges_not_complete_original_byte_SHA_proof='Currentprefix plus cachedhistoricaltail; no fresh reread/hash of historicaltail',
            model_raw_NPZ_SDK_GPU_reads=0)
        put('CURRENT_ACTUAL206_FORWARD_TRAIN_HISTORY_PRIMARY_VS_E0_AND_CIRCLE_COMMAND.json',summary)
        print(json.dumps(dict(passed=True,original_iteration_rows=len(iterations),first_iteration=iterations[0] if iterations else None,last_iteration=iterations[-1] if iterations else None,last_total_steps=steps[-1] if steps else None,old_tail_reread=0,model_reads=0)))
    finally:
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT206_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_client_lease='FREE'))
if __name__=='__main__':
    try:main()
    except BaseException:
        put('ROOT206_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
