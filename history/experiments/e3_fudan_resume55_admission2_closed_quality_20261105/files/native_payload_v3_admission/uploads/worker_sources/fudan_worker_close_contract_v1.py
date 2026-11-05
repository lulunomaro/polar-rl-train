"""FDN-only qualification AFTER the original owner has really waited its child.
No selected/new model byte read or SDK call; one output stat checks producer size.
This is execution/save/closure qualification, never a skill acceptance predicate.
"""
from pathlib import Path
import hashlib,json,time,os
KIND='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1'
def qualify_actual_wait(job,returncode,final):
 J=Path(job).resolve();P=J/'production';checks={};error=None
 try:
  fp=P/'FDN_FINAL.json';raw=fp.read_bytes();f=json.loads(raw);intent=json.loads((P/'FDN_APP_FAST_CLOSE_INTENT.json').read_bytes());latest=json.loads((P/'FDN_LATEST_COMPLETE_SAVE.json').read_bytes());g=json.loads((J/'GO_PRODUCTION.json').read_bytes());c=f['counters'];native=f['native_counters'];s=f['latest_complete_save'];b=intent['original_bound_close'];dest=Path(s['path']).resolve();stat=dest.stat()
  checks.update(actual_child_returncode_zero=returncode==0,kind=f['kind']==intent['kind']==KIND,run=f['run']==g['run_id'],role=f['role']=='E3',actual_original_parent=f['parent_pid']==os.getpid(),actual_parent_binding=f['resource_binding']['actual_parent_pid']==os.getpid(),final_qualified=f['final']is True,full_save=f['complete_save']is True,error_absent=f['error']is None and f['close_errors']==[] and intent['error_before_close']is None and intent['close_errors']==[],policy_and_encoder_optimizer_steps=c['policy_optimizer_steps']>0 and c['encoder_optimizer_steps']>0,actual_native_controls=native['actual_native_policy_steps']>0,checkpoint_receipts=s==latest==intent['latest_complete_save'],checkpoint_exists_and_size=dest.is_relative_to(P)and stat.st_size==s['bytes'],producer_fullstate_components=s['fullstate_required_components_complete']and s['both_Adam_states_present']and s['model_and_all_required_RNG_present']and s['new_asset_and_fresh_D0_D7_state_present'],complete_final_sha=hashlib.sha256(raw).hexdigest()==intent['final_sha256'],original_fast_close=b['fast_shutdown']is True,env_close_returned=intent['env_close_returned']is True,final_intent_qualified=intent['worker_final_qualified']is True,worker_identity=f['worker_pid']==intent['worker_pid'],no_runtime_error_files=not any((P/n).exists()for n in('FDN_APP_CLOSE_ERROR.json','FDN_NATIVE_ERROR.json','FDN_SAVE_ERROR.json')))
 except Exception as exc:error=repr(exc)
 result=dict(kind=KIND,epoch=time.time(),original_owner_pid=os.getpid(),actual_child_wait_returncode=returncode,qualified=bool(error is None and checks and all(checks.values())),checks=checks,error=error,skill_acceptance_claim=False,new_model_byte_reads=0,new_model_stat_operations=1 if error is None else None)
 (P/'FDN_PARENT_WAIT_QUALIFICATION.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8');return result['qualified']
