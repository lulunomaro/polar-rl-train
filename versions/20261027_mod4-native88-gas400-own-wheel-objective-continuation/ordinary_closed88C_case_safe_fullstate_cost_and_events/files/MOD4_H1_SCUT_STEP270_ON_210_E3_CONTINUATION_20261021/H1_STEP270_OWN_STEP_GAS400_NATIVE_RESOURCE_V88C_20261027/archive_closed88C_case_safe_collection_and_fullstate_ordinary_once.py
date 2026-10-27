"""Ordinary closed88C supplement; existing unique88 trial/tag never repeated."""
from pathlib import Path
import importlib.util, json, time, traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=N/'archive_actual88C_two_new_Pi_hourly_handoff_ordinary_unused_once.py'
sp=importlib.util.spec_from_file_location('consumed_ordinary88C_definitions_only_for_new_closure',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("'ordinary_actual88C_reset_two_NEW_Pi_hourly_handoff'","'ordinary_closed88C_case_safe_fullstate_cost_and_events'")
patch("nr/'ACTUAL88C_TWO_NEW_PI_HOURLY_ORDINARY_GIT_NOTE.md'","nr/'CLOSED88C_CASE_SAFE_FULLSTATE_ORDINARY_GIT_NOTE.md'")
patch("nr/'ACTUAL88C_HOURLY_ORDINARY_ARCHIVE_STARTED_ACTUAL.json'","nr/'CLOSED88C_CASE_SAFE_FULLSTATE_ORDINARY_ARCHIVE_STARTED_ACTUAL.json'")
ns={'__name__':'closed88C_case_safe_ordinary_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='1121f1e55050063119622e608168728cc6e43493' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1461
 assert git('rev-parse','trial-20261027-mod4-native88-gas400-own-wheel-objective-continuation')=='f64656b2a31d6f3c4e4ced50262950ce8cbbd796'
 v=json.loads((R/'NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json').read_bytes())
 assert v['actual_finite_transport_returned'] and v['all_active_node_collection_passed'] and not v['collection_errors']
 assert (R/'CURRENT_CLOSED88C_ACTUAL_RESULTS_READER_REPAIR_AND_NEXT_DIAGNOSTIC_WORK_ORDER.json').is_file()
 prior=G/'versions/20261027_mod4-native88-gas400-own-wheel-objective-continuation'
 for p in [prior/'COMPLETE_FILE_CAPTURE_INDEX.json',prior/'ordinary_frozen_gas400_reset_bank17_next88C_plan/ORDINARY_CAPTURE_INDEX.json',prior/'ordinary_actual88C_reset_two_NEW_Pi_hourly_handoff/ORDINARY_CAPTURE_INDEX.json']:ns['prior'](p)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 note=(R/'CLOSED88C_ORDINARY_ARCHIVE_DESCRIPTION_SOURCE.txt').read_text('utf8')
 roots=[N]+[L/x for x in ['native88C_case_safe_missing_close_source_v1','native88C_initial_reader_name_dependency_repair_source_v1','native88C_fullstate_qualification_reader_repair_v2']]
 assert all(p.is_dir() for p in roots)
 for d in roots[1:]:assert (d/'INDEX_SHA256_ACTUAL.json').is_file(),'no mutable helper captured as frozen'
 extras=[W/'AGENTS.md',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v222.py']
 ns['run_stage']('fudan',roots,extras,note,'Preserve closed88C two native windows, case-safe collection and fullstate reader repair')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CLOSED88C_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_new_record_or_tag=True),f,indent=2)
  raise
