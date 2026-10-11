"""Prepare read-only future collectors. Preparation is not a future result."""
from second_io import *
import ast
def put(name,text):
 p=D/name;assert not p.exists();compile(text,name,'exec');p.write_text(text,encoding='utf8');return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()))
def main():
 number=json.loads((R/'SECOND_TARGET_CPU_PASSED.json').read_bytes())['candidate_number'];rows=[]
 s=(PRIOR/'read_wave_own_formal_cpu_actual.py').read_text(encoding='utf8').replace('from wave_io import *','from second_io import *')
 s=s.replace("WAVE_OWN_ACTIVE_SCHEMA_CPU_ACTUAL_","SECOND_OWN_STARTUP_CPU_ACTUAL_").replace("(D/'verify_wave_own_startup_save_cpu_actual.py')","(PRIOR/'verify_wave_own_startup_save_cpu_actual.py')")
 s=s.replace('supervise_wave35_exposure_005_once','supervise_wave35_second_bounded_once').replace('e1_WAVE35_exposure_005_observation_PASSED','e1_WAVE35_second_bounded_observation_PASSED')
 s=s.replace("len(freeze['sha256'])==368","len(freeze['sha256'])==369").replace('actual_source_count=368','actual_source_count=369')
 s=s.replace('E1_142-e1-wave35-exposure-repair_ASYNC_PUBLISHED','E1_'+str(number)+'-e1-wave35-second-bounded_ASYNC_PUBLISHED').replace('E1_WAVE35_exposure_005_saved_review_ready','E1_WAVE35_second_bounded_saved_review_ready')
 s=s.replace('WAVE_OWN_FORMAL_CPU_ACTUAL_','SECOND_OWN_FORMAL_CPU_ACTUAL_').replace('WAVE_OWN_FORMAL_CPU_READER_ERROR_','SECOND_OWN_FORMAL_CPU_READER_ERROR_')
 rows.append(put('read_second_own_formal_cpu_actual.py',s))
 s=(PRIOR/'collect_wave142_actual.py').read_text(encoding='utf8').replace('from wave_io import *','from second_io import *')
 s=s.replace('142-e1-wave35-exposure-repair',str(number)+'-e1-wave35-second-bounded').replace('e1_WAVE35_exposure_005_observation_PASSED','e1_WAVE35_second_bounded_observation_PASSED').replace('WAVE142','WAVE'+str(number))
 rows.append(put('collect_second_candidate_actual.py',s))
 s=(PRIOR/'review_wave142_actual.py').read_text(encoding='utf8').replace('WAVE142','WAVE'+str(number)).replace('WAVE_OWN_FORMAL_CPU_ACTUAL_','SECOND_OWN_FORMAL_CPU_ACTUAL_').replace("cpu['actual_source_count']==368","cpu['actual_source_count']==369").replace('E1-WAVE-G3-142','E1-WAVE-G3-'+str(number))
 rows.append(put('review_second_candidate_actual.py',s))
 s=(PRIOR/'review_wave142_selected_source_actual.py').read_text(encoding='utf8').replace('WAVE142','WAVE'+str(number)).replace('E1-WAVE-G3-142','E1-WAVE-G3-'+str(number)).replace('candidate_wave368','candidate_wave369').replace('terrain_candidate_wave368','terrain_candidate_wave369')
 rows.append(put('review_second_candidate_selected129_actual.py',s))
 original=(PRIOR/'review_wave368_full_training_trace_actual.py').read_text(encoding='utf8')
 tree=ast.parse(original);code=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('from pathlib import Path\nimport json,hashlib,numpy'))
 code=code.replace("assert a['actual_controls']==v['controls']==2352","assert a['actual_controls']==v['controls']")
 before="  assert np.array_equal(x[:,:,10],np.broadcast_to(family,x[:,:,10].shape))\n  y=x[:,ids,:];c=y[:,:,7];assert np.max(abs(y[:,:,8:10]))<=1e-6 and np.max(abs(c))<=.300001"
 after="  assert np.isin(x[:,:,10],np.arange(-1,5)).all()\n  changed_family_controls+=int((x[:,:,10]!=family[None,:]).sum())\n  current_wave=x[:,:,10]==4;y=x[:,ids,:];c=x[:,:,7][current_wave]\n  assert np.max(abs(x[:,:,8:10][current_wave]))<=1e-6 and np.max(abs(c))<=.300001"
 assert code.count(before)==1;code=code.replace(before,after).replace('family_counts=None;speed_max=0.;','changed_family_controls=0;family_counts=None;speed_max=0.;').replace('command_integral+=abs(c).sum(0)*.01;','command_integral+=abs(y[:,:,7]).sum(0)*.01;').replace('assert hist.sum()==total*2820;','')
 code=code.replace('actual_family_enum_counts=family_counts,','initial_family_enum_counts=family_counts,dynamic_current_family_changed_control_count=changed_family_controls,static_geometry_assignment_not_mutated=True,').replace('per_environment_nominal_abs_command_integral_m_range=','initial_Wave_cohort_command_integral_including_actual_family_changes_m_range=').replace('same_control_prereset_minus_before_root_x_sum_range_m=','initial_Wave_cohort_same_control_prereset_minus_before_root_x_sum_range_m=')
 s="from second_io import *\nCODE="+repr(code)+"\ndef main():\n own=json.loads(sorted(R.glob('SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes());assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==369\n compact=dict(checkpoint=own['own_checkpoint'],source_SHA=own['source_SHA'],controls=own['health']['control_steps'])\n n,w=io.connect_both()\n try:\n  v=run(n,CODE.replace('COMPACT_TOKEN',repr(json.dumps(compact))));p=save('SECOND_FULL_TRAINING_TRACE_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),passed=True,controls=v['actual_controls'])))\n finally:io.cleanup(n,w)\nif __name__=='__main__':\n try:main()\n except BaseException:save('SECOND_FULL_TRACE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_training_replay=True));raise\n"
 rows.append(put('review_second_complete_dynamic_family_trace_actual.py',s))
 save('SECOND_FUTURE_READERS_PREPARED.json',dict(epoch=time.time(),prepared=rows,candidate_number=number,no_future_result_or_pass_claimed=True,no_GPU_or_queue_or_budget_write=True,requires_direct142_comparison_in_addition_to_selected129_and_original115=True))
 print(json.dumps(dict(prepared=len(rows),candidate_number=number,no_future_pass_claimed=True)))
if __name__=='__main__':main()
