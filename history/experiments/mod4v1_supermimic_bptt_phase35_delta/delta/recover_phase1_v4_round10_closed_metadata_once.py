"""NEW terminal-only metadata recovery after lost local collector; never a watcher.
Requires original outer actual wait and zero live original local collector. Old
once marker/output namespace are preserved; all original grading stays intact.
"""
from pathlib import Path
import ast,json,hashlib,sys,time,shlex
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_result_collector_v4';out=R/'reports/PHASE1_V4_ROUND10_CLOSED_METADATA_RECOVERY_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_V4_R10_CLOSED_METADATA_RECOVERY_STARTED_ONCE.json';pointer=R/'PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_LATEST_CLOSED_RESULT_PATH.json';assert not out.exists()and not marker.exists()and not pointer.exists();H=lambda b:hashlib.sha256(b).hexdigest()
snapshot=json.loads((R/'reports/PHASE1_V4_ROUND10_PUBLISHED_CLOSURE_RECOVERY_SNAPSHOT_V1.json').read_bytes());a=snapshot['actual'];docs=a['published_metadata'];w=docs['PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json'];e=docs['PARENT_EXIT_SCOPE.json'];assert snapshot['returncode']==0 and w['actual_parent_p_wait_returned']and w['returncode']==1 and e['all_own_children_waited']and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released'];assert all(x['observed']is None for x in a['known_own_process_identities'].values())
raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(4866,'23a5267920106b40b1efcf5db7921a16c6418621365d18933f0c9d69bfefc594');seal=json.loads(raw)
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256'])
sys.path.insert(0,str(D));import source_pins;source_pins.verify_sources();import collect_capture_result as collector
from remote_metadata_reader import validate_dispatch
vdispatch=json.loads((R/'reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json').read_bytes());validate_dispatch(vdispatch);assert vdispatch['root']==a['root']
source=(D/'remote_metadata_reader.py').read_text(encoding='utf-8');extra=r'''
def terminal_only_recovery(dispatch,expected_outer_sha):
    validate_dispatch(dispatch);reader=MetadataReader(dispatch['root'])
    outer=reader.read(OUTER);scope=reader.read('PARENT_EXIT_SCOPE.json')
    require(type(outer)is dict and outer.get('actual_parent_p_wait_returned')is True
        and outer.get('returncode')==1 and outer.get('parent')==dispatch['parent']
        and reader.info[OUTER].get('SHA256')==expected_outer_sha,'published actual original outer wait changed')
    require(type(scope)is dict and scope.get('all_own_children_waited')is True
        and scope.get('original_single_GPU_private_EX_released')is True
        and scope.get('original_global_finite_EX_released')is True,'original closed EX scope required')
    closure=load_metadata_closure(dispatch['root'])
    for name in SMALL:reader.read(name)
    for name in BIG:reader.read(name,terminal=True)
    value=dict(kind='PHASE1_CAPTURE_OWN_METADATA_PACKET_V1',source_version=SOURCE_VERSION,source_derivation=SOURCE_DERIVATION,
        documents={name:project(name,item)for name,item in reader.cache.items()},file_metadata=reader.info,
        closure=closure['receipt'],metadata_validation=validate_terminal_cache(reader,dispatch,closure),
        collector_errors=list(reader.errors),log_tails={name:reader.tail(name)for name in LOGS},
        watch=dict(stop_reason='TERMINAL_ONLY_ORIGINAL_OUTER_WAIT_PREVERIFIED',polls=0,collector_elapsed_seconds=0,
            original_watcher_restarted=False,parent_restarted=False,native_deadline_extended=False,remote_writes=0,signals_sent=0))
    print(json.dumps(value,allow_nan=False,separators=(',',':')))
'''
code=source+extra+'\nterminal_only_recovery('+repr(vdispatch)+','+repr(a['metadata_identities']['PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json']['SHA256'])+')\n';ast.parse(code)
output=R/'reports'/('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_RECOVERED_CLOSED_R10_'+time.strftime('%Y%m%d_%H%M%S'));assert not output.exists()
config=dict(kind='NEW_ROUND10_TERMINAL_METADATA_RECOVERY_NOT_WATCHER_OR_PARENT_RETRY',epoch=time.time(),root=a['root'],local_output_root=str(output),old_job_unknown_and_joblist_empty=True,old_exact_own_local_collector_process_count_observed=0,old_marker_preserved=True,original_parent_controller_observed_absent=True,actual_original_outer_wait_already_published=True,original_outer_parent_rc=1,remote_watch_calls=0,remote_parent_SDK_model_C_lock_signal_operations=0)
with marker.open('x',encoding='utf-8')as f:json.dump(config,f,indent=2)
c=collector.connect_original()
try:
 i,o,err=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(code),timeout=120);i.close();packet_raw=o.read(collector.REMOTE_LIMIT+1);error=err.read(65537);rc=o.channel.recv_exit_status();assert len(packet_raw)<=collector.REMOTE_LIMIT and len(error)<=65536
 if rc!=0:
  value=dict(config,returncode=rc,stderr=error.decode('utf-8','replace'),stdout=packet_raw.decode('utf-8','replace'))
  with out.open('x',encoding='utf-8')as f:json.dump(value,f,indent=2)
  raise AssertionError(value['stderr'])
 packet=json.loads(packet_raw);packet['transport']=dict(returncode=rc,stderr_tail=error.decode('utf-8','replace'));summary=collector.summarize(vdispatch,packet);summary['local_state_recovery']=config;target=collector.atomic_closed(output,summary);body=target.read_bytes()
 with pointer.open('x',encoding='utf-8')as f:json.dump(dict(path=str(target),bytes=len(body),SHA256=H(body),collector_returncode=1,actual_closed_status=summary['status'],new_terminal_only_recovery_purpose=True,old_once_preserved=True,epoch=time.time()),f,indent=2)
 result=dict(config,returncode=rc,actual_parent_returncode=w['returncode'],closed_pointer=str(pointer),closed_result=str(target),closed_status=summary['status'],published_controls=summary['worker_observed']['controls'],whole_trace_exported=False,metadata_packet_bytes=len(packet_raw),source_closure=packet['closure'])
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 print(json.dumps(result,indent=2))
finally:c.close()
