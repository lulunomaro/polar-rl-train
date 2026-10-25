"""Unique real73 stage: preserve rejected73a plus fixed actual73b, no old once replay."""
from pathlib import Path
import json,time,tomllib,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';A=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V73_20261025'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
s=engine.read_text('utf8');a="'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'";assert s.count(a)==1;s=s.replace(a,a+",'continuation73':'mod4-three4090-closed72-e2-samebackend-install-fix73'")
a="nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'";assert s.count(a)==1;s=s.replace(a,"nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V73B_20261025'/'reports'")
a="'--kind','diagnostic'";assert s.count(a)==1;s=s.replace(a,"'--kind','training'")
ns={'__name__':'stage73_archive_utilities_only','__file__':str(engine)};exec(compile(s,str(engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='8c7a5476d75acbb995a5379354761d8621935565' and not git('status','--porcelain') and len(git('tag','--list').splitlines())==1444
 first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
 a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353' and a['prompt']==(R/'CURRENT_ACTUAL73B_THREE4090_MONITOR_SOURCE.txt').read_text('utf8')
 for p in [G/'versions/20261025_mod4-three4090-h1-v7-e2-e3-training72/COMPLETE_FILE_CAPTURE_INDEX.json',G/'versions/20261025_mod4-three4090-h1-v7-e2-e3-training72/ordinary_closed72_three_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json',G/'versions/20261025_mod4-step270-closed70-http-channel-lifetime-fix71/COMPLETE_FILE_CAPTURE_INDEX.json']:
  ns['prior'](p)
 note="""Continue all three4090 experts from the three complete72 fullstate models after actual original writer closure. H1 complete132/Adam800880, E2 complete88/841680 and E3 complete83/842500 passed twohost SHA and CPU finite/17Adam x20/actor9 includingSTD/critic8/clock checks; original72 sumonce10940.542178869247s, closing712152.5117254257 snapshot, all normal duration flags true and all original processes/canonical/locks closed. Full72 original control-error files0 each. Its new saved-only48control replay across20k has273 takeoff increments but no crossing/landing/recovery;99 selected cases, no qualified same-episode takeoff/270clearance case. Kinematics is not physical reintegration, whole-window or frozen skill evaluation; no V7 improvement/regression or270mm graduation claimed. Closed72 reports were archived in a prior ordinary supplement without retagging.

New73a actual preGO attempt rejected the E2 target72 root because legacy two50 installer selects210 durable by key=e2. It rejected before E2mkdir/owner/node/GO, after E3 CPU-only install, and had no new fee. Original73a source/partial/error and source-only V1..V3 guards/binders, exact prebind histories, local reader mistakes,21 metadata/AST and26 actual valid_ready synthetic fixtures retained. No same once/root replay. New73b fresh namespace fixes only this installation scope with exact target72 E2 UUID, actual closed72 complete source/normal cost/real old terminal and childrenwaited, old partial no-GO/no-node checks, original private/shared locks and GPU/RAM/disk guards. Original complete file-copy loop and its source producer/path checks are byteexact. Those210 legacy47/49 E2 paths do not describe the now-completed72 source. H1/E3 controllers, physics, reward, PPO and original writer are unchanged.

Actual73b all three installed source/SDK/RSL/wholeCPU/resource-after-copy/valid_ready/GO/first complete PPO updates passed, with distinct own UUIDs and exact identities. This is a running snapshot, no final-model/skill/continuous-alive claim. H1 sameV7 near-edge reward-only gate continues; E2/E3 both50Hz same-backend72 from72 complete sources. Original one canonical writer charges independent actual GO-to-terminal intervals under11700 reserve and86412.86069250107 strict guard; no new budget extension, refund, copied/cleared canonical, second writer or live runtime patch. Credentials remain memory/stdin only. No subagents, unknown-peer interference, extra model download or automatic T2-z training.

All saved sources, failed/unused namespaces, CPU source tests, installed receipts, actual GO-PPO, final collector protocol and active hourly monitor are captured in full. Large binaries retain only real paths,bytes,existing producer SHA; no model/raw/USD/GPU/host query for Git. Unique new stage; future reports append ordinary commits.
"""
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(111,114)]+[engine,W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/deploy_two50_reconciled_original_writer_once.py']
 ns['run_stage']('continuation73',[A,N],extras,note,'Continue H1 V7 E2 E3 from complete72 and fix E2 target72 installation scope')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ARCHIVE73_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeat_trial_tag_or_training=True),f,ensure_ascii=False,indent=2)
  raise
