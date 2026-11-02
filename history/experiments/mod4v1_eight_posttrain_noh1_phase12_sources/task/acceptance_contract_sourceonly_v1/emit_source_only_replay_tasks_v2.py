"""ExecutableLOCAL contract/dependency validation and futuretask descriptor emitter.
This CLI NEVER launches SDK/importsTorch/SSH/steps/models. Itsoutput is SOURCE_ONLY,
not TaskReady/GO. E3alreadyconsumed160 andliveW35 are neveremitted asruntasks.
"""
from pathlib import Path
import argparse,hashlib,json,time,traceback
B=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();data=json.loads((B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json').read_bytes());matrix=json.loads((B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json').read_bytes());validated=[]
 for id,r in matrix['references'].items():
  path=Path(r['path']);assert path.suffix.lower() in ('.json','.py','.md','.txt')
  raw=path.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA'],id;validated.append(id)
 a.output.mkdir(exist_ok=False);rows=[];excluded=[]
 for plan in data['plans']:
  name=plan['lineage']
  if name in ('W35','E3'):excluded.append(dict(lineage=name,status=plan['status'],no_runtime_task_emitted=True));continue
  assert not plan['actual_SDK_permission'] and not plan['dispatch_or_model_io'] and plan['source_only_plan_emitter']
  plan=dict(plan);plan['missing_original_rule_is_not_skillpass']=True;plan['future_actual_permission']='PARENT_TO_GRANT_SEPARATELY_NOT_GRANTED_BY_THISCLI'
  dest=a.output/(name+'_FUTURE_SOURCE_ONLY_REPLAY_TASK.json')
  with dest.open('x',encoding='utf-8') as f:json.dump(plan,f,ensure_ascii=False,indent=2)
  rows.append(dict(lineage=name,path=str(dest),SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),runtime_dispatched=False))
 report=dict(kind='EXECUTED_LOCAL_SOURCE_ONLY_DESCRIPTOR_EMISSION_NO_ACTUAL',validated_reference_ids=validated,emitted=rows,excluded=excluded,SDK_Torch_SSH_model_stat_read_hash_decode=0,new_runtime_tasks_dispatched=0,sourceonly_future_notReady=True)
 with (a.output/'LOCAL_SOURCE_ONLY_EMISSION_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(emitted_sourceonly_descriptors=len(rows),excluded=excluded,validated_text_references=len(validated),SDK_model_operations=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('PLAN_EMISSION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),model_SDK_operations=0),f,indent=2)
  raise
