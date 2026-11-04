"""One controller and one unchanged original holdout parent after real static stage.
Popen is not resource/SDK/skill admission. Original parent retains all ownership.
"""
from pathlib import Path
import sys,json,hashlib,shlex,time,importlib.util
R=Path(__file__).resolve().parent;D=R/'source_good_holdout_lifecycle_routes_v5';out=R/'reports/GOOD_HOLDOUT_D7_SEED20260929_ORIGINAL_PARENT_DISPATCH_ONCE.json';typed=R/'reports/GOOD_HOLDOUT_D7_SEED20260929_TYPED_PARENT_DISPATCH_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D7_SEED20260929_PARENT_DISPATCH_STARTED_ONCE.json';assert not any(p.exists()for p in(out,typed,marker));H=lambda b:hashlib.sha256(b).hexdigest();sys.dont_write_bytecode=True
def _require_published_seed30_qualified():
 summary_raw=(R/'reports/GOOD_HOLDOUT_D7_SEED20260930_QUALIFIED_SUMMARY_V1.json').read_bytes();summary=json.loads(summary_raw);assert summary['kind']=='QUALIFIED_GOOD_ORIGINAL_CONDITIONAL_HOLDOUT_SINGLE_SEED_METADATA_SUMMARY_V1'and summary['seed']==20260930 and summary['passed_closed_execution']is True and summary['errors']==[]and summary['producer_grade_rewritten']is False
 info=summary['closed_metadata'];p=Path(info['path']);assert p.is_absolute()and p.resolve().is_relative_to((R/'reports').resolve())and p.name=='CLOSED_RESULT.json'and p.is_file()and not p.is_symlink();raw=p.read_bytes();assert(len(raw),H(raw))==(info['bytes'],info['SHA256']);closed=json.loads(raw);assert closed['kind']=='GOOD_HOLDOUT_CLOSED_RESULT_V1'and closed['seed']==20260930 and closed['passed_closed_good_reference_execution']is True and closed['errors']==[]and closed['root']==summary['root']and closed['requested_roles']==['CURB_PROTECTED878','SLOPE135']
 gates=closed['gates'];assert type(gates)is dict and gates and all(v is True for v in gates.values())and summary['gates']==gates;assert all(gates[k]is True for k in('producer_original_source_grade','original_ownchild_actual_waits','original_both_EX_released','independent_outer_actual_Popen_wait'))
 docs=closed['metadata']['documents'];end=docs['PARENT_EXIT_SCOPE.json'];outer=docs['GOOD_HOLDOUT_PARENT_WAITED_ACTUAL_V1.json'];waits=closed['own_child_waits'];assert waits==summary['own_child_waits']==end['child_waits']and len(waits)==2 and {v['role']for v in waits}=={'CURB_PROTECTED878','SLOPE135'}and all(v['actual_waited']is True and type(v['returncode'])is int and v['returncode']==0 for v in waits)
 assert end['all_own_children_waited']is True and end['original_single_GPU_private_EX_released']is True and end['original_global_finite_EX_released']is True and end['errors']==[]and type(end['canonical_writes'])is int and end['canonical_writes']==0
 assert outer['actual_parent_p_wait_returned']is True and type(outer['returncode'])is int and outer['returncode']==closed['actual_outer_parent_returncode']==summary['actual_outer_parent_returncode']==0 and outer['controller_errors']==[]and outer['original_parent_resource_close_wait_not_replaced']is True and type(outer['actual_native_parent_Popen_calls'])is int and outer['actual_native_parent_Popen_calls']==1 and outer['root']==closed['root']and outer['seed']==20260930
_require_published_seed30_qualified()
stage=json.loads((R/'reports/GOOD_HOLDOUT_D7_SEED20260929_ACTUAL_STAGE_V1.json').read_bytes());snapshot_raw=(R/'reports/GOOD_HOLDOUT_D7_SEED20260929_RESOURCE_PRELAUNCH_SNAPSHOT_V1.json').read_bytes();snap=json.loads(snapshot_raw);a=snap['actual'];c=a['canonical_summary'];assert stage['returncode']==0 and stage['receipt']['materialized']and stage['receipt']['metadata_validation']['passed']and stage['receipt']['parent_launches']==0 and stage['seed']==20260929;assert snap['root']==stage['root']and snap['stage_receipt_SHA256']==stage['stage_receipt_SHA256']and snap['returncode']==0 and a['original_relevant_leases_clear']and a['original_frozen_resources_observed_clear']and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['active_segment']is None and c['remaining_training_seconds']>c['finite_minimum_remaining_seconds']and len(a['required_project_lock_rows'])==4 and all(not x.get('missing')and x['records']==[]for x in a['required_project_lock_rows'])
raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2446,'ddfa3f19c4be7961003207ac6e6c79f96f8befad97a91a2477e0589c37e0ab6d');seal=json.loads(raw);assert len(seal['files'])==13 and seal['root_SHA256']=='4ec4589ea395eed235c2690a05b250cdecd9b61a37dcd9ccf49ce0b42a9e3f89';sources={}
for row in seal['files']:
 name=row['name'];assert Path(name).name==name;b=(D/name).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);sources[name]=b
