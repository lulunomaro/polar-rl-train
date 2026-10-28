from pathlib import Path
import ast,copy,hashlib,json,shutil,time,sys,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';OLD=L/'TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1';C=L/'TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,s):p.write_text(s,encoding='utf8')
def assign(s,name,value):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(value)+'\n'+''.join(lines[x.end_lineno:])
def main():
 assert not C.exists();C.mkdir();R=C/'reports';R.mkdir();prep=read(N/'reports/TWO101_EXACT_PRODUCER_REFERENCE_FIX_PAYLOADS_PREPARED_ACTUAL.json');actual=read(N/'reports/TWO101_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json');assert actual['passed'];old=read(OLD/'reports/TWO100_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json');public=copy.deepcopy(old);runid='TWO101_PRODUCER_REFERENCE_FIXED_NATIVE20_'+str(time.time_ns());stage='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO101_PRODUCER_FIXED_FLAT20_2610v101'
 public.update(run_id=runid,owner_root=stage+'/owner',owner_source=str(C/'owner'),expected_closed_remaining=524081.4115035534,node_roots={},node_sources={},task_templates={});protocols={}
 for mode,row in prep['payloads'].items():
  key=row['logical_slot'];spec=public['experts'][key];result=actual['results'][mode];v=result['value'];assert result['passed'] and result['proof']['actual_waited'] and result['proof']['returncode']==0 and v['source101_metadata_only_producer_reference_fix_passed'] and v['source101_no_saved_weights_or_norms_or_opts_redecoded']
  spec.update(run_id=runid,job_root=row['job_root'],CPU_path=row['job_root']+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=row['job_root']+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'],payload_manifest_SHA=row['manifest_SHA'],source_contract_SHA=row['source_contract_SHA'],payload_manifest_path=row['job_root']+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=row['job_root']+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',source101_metadata_only_producer_reference_fix=True,source100_original_fullstate_CPU_SHA=row['source100_original_CPU_SHA'])
  name='h1_next72_protocol_actual95_v2.py' if key=='h1' else 'h1_seed28_next72_protocol_v100.py';s=(OLD/'owner'/name).read_text();s=assign(s,'JOB',row['job_root'])
  a=" require(s.get('key')==KEY";i=s.index(a);end=s.index('\n',i);s=s[:end]+"\n require(s.get('source101_metadata_only_producer_reference_fix') is True and s.get('source100_original_fullstate_CPU_SHA')=="+repr(row['source100_original_CPU_SHA'])+",'exact101 reference-label code admission')"+s[end:]
  a=" require(v.get('passed') is True";i=s.index(a);end=s.index('\n',i);s=s[:end]+"\n require(v.get('source101_metadata_only_producer_reference_fix_passed') is True and v.get('source101_no_saved_weights_or_norms_or_opts_redecoded') is True and v.get('source100_original_fullstate_CPU_SHA')==s['source100_original_fullstate_CPU_SHA'],'actual101 metadata extension and original fullstate CPU')"+s[end:]
  a="fields=('flat_jump_target_m',";assert s.count(a)==1;s=s.replace(a,"fields=('source101_metadata_only_producer_reference_fix','source100_original_fullstate_CPU_SHA','flat_jump_target_m',")
  a="for k in ('flat_jump_target_m',";assert s.count(a)==1;s=s.replace(a,"for k in ('source101_metadata_only_producer_reference_fix','source100_original_fullstate_CPU_SHA','flat_jump_target_m',")
  ast.parse(s);protocols[name]=s;public['node_roots'][key]=stage+'/node_'+key;public['node_sources'][key]=str(C/('node_'+key))
 for role in ['owner','node_h1','node_h1_seed28']:
  d=C/role;d.mkdir()
  for p in (OLD/role).iterdir():
   if p.is_file() and p.suffix=='.py':shutil.copy2(p,d/p.name)
  for name,s in protocols.items():write(d/name,s)
  assert (d/'three_slot_common_v1.py').read_bytes()==(OLD/role/'three_slot_common_v1.py').read_bytes()
  assert (d/'forwarded_original_owner_control_v1.py').read_bytes()==(OLD/role/'forwarded_original_owner_control_v1.py').read_bytes()
 assert (C/'owner/two95_finite_owner_authority72_v1.py').read_bytes()==(OLD/'owner/two95_finite_owner_authority72_v1.py').read_bytes()
 for key,spec in public['experts'].items():
  d=Path(public['node_sources'][key]);put(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(d.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json');public['task_templates'][key]=copy.deepcopy(spec)
 sys.path.insert(0,str(C/'owner'));import mixed72_next_protocol_v1 as dispatch;assert dispatch.validate_schedule(public);negative=0
 for mode,row in prep['payloads'].items():
  spec=public['experts'][row['logical_slot']];p=dispatch.module_for(spec);v=actual['results'][mode]['value'];assert p.validate_cpu_value(v,spec)
  for field in ['source101_metadata_only_producer_reference_fix_passed','source100_original_fullstate_CPU_SHA','flat_jump_target_m']:
   bad=copy.deepcopy(v);bad[field]=False if field.endswith('passed') else 'bad'
   try:p.validate_cpu_value(bad,spec)
   except (ValueError,KeyError,TypeError):negative+=1
   else:raise AssertionError('uncorrected CPU accepted '+field)
 activation=(OLD/'activate_two100_actual20cm_original_single_writer_once.py').read_text().replace('TWO100_','TWO101_');ast.parse(activation);write(C/'activate_two101_producer_fixed_native20_original_single_writer_once.py',activation)
 for p in C.rglob('*.py'):ast.parse(p.read_bytes())
 put(R/'TWO101_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public);put(R/'TWO101_ORIGINAL_WRITER_BYTES_AND_METADATA_EXTENSION_ROUTING_SOURCE_CPU_ACTUAL.json',dict(passed=True,original_owner_common_and_forward_bytes_exact=True,actual_metadata_extension_two_sources_bound=True,uncorrected_or_wrongtarget_CPU_negative_rejected=negative,no_model_read_GPU_or_network=True,no_GO=True))
 put(C/'FROZEN_UNUSED_TWO101_NATIVE20_ORIGINAL_OWNER_INDEX_V1.json',dict(epoch=time.time(),frozen=True,unused=True,files=[dict(relative=p.relative_to(C).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(prepared=True,run_id=runid,actual_CPU_bound=True,original_writer_bytes_exact=True,no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (C/'reports').is_dir():put(C/'reports/TWO101_CONTROLLER_PREPARER_ORIGINAL_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),no_network=True))
  raise
