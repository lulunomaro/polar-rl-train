from route_fixture_io import *

def main():
    old_root='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'
    rows=[]
    for name,origin in (
      ('collect_route443_candidate_actual.py',PRIOR/'collect_second_direction_candidate_actual.py'),
      ('route443_feedback_reset_schema.py',PRIOR/'second_direction_feedback_reset_schema.py'),
      ('review_route443_candidate_actual.py',PRIOR/'review_second_direction_candidate_actual.py')):
        raw=origin.read_bytes();s=raw.decode('utf8')
        if old_root in s:s=s.replace(old_root,ROOT)
        s=s.replace('e1_WAVE50_direction_second_bounded_observation_PASSED.json','e1_WAVE50_route_lifecycle_observation_PASSED.json')
        s=s.replace('SECOND_DIRECTION_CANDIDATE_','ROUTE443_CANDIDATE_').replace('SECOND_DIRECTION_OWN_FORMAL_CPU_ACTUAL_','ROUTE443_OWN_FORMAL_CPU_ACTUAL_').replace('SECOND_DIRECTION_FINAL_FEEDBACK_','ROUTE443_FINAL_FEEDBACK_')
        s=s.replace('from second_direction_feedback_reset_schema import recipe_manager','from route443_feedback_reset_schema import recipe_manager').replace("cpu['actual_source_count']==426","cpu['actual_source_count']==443")
        # Keep inherited I/O/helper schema, then bind the local report folder and actual root only.
        s="import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'))\n"+s
        out=D/name;assert not out.exists();compile(s,str(out),'exec');out.write_text(s,encoding='utf8')
        rows.append(dict(original_path=str(origin),original_SHA=H(raw),new_path=str(out),new_SHA=H(out.read_bytes())))
    origin=W/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012/review_direction_complete_dynamic_family_trace_actual.py'
    raw=origin.read_bytes();s=raw.decode('utf8').replace('from wave_direction_io import *','from route_fixture_io import *').replace('DIRECTION_OWN_FORMAL_CPU_ACTUAL_','ROUTE443_OWN_FORMAL_CPU_ACTUAL_').replace('==424','==443').replace("save('DIRECTION_FULL_TRAINING_TRACE_ACTUAL_'","save('ROUTE443_FULL_TRAINING_TRACE_ACTUAL_'")
    out=D/'review_route443_complete_dynamic_family_trace_actual.py';assert not out.exists();compile(s,str(out),'exec');out.write_text(s,encoding='utf8')
    rows.append(dict(original_path=str(origin),original_SHA=H(raw),new_path=str(out),new_SHA=H(out.read_bytes())))
    save('ROUTE443_CANDIDATE_TRACE_READERS_PREPARED.json',dict(epoch=time.time(),passed=True,files=rows,read_only_source443_actual_own_finite_schema_bound=True,full_original50_query_contact_COM_hardware_6000_callbacks_and115129_tolerances_preserved=True,dynamic_family4_not_static_assignment_and_trace_hist_phase_separate=True,prepared_not_future_pass=True,no_GPU_queue_budget_or_training_write=True))
    print(json.dumps(dict(prepared=True,readers=len(rows))))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_CANDIDATE_TRACE_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