sp=importlib.util.spec_from_file_location('_parent_good_d7_dispatch_contract',D/'good_holdout_contract.py');C=importlib.util.module_from_spec(sp);sp.loader.exec_module(C);C.require_final_pins();C.root_identity(stage['root'],stage['group_id'],20260929,stage['GPU_UUID']);ops=stage['source_input']+'/GOOD_LIFECYCLE_V5_SOURCE';config=dict(kind='GOOD_HOLDOUT_D7_SEED29_ONE_ORIGINAL_PARENT_POPEN_NOT_ADMISSION',epoch=time.time(),root=stage['root'],group_id=stage['group_id'],seed=20260929,GPU_UUID=stage['GPU_UUID'],stage_receipt_SHA256=stage['stage_receipt_SHA256'],resource_snapshot_SHA256=H(snapshot_raw),readonly_snapshot_not_lease_original_parent_fresh_gates=True,operations_source_root=ops,controller_source_SHA256=C.CONTROLLER_SOURCE_PIN[1],parent_source_SHA256=C.PARENT_PIN[1])
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
client=connect72();s=client.open_sftp();B='/home/lc01/Zonglin Li/zonglin2'
try:
 try:s.lstat(ops)
 except FileNotFoundError:pass
 else:raise AssertionError('One-use controller source directory already exists')
 s.mkdir(ops)
 for name in('good_holdout_contract.py','good_holdout_parent_actual_wait_controller_v1.py'):
  with s.open(ops+'/'+name,'wx')as f:f.write(sources[name])
 argv=[B+'/run-python.sh','-u','-B',ops+'/good_holdout_parent_actual_wait_controller_v1.py','--root',stage['root'],'--group-id',stage['group_id'],'--seed','20260929','--gpu-uuid',stage['GPU_UUID'],'--stage-sha',stage['stage_receipt_SHA256']]
 code="""from pathlib import Path
import sys,json,subprocess,time,hashlib
root=Path(ROOT);ops=Path(OPS)
for name,pin in PINS.items():
 raw=(ops/name).read_bytes();assert (len(raw),hashlib.sha256(raw).hexdigest())==tuple(pin)
sys.path.insert(0,str(ops));import good_holdout_contract as C
for name in(C.STARTED,C.DISPATCH,C.WAITED,C.ERROR,'PARENT_STARTED.json','PARENT_EXIT_SCOPE.json'):assert not(root/name).exists()
log=(ops/'OUTER_CONTROLLER_STDOUT_STDERR.log').open('xb');child=subprocess.Popen(ARGV,cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
text=Path('/proc') .joinpath(str(child.pid),'stat').read_text();vals=text[text.rfind(')')+2:].split();own=dict(pid=child.pid,linux_start_ticks=vals[19],state=vals[0]);receipt=None
for _ in range(120):
 if(root/C.DISPATCH).exists():receipt=json.loads((root/C.DISPATCH).read_bytes());break
 if child.poll()is not None:break
 time.sleep(.25)
result=dict(controller=own,controller_Popen_calls=1,controller_returncode_if_already_exited=child.poll(),dispatch=receipt,handshake_only_not_original_wait_deadline=True)
if receipt is not None:C.validate_dispatch(receipt)
print(json.dumps(result));assert receipt is not None,'Controller has no published original-parent dispatch; inspect own log, do not replay'
""".replace('ROOT',repr(stage['root'])).replace('OPS',repr(ops)).replace('PINS',repr({n:(len(sources[n]),H(sources[n]))for n in('good_holdout_contract.py','good_holdout_parent_actual_wait_controller_v1.py')})).replace('ARGV',repr(argv))
 i,o,e=client.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr,dispatcher_Cwrites_lock_model_SDK_or_foreign_signal_operations=0)
 if rc==0:
  remote=json.loads(stdout);C.validate_dispatch(remote['dispatch']);v['receipt']=remote
  with typed.open('x',encoding='utf8')as f:json.dump(remote['dispatch'],f,indent=2)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps(v,indent=2));assert rc==0,stderr
finally:s.close();client.close()
