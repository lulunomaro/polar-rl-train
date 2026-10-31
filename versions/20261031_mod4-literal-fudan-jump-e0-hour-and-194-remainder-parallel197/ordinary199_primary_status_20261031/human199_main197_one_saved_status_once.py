"""Human-requested primary197 saved status only, not a formal collector or watcher."""
from pathlib import Path
import importlib.util, json, os, subprocess, sys, time, traceback

N=Path(__file__).resolve().parent; T=N.parent; W=T.parent; R=N/'reports'
def put(name, value):
    with (R/name).open('x',encoding='utf8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
    query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'human199_main197_one_saved_status_once|collect197_original_two_role_formals|launch197_unified_194_remaining|request197_original194_saved|install198_E0_72_source_CPU|human196_194_one_saved|collect194_original|start195_literal|collect195_original|install195_literal' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
    x=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(x.stdout) if x.stdout.strip() else []; rows=rows if isinstance(rows,list) else [rows]
    own=[v for v in rows if v['ProcessId']==os.getpid()]; other=[v for v in rows if v['ProcessId']!=os.getpid()]
    put('ROOT199_PRIMARY_STATUS_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,exact_CIM=rows))
    assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
    assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
    binding=json.loads((R/'KNOWN_ACTIVE197_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json').read_bytes())
    put('ROOT199_HUMAN_PRIMARY_SAVED_STATUS_PURPOSE_CONSUMED.json',dict(epoch=time.time(),human='非分支训练的如何？跳了吗？',
        scope='One current primary197 saved-progress/FINAL/error/node-terminal small JSON read, fresh exact197 authority first',
        maximum72_small_JSON_reads=3,maximum210_small_JSON_reads=5,maximum_seconds=180,
        model_raw_NPZ_SDK_GPU_reads=0,formal_download_or_hash=0,normal_collector_calls=0,
        source_physics_reward_or_account_writes=0,no_watcher_or_automatic_repeat=True))
    wrapper=module('status199_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    client=None;transport=None;previous=None;secret=None
    try:
        transport,previous=wrapper.install()
        sec=module('status199_memory_authority',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
        secret=sec.recover();client=d.connect72(secret);secret=None
        auth="""from pathlib import Path
import hashlib,json,time
b=v['binding'];P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
O=Path(b['owner']['root']);identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());current=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert identity['pid']==b['owner']['pid'] and identity['creation']==b['owner']['creation'] and current['go']==b['go']
a=c['active_segment'];matched=a is not None and a['owner_parent_pid']==b['owner']['pid']
assert a is None or matched,'Different current owner cannot use historical197 binding'
print(json.dumps(dict(epoch=time.time(),passed=True,exact197_owner_run_GO_matched=True,run_id=b['run_id'],canonical_None=a is None,current197_active_at_read=matched,canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_writes=0,small_JSON_reads=3)))"""
        try:
            authority=d.code(client,d.PY72,auth,dict(binding=binding),timeout=45)
            put('ROOT199_FRESH72_EXACT197_AUTHORITY_READONLY.json',authority)
        finally:
            client.close();client=None
        client=route.connect()
        remote="""from pathlib import Path
import hashlib,json,os,time
B=Path('/mnt/mod4_linux_durable_20261013/MOD4_JUMP194_REMAINING_PARALLEL_20261031v197/h1_210')
names=['production/LATEST_PROGRESS.json','production/FINAL.json','production/ORIGINAL_ERROR.json','control197/NODE_TERMINAL_ACTUAL.json','control197/NODE_EXIT_ACTUAL.json'];rows=[];absent=[]
for name in names:
 p=B/name
 if not p.is_file():absent.append(name);continue
 assert p.stat().st_size<100000
 with p.open('rb') as f:
  before=os.fstat(f.fileno());raw=f.read();after=os.fstat(f.fileno())
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and len(raw)==before.st_size
 rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),value=json.loads(raw),byte_reads=1))
print(json.dumps(dict(epoch=time.time(),files=rows,absent=absent,small_JSON_reads=len(rows),model_raw_NPZ_SDK_GPU_or_account_calls=0,no_remote_write=True)))"""
        actual=d.code(client,route.PY,remote,{},timeout=45)
        put('ROOT199_PRIMARY197_ONE_SAVED_STATUS_RETURNED_ACTUAL.json',dict(epoch=time.time(),human='非分支训练的如何？跳了吗？',
            authority=authority,source210=actual,no_model_or_early_formal_read=True,
            scope='Original contact-flight env-controls and absolute root-height are diagnostics, not verified wheel clearance/controlled flight-landing or270 skill'))
        print(json.dumps(dict(passed=True,files=[dict(file=Path(v['path']).name,value=v['value']) for v in actual['files']]),ensure_ascii=False))
    finally:
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT199_PRIMARY_STATUS_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_client_lease='FREE'))
if __name__=='__main__':
    try:main()
    except BaseException:
        put('ROOT199_PRIMARY_STATUS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
