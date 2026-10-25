"""Actual candidate/source CPU tests, no checkpoint/raw/SDK scene/policy/physics/GPU."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;M=N.parent/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026';C=M/'candidate_v1';R=M/'reports'
try:
 sys.path.insert(0,str(C));p=C/'sampling_acceleration_installed_CPU_v2.py';spec=importlib.util.spec_from_file_location('new_landing_journal_sampler_CPU',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);result=mod.check(C,'h1')
 assert result['passed'] and result['landing_event_journal_CPU']['passed'] and result['lifetime_goal_diagnostic_CPU']['passed']
 with (R/'READONLY_LANDING_JOURNAL_CANDIDATE_V1_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_local_CPU_source_only=True,result=result,actual_new_payload_target_SDK_source_admission_pending=True,no_current79c_mutation=True),f,indent=2)
 print(json.dumps(dict(passed_local_source_CPU=True,original_counter=result['lifetime_goal_diagnostic_CPU']['passed'],new_journal=result['landing_event_journal_CPU']['passed'])))
except BaseException:
 with (R/('LANDING_JOURNAL_CPU_V1_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),not_current_training_failure=True,no_same_once_rerun=True),f,indent=2)
 raise
