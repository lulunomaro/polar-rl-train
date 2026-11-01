"""New closed-failure purpose: original235V2 owner/fee/UTF8; no model or SDK."""
from pathlib import Path
import argparse, ast, hashlib, importlib.util, json, os, subprocess, sys, time, traceback

T=Path(__file__).resolve().parent; W=T.parent
C=T/'E2_QUALIFIED_FULLSTATE_SOLO_ROOT_CALLERS_PY314_V2_20261101'
N=T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101'; R=N/'reports'
def read(p): return json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f: json.dump(v,f,indent=2,allow_nan=False)
def mod(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
    assert sys.version_info[:2]==(3,14)
    p=argparse.ArgumentParser();p.add_argument('--root-lease-label',required=True);a=p.parse_args()
    assert a.root_lease_label.startswith('ROOT235_EXCLUSIVE_CLOSED_FAILURE_')
    R.mkdir(parents=True,exist_ok=True)
    first=read(C/'reports/ROOT_E2_SOLO_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')
    assert first['passed'] is False and first['first'] is None
    chosen={Path(x['path']).name:x for x in first['full_selected_UTF8']}
    err=json.loads(chosen['ORIGINAL_E2_PPO_ERROR.json']['UTF8'])
    node_exit=json.loads(chosen['NODE_EXIT_ACTUAL.json']['UTF8'])
    assert err['actual_new_PPO_updates']==0 and node_exit['all_own_children_waited'] and node_exit['private_EX_released']
    launch=read(C/'reports/ROOT_E2_SOLO_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json')
    state=read(C/'reports/ROOT_E2_SOLO_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
    owner=launch['owner'];go=state['current']['go'];assert set(go)=={'e2'}
    assert go['e2']['run_id']==launch['run_id'] and go['e2']['original_owner_pid']==owner['pid'] and go['e2']['original_owner_creation']==owner['creation']
    # Reuse the complete original fee/close/wait implementation byte-literal.
    source=(C/'collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py').read_text(encoding='utf8')
    tree=ast.parse(source)
    node_payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='COLLECT_NODE' for t in n.targets))
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    owner_payload=next(ast.literal_eval(n.value) for n in ast.walk(fn) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in n.targets))
    assert "closed=(O/'COHORT_FINAL.json').is_file()" in owner_payload and 'rawsum=sum(fees.values())' in owner_payload
    closed_guard="from pathlib import Path\nimport json\nO=Path(v['owner']['root']);assert (O/'COHORT_FINAL.json').is_file() and (O/'OWNER_EXIT_ACTUAL.json').is_file(),'Not actually closed;no early original fee collection'\n"
    payload=closed_guard+owner_payload
    ast.parse(payload);ast.parse(node_payload)
    put('ROOT235_CLOSED_FAILURE_PURPOSE_FROZEN.json',dict(epoch=time.time(),run_id=launch['run_id'],owner=owner,go=go,
        original_worker_wait_RC=0,original_new_PPO_updates=0,original_FIRST_false_preserved=True,
        remote_both_owner_terminal_files_required_before_original_fee_code=True,
        original_fee_close_source_SHA=hashlib.sha256(owner_payload.encode()).hexdigest(),
        original_node_collect_source_SHA=hashlib.sha256(node_payload.encode()).hexdigest(),
        model_raw_SDK_training_account_writes=0,formal_transfer=0,no_signal=True,root_lease_label=a.root_lease_label))
    pattern='collect235_failed_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|collect227D_|launch227D_|read234|probe234|parent234|install234|launch234|ROOT234|run232|parent232|read233|run_actual|e2_target_metadata'
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
    own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
    assert len(own)==1 and not other and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
    assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
    put('ROOT235_CLOSED_FAILURE_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
    put('ROOT235_CLOSED_FAILURE_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=launch['run_id'],source_model_reads=0,no_new_GO=True))
    wrapper=mod('root235_closed_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    client=None;transport=None;previous=None;secret=None
    try:
        transport,previous=wrapper.install()
        sec=mod('root235_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
        secret=sec.recover();client=d.connect72(secret);secret=None
        closed=d.code(client,d.PY72,payload,dict(owner=owner,go=go,already_closed=True),timeout=900)
        put('ROOT235_FAILED_OWNER_ORIGINAL_FEE_CLOSED_ACTUAL.json',closed)
        result=d.code(client,d.PY72,node_payload,dict(spec=launch['specs']['e2']),timeout=210)
        put('ROOT235_FAILED_NODE_ALL_FULL_UTF8_CLOSED_ACTUAL.json',result)
        assert not result['qualified_formal'] and result['formal'] is None and result['final'] is None
        put('ROOT235_ZERO_PPO_COMPLETE_FAILURE_COLLECTION_ACTUAL.json',dict(epoch=time.time(),passed_collection=True,
            run_id=launch['run_id'],new_PPO_updates=0,qualified_formal=False,formal_transfer=0,source_model_reads=0,
            owner_closed=closed,node_result=result,original_FIRST_false_preserved=True))
        print(json.dumps(dict(passed_collection=True,updates=0,raw_fee_sum_once=closed['raw_fee_sum_once'],closing_snapshot=closed['closing_balance_snapshot'],canonical_None=True)),flush=True)
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT235_CLOSED_FAILURE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
    try:main()
    except BaseException:
        R.mkdir(parents=True,exist_ok=True)
        put('ROOT235_CLOSED_FAILURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
