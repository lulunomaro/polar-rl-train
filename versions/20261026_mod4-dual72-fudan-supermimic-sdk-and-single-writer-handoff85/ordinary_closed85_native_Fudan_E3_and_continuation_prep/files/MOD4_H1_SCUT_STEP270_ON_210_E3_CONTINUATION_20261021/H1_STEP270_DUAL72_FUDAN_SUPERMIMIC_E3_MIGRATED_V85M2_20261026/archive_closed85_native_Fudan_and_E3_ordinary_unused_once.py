from pathlib import Path
import importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';G=W/'polar-rl-train';R=N/'reports'
p=N/'archive_dual72_Fudan_SuperMimic_authority85_unique_once.py';sp=importlib.util.spec_from_file_location('unique85_defs_only',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)/'ordinary_closed85_native_Fudan_E3_and_continuation_prep'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL_ORDINARY_CLOSED85_NATIVE_FUDAN_E3_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ORDINARY_CLOSED85_NATIVE_FUDAN_E3_ARCHIVE_STARTED_ACTUAL.json'")
start=s.index(' def recgit(*args):');end=s.index(" head=git('rev-parse','HEAD');",start)
s=s[:start]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[end:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'closed85_ordinary_capture_only','__file__':str(m.m.engine)};exec(compile(s,str(m.m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='dca308bb4a7f050d9a6651dd8002375bda041a5f' and len(git('tag','--list').splitlines())==1456 and not git('status','--porcelain')
 ns['prior'](G/'versions/20261026_mod4-dual72-fudan-supermimic-sdk-and-single-writer-handoff85/COMPLETE_FILE_CAPTURE_INDEX.json')
 receipt=json.loads((R/'V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_RETURNED_ACTUAL.json').read_bytes());assert receipt['actual_finite_transport_returned'] and receipt['original_canonical_cost_settled']
 classification=R/'CLOSED85_ACTUAL_RESULTS_AND_NEXT_SOURCE_WORK_ORDER.json';assert classification.is_file()
 note='''Ordinary supplement to the already-consumed85 dual4090 Fudan/SuperMimic and single-authority trial, no record/tag. All actual closure/model/CPU/curve/failed reader results are preserved as returned; qualification and next-source limitations are in CLOSED85_ACTUAL_RESULTS_AND_NEXT_SOURCE_WORK_ORDER.json. Do not infer normal or native FINAL/skill success from this archive title. Fees are original72 writer actualGO-terminal independent sumonce, never refund/clamp/rewrite; old210tombstone and old83 histories remain. New current tensors/PT/raw are indexed only by actual path/bytes/existing producerSHA, with no model/native/GPU/host query for Git.

ReviewerV2 was never run. NewunusedV3 preserves original native review function exactly, adds original normalE3 terminal rc0/no-original-error/exactFINAL admission before the initial model load and persists the normalE3 one-load CPU result before independent native validation. Native failure cannot erase already obtained baseline qualification evidence; no model replay or relaxed source/success gate. The first local AST check accidentally compared modulebody index2, not the named function; original report is retained with later correct named-function AST evidence. All actual reader/schema/formatter/native errors remain unchanged.

Source-only next-native continuation preserves the actual85 publisher contract that replay was not saved, never claims exact replay/PhysX/episode restoration, and awaits qualified formalFINAL/wholeCPU/sourcecost/allout. Candidate newepisode+freshreplay refill does not silently reset native trainedWM/Pi/Critic/optimizer or global counters; future runtime/source admission remains necessary. Text-only curve parsing separates true completed-control physical events from loss and genericvelocity metrics, respects missing/null/partial coverage and interval-censored firstpositive time. Source-only threeGPU planning does not add a node to a running pair or start a secondwriter. No automaticT2z/otherweights/GUI/localpolicy rollout. All saved source/failed fixtures/reports/fullUTF8/monitors captured, active helpers listedpending until frozen if necessary; later additions ordinary on actualHEAD. PostGit verification remains conversation-only.
'''
 roots=[N,J/'agent_native_Fudan_continuation86_cpu',J/'agent_closed85_native_curve_analysis_cpu',J/'agent_threeGPU_native_continuation86_protocol_cpu',J/'agent_Fudan_SuperMimic_zero_takeoff_rootcause_cpu_20261026',J/'agent_Fudan_SuperMimic_phase_replay_starvation_cpu_20261026',J/'root_Fudan_SuperMimic_objective_source_CPU_20261026',J/'root_Fudan_SuperMimic_actual_WM_sensitivity_20261026']
 extras=[N/'archive_closed85_native_Fudan_and_E3_ordinary_unused_once.py']
 ns['run_stage']('fudan',roots,extras,note,'Record closed Fudan-native85 results and prepare truthful continuation')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORDINARY_CLOSED85_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_second_record_or_tag=True,resume_existing_commit_if_push_failed=True),f,indent=2)
  raise
