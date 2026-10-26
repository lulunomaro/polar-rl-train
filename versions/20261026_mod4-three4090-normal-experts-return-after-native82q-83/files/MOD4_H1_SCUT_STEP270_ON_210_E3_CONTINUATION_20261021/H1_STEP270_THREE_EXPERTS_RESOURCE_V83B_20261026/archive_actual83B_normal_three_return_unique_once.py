"""One real phase: preGO83 schema rejection and byte-exact83B normal-three return."""
from pathlib import Path
import json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py';s=engine.read_text('utf8')
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'","'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','normal83':'mod4-three4090-normal-experts-return-after-native82q-83'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'","nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("and '__pycache__' not in p.parts and not p.is_symlink()","and '__pycache__' not in p.parts and '.git' not in p.parts and not p.is_symlink()")
patch("'--kind','diagnostic'","'--kind','training'")
ns={'__name__':'normal83_archive_utilities_only','__file__':str(engine)};exec(compile(s,str(engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='877a3714e3f4a9d065c2317f5d04d9265b2b861a' and len(git('tag','--list').splitlines())==1453 and not git('status','--porcelain')
 prior=G/'versions/20261026_mod4-unisupermimic-h1-step270-single4090-convergence-test'
 for rel in ('COMPLETE_FILE_CAPTURE_INDEX.json','ordinary_closed81o_disk_relocation82q_native_first_policy/ORDINARY_CAPTURE_INDEX.json','ordinary_closed82q_native_manifest_gap_fudan_reference/ORDINARY_CAPTURE_INDEX.json'):ns['prior'](prior/rel)
 a=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert a['passed'] and a['actual_finite_returned']
 assert json.loads((R/'PREGO83_OWN_TWO_TARGETS_NO_NODE_GO_AND_PROCESSES_OUT_ACTUAL.json').read_bytes())['no_node_or_GO'] and json.loads((R/'PREGO83_ORIGINAL_SOURCE_OWNER_H1_ABSENT_NO_FEE_ACTUAL.json').read_bytes())['original83_owner_H1_roots_absent']
 note='''Restore all three normal production experts after the bounded native Uni-SuperMimic H1 pilot closes. H1 and E3 sources are qualified complete82Q, normalE2 source is qualified complete80. Native method checkpoints and unpublished final are not production sources. Independent source80 E2 terminal/model/cost and displaced82Q-native original error/terminal/allout/cost/resource checks remain distinct, with the original per-file copy loop and startup guards retained. Original single-writer owner/common/node code and independent charge_values unchanged.

New83 first actual upload passed E3 and E2 target SDK/source CPU checks but rejected E2 source authorization because the generated kind added the word same and did not match the exact guard schema. This was preGO: no owner/node/GO/fee. Preserve its original source/auth/error/partial and CPU receipts. New83B namespace corrects the source-auth schema and filenames; verifies exact83 partial roots no NODE/GO and own processes out before launching; passes actual all-three installed source/SDK/RSL/wholeCPU, actual copied payload disk25GiB/GPU/RAM, original valid_ready, three actual GO, UUID/exe/argv/create, and first complete PPO update each. Current fees and final qualification remain pending. This is no step270 or expert graduation claim.

Fresh source disk below25GiB was resolved by minimal authorized closed81O/82Q NPZ-only relocation: four files1401011746bytes, existing fullSHA verified at both ends and signed acknowledgments before source duplicate unlink. Complete transfer/controller text receipts retained; sourcefree27021983744 is a snapshot, actual post-copy25 guard passed. No PT/FINAL/model/source/error/cache deletion, no budget write or prior transfer replay.

All original physical/reward/action/PPO/FP32/clock/success/trace/retention/error-save and control functions retained. H1 V8 and read-only lifetime/landing journal unchanged; no Fudan reference, native model or T2-z deployment. No subagents. Preserve local discovery reader misses, nonfatal backslash-S warnings, an overly broad KeyError catch in a recovery negative fixture and its separate corrected AssertionError-only test, and monitor-writer numeric-keyword SyntaxError with newV2 source. Original false/error bytes remain. Existing heartbeat updated in place, no new monitor. One unique real stage; later closure reports ordinary supplements only.
'''
 roots=[T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026',N]
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in (137,138)]
 ns['run_stage']('normal83',roots,extras,note,'Restore H1 E2 E3 production after native82Q and fix preGO source-auth schema')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('UNIQUE_NORMAL83_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_repeat_record_tag=True),f,indent=2)
  raise
