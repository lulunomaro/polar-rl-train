"""One NEW concentrated functional SOURCE-input diagnostic, no preflight replay."""
from pathlib import Path
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_CONCENTRATED_ACTUAL_SOURCE_INPUT_DIAGNOSTIC_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_INPUT_DIAGNOSTIC_V1_STARTED_ONCE.json';dest=R/'discovery/good_holdout_concentrated_source_inputs_v1';assert not out.exists()and not marker.exists()and not dest.exists();H=lambda b:hashlib.sha256(b).hexdigest();audit=json.loads((R/'source_good_holdout_d4_input_assumption_audit_v1/SOURCE_AUDIT.json').read_bytes());assert audit['confirmed_finding']['strict_condition_correct']and audit['bounded_source_request']['total_small_files']==15;rootmeta=json.loads((R/'reports/GOOD_HOLDOUT_RUNTIME_ROOT_CANONICAL_METADATA_DIAGNOSIS_V2.json').read_bytes());assert len(rootmeta['rows'])==2 and all(x['canonical_equals_role']for x in rootmeta['rows']);src=R/'source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py';b=src.read_bytes();assert(len(b),H(b))==(53515,'c6be5e8acd2bd1a83f09427fb717cc1d102077cf363b67034d65d09f4e86ab0d');idx=json.loads((R/'source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json').read_bytes());e=next(x for x in idx['overlay_entries']if x['relative']=='producer_teacher_guard_v1.py');g=Path(e['path']).read_bytes();assert(len(g),H(g))==(e['bytes'],e['SHA256']);payload={src.name:b,'producer_teacher_guard_v1.py':g};pins={k:dict(bytes=len(v),SHA256=H(v))for k,v in payload.items()};B='/home/lc01/Zonglin Li/zonglin2';N=B+'/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000';payload['INPUT.json']=json.dumps(dict(native_root=N,program_inputs=pins),indent=2).encode();program=R/'good_holdout_bounded_source_inputs_diagnostic_v1.py';z=program.read_bytes();ast.parse(z);payload[program.name]=z;root=B+'/tasks/GOOD_HOLDOUT_BOUNDED_SOURCE_INPUT_DIAGNOSTIC_V1_'+str(time.time_ns());config=dict(kind='NEW_CONCENTRATED_SOURCE_INPUT_PURPOSE_NOT_PREPARE',epoch=time.time(),root=root,native_root=N,uploaded=[dict(name=k,bytes=len(v),SHA256=H(v))for k,v in payload.items()],source_guard_predicates_unmodified=True,actual_model_raw_SDK_bank_C_lock_signal_parent_operations=0)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(root)
 except FileNotFoundError:pass
 else:raise AssertionError('new diagnostic purpose exists')
 s.mkdir(root)
 for k,v in payload.items():
  with s.open(root+'/'+k,'wx')as f:f.write(v)
 code='import sys,runpy;sys.path.insert(0,%r);runpy.run_path(%r,run_name="__main__")'%(root,root+'/'+program.name);i,o,e2=c.exec_command('PYTHONDONTWRITEBYTECODE=1 '+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=300);i.close();stdout=o.read().decode('utf8','replace');stderr=e2.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 try:
  with s.open(root+'/RESULT.json','rb')as f:r=f.read(2*1024*1024+1)
  assert len(r)<=2*1024*1024;v['receipt']=json.loads(r);v['receipt_SHA256']=H(r);dest.mkdir();saved=[]
  for row in v['receipt']['input_rows']:
   if not row['core_source_input']:continue
   rel=row['captured_relative'];assert rel.startswith('captured_inputs/')and '..'not in Path(rel).parts and Path(rel).suffix in('.json','.py')
   with s.open(root+'/'+rel,'rb')as f:z=f.read(8*1024*1024+1)
   assert(len(z),H(z))==(row['bytes'],row['SHA256']);p=dest/Path(row['relative_to_native']);p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('xb')as f:f.write(z)
   saved.append(dict(local_path=str(p),bytes=len(z),SHA256=H(z),original_source_physical_read_count=row['physical_byte_reads']))
  v['local_SOURCE_captures']=saved
 except FileNotFoundError:v['receipt']=None
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 q=v['receipt'];print(json.dumps(dict(returncode=rc,status=None if q is None else q['status'],core_source_files_read=None if q is None else q['core_source_files_read'],upstream_metadata_files_read=None if q is None else q['upstream_metadata_files_read'],errors=None if q is None else q['errors'],result=str(out)),indent=2));assert rc==0 and q['status']=='PASS',stderr
finally:s.close();c.close()
