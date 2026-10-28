from pathlib import Path
import copy,hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;R=N/'reports';C=N/'controllers'
def read(p):return json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 result=read(R/'NATIVE95_ACTUAL_SOURCE_SDK_CPU_AND_RESOURCE_RETURNED_ACTUAL.json')
 assert result['passed'] and result['actual_finite_returned'] and result['actual_CPU_waited_EXIT0']
 original=C/'h1_next72_protocol.py';s=original.read_text('utf8')
 needle="require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual typed sourceCPU')"
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n require(v.get('native_learning_seed')==s['native_learning_seed']==27 and v.get('task_focused_real_replay')==s['task_focused_real_replay'],'actual selected sampling and saved learning seed CPU binding')",1)
 selected=C/'h1_next72_protocol_actual95_v2.py'
 with selected.open('x',encoding='utf8') as f:f.write(s)
 spec=copy.deepcopy(read(R/'NATIVE95_SOURCE_PREPARED_ACTUAL.json')['h1_spec_pending_actual_CPU_and_controller'])
 spec.update(source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'])
 m=importlib.util.spec_from_file_location('selected95_protocol_source',selected);p=importlib.util.module_from_spec(m);m.loader.exec_module(p)
 p.validate_cpu_value(result['value'],spec);p.validate_waited_value(result['proof'],spec)
 cases=[]
 for key,value in [('source_SHA','0'*64),('native_learning_seed',28),('task_focused_replay_source_CPU_passed',False),('execution_backend','source210'),('task_focused_real_replay',{})]:
  wrong=copy.deepcopy(result['value']);wrong[key]=value
  try:p.validate_cpu_value(wrong,spec)
  except ValueError:cases.append(key)
  else:raise AssertionError('incorrect CPU accepted '+key)
 put(R/'NATIVE95_ACTUAL_CPU_BOUND_SPEC_PENDING_CONTROLLER_SEAL.json',dict(passed=True,epoch=time.time(),spec=spec,selected_protocol=str(selected),selected_protocol_SHA=H(selected),
  actual_CPU_report_SHA=result['proof']['report_SHA'],actual_waited_proof_SHA=result['proof_SHA'],actual_report_value=result['value'],actual_waited_proof=result['proof'],
  original_protocol_retained=str(original),new_v2_delta='Explicit CPU value binding for task focus and saved learner seed; all original protocol guards unchanged',rejected_wrong_CPU_fields=cases,
  pending_fields=['manifest_SHA from actual new controller manifest','run_id and authenticated owner registration at activation'],no_dummy_manifest_SHA=True,no_owner_or_GO_or_fee=True))
 print(json.dumps(dict(passed=True,actual_CPU_bound=True,negative_CPU_fields=len(cases),controller_and_GO_pending=True)))

if __name__=='__main__':main()
