from pathlib import Path
import ast,hashlib,json,time,textwrap,traceback
T=Path(__file__).resolve().parent;A=T/'H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_N1_V105_20261029';S=T/'H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_N1_V105_V2_20261029';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not S.exists();S.mkdir();(S/'code').mkdir();(S/'reports').mkdir();rows=[]
 for p in sorted((A/'code').glob('*.py')):
  s=p.read_text(encoding='utf8')
  if p.name=='fudan105_frozen_diag_driver_v1.py':
   old="require(all(torch.isfinite(v).all() for v in objective.values()),'finite existing own-flat objective required')";assert s.count(old)==1;s=s.replace(old,"require(nested_finite(objective),'finite nested Fudan reward and metadata required')")
   marker=' # First-action sensitivity uses frozen models';a=s.index(marker);b=s.index(" with (out/'FROZEN_FUDAN270_32STEP_FIRST_ACTION_SENSITIVITY_ACTUAL.json')",a)
   block=s[a:b];body=block[block.index(' sensitivity=[]'):];body=textwrap.dedent(body)
   s=s[:a]+' sensitivity=frozen_first_action_sensitivity(paired,bridge,pi,wm,critic,model_args)\n'+s[b:]
   helper='''
def nested_finite(value):
 import torch,math
 if torch.is_tensor(value):return bool(torch.isfinite(value).all())
 if isinstance(value,dict):return all(nested_finite(x) for x in value.values())
 if isinstance(value,(tuple,list)):return all(nested_finite(x) for x in value)
 if isinstance(value,float):return math.isfinite(value)
 return value is None or isinstance(value,(str,int,bool))

def frozen_first_action_sensitivity(paired,bridge,pi,wm,critic,model_args):
 """Frozen original32-step equations; derivative wrt first imagined action only.

 No policy-parameter gradient, optimizer, physical counterfactual or skill claim.
 """
 import torch
 from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack
'''+textwrap.indent(body,' ')+' return sensitivity\n'
   s+=helper
  if p.name=='run_native105_frozen_flat_WM_N1_once.py':
   s=s.replace('frozen flat episode','frozen actual270mm step episode').replace('exact already admitted97 runtime','exact admitted103 runtime for qualified104 output')
   needle="  out.mkdir();put(out,'ENTRY_STARTED_BEFORE_APP_ACTUAL.json'" # admission is before App/model, unchanged.
   # Pin the explicit human shared-GPU contract, never infer free from old snapshots.
   old="  authority()\n  for path,mode"
   assert s.count(old)==1;s=s.replace(old,"  require(q['resource_policy']==dict(schema='mod4.user_allowed_light_compute.20261029.v1',free_MiB_strictly_above=15669,utilization_percent_max=30,compute_UUID_rows_allowed=True,other_processes_untouched=True),'exact human shared-GPU policy')\n  authority()\n  for path,mode")
  ast.parse(s);q=S/'code'/p.name;q.write_text(s,encoding='utf8');rows.append(dict(original_path=str(p),original_SHA=H(p),new_path=str(q),SHA=H(q)))
 entry=A/'run_NEW105_qualified104_fixed_Fudan270_motion_WM_case_UNUSED_once.py';s=entry.read_text(encoding='utf8').replace('_20261029r1','_20261029r2').replace('after actual97 closed','after actual104 closed').replace('new98_frozen_diag','new105_frozen_diag').replace('frozen98_secret_memory_only','frozen105_secret_memory_only')
 q=S/entry.name;ast.parse(s);q.write_text(s,encoding='utf8')
 for n in ast.parse(s).body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PRE','RUN') for t in n.targets):ast.parse(ast.literal_eval(n.value))
 put(S/'V1_SOURCE_REVIEW_REFUSAL_BEFORE_EXECUTION_AND_V2_REPAIR.json',dict(epoch=time.time(),V1_entry_UNUSED_no_remote_or_model=True,reason='Old flat driver assumed every objective value was a tensor; actual Fudan objective is nested dictionaries/metadata and would fail the first-step finite reader. Caught in source review before any App/model/control.',repair='Recursive finite tensor and finite numeric metadata verification, no reward value/gradient/action/physics change; extracted same32-step first-action sensitivity helper for analytic source-CPU verification.',source_rows=rows,entry_SHA=H(q),all_AST_and_embedded_CODE_passed=True,extra_whole_model_CPU_loads=0))
 # Preserve local exploration/reader errors as errors, not GPU failures.
 put(S/'LOCAL_SOURCE_READER_ERRORS_RETAINED.json',dict(errors=[dict(tool='exec_command',error='PowerShell pipeline after foreach without subexpression: An empty pipe element is not allowed',effect='first local workorder read refused; corrected by assigning foreach result to a variable'),dict(tool='Get-Content',error='optional guessed frozen_native98_motion_WM_instrument_v1.py absent',effect='actual four code filenames then enumerated with directory read'),dict(tool='Get-Content',error='native_flat90_source_guard_v1.py guessed below source; actual file is payload root',effect='located via rg --files before reading actual guard'),dict(tool='rg/Get-Content',error='guessed source/sm_deps/supermimic_wheel_leg_v3/networks.py absent; actual source/supermimic_wheel_leg_v3/networks.py',effect='located via rg --files; no model/GPU/remote action')],original_errors_not_reclassified_as_training_or_model_failures=True))
 print(json.dumps(dict(prepared_source_only=True,folder=str(S),entry_SHA=H(q))))
if __name__=='__main__':
 try:main()
 except BaseException:
  if S.exists():put(S/('SOURCE_V2_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_model_or_remote=True))
  raise
