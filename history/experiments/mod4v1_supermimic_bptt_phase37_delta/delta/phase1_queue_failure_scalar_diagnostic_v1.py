"""NEW functional diagnosis of the prior decoded queue contradiction.
One own worker FINAL open/hash/decode, whole immutable cache; no group FINAL,
model, SDK, policy, environment, canonical ledger or resource operations.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
PURE_PIN=(41739,'2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979')
CAPTURE_ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_ADMISSION2_20261104_005511_1793724911451546000'
WORKER_PIN=(15060087,'a0c20af6a3c0e727124363337e8811156758f6cb944a67ee1cc2050298ea8a78')
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);a=p.parse_args();ip=Path(a.input);assert ip.resolve().parent==HERE and ip.name=='INPUT_METADATA.json';v=json.loads(ip.read_bytes());assert v['kind']=='NEW_OWN_QUEUE_CONTRADICTION_FUNCTIONAL_LOCATOR_V1'and v['qualified_closed_execution']is True and v['capture_root']==CAPTURE_ROOT
 assert v['prior_science_status']=='CONTRADICTED'and v['prior_queue_detail']=='typed integer/range'and v['closed_result_SHA256']=='02cf9d4b2e11c3f53e3101fe8f42624bda6fde52e135076a9290b7ea668c6025'
 assert(v['worker_final']['bytes'],v['worker_final']['SHA256'])==WORKER_PIN
 for name,pin in [('capture_evidence_verifier_v1.py',dict(bytes=PURE_PIN[0],SHA256=PURE_PIN[1])),('queue_failure_locator_v1.py',v['locator_pin'])]:
  b=(HERE/name).read_bytes();assert len(b)==pin['bytes']and H(b)==pin['SHA256']
 sys.path.insert(0,str(HERE));import capture_evidence_verifier_v1 as pure;import queue_failure_locator_v1 as locator
 assert not any(n.split('.')[0]in{'torch','isaacsim','isaaclab','omni','warp','pxr','paramiko','fcntl'}for n in sys.modules)
 root=Path(CAPTURE_ROOT);assert root.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks')and not root.is_symlink();path=root/'cases/E3/FINAL.json';assert path.resolve().is_relative_to(root.resolve())and not path.is_symlink()
 cache={};counts=dict(physical_worker_FINAL_opens=0,original_worker_byte_hashes=0,worker_JSON_decodes=0)
 def whole():
  if 'worker'not in cache:
   counts['physical_worker_FINAL_opens']+=1
   with path.open('rb')as f:b=f.read(64*1024*1024+1)
   counts['original_worker_byte_hashes']+=1;sha=H(b);assert(len(b),sha)==WORKER_PIN
   x=json.loads(b);counts['worker_JSON_decodes']+=1;assert type(x)is dict;cache['worker']=x
  return cache['worker']
 worker=whole();assert worker['group_id']==root.name and worker['passed_execution']is True and worker['controls']==64 and worker['physics_callbacks']==512 and worker['feedback_samples']==128 and worker['model_PT_reads']==worker['training_updates']==worker['optimizer_updates']==0
 original_canonical=pure.digest(worker);assert original_canonical==v['worker_canonical_SHA256'];keys=set(vars(pure));functions={name:vars(pure)[name]for name in locator.API_LINES};calls=[];code=pure.actuation_component.__code__;old_profile=sys.getprofile();assert old_profile is None
 def profile(frame,event,arg):
  if event=='call'and frame.f_code is code:
   assert frame.f_locals.get('final')is worker or any(x is worker for x in frame.f_locals.values());calls.append(1)
 sys.setprofile(profile)
 try:result=locator.locate_queue_failure(worker,pure)
 finally:sys.setprofile(old_profile)
 assert len(calls)==1 and all(x==1 for x in counts.values())and whole()is worker and pure.digest(worker)==original_canonical and result['input_unchanged']and result['canonical_before_SHA256']==result['canonical_after_SHA256']and keys==set(vars(pure))and all(vars(pure)[k]is x for k,x in functions.items())
 assert result['gate1']=='UNKNOWN'and result['exact']is False and result['stage2_GO']is False
 output=dict(kind='ACTUAL_OWN_QUEUE_CONTRADICTION_SCALAR_DIAGNOSIS_V1',epoch=time.time(),capture_root=CAPTURE_ROOT,source_scope='NEW_FUNCTIONAL_EXCEPTION_LOCALIZATION_NOT_STATUS_LABEL_GIT_OR_NATIVE_REPLAY',original_worker_bytes=WORKER_PIN[0],original_worker_SHA256=WORKER_PIN[1],original_worker_canonical_SHA256=original_canonical,**counts,original_actuation_component_calls=len(calls),cache_reused_identity=True,whole_input_unchanged=True,whole_group_FINAL_reads=0,original_pure_module_unchanged=True,raw_trace_payload_exported=False,actual_model_SDK_GPU_C_lock_or_signal_operations=0,previous_application_report_changed=False,locator=result,gate1='UNKNOWN',exact=False,stage2_GO=False)
 print(json.dumps(output,allow_nan=False))
if __name__=='__main__':main()
