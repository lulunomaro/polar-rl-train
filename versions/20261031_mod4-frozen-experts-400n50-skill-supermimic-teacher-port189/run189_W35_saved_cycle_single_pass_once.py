"""New bounded acceptance purpose; fresh72 -> close -> strict86, one raw read."""
from pathlib import Path
import hashlib, importlib.util, json, os, shlex, socket, subprocess, sys, time, traceback
import paramiko

B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports'
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
    sys.modules[name]=value;spec.loader.exec_module(value);return value

def put(name,value):
    with (R/name).open('x',encoding='utf8') as file:json.dump(value,file,indent=2,allow_nan=False)

def main():
    protocol_raw=(R/'W35_189_FIRST_SAVED_CYCLE_READ_PURPOSE_FROZEN.json').read_bytes()
    protocol=json.loads(protocol_raw)
    assert protocol['maximum_raw_opens']==1 and protocol['maximum_model_opens']==0
    parser=(B/'w35_cycle_acceptance189.py').read_bytes()
    assert hashlib.sha256(parser).hexdigest()==protocol['parser_SHA']
    binding=json.loads((T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031/reports/KNOWN_ACTIVE188_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json').read_bytes())
    assert set(binding)=={'owner','run_id','go'}
    query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'run189_W35_saved_cycle_single_pass_once|collect188_original_formal_cost_normal900_UNUSED_once|start188_literal_STAIRS3_single_forwarded4090_FIRST|install188_literal_STAIRS3_native_admission|collect_E3_source210|run_W35_V2_NORMAL|upload_admit_detach|collect_ONE178_original' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
    cmd=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(cmd.stdout) if cmd.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
    own=[row for row in rows if row['ProcessId']==os.getpid()]
    assert len(own)==1 and len(rows)==1
    assert own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
    assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
    put('W35_189_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),self_pid=os.getpid(),self_exe=sys.executable,self_argv=sys.argv,rows=rows))
    put('W35_189_SINGLE_PASS_STARTED_CONSUMED.json',dict(epoch=time.time(),protocol_SHA=hashlib.sha256(protocol_raw).hexdigest(),maximum_remote_seconds=110,model_reads=0,SDK_GPU=0))
    transport=previous=client=channel=connection=secret=req=None
    result=dict(passed=False,errors=[],all_SSH_closed=False,SESSION_restored=False)
    started=time.time()
    try:
        wrapper=module('expert189_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
        transport,previous=wrapper.install()
        sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
        import deploy_two50_reconciled_original_writer_once as d
        memory=module('expert189_memory72',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
        secret=memory.recover();client=d.connect72(secret);secret=None
        authority_code="""from pathlib import Path
import json,time,psutil
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes())
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
assert c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
active=c['active_segment'];k=v['binding']
if active is not None:
 e=k['owner'];assert active['owner_parent_pid']==e['pid'] and set(active['experts'])==set(k['go'])
 p=psutil.Process(e['pid']);assert p.create_time()==e['creation'] and p.exe()==e['exe'] and p.cmdline()==e['argv'] and p.cwd()==e['cwd']
 assert all(g['run_id']==k['run_id'] and active['experts'][name]['started_epoch']==g['learning_started_epoch'] for name,g in k['go'].items())
print(json.dumps(dict(passed=True,epoch=time.time(),CNone=active is None,exact_active188_matched=active is not None,run_id=k['run_id'] if active else None,no_canonical_or_account_write=True)))"""
        result['fresh72_authority']=d.code(client,d.PY72,authority_code,dict(binding=binding),timeout=30)
        assert result['fresh72_authority']['passed']
        client.close();client=None
        transport.SESSION=previous;transport=None
        # Only the prior proved credential-recovery function is used, never its main/once.
        old=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_UID_CYCLE_V2_NORMAL_AST_ONLY_SECURE_WRAPPER_20261030_V1/run_W35_V2_NORMAL_exact_AST_recover_secure_ingress_UNUSED_once.py'
        assert hashlib.sha256(old.read_bytes()).hexdigest()==protocol['secure_recover_wrapper_SHA']
        recovered=module('expert189_recover_only',old).recover_namespace()
        req=recovered['recover']()
        assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo'
        secret=req.pop('password')
        connection=paramiko.Transport(socket.create_connection((req['host'],22),timeout=10))
        connection.banner_timeout=10;connection.auth_timeout=10;connection.start_client(timeout=10)
        assert hashlib.sha256(connection.get_remote_server_key().asbytes()).hexdigest()==PIN
        connection.auth_password(req['username'],secret,fallback=False);secret=None;req=None
        channel=connection.open_session(timeout=10);channel.settimeout(50)
        channel.exec_command('/usr/bin/python3 -B -c '+shlex.quote("import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"))
        code=parser.decode('utf8')+"""
from pathlib import Path
import hashlib,json,time
p=Path(v['producer']['path']);assert p.is_relative_to('/data/robemo/polar-rl-train')
a=CycleAccumulator();h=hashlib.sha256();size=0;opens=0;passes=0
with p.open('rb') as file:
 opens+=1
 for raw in file:
  h.update(raw);size+=len(raw);a.add(json.loads(raw))
 passes+=1
assert size==v['producer']['bytes'] and h.hexdigest()==v['producer']['SHA'] and a.rows==v['producer']['rows']
value=a.finish();assert value['all_complete']['events']==1229 and value['partial_cycle_events']==3810
assert value['nonterminal_complete']['events']==1214
print(json.dumps(dict(passed=True,epoch=time.time(),producer=v['producer'],raw_opens=opens,forward_passes_including_EOF=passes,accepted_SHA=h.hexdigest(),actual_bytes=size,numerical=value,model_opens=0,SDK_GPU=0,no_remote_write=True)))"""
        file=channel.makefile_stdin('wb');file.write((json.dumps(dict(code=code,producer=protocol['producer']))+'\n').encode());file.flush();channel.shutdown_write()
        out=channel.makefile('rb').read().decode('utf8');err=channel.makefile_stderr('rb').read().decode('utf8');rc=channel.recv_exit_status()
        result['original_remote_returncode']=rc;result['original_remote_stderr']=err
        assert rc==0,(rc,err,out)
        result['readback']=json.loads(out);assert result['readback']['passed']
        result['passed']=True
    except BaseException:
        result['errors'].append(traceback.format_exc())
    finally:
        secret=req=None
        if channel:channel.close()
        if connection:connection.close()
        if client:client.close()
        if transport is not None:transport.SESSION=previous
        result['all_SSH_closed']=True;result['SESSION_restored']=True
        result['elapsed_seconds']=time.time()-started;result['epoch']=time.time()
        result['raw_local_saved_or_reopened']=False
        put('ROOT189_W35_FIRST_SAVED_CYCLE_SINGLE_PASS_RETURNED_ACTUAL.json',result)
        print(json.dumps(dict(passed=result['passed'],errors=result['errors'],all_SSH_closed=True,
                             numerical=result.get('readback',{}).get('numerical'))))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
